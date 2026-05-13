#!/usr/bin/env python3
"""
dotnet-chunk-regenerator v0.8.4

Regenerate local Markdown documentation for one or more analysis chunks.

Usage examples:
    python regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-id MainForm
    python regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-path exports/analysis_chunks/forms/MainForm.json
    python regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-type form
    python regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --all
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
from typing import Any

PLURAL = {
    "project": "projects",
    "form": "forms",
    "event_flow": "event_flows",
    "method": "methods",
    "dependency": "dependencies",
    "config": "configs",
    "risk": "risks",
}

def load(path: Path, default: Any = None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def esc(v: Any) -> str:
    if v in (None, ""):
        return "N/A"
    s = str(v).replace("\n", " ").replace("|", "\\|")
    return s[:2000] + "..." if len(s) > 2000 else s

def bullet(items):
    if not items:
        return "- N/A\n"
    if isinstance(items, str):
        items = [items]
    return "".join(f"- {esc(x)}\n" for x in items)

def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(out) + "\n"

def mermaid_flow(title: str, steps: list[str]) -> str:
    lines = ["```mermaid", "flowchart TD"]
    if not steps:
        lines.append(f'  A["{esc(title)}"]')
    else:
        prev = "N0"
        lines.append(f'  {prev}["{esc(steps[0])}"]')
        for i, s in enumerate(steps[1:], start=1):
            cur = f"N{i}"
            lines.append(f'  {prev} --> {cur}["{esc(s)}"]')
            prev = cur
    lines.append("```")
    return "\n".join(lines)

def simplified_sequence(entry: str, handler: str, calls: list[str]) -> str:
    lines = [
        "```mermaid",
        "sequenceDiagram",
        "  participant User",
        "  participant UI",
        "  participant Handler",
        "  participant Logic",
        "  participant Device",
        f"  User->>UI: {esc(entry)}",
        f"  UI->>Handler: {esc(handler)}()",
    ]
    for c in calls[:30]:
        target = "Device" if any(k in str(c).lower() for k in ["plc", "camera", "grab", "serial", "socket", "modbus", "halcon", "opencv"]) else "Logic"
        lines.append(f"  Handler->>{target}: {esc(c)}()")
        lines.append(f"  {target}-->>Handler: result/status")
    if len(calls) > 30:
        lines.append(f"  Note over Handler,Logic: {len(calls)-30} additional calls omitted")
    lines.append("  Handler-->>UI: update/complete")
    lines.append("```")
    return "\n".join(lines)

def render_project(chunk):
    data = chunk.get("data", {})
    p = data.get("project", {})
    deps = data.get("dependencies", [])
    risks = data.get("risk_candidates", [])
    title = chunk.get("title")
    doc = f"# {esc(title)}\n\n"
    doc += "## Summary\n\n"
    doc += esc(chunk.get("summary")) + "\n\n"
    doc += "## Project Metadata\n\n"
    doc += table(["Item", "Value"], [
        ["Name", p.get("name")],
        ["Language", p.get("language")],
        ["Path", p.get("path")],
        ["Target Framework", p.get("target_framework")],
        ["GUI Project", p.get("is_gui")],
        ["Responsibility Inference", p.get("responsibility_inference")],
    ])
    doc += "\n## Local Dependency Graph\n\n"
    lines = ["```mermaid", "flowchart LR"]
    lines.append(f'  P["{esc(p.get("name"))}"]')
    for i, d in enumerate(deps):
        lines.append(f'  D{i}["{esc(d.get("target"))}"]')
        lines.append(f'  P --> D{i}')
    lines.append("```")
    doc += "\n".join(lines) + "\n\n"
    doc += "## Dependencies\n\n" + table(["Type", "Target", "Source"], [[d.get("type"), d.get("target"), d.get("source")] for d in deps])
    doc += "\n## Module Responsibility\n\n"
    doc += "- 主要責任：" + esc(p.get("responsibility_inference") or "需人工確認。推測") + "\n"
    doc += "- 維護注意：確認此模組是否同時承擔 UI、業務邏輯、設備控制或資料存取，避免耦合過高。\n"
    doc += "\n## Risks\n\n" + table(["Risk", "Evidence", "Confidence"], [[r.get("risk_type"), r.get("evidence"), r.get("confidence")] for r in risks])
    return doc

def render_form(chunk):
    data = chunk.get("data", {})
    form = data.get("form_name")
    events = data.get("events", [])
    flows = data.get("event_flows", [])
    methods = data.get("handler_methods", [])
    risks = data.get("risk_candidates", [])
    doc = f"# Form: {esc(form)}\n\n"
    doc += "## Responsibility Summary\n\n"
    doc += "- 畫面用途：根據事件與方法推測，此 Form 可能負責使用者操作入口、狀態顯示或特定功能流程。推測\n"
    doc += "- 需人工確認：畫面實際責任、導航來源、是否包含設備控制或資料存取。\n\n"
    doc += "## UI Event Entries\n\n"
    doc += table(["Control", "Event", "Handler", "Source", "Line"], [[e.get("control"), e.get("event"), e.get("handler"), e.get("source"), e.get("line")] for e in events])
    doc += "\n## Form Event Flow Graph\n\n"
    lines = ["```mermaid", "flowchart TD", f'  Form["{esc(form)}"]']
    for i, f in enumerate(flows[:80]):
        node = f"E{i}"
        lines.append(f'  {node}["{esc(f.get("entry"))}<br/>{esc(f.get("handler"))}"]')
        lines.append(f"  Form --> {node}")
    lines.append("```")
    doc += "\n".join(lines) + "\n\n"
    doc += "## Handler Methods\n\n"
    doc += table(["Method", "Calls", "Side Effects", "Source"], [[m.get("name"), m.get("calls"), m.get("side_effects"), m.get("source")] for m in methods])
    doc += "\n## Maintenance Notes\n\n"
    doc += "- 檢查此 Form 是否過度集中業務邏輯。\n"
    doc += "- 檢查事件 handler 是否直接操作設備、DB 或設定檔。\n"
    doc += "- 檢查長時間操作是否會阻塞 UI thread。\n"
    doc += "\n## Risks\n\n" + table(["Risk", "Evidence", "Confidence"], [[r.get("risk_type"), r.get("evidence"), r.get("confidence")] for r in risks])
    return doc

def render_event_flow(chunk):
    data = chunk.get("data", {})
    f = data.get("event_flow", {})
    handler_methods = data.get("handler_methods", [])
    purposes = data.get("method_purpose", [])
    doc = f"# {esc(chunk.get('title'))}\n\n"
    doc += "## Event Entry\n\n"
    doc += table(["Item", "Value"], [
        ["Entry", f.get("entry")],
        ["Handler", f.get("handler")],
        ["Source", f.get("source")],
        ["Line", f.get("line")],
        ["Confidence", f.get("confidence")],
    ])
    doc += "\n## Simplified Sequence Diagram\n\n"
    doc += simplified_sequence(f.get("entry"), f.get("handler"), [x for x in (f.get("call_chain") or []) if x != f.get("handler")]) + "\n\n"
    doc += "## Call Chain\n\n"
    doc += mermaid_flow(f.get("entry") or "Event", f.get("call_chain") or []) + "\n\n"
    doc += "## Handler Method Details\n\n"
    doc += table(["Method", "Calls", "Side Effects", "Source"], [[m.get("name"), m.get("calls"), m.get("side_effects"), m.get("source")] for m in handler_methods])
    doc += "\n## Method Purpose Analysis\n\n"
    for p in purposes:
        doc += f"### {esc(p.get('method'))}\n\n"
        doc += "**用途：**\n" + esc(p.get("inferred_purpose")) + "\n\n"
        doc += "**推測依據：**\n" + bullet(p.get("evidence")) + "\n"
        doc += "**副作用：**\n" + bullet(p.get("side_effects")) + "\n"
        doc += "**維護注意事項：**\n" + bullet(p.get("maintenance_notes")) + "\n"
    doc += "\n## Review Notes\n\n"
    doc += "- 確認事件是否可能被重複觸發。\n"
    doc += "- 確認 handler 是否包含長時間阻塞操作。\n"
    doc += "- 確認設備或資料存取是否有例外處理。\n"
    return doc

def render_method(chunk):
    data = chunk.get("data", {})
    m = data.get("method", {})
    purposes = data.get("purpose_analysis", [])
    triggers = data.get("event_triggers", [])
    flows = data.get("event_flows", [])
    doc = f"# Method: {esc(m.get('name'))}\n\n"
    if purposes:
        p = purposes[0]
        doc += "**用途：**\n" + esc(p.get("inferred_purpose")) + "\n\n"
        doc += "**推測依據：**\n" + bullet(p.get("evidence")) + "\n"
        doc += "**觸發來源：**\n" + bullet([t.get("trigger") for t in p.get("triggers", []) if isinstance(t, dict)] or ["未偵測到明確 GUI 事件觸發來源。推測"]) + "\n"
        doc += "**主要責任：**\n" + bullet(p.get("main_responsibility")) + "\n"
        doc += "**副作用：**\n" + bullet(p.get("side_effects")) + "\n"
        doc += "**維護注意事項：**\n" + bullet(p.get("maintenance_notes")) + "\n"
    else:
        doc += "**用途：**\n用途需人工確認。推測\n\n"
    doc += "## Method Metadata\n\n"
    doc += table(["Item", "Value"], [
        ["Source", m.get("source")],
        ["Line", m.get("line")],
        ["Called By", m.get("called_by")],
        ["Calls", m.get("calls")],
        ["Existing Purpose", m.get("purpose")],
        ["Existing Side Effects", m.get("side_effects")],
    ])
    doc += "\n## Event Triggers\n\n"
    doc += table(["Trigger", "Source", "Line"], [[t.get("trigger"), t.get("source"), t.get("line")] for t in triggers])
    doc += "\n## Related Event Flows\n\n"
    doc += table(["Entry", "Handler", "Call Chain"], [[f.get("entry"), f.get("handler"), f.get("call_chain")] for f in flows])
    return doc

def render_dependency(chunk):
    d = chunk.get("data", {})
    doc = f"# {esc(chunk.get('title'))}\n\n"
    doc += table(["Field", "Value"], [[k, v] for k, v in d.items()])
    doc += "\n## Maintenance Notes\n\n"
    doc += "- 確認版本、部署路徑、x86/x64 相容性。\n"
    doc += "- 若為 SDK / COM / Native DLL，需確認 runtime 與授權。\n"
    return doc

def render_config(chunk):
    c = chunk.get("data", {})
    doc = f"# {esc(chunk.get('title'))}\n\n"
    doc += table(["Field", "Value"], [[k, v] for k, v in c.items()])
    doc += "\n## Maintenance Notes\n\n"
    doc += "- 確認此設定來源是否為正式 runtime 設定。\n"
    doc += "- 檢查是否依賴特定機台路徑、環境變數或 Registry。\n"
    return doc

def render_risk(chunk):
    r = chunk.get("data", {})
    doc = f"# {esc(chunk.get('title'))}\n\n"
    doc += table(["Field", "Value"], [[k, v] for k, v in r.items()])
    doc += "\n## Suggested Review\n\n"
    doc += "- 確認此風險是否真實存在。\n"
    doc += "- 補充影響範圍、修正成本與建議改善順序。\n"
    return doc

RENDERERS = {
    "project": render_project,
    "form": render_form,
    "event_flow": render_event_flow,
    "method": render_method,
    "dependency": render_dependency,
    "config": render_config,
    "risk": render_risk,
}

def load_chunk(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def chunk_output_path(out_dir: Path, chunk: dict[str, Any]) -> Path:
    ctype = chunk.get("chunk_type")
    folder = PLURAL.get(ctype, f"{ctype}s")
    return out_dir / folder / f"{chunk.get('chunk_id')}.md"

def render_chunk(path: Path, out_dir: Path) -> Path:
    chunk = load_chunk(path)
    ctype = chunk.get("chunk_type")
    renderer = RENDERERS.get(ctype)
    if not renderer:
        raise ValueError(f"Unsupported chunk_type: {ctype} from {path}")
    doc = renderer(chunk)
    out_path = chunk_output_path(out_dir, chunk)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc, encoding="utf-8")
    return out_path

def find_chunk_by_id(chunks_dir: Path, chunk_id: str) -> list[Path]:
    return list(chunks_dir.rglob(f"{chunk_id}.json"))

def find_chunks_by_type(chunks_dir: Path, chunk_type: str) -> list[Path]:
    folder = PLURAL.get(chunk_type, f"{chunk_type}s")
    return sorted((chunks_dir / folder).glob("*.json"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chunks_dir")
    ap.add_argument("docs_chunks_dir")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--chunk-id")
    g.add_argument("--chunk-path")
    g.add_argument("--chunk-type")
    g.add_argument("--all", action="store_true")
    args = ap.parse_args()

    chunks_dir = Path(args.chunks_dir)
    out_dir = Path(args.docs_chunks_dir)

    paths = []
    if args.chunk_path:
        paths = [Path(args.chunk_path)]
    elif args.chunk_id:
        paths = find_chunk_by_id(chunks_dir, args.chunk_id)
    elif args.chunk_type:
        paths = find_chunks_by_type(chunks_dir, args.chunk_type)
    elif args.all:
        paths = sorted(chunks_dir.rglob("*.json"))
        paths = [p for p in paths if p.name != "index.json"]

    if not paths:
        raise SystemExit("No matching chunk found.")

    written = []
    for p in paths:
        written.append(render_chunk(p, out_dir))

    print("Regenerated chunk docs:")
    for p in written:
        print("-", p)

if __name__ == "__main__":
    main()
