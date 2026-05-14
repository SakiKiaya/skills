#!/usr/bin/env python3
"""
dotnet-chunk-aware-doc-generator v1.0

Generate final 01-09 enterprise GUI handover docs from:
- exports/enterprise_analysis
- exports/analysis_chunks
- docs/chunks

Usage:
    python generate_chunk_aware_docs.py exports/enterprise_analysis exports/analysis_chunks docs/chunks docs
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sys
from typing import Any

LIMIT_INLINE_CHUNKS = 20

def load(path: Path, default: Any):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def read_md(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""

def esc(v: Any) -> str:
    if v in (None, ""):
        return "N/A"
    s = str(v).replace("\n", " ").replace("|", "\\|")
    return s[:1200] + "..." if len(s) > 1200 else s

def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(out) + "\n"

def rel_link(from_doc_dir: Path, target: Path) -> str:
    try:
        return target.relative_to(from_doc_dir).as_posix()
    except Exception:
        try:
            return target.as_posix()
        except Exception:
            return str(target)

def list_chunk_json(chunks_dir: Path, folder: str):
    d = chunks_dir / folder
    return sorted([p for p in d.glob("*.json") if p.name != "index.json"]) if d.exists() else []

def chunk_md_path(docs_chunks_dir: Path, chunk: dict[str, Any]) -> Path:
    ctype = chunk.get("chunk_type")
    folder = {
        "project": "projects",
        "form": "forms",
        "event_flow": "event_flows",
        "method": "methods",
        "dependency": "dependencies",
        "config": "configs",
        "risk": "risks",
        "source_file": "source_files",
        "large_file_task": "large_file_tasks",
    }.get(ctype, f"{ctype}s")
    return docs_chunks_dir / folder / f"{chunk.get('chunk_id')}.md"

def load_chunk(path: Path):
    return load(path, {})

def project_graph(project_chunks: list[dict[str, Any]]):
    lines = ["```mermaid", "graph TD"]
    if not project_chunks:
        lines.append('  A["No project chunks found"]')
    for c in project_chunks:
        p = (c.get("data") or {}).get("project", {})
        pid = "P_" + safe_id(p.get("name"))
        lines.append(f'  {pid}["{esc(p.get("name"))}<br/>{esc(p.get("language"))}"]')
        for d in (c.get("data") or {}).get("dependencies", []):
            if d.get("type") == "ProjectReference":
                tid = "P_" + safe_id(Path(str(d.get("target") or d.get("include") or "Unknown")).stem)
                lines.append(f"  {pid} --> {tid}")
    lines.append("```")
    return "\n".join(lines)

def safe_id(v):
    return "".join(ch if ch.isalnum() else "_" for ch in str(v or "Unknown"))

def architecture_graph(project_chunks, dep_chunks):
    lines = ["```mermaid", "graph TD"]
    lines.extend([
        '  User["User / Operator"]',
        '  UI["GUI Layer"]',
        '  Logic["Application / Service Layer"]',
        '  Data["Data / Repository Layer"]',
        '  Device["External Device / SDK Layer"]',
        '  Config["Configuration"]',
        '  User --> UI',
        '  UI --> Logic',
        '  Logic --> Data',
        '  Logic --> Device',
        '  UI --> Config',
        '  Logic --> Config',
    ])
    for c in project_chunks:
        p = (c.get("data") or {}).get("project", {})
        pid = "P_" + safe_id(p.get("name"))
        if p.get("is_gui"):
            lines.append(f'  UI --> {pid}["{esc(p.get("name"))}"]')
        else:
            lines.append(f'  Logic --> {pid}["{esc(p.get("name"))}"]')
    for c in dep_chunks[:25]:
        d = c.get("data") or {}
        name = d.get("dependency_type") or d.get("name") or d.get("target")
        if name:
            did = "D_" + safe_id(name)
            lines.append(f'  Device -.-> {did}["{esc(name)}"]')
    lines.append("```")
    return "\n".join(lines)

def extract_chunk_summary(chunk: dict[str, Any]):
    return [
        chunk.get("chunk_id"),
        chunk.get("title"),
        chunk.get("summary"),
        ", ".join(chunk.get("source_refs") or []),
        ", ".join(chunk.get("related_chunks") or []),
    ]

def include_chunk_md_section(docs_dir: Path, docs_chunks_dir: Path, chunk: dict[str, Any], max_chars=5000):
    md_path = chunk_md_path(docs_chunks_dir, chunk)
    if not md_path.exists():
        return ""
    text = read_md(md_path)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n> Content truncated. See full chunk doc.\n"
    link = rel_link(docs_dir, md_path)
    return f"\n### [{esc(chunk.get('title'))}]({link})\n\n{text}\n"

def chunk_link(docs_dir: Path, docs_chunks_dir: Path, chunk: dict[str, Any], label: Any | None = None) -> str:
    md_path = chunk_md_path(docs_chunks_dir, chunk)
    text = esc(label if label is not None else chunk.get("chunk_id"))
    if not md_path.exists():
        return text
    return f"[{text}]({rel_link(docs_dir, md_path)})"

def method_data(chunk: dict[str, Any]) -> dict[str, Any]:
    return (chunk.get("data") or {}).get("method") or {}

def method_label(method: dict[str, Any]) -> str:
    name = method.get("name") or "Unknown"
    source = method.get("source") or "Unknown"
    return f"{source}::{name}"

def method_graph(method_chunks: list[dict[str, Any]], event_flow_chunks: list[dict[str, Any]]) -> str:
    lines = ["```mermaid", "flowchart TD"]
    edges: set[tuple[str, str]] = set()
    nodes: dict[str, str] = {}

    def node_id(name: Any) -> str:
        key = str(name or "Unknown")
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]
        nodes.setdefault(key, f"M_{safe_id(key)}_{digest}")
        return nodes[key]

    def add_edge(src: Any, dst: Any):
        if not src or not dst or src == dst:
            return
        edges.add((str(src), str(dst)))

    for c in event_flow_chunks:
        flow = (c.get("data") or {}).get("event_flow") or {}
        add_edge(flow.get("entry"), flow.get("handler"))

    for c in method_chunks:
        m = method_data(c)
        source = str(m.get("source") or "")
        if "Forms/" not in source and "Forms\\" not in source:
            continue
        for callee in m.get("calls") or []:
            add_edge(m.get("name"), callee)
        text = " ".join([str(m.get("name") or ""), " ".join(m.get("side_effects") or [])]).lower()
        if "update" in text or "status" in text or "ui thread" in text:
            add_edge(m.get("name"), "UI thread update / BeginInvoke")

    if not edges:
        lines.append('  Empty["No method edges detected"]')
    else:
        for src, dst in sorted(edges):
            lines.append(f'  {node_id(src)}["{esc(src)}"] --> {node_id(dst)}["{esc(dst)}"]')
    lines.append("```")
    return "\n".join(lines)

def method_summary(method_chunks: list[dict[str, Any]]) -> str:
    form_methods = []
    for c in method_chunks:
        m = method_data(c)
        if "Forms/" in str(m.get("source") or ""):
            form_methods.append(m)
    by_name = {m.get("name"): m for m in form_methods}
    lines = ["```text"]
    for entry in ["btnStart_Click", "btnSave_Click", "UpdateStatus"]:
        if entry not in by_name:
            continue
        lines.append(str(entry))
        calls = by_name[entry].get("calls") or []
        if entry == "btnStart_Click" and "StartInspection" in by_name:
            calls = ["StartInspection"]
        for call in calls:
            lines.append(f"  -> {call}")
            nested = by_name.get(call, {}).get("calls") or []
            for nested_call in nested:
                lines.append(f"      -> {nested_call}")
        if entry == "UpdateStatus":
            lines.append("  -> UI thread update / BeginInvoke")
        lines.append("")
    if len(lines) == 1:
        lines.append("No concise method flow inferred.")
    lines.append("```")
    return "\n".join(lines)

def method_index_table(docs_dir: Path, docs_chunks_dir: Path, method_chunks: list[dict[str, Any]]) -> str:
    rows = []
    for c in method_chunks:
        m = method_data(c)
        calls = m.get("calls") or []
        called_by = m.get("called_by") or []
        rows.append([
            chunk_link(docs_dir, docs_chunks_dir, c, m.get("name") or c.get("title")),
            m.get("source"),
            f"{m.get('line')}-{m.get('end_line')}",
            len(calls),
            len(called_by),
            ", ".join(str(x) for x in calls[:6]) + (" ..." if len(calls) > 6 else ""),
        ])
    return table(["Method", "Source", "Lines", "Calls", "Called By", "Top Callees"], rows)

def event_flow_data(chunk: dict[str, Any]) -> dict[str, Any]:
    return (chunk.get("data") or {}).get("event_flow") or {}

def method_chunks_by_name(method_chunks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for c in method_chunks:
        m = method_data(c)
        out.setdefault(str(m.get("name") or ""), []).append(c)
    return out

def workflow_title(flow: dict[str, Any]) -> str:
    handler = str(flow.get("handler") or "")
    entry = str(flow.get("entry") or handler or "Workflow")
    text = handler or entry.split(".", 1)[0]
    lower = text.lower()
    if "start" in lower:
        return "Start Inspection"
    if "save" in lower:
        return "Save Recipe"
    if "stop" in lower:
        return "Stop Operation"
    if "load" in lower:
        return "Open Screen"
    if "update" in lower:
        return "Update Status"
    return entry.replace(".", " ")

def workflow_expected_result(flow: dict[str, Any]) -> str:
    chain = [str(x) for x in (flow.get("call_chain") or []) if x]
    lower = " ".join(chain + [str(flow.get("entry") or ""), str(flow.get("handler") or "")]).lower()
    if "startinspection" in lower or "capturecameraimage" in lower or "evaluateresult" in lower:
        return "Run inspection logic, interact with device/camera simulation, evaluate result, then refresh status."
    if "saverecipe" in lower:
        return "Save recipe/configuration data and refresh status."
    if "updatestatus" in lower:
        return "Refresh the UI status display."
    return "Complete the handler call chain and return control to the UI."

def workflow_graph(event_flow_chunks: list[dict[str, Any]]) -> str:
    lines = ["```mermaid", "flowchart TD", '  User["Operator"]', '  UI["MainForm"]']
    if not event_flow_chunks:
        lines.append('  Empty["No user workflows detected"]')
    for i, c in enumerate(event_flow_chunks):
        flow = event_flow_data(c)
        title = workflow_title(flow)
        wf_id = f"W{i}"
        event_id = f"E{i}"
        lines.append(f'  {wf_id}["{esc(title)}"]')
        lines.append(f'  {event_id}["{esc(flow.get("entry"))}"]')
        lines.append(f"  User --> {wf_id}")
        lines.append(f"  {wf_id} --> UI")
        lines.append(f"  UI --> {event_id}")
        previous = event_id
        for j, step in enumerate(flow.get("call_chain") or []):
            step_id = f"{wf_id}_S{j}"
            lines.append(f'  {step_id}["{esc(step)}"]')
            lines.append(f"  {previous} --> {step_id}")
            previous = step_id
    lines.append("```")
    return "\n".join(lines)

def workflow_overview_table(
    docs_dir: Path,
    docs_chunks_dir: Path,
    event_flow_chunks: list[dict[str, Any]],
    method_chunks: list[dict[str, Any]],
) -> str:
    method_lookup = method_chunks_by_name(method_chunks)
    rows = []
    for c in event_flow_chunks:
        flow = event_flow_data(c)
        chain = [str(x) for x in (flow.get("call_chain") or []) if x]
        method_links = []
        for name in chain[:6]:
            method_chunk = (method_lookup.get(name) or [None])[0]
            method_links.append(chunk_link(docs_dir, docs_chunks_dir, method_chunk, name) if method_chunk else esc(name))
        rows.append([
            workflow_title(flow),
            flow.get("entry"),
            flow.get("handler"),
            workflow_expected_result(flow),
            " -> ".join(method_links),
            chunk_link(docs_dir, docs_chunks_dir, c, "event flow"),
        ])
    return table(["Workflow", "User Action / Event", "Handler", "Expected Result", "Key Technical Path", "Detail"], rows)

def workflow_detail_sections(
    docs_dir: Path,
    docs_chunks_dir: Path,
    event_flow_chunks: list[dict[str, Any]],
    method_chunks: list[dict[str, Any]],
) -> str:
    method_lookup = method_chunks_by_name(method_chunks)
    sections = []
    for c in event_flow_chunks:
        flow = event_flow_data(c)
        chain = [str(x) for x in (flow.get("call_chain") or []) if x]
        steps = [
            ["1", "Operator action", f"Trigger `{flow.get('entry')}` on the UI."],
            ["2", "Event dispatch", f"WinForms routes the event to `{flow.get('handler')}`."],
        ]
        for index, name in enumerate(chain[1:] if chain and chain[0] == flow.get("handler") else chain, start=3):
            steps.append([str(index), "Application logic", f"Call `{name}`."])
        method_links = []
        for name in chain:
            method_chunk = (method_lookup.get(name) or [None])[0]
            method_links.append(chunk_link(docs_dir, docs_chunks_dir, method_chunk, name) if method_chunk else esc(name))
        sections.append(
            f"\n### {esc(workflow_title(flow))}\n\n"
            + table(["Field", "Value"], [
                ["Entry Event", flow.get("entry")],
                ["Handler", flow.get("handler")],
                ["Source", flow.get("source")],
                ["Expected Result", workflow_expected_result(flow)],
                ["Related Event Flow", chunk_link(docs_dir, docs_chunks_dir, c, c.get("chunk_id"))],
                ["Related Methods", ", ".join(method_links) if method_links else "N/A"],
            ])
            + "\n#### Scenario Steps\n\n"
            + table(["Step", "Role", "Action"], steps)
            + "\n#### Review Checklist\n\n"
            + "- Confirm the UI event is wired to the expected handler.\n"
            + "- Confirm validation, device/config access, and status updates are intentional.\n"
            + "- Confirm failures are visible to the operator and do not leave the UI in an inconsistent state.\n"
        )
    return "\n".join(sections)

def source_file_index_table(docs_dir: Path, docs_chunks_dir: Path, source_file_chunks: list[dict[str, Any]]) -> str:
    rows = []
    for c in source_file_chunks:
        data = c.get("data") or {}
        sf = data.get("source_file") or {}
        rows.append([
            chunk_link(docs_dir, docs_chunks_dir, c, sf.get("path") or c.get("title")),
            sf.get("line_count"),
            sf.get("method_count"),
            sf.get("class_count"),
        ])
    return table(["Source File", "Lines", "Methods", "Classes / Modules"], rows)

def regions_by_source(source_file_chunks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for c in source_file_chunks:
        data = c.get("data") or {}
        sf = data.get("source_file") or {}
        source = sf.get("path")
        regions = [b for b in data.get("source_blocks") or [] if b.get("kind") == "region"]
        out[source] = sorted(regions, key=lambda r: int(r.get("start_line") or 0))
    return out

def region_for_range(regions: list[dict[str, Any]], start: int, end: int) -> str:
    best = None
    for r in regions:
        r_start = int(r.get("start_line") or 0)
        r_end = int(r.get("end_line") or 0)
        if r_start <= start and end <= r_end:
            if best is None or (r_end - r_start) < (int(best.get("end_line") or 0) - int(best.get("start_line") or 0)):
                best = r
    return best.get("name") if best else "No #Region"

def structural_block_summary(blocks: list[dict[str, Any]]) -> str:
    names = []
    for block in blocks:
        kind = block.get("kind")
        if kind not in {"switch", "if", "try"}:
            continue
        label = {"switch": "Switch/Case", "if": "If/Else", "try": "Try/Catch"}.get(kind, kind)
        name = str(block.get("name") or "").strip()
        names.append(f"{label}: {name}" if name else label)
    return ", ".join(dict.fromkeys(names)) or "N/A"

def large_task_group_table(
    docs_dir: Path,
    docs_chunks_dir: Path,
    large_file_tasks: list[dict[str, Any]],
    source_file_chunks: list[dict[str, Any]],
) -> str:
    region_lookup = regions_by_source(source_file_chunks)
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for c in large_file_tasks:
        data = c.get("data") or {}
        line_range = data.get("line_range") or {}
        start = int(line_range.get("start") or 0)
        end = int(line_range.get("end") or 0)
        source = ((data.get("source_file") or {}).get("path") or ",".join(c.get("source_refs") or []) or "Unknown")
        methods = data.get("methods") or []
        method = methods[0].get("name") if methods else "(file gap)"
        region = region_for_range(region_lookup.get(source, []), start, end)
        structural_blocks = structural_block_summary(data.get("semantic_blocks") or [])
        grouped.setdefault((source, region, method, structural_blocks), []).append(c)

    rows = []
    for (source, region, method, structural_blocks), chunks in sorted(grouped.items()):
        ranges = []
        links = []
        for c in sorted(chunks, key=lambda x: int(((x.get("data") or {}).get("line_range") or {}).get("start") or 0)):
            line_range = (c.get("data") or {}).get("line_range") or {}
            ranges.append(f"{line_range.get('start')}-{line_range.get('end')}")
            links.append(chunk_link(docs_dir, docs_chunks_dir, c, line_range.get("start")))
        rows.append([source, region, method, structural_blocks, ", ".join(ranges), ", ".join(links)])
    return table(["Source", "Region", "Method / Segment", "Structural Blocks", "Line Ranges", "Task Links"], rows)

def main(analysis_dir: str, chunks_dir: str, docs_chunks_dir: str, docs_dir: str) -> int:
    analysis = Path(analysis_dir)
    chunks = Path(chunks_dir)
    docs_chunks = Path(docs_chunks_dir)
    docs = Path(docs_dir)
    docs.mkdir(parents=True, exist_ok=True)

    index = load(chunks / "index.json", {"chunks": [], "counts": {}})
    projects = [load_chunk(p) for p in list_chunk_json(chunks, "projects")]
    forms = [load_chunk(p) for p in list_chunk_json(chunks, "forms")]
    event_flows = [load_chunk(p) for p in list_chunk_json(chunks, "event_flows")]
    methods = [load_chunk(p) for p in list_chunk_json(chunks, "methods")]
    dependencies = [load_chunk(p) for p in list_chunk_json(chunks, "dependencies")]
    configs = [load_chunk(p) for p in list_chunk_json(chunks, "configs")]
    risks = [load_chunk(p) for p in list_chunk_json(chunks, "risks")]
    source_files = [load_chunk(p) for p in list_chunk_json(chunks, "source_files")]
    large_file_tasks = [load_chunk(p) for p in list_chunk_json(chunks, "large_file_tasks")]

    # fallback counts / data
    enterprise_projects = load(analysis / "projects.json", [])
    enterprise_deps = load(analysis / "dependencies.json", [])
    enterprise_methods = load(analysis / "methods.json", [])
    enterprise_event_flows = load(analysis / "event_flows.json", [])

    # README
    (docs / "README.md").write_text(f"""# Enterprise GUI Project Handover Documentation

