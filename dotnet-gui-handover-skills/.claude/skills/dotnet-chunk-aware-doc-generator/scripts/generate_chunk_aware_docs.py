#!/usr/bin/env python3
"""
dotnet-chunk-aware-doc-generator v0.8.5

Generate final 01-09 enterprise GUI handover docs from:
- exports/enterprise_analysis
- exports/analysis_chunks
- docs/chunks

Usage:
    python generate_chunk_aware_docs.py exports/enterprise_analysis exports/analysis_chunks docs/chunks docs
"""
from __future__ import annotations

from pathlib import Path
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
    doc += "## Method Chunk Index\n\n"
    doc += table(["Chunk ID", "Title", "Summary", "Source Refs", "Related"], [extract_chunk_summary(c) for c in methods])
    doc += "\n## Method Details from Chunks\n\n"
    for c in methods[:LIMIT_INLINE_CHUNKS]:
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=5000)
        if section:
            doc += section
        else:
            m = (c.get("data") or {}).get("method", {})
            doc += f"\n### {esc(c.get('title'))}\n\n"
            doc += table(["Method", "Calls", "Called By", "Source"], [[m.get("name"), m.get("calls"), m.get("called_by"), m.get("source")]])
    if len(methods) > LIMIT_INLINE_CHUNKS:
        doc += f"\n> {len(methods)-LIMIT_INLINE_CHUNKS} additional method chunks omitted. See docs/chunks/methods/.\n"
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
    doc += "## Workflow Candidates from Event/Form Chunks\n\n"
    doc += "This document is assembled from form and event-flow chunks. Regenerate individual form or event-flow chunks to improve workflow quality.\n\n"
    doc += "## Form Chunks\n\n"
    doc += table(["Chunk ID", "Title", "Source Refs"], [[c.get("chunk_id"), c.get("title"), c.get("source_refs")] for c in forms])
    doc += "\n## Event Flow Chunks\n\n"
    doc += table(["Chunk ID", "Title", "Source Refs"], [[c.get("chunk_id"), c.get("title"), c.get("source_refs")] for c in event_flows])
    doc += "\n## Curated Form/Event Chunk Details\n\n"
    for c in (forms[:8] + event_flows[:8]):
        section = include_chunk_md_section(docs, docs_chunks, c, max_chars=2500)
        if section:
            doc += section
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
