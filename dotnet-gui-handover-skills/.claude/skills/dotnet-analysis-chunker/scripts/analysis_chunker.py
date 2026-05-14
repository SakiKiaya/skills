#!/usr/bin/env python3
"""
dotnet-analysis-chunker v1.0

Step 1 of problem 3:
- Add analysis_chunks split output.
- Add source-file and large-file task chunks for files over 1000 lines.
- Prefer class, method, and switch-aware large-file task splitting.
- Do not change final docs generator yet.

Usage:
    python analysis_chunker.py exports/enterprise_analysis exports/analysis_chunks
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys
from typing import Any

LARGE_FILE_LINE_THRESHOLD = 1000
LARGE_FILE_TASK_LINES = 800
OVERLAP_CONTEXT_LINES = 10
CHUNK_FOLDERS = [
    "source_files",
    "large_file_tasks",
    "projects",
    "methods",
    "event_flows",
    "forms",
    "dependencies",
    "configs",
    "risks",
]

def load(path: Path, default: Any):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def write(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def clean_generated_chunks(out: Path):
    for folder in CHUNK_FOLDERS:
        chunk_dir = out / folder
        if chunk_dir.exists():
            for path in chunk_dir.glob("*.json"):
                path.unlink()
    index_path = out / "index.json"
    if index_path.exists():
        index_path.unlink()

def safe_id(value: Any) -> str:
    s = str(value or "unknown")
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")
    return s[:180] or "unknown"

def source_refs_from(obj: Any) -> list[str]:
    refs = set()
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                lk = str(k).lower()
                if lk in {"source", "source_file", "path", "project_file"} and isinstance(v, str):
                    refs.add(v)
                else:
                    walk(v)
        elif isinstance(x, list):
            for i in x:
                walk(i)
    walk(obj)
    return sorted(refs)

def make_chunk(chunk_type: str, chunk_id: str, title: str, data: Any, summary: str = "", related: list[str] | None = None):
    return {
        "chunk_type": chunk_type,
        "chunk_id": chunk_id,
        "title": title,
        "summary": summary,
        "source_refs": source_refs_from(data),
        "data": data,
        "related_chunks": related or [],
    }

def dependency_name(value: Any) -> str:
    return str(value or "").split(",", 1)[0].strip()

def is_system_reference(dep: dict[str, Any]) -> bool:
    name = dependency_name(dep.get("target"))
    return dep.get("type") == "Reference" and (name == "System" or name.startswith("System."))

def method_key(method: dict[str, Any]) -> str:
    return safe_id(f"{method.get('source','unknown')}::{method.get('name','method')}::{method.get('line','')}")

def line_value(item: dict[str, Any]) -> int:
    try:
        return int(item.get("line") or 0)
    except (TypeError, ValueError):
        return 0

def int_value(item: dict[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(item.get(key) or default)
    except (TypeError, ValueError):
        return default

def ranges_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start <= b_end and b_start <= a_end

def context_range(start_line: int, end_line: int, total_lines: int) -> dict[str, int]:
    return {
        "start": max(1, start_line - OVERLAP_CONTEXT_LINES),
        "end": min(total_lines, end_line + OVERLAP_CONTEXT_LINES),
    }

def line_windows(line_count: int, window_size: int = LARGE_FILE_TASK_LINES) -> list[tuple[int, int]]:
    if line_count <= 0:
        return []
    windows = []
    start = 1
    while start <= line_count:
        end = min(start + window_size - 1, line_count)
        windows.append((start, end))
        start = end + 1
    return windows

def line_windows_for_range(start_line: int, end_line: int, window_size: int = LARGE_FILE_TASK_LINES) -> list[tuple[int, int]]:
    if start_line > end_line:
        return []
    windows = []
    start = start_line
    while start <= end_line:
        end = min(start + window_size - 1, end_line)
        windows.append((start, end))
        start = end + 1
    return windows

def block_start(block: dict[str, Any]) -> int:
    return int_value(block, "start_line", int_value(block, "line"))

def block_end(block: dict[str, Any]) -> int:
    return int_value(block, "end_line", block_start(block))

def block_size(start_line: int, end_line: int) -> int:
    return max(0, end_line - start_line + 1)

SCOPE_CHILD_PRIORITIES: dict[str, list[set[str]]] = {
    "file": [{"class"}],
    "class": [{"region", "method"}],
    "region": [{"method"}, {"switch", "if", "try"}],
    "method": [{"region"}, {"switch", "if", "try"}],
    "switch": [{"if", "try"}],
    "if": [{"try"}],
    "try": [{"switch", "if"}],
}

def sorted_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(blocks, key=lambda b: (block_start(b), block_end(b), str(b.get("kind")), str(b.get("name"))))

def priority_child_blocks(
    blocks: list[dict[str, Any]],
    start_line: int,
    end_line: int,
    priority_levels: list[set[str]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected_ranges: list[tuple[int, int]] = []
    for kinds in priority_levels:
        candidates = []
        for block in blocks:
            b_start = block_start(block)
            b_end = block_end(block)
            if block.get("kind") not in kinds:
                continue
            if not (start_line <= b_start <= end_line and b_end <= end_line):
                continue
            if b_start == start_line and b_end == end_line:
                continue
            if any(ranges_overlap(b_start, b_end, s, e) for s, e in selected_ranges):
                continue
            candidates.append(block)
        for child in sorted_blocks(candidates):
            c_start = block_start(child)
            c_end = block_end(child)
            if any(ranges_overlap(c_start, c_end, s, e) for s, e in selected_ranges):
                continue
            selected.append(child)
            selected_ranges.append((c_start, c_end))
    return sorted_blocks(selected)

def covering_semantic_blocks(
    blocks: list[dict[str, Any]],
    start_line: int,
    end_line: int,
    kinds: set[str],
) -> list[dict[str, Any]]:
    covering = []
    span = block_size(start_line, end_line)
    for block in blocks:
        b_start = block_start(block)
        b_end = block_end(block)
        overlap = max(0, min(end_line, b_end) - max(start_line, b_start) + 1)
        contains_range = b_start <= start_line and end_line <= b_end
        mostly_overlaps_range = span > 0 and overlap / span >= 0.5
        if block.get("kind") in kinds and (contains_range or mostly_overlaps_range):
            covering.append(block)
    return sorted(covering, key=lambda b: (block_size(block_start(b), block_end(b)), block_start(b), block_end(b)))

def merge_semantic_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    merged = []
    for block in sorted_blocks([b for b in blocks if b]):
        key = (block.get("kind"), block.get("source"), block_start(block), block_end(block), block.get("name"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(block)
    return merged

def fallback_task_specs(
    start_line: int,
    end_line: int,
    reason: str,
    semantic_blocks: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    return [
        {
            "line_range": {"start": start, "end": end},
            "split_strategy": reason,
            "semantic_blocks": merge_semantic_blocks(semantic_blocks or []),
        }
        for start, end in line_windows_for_range(start_line, end_line)
    ]

def split_semantic_range(
    start_line: int,
    end_line: int,
    scope_kind: str,
    blocks: list[dict[str, Any]],
    scope_block: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if start_line > end_line:
        return []

    if block_size(start_line, end_line) <= LARGE_FILE_TASK_LINES:
        semantic_blocks = [scope_block] if scope_block else []
        return [{
            "line_range": {"start": start_line, "end": end_line},
            "split_strategy": f"{scope_kind}_aware",
            "semantic_blocks": semantic_blocks,
        }]

    children = priority_child_blocks(blocks, start_line, end_line, SCOPE_CHILD_PRIORITIES.get(scope_kind, []))
    if not children:
        return fallback_task_specs(
            start_line,
            end_line,
            f"{scope_kind}_line_window_fallback",
            [scope_block] if scope_block else [],
        )

    specs = []
    cursor = start_line
    for child in children:
        child_start = block_start(child)
        child_end = block_end(child)
        if cursor < child_start:
            gap_end = child_start - 1
            gap_blocks = ([scope_block] if scope_block else []) + covering_semantic_blocks(
                blocks,
                cursor,
                gap_end,
                {"region", "method", "switch", "if", "try"},
            )
            specs.extend(fallback_task_specs(cursor, gap_end, f"{scope_kind}_gap_fallback", gap_blocks))
        specs.extend(split_semantic_range(child_start, child_end, str(child.get("kind") or "block"), blocks, child))
        cursor = max(cursor, child_end + 1)
    if cursor <= end_line:
        gap_blocks = ([scope_block] if scope_block else []) + covering_semantic_blocks(
            blocks,
            cursor,
            end_line,
            {"region", "method", "switch", "if", "try"},
        )
        specs.extend(fallback_task_specs(cursor, end_line, f"{scope_kind}_gap_fallback", gap_blocks))
    return specs

def main(analysis_dir: str, chunks_dir: str) -> int:
    analysis = Path(analysis_dir)
    out = Path(chunks_dir)
    out.mkdir(parents=True, exist_ok=True)
    clean_generated_chunks(out)

    projects = load(analysis / "projects.json", [])
    dependencies = load(analysis / "dependencies.json", [])
    source_files = load(analysis / "source_files.json", [])
    source_blocks = load(analysis / "source_blocks.json", [])
    methods = load(analysis / "methods.json", [])
    method_purposes = load(analysis / "method_purposes.json", [])
    events = load(analysis / "events.json", [])
    event_flows = load(analysis / "event_flows.json", [])
    configuration = load(analysis / "configuration.json", {"files": [], "code_references": []})
    external_dependencies = load(analysis / "external_dependencies.json", [])
    workflows = load(analysis / "user_workflows.json", [])
    risks = load(analysis / "risks.json", [])

    index = {
        "version": "1.0.0",
        "source_analysis_dir": str(analysis),
        "chunks_dir": str(out),
        "counts": {},
        "chunks": []
    }

    def add_index(chunk):
        index["chunks"].append({
            "chunk_type": chunk["chunk_type"],
            "chunk_id": chunk["chunk_id"],
            "title": chunk["title"],
            "path": f"{chunk['chunk_type']}s/{chunk['chunk_id']}.json" if chunk["chunk_type"] not in {"config", "risk"} else f"{chunk['chunk_type']}s/{chunk['chunk_id']}.json",
            "source_refs": chunk.get("source_refs", []),
            "related_chunks": chunk.get("related_chunks", []),
        })

    # Build lookup
    methods_by_name: dict[str, list[dict[str, Any]]] = {}
    for m in methods:
        methods_by_name.setdefault(m.get("name"), []).append(m)

    purposes_by_method: dict[str, list[dict[str, Any]]] = {}
    for p in method_purposes:
        purposes_by_method.setdefault(p.get("method"), []).append(p)

    events_by_handler: dict[str, list[dict[str, Any]]] = {}
    for e in events:
        events_by_handler.setdefault(e.get("handler"), []).append(e)

    flows_by_handler: dict[str, list[dict[str, Any]]] = {}
    for f in event_flows:
        flows_by_handler.setdefault(f.get("handler"), []).append(f)

    deps_by_project: dict[str, list[dict[str, Any]]] = {}
    for d in dependencies:
        deps_by_project.setdefault(d.get("project"), []).append(d)

    risks_by_source: dict[str, list[dict[str, Any]]] = {}
    for r in risks:
        risks_by_source.setdefault(r.get("source"), []).append(r)

    methods_by_source: dict[str, list[dict[str, Any]]] = {}
    for m in methods:
        methods_by_source.setdefault(m.get("source"), []).append(m)

    events_by_source: dict[str, list[dict[str, Any]]] = {}
    for e in events:
        events_by_source.setdefault(e.get("source"), []).append(e)

    blocks_by_source: dict[str, list[dict[str, Any]]] = {}
    for b in source_blocks:
        blocks_by_source.setdefault(b.get("source"), []).append(b)

    # Source file chunks
    for sf in source_files:
        path = sf.get("path")
        cid = safe_id(path)
        related = [f"method:{method_key(m)}" for m in methods_by_source.get(path, [])]
        sfdata = {
            "source_file": sf,
            "source_blocks": sorted(blocks_by_source.get(path, []), key=lambda b: (block_start(b), block_end(b))),
            "methods": sorted(methods_by_source.get(path, []), key=line_value),
            "events": sorted(events_by_source.get(path, []), key=line_value),
            "risk_candidates": risks_by_source.get(path, []),
        }
        chunk = make_chunk(
            "source_file",
            cid,
            f"Source File: {path}",
            sfdata,
            "Source-file chunk for file-level ownership, size, methods, events, and risks.",
            related,
        )
        write(out / "source_files" / f"{cid}.json", chunk)
        add_index(chunk)

    # Large file task chunks
    for sf in source_files:
        path = sf.get("path")
        try:
            total_lines = int(sf.get("line_count") or 0)
        except (TypeError, ValueError):
            total_lines = 0
        if total_lines <= LARGE_FILE_LINE_THRESHOLD:
            continue

        source_methods = sorted(methods_by_source.get(path, []), key=line_value)
        source_events = sorted(events_by_source.get(path, []), key=line_value)
        source_blocks_for_file = sorted(blocks_by_source.get(path, []), key=lambda b: (block_start(b), block_end(b)))
        source_related = [f"source_file:{safe_id(path)}"]
        task_specs = split_semantic_range(1, total_lines, "file", source_blocks_for_file)
        for task_no, spec in enumerate(task_specs, start=1):
            start_line = spec["line_range"]["start"]
            end_line = spec["line_range"]["end"]
            context = context_range(start_line, end_line, total_lines)
            task_methods = [
                m for m in source_methods
                if ranges_overlap(start_line, end_line, line_value(m), int_value(m, "end_line", line_value(m)))
            ]
            task_events = [e for e in source_events if start_line <= line_value(e) <= end_line]
            related = source_related + [f"method:{method_key(m)}" for m in task_methods]
            task = {
                "source_file": sf,
                "task_no": task_no,
                "line_range": {"start": start_line, "end": end_line},
                "context_line_range": context,
                "context_before_lines": start_line - context["start"],
                "context_after_lines": context["end"] - end_line,
                "split_reason": f"File has {total_lines} lines, exceeding the {LARGE_FILE_LINE_THRESHOLD}-line threshold.",
                "task_strategy": spec["split_strategy"],
                "semantic_blocks": spec["semantic_blocks"],
                "methods": task_methods,
                "events": task_events,
                "risk_candidates": risks_by_source.get(path, []),
                "review_goals": [
                    "Summarize responsibilities in this line range.",
                    "Identify event handlers, side effects, device/config/database interactions, and maintenance risks.",
                    "Link findings back to related method, event-flow, form, and source-file chunks.",
                ],
            }
            cid = safe_id(f"{path}::lines_{start_line}_{end_line}")
            chunk = make_chunk(
                "large_file_task",
                cid,
                f"Large File Task: {path} lines {start_line}-{end_line}",
                task,
                "Task chunk for reviewing a large source file in a bounded line range.",
                related,
            )
            write(out / "large_file_tasks" / f"{cid}.json", chunk)
            add_index(chunk)

    # Project chunks
    for p in projects:
        cid = safe_id(p.get("name"))
        pdata = {
            "project": p,
            "dependencies": deps_by_project.get(p.get("name"), []),
            "related_methods": [m for m in methods if str(m.get("source", "")).startswith(str(p.get("name", "")))],
            "external_dependency_candidates": [
                e for e in external_dependencies
                if e.get("project") == p.get("name") or p.get("name") in str(e)
            ],
            "risk_candidates": [
                r for r in risks
                if p.get("path") == r.get("source") or p.get("name") in str(r)
            ],
        }
        chunk = make_chunk("project", cid, f"Project: {p.get('name')}", pdata, "Project-level chunk for module responsibility and dependencies.")
        write(out / "projects" / f"{cid}.json", chunk)
        add_index(chunk)

    # Method chunks
    for m in methods:
        cid = method_key(m)
        name = m.get("name")
        mdata = {
            "method": m,
            "purpose_analysis": purposes_by_method.get(name, []),
            "event_triggers": events_by_handler.get(name, []),
            "event_flows": flows_by_handler.get(name, []),
            "callers": m.get("called_by", []),
            "callees": m.get("calls", []),
            "risk_candidates": risks_by_source.get(m.get("source"), []),
        }
        related = []
        for callee in m.get("calls", []) or []:
            for cm in methods_by_name.get(callee, []):
                related.append(f"method:{method_key(cm)}")
        chunk = make_chunk("method", cid, f"Method: {name}", mdata, "Method-level chunk for purpose, flow, side effects, and maintenance notes.", related)
        write(out / "methods" / f"{cid}.json", chunk)
        add_index(chunk)

    # Event flow chunks
    for i, f in enumerate(event_flows):
        cid = safe_id(f"{i:04d}_{f.get('entry')}_{f.get('handler')}")
        handler = f.get("handler")
        fdata = {
            "event_flow": f,
            "handler_methods": methods_by_name.get(handler, []),
            "method_purpose": purposes_by_method.get(handler, []),
            "related_events": events_by_handler.get(handler, []),
            "workflow_candidates": [w for w in workflows if handler in str(w) or f.get("entry") in str(w)],
        }
        related = [f"method:{method_key(m)}" for m in methods_by_name.get(handler, [])]
        chunk = make_chunk("event_flow", cid, f"Event Flow: {f.get('entry')} -> {handler}", fdata, "Event-flow chunk for single user action or UI event.", related)
        write(out / "event_flows" / f"{cid}.json", chunk)
        add_index(chunk)

    # Form chunks inferred from event/control names if full form model is not available
    form_names = set()
    for e in events:
        src = str(e.get("source") or "")
        form_names.add(Path(src).stem.replace(".Designer", ""))
    for f in event_flows:
        src = str(f.get("source") or "")
        if src:
            form_names.add(Path(src).stem.replace(".Designer", ""))

    for form in sorted(x for x in form_names if x and x != "unknown"):
        cid = safe_id(form)
        form_events = [e for e in events if form in str(e.get("source", "")) or form in str(e)]
        form_flows = [f for f in event_flows if form in str(f.get("source", "")) or form in str(f)]
        handlers = {e.get("handler") for e in form_events} | {f.get("handler") for f in form_flows}
        form_methods = []
        for h in handlers:
            form_methods.extend(methods_by_name.get(h, []))
        fdata = {
            "form_name": form,
            "events": form_events,
            "event_flows": form_flows,
            "handler_methods": form_methods,
            "risk_candidates": [r for r in risks if form in str(r)],
        }
        related = []
        for m in form_methods:
            related.append(f"method:{method_key(m)}")
        chunk = make_chunk("form", cid, f"Form: {form}", fdata, "Form-level chunk for UI responsibility and event analysis.", related)
        write(out / "forms" / f"{cid}.json", chunk)
        add_index(chunk)

    # Dependency chunks
    system_dependencies = [d for d in dependencies if is_system_reference(d)]
    regular_dependencies = [d for d in dependencies if not is_system_reference(d)]

    if system_dependencies:
        data = {
            "dependency_group": "System References",
            "count": len(system_dependencies),
            "dependencies": system_dependencies,
        }
        chunk = make_chunk(
            "dependency",
            "0000_System_References",
            "Dependency Group: System References",
            data,
            "Aggregated framework references from System.* assemblies.",
        )
        write(out / "dependencies" / "0000_System_References.json", chunk)
        add_index(chunk)

    offset = 1 if system_dependencies else 0
    for i, d in enumerate(regular_dependencies, start=offset):
        cid = safe_id(f"{i:04d}_{d.get('project')}_{d.get('target')}")
        chunk = make_chunk("dependency", cid, f"Dependency: {d.get('project')} -> {d.get('target')}", d, "Dependency chunk.")
        write(out / "dependencies" / f"{cid}.json", chunk)
        add_index(chunk)

    for i, d in enumerate(external_dependencies):
        cid = safe_id(f"external_{i:04d}_{d.get('dependency_type') or d.get('name')}")
        chunk = make_chunk("dependency", cid, f"External Dependency: {d.get('dependency_type') or d.get('name')}", d, "External dependency candidate chunk.")
        write(out / "dependencies" / f"{cid}.json", chunk)
        add_index(chunk)

    # Config chunks
    for i, f in enumerate(configuration.get("files", [])):
        cid = safe_id(f"config_file_{i:04d}_{f.get('path')}")
        chunk = make_chunk("config", cid, f"Config File: {f.get('path')}", f, "Configuration file chunk.")
        write(out / "configs" / f"{cid}.json", chunk)
        add_index(chunk)

    for i, r in enumerate(configuration.get("code_references", [])):
        cid = safe_id(f"config_ref_{i:04d}_{r.get('source')}_{r.get('line')}")
        chunk = make_chunk("config", cid, f"Config Reference: {r.get('source')}:{r.get('line')}", r, "In-code configuration reference chunk.")
        write(out / "configs" / f"{cid}.json", chunk)
        add_index(chunk)

    # Risk chunks
    for i, r in enumerate(risks):
        cid = safe_id(f"risk_{i:04d}_{r.get('risk_type')}_{r.get('source')}")
        chunk = make_chunk("risk", cid, f"Risk: {r.get('risk_type')}", r, "Maintainability or architecture risk chunk.")
        write(out / "risks" / f"{cid}.json", chunk)
        add_index(chunk)

    # Write index
    counts = {}
    for item in index["chunks"]:
        counts[item["chunk_type"]] = counts.get(item["chunk_type"], 0) + 1
    index["counts"] = counts
    write(out / "index.json", index)

    print(f"Wrote analysis chunks to {out}")
    for k, v in sorted(counts.items()):
        print(f"- {k}: {v}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: analysis_chunker.py <enterprise_analysis_dir> <analysis_chunks_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