This documentation is generated with chunk-aware merging.

## Chunk Counts

{table(["Chunk Type", "Count"], [[k, v] for k, v in (index.get("counts") or {}).items()])}

## Documents

1. [Solution Structure](01_solution_structure.md)
2. [Architecture](02_architecture.md)
3. [Project Dependencies](03_project_dependencies.md)
4. [Event Flow](04_event_flow.md)
5. [Method Flow](05_method_flow.md)
6. [Configuration](06_configuration.md)
7. [User Workflow](07_user_workflow.md)
8. [External Dependencies](08_external_dependencies.md)
9. [Risk Analysis](09_risk_analysis.md)

## Chunk Docs

See `docs/chunks/` for regenerated single-chunk documentation.
""", encoding="utf-8")

    # 01
    doc = "# 01 Solution Structure\n\n"
    doc += "## Project Dependency Graph\n\n" + project_graph(projects) + "\n\n"
    doc += "## Project Chunk Index\n\n"
    doc += table(["Chunk ID", "Title", "Summary", "Source Refs", "Related"], [extract_chunk_summary(c) for c in projects])
    doc += "\n## Project Details from Chunks\n\n"
    for c in projects[:LIMIT_INLINE_CHUNKS]:
        section = include_chunk_md_section(docs, docs_chunks, c)
        if section:
            doc += section
        else:
            p = (c.get("data") or {}).get("project", {})
            doc += f"\n### {esc(c.get('title'))}\n\n"
            doc += table(["Item", "Value"], [
                ["Name", p.get("name")],
                ["Language", p.get("language")],
                ["Path", p.get("path")],
                ["Target", p.get("target_framework")],
                ["GUI", p.get("is_gui")],
                ["Responsibility", p.get("responsibility_inference")],
            ])
    if len(projects) > LIMIT_INLINE_CHUNKS:
        doc += f"\n> {len(projects)-LIMIT_INLINE_CHUNKS} additional project chunks omitted. See docs/chunks/projects/.\n"
    (docs / "01_solution_structure.md").write_text(doc, encoding="utf-8")

    # 02
    doc = "# 02 Architecture\n\n"
    doc += "## Overall Block Architecture\n\n" + architecture_graph(projects, dependencies) + "\n\n"
    doc += "## Layer Explanation\n\n"
    doc += table(["Layer", "Responsibility", "Review Focus"], [
        ["GUI Layer", "Forms / Windows / UserControls, user events, UI updates", "UI-logic coupling, thread safety"],
        ["Application / Service Layer", "Workflow orchestration and business logic", "God service, testability"],
        ["Data / Repository Layer", "Database/file persistence", "connection/config/runtime risk"],
        ["External Device / SDK Layer", "Camera, PLC, motion, native SDKs", "runtime, timeout, x86/x64, license"],
        ["Configuration", "App.config, settings, registry, environment", "hardcoded and environment-specific behavior"],
    ])
    doc += "\n## Module Responsibility from Project Chunks\n\n"
    doc += table(["Project", "Responsibility", "Sources"], [
        [
            ((c.get("data") or {}).get("project") or {}).get("name"),
            ((c.get("data") or {}).get("project") or {}).get("responsibility_inference"),
            c.get("source_refs"),
        ] for c in projects
    ])
    doc += "\n## Architecture Details from Curated Chunks\n\n"
    for c in projects[:10]:
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=2500)
        if section:
            doc += section
    (docs / "02_architecture.md").write_text(doc, encoding="utf-8")

    # 03
    doc = "# 03 Project Dependencies\n\n"
    doc += "## Dependency Chunk Index\n\n"
    doc += table(["Chunk ID", "Title", "Summary", "Source Refs", "Related"], [extract_chunk_summary(c) for c in dependencies])
    doc += "\n## Dependency Details\n\n"
    for c in dependencies[:LIMIT_INLINE_CHUNKS]:
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=2500)
        if section:
            doc += section
        else:
            d = c.get("data") or {}
            doc += f"\n### {esc(c.get('title'))}\n\n" + table(["Field", "Value"], [[k, v] for k, v in d.items()])
    (docs / "03_project_dependencies.md").write_text(doc, encoding="utf-8")

    # 04
    doc = "# 04 Event Flow\n\n"
    doc += "## Event Flow Chunk Index\n\n"
    doc += table(["Chunk ID", "Title", "Summary", "Source Refs", "Related"], [extract_chunk_summary(c) for c in event_flows])
    doc += "\n## Event Flow Details from Chunks\n\n"
    for c in event_flows[:LIMIT_INLINE_CHUNKS]:
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=6000)
        if section:
            doc += section
        else:
            f = (c.get("data") or {}).get("event_flow", {})
            doc += f"\n### {esc(c.get('title'))}\n\n"
            doc += table(["Entry", "Handler", "Call Chain", "Source"], [[f.get("entry"), f.get("handler"), f.get("call_chain"), f.get("source")]])
    if len(event_flows) > LIMIT_INLINE_CHUNKS:
        doc += f"\n> {len(event_flows)-LIMIT_INLINE_CHUNKS} additional event flow chunks omitted. See docs/chunks/event_flows/.\n"
    (docs / "04_event_flow.md").write_text(doc, encoding="utf-8")

    # 05
    doc = "# 05 Method Flow\n\n"
    doc += "## Method Flow Overview\n\n"
    doc += method_graph(methods, event_flows) + "\n\n"
    doc += "## Key Flow Summary\n\n"
    doc += method_summary(methods) + "\n\n"
    doc += "## How To Read This Document\n\n"
    doc += (
        "- Start with the Mermaid overview to understand the main call path.\n"
        "- Use the method index to jump to a single-method chunk when you need details.\n"
        "- Use the source-file index to understand which files own which responsibilities.\n"
        "- Large file tasks are AI review slices; the grouped table below recombines them by method and region for human reading.\n\n"
    )
    doc += "## Method Index\n\n"
    doc += method_index_table(docs, docs_chunks, methods)
    doc += "\n## Source File Index\n\n"
    doc += source_file_index_table(docs, docs_chunks, source_files)
    doc += "\n## Large File Method / Region Index\n\n"
    doc += large_task_group_table(docs, docs_chunks, large_file_tasks, source_files)
    doc += "\n## Method Details\n\n"
    doc += "Detailed per-method notes live in `docs/chunks/methods/`. Use the links in the method index above.\n"
    if large_file_tasks:
        doc += "\n## Large File Task Details\n\n"
        doc += "Detailed large-file review slices live in `docs/chunks/large_file_tasks/`. Use the grouped links above when reviewing long methods.\n"
    (docs / "05_method_flow.md").write_text(doc, encoding="utf-8")

    # 06
    doc = "# 06 Configuration\n\n"
    doc += "## Configuration Chunk Index\n\n"
    doc += table(["Chunk ID", "Title", "Summary", "Source Refs", "Related"], [extract_chunk_summary(c) for c in configs])
    doc += "\n## Configuration Details from Chunks\n\n"
    for c in configs[:LIMIT_INLINE_CHUNKS]:
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=3000)
        if section:
            doc += section
        else:
            doc += f"\n### {esc(c.get('title'))}\n\n" + table(["Field", "Value"], [[k, v] for k, v in (c.get("data") or {}).items()])
    (docs / "06_configuration.md").write_text(doc, encoding="utf-8")

    # 07
    doc = "# 07 User Workflow\n\n"
    doc += "## Workflow Overview\n\n"
    doc += workflow_graph(event_flows) + "\n\n"
    doc += "## How To Read This Document\n\n"
    doc += (
        "- Read this as an operator or handover scenario guide: what the user does, what should happen, and which code path supports it.\n"
        "- Use `04_event_flow.md` when you need the lower-level event-to-handler sequence details.\n"
        "- Use the links below to jump from a user workflow to the related event-flow and method chunks.\n\n"
    )
    doc += "## Workflow Summary\n\n"
    doc += workflow_overview_table(docs, docs_chunks, event_flows, methods)
    doc += "\n## Scenario Details\n\n"
    doc += workflow_detail_sections(docs, docs_chunks, event_flows, methods)
    doc += "\n## UI Entry Points\n\n"
    doc += table(["Form", "Chunk", "Source Refs"], [[c.get("title"), chunk_link(docs, docs_chunks, c, c.get("chunk_id")), c.get("source_refs")] for c in forms])
    (docs / "07_user_workflow.md").write_text(doc, encoding="utf-8")

    # 08
    doc = "# 08 External Dependencies\n\n"
    doc += "## External / Project Dependency Chunks\n\n"
    doc += table(["Chunk ID", "Title", "Summary", "Sources"], [extract_chunk_summary(c)[:4] for c in dependencies])
    doc += "\n## Dependency Details\n\n"
    for c in dependencies[:LIMIT_INLINE_CHUNKS]:
        title = c.get("title") or ""
        if "External" not in title and "Dependency" not in title:
            continue
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=3000)
        if section:
            doc += section
    (docs / "08_external_dependencies.md").write_text(doc, encoding="utf-8")

    # 09
    doc = "# 09 Risk Analysis\n\n"
    doc += "## Risk Chunk Index\n\n"
    doc += table(["Chunk ID", "Title", "Summary", "Source Refs", "Related"], [extract_chunk_summary(c) for c in risks])
    doc += "\n## Risk Details from Chunks\n\n"
    for c in risks[:LIMIT_INLINE_CHUNKS]:
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=3000)
        if section:
            doc += section
        else:
            doc += f"\n### {esc(c.get('title'))}\n\n" + table(["Field", "Value"], [[k, v] for k, v in (c.get("data") or {}).items()])
    doc += "\n## Required Review Areas\n\n"
    doc += "- God Object / Giant Form\n- UI and logic coupling\n- static / Singleton abuse\n- hardcoded configuration\n- cross-thread UI update\n- event leak\n- circular dependency\n- async deadlock\n"
    (docs / "09_risk_analysis.md").write_text(doc, encoding="utf-8")

    print(f"Wrote chunk-aware docs to {docs}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: generate_chunk_aware_docs.py <analysis_dir> <analysis_chunks_dir> <docs_chunks_dir> <docs_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
