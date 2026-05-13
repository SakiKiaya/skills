#!/usr/bin/env python3
"""
dotnet-analysis-chunker v0.8.3

Step 1 of problem 3:
- Add analysis_chunks split output.
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

def method_key(method: dict[str, Any]) -> str:
    return safe_id(f"{method.get('source','unknown')}::{method.get('name','method')}::{method.get('line','')}")

def main(analysis_dir: str, chunks_dir: str) -> int:
    analysis = Path(analysis_dir)
    out = Path(chunks_dir)
    out.mkdir(parents=True, exist_ok=True)

    projects = load(analysis / "projects.json", [])
    dependencies = load(analysis / "dependencies.json", [])
    methods = load(analysis / "methods.json", [])
    method_purposes = load(analysis / "method_purposes.json", [])
    events = load(analysis / "events.json", [])
    event_flows = load(analysis / "event_flows.json", [])
    configuration = load(analysis / "configuration.json", {"files": [], "code_references": []})
    external_dependencies = load(analysis / "external_dependencies.json", [])
    workflows = load(analysis / "user_workflows.json", [])
    risks = load(analysis / "risks.json", [])

    index = {
        "version": "0.8.3",
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
    for i, d in enumerate(dependencies):
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
