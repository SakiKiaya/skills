#!/usr/bin/env python3
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


def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_text(path: Path) -> str:
    for enc in ["utf-8-sig", "utf-8", "cp950", "big5"]:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return path.read_text(errors="replace")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except Exception:
        return path.as_posix()


def esc(value: Any) -> str:
    if value in (None, ""):
        return "N/A"
    return str(value).replace("\n", " ").replace("|", "\\|")


def anchor(value: Any) -> str:
    text = str(value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9_\-\s]+", "", text)
    text = re.sub(r"\s+", "-", text)
    return text or "unknown"


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(esc(x) for x in row) + " |")
    return "\n".join(out) + "\n"


def line_slice(text: str, start: int, end: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[max(1, start) - 1:max(1, end)])


def method_body(source_text: str, method: dict[str, Any]) -> str:
    start = int(method.get("line") or 1)
    end = int(method.get("end_line") or start)
    return line_slice(source_text, start, end)


def action_summary(name: str, calls: list[str], body: str) -> str:
    lower = " ".join([name, " ".join(calls), body]).lower()
    if "startinspection" in lower or "capturecameraimage" in lower or "evaluateresult" in lower:
        return "執行檢測流程，包含連線、取像、結果評估與狀態更新。"
    if "saverecipe" in lower or "configurationmanager" in lower or "appsettings" in lower:
        return "儲存配方或設定資料，並更新畫面狀態。"
    if "begininvoke" in lower or "invoke" in lower:
        return "透過 UI 執行緒更新畫面狀態。"
    if calls:
        return "依序呼叫已確認的方法鏈：" + " -> ".join(calls)
    return "已定位方法內容；實際業務語意仍需人工確認。"


def method_description(method: dict[str, Any], body: str) -> str:
    return action_summary(str(method.get("name") or ""), [str(x) for x in method.get("calls") or []], body)


def method_logic(method: dict[str, Any], body: str) -> str:
    calls = [str(x) for x in method.get("calls") or []]
    items = []
    if calls:
        items.append("Calls: " + " -> ".join(calls))
    effects = [s["effect"] for s in side_effects_for(method, body)]
    if effects:
        items.append("已確認副作用：" + ", ".join(dict.fromkeys(effects)))
    if "Select Case" in body or "switch" in body:
        items.append("Contains branch/state-machine style logic.")
    if "If " in body or "If(" in body:
        items.append("Contains conditional logic.")
    if "Try" in body:
        items.append("Contains exception-handling logic.")
    return " ".join(items) if items else "靜態分析未偵測到內部呼叫或主要副作用。"


def parse_params(params: Any) -> list[dict[str, str]]:
    text = str(params or "").strip()
    if not text:
        return []
    out = []
    for raw in [p.strip() for p in text.split(",") if p.strip()]:
        name = raw
        typ = "Unknown"
        m = re.search(r"(?i)(?:ByVal|ByRef)?\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+As\s+(?P<type>.+)$", raw)
        if m:
            name = m.group("name")
            typ = m.group("type").strip()
        out.append({"name": name, "type": typ, "range": "See caller / validation logic", "description": raw})
    return out


def returns_or_creates_object(body: str) -> str:
    if re.search(r"(?i)\bReturn\s+New\b|\bNew\s+[A-Za-z_][A-Za-z0-9_]*", body):
        return "可能會建立新物件。"
    if re.search(r"(?i)^\s*Function\b", body, re.M):
        return "回傳 VB Function 簽章定義的結果。"
    return "未偵測到輸出參數或新物件建立。"


def side_effects_for(method: dict[str, Any], body: str) -> list[dict[str, Any]]:
    checks = [
        ("config access", ["ConfigurationManager", "My.Settings", "Settings.Default"]),
        ("ui thread update", ["BeginInvoke", ".Invoke(", "InvokeRequired"]),
        ("blocking wait", ["Thread.Sleep", ".Wait(", ".Result"]),
        ("device/camera/plc call", ["Plc", "PLC", "Camera", "Capture", "Grab"]),
        ("file access", ["File.", "StreamWriter", "StreamReader", "Directory."]),
        ("database access", ["SqlConnection", "OleDb", "SQLite", "ExecuteNonQuery"]),
    ]
    out = []
    for effect, tokens in checks:
        hits = [token for token in tokens if token in body]
        if hits:
            out.append({
                "method": method.get("name"),
                "effect": effect,
                "evidence": hits,
                "source": method.get("source"),
                "line_range": {"start": method.get("line"), "end": method.get("end_line")},
                "status": "confirmed",
            })
    return out


def method_lookup(methods: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(m.get("name") or ""): m for m in methods}


def select_core_sources(source_files: list[dict[str, Any]], requested: list[str]) -> list[str]:
    if requested:
        return requested
    selected = []
    for sf in source_files:
        path = str(sf.get("path") or "")
        lower = path.lower()
        line_count = int(sf.get("line_count") or 0)
        if lower.endswith(".vb") and ("/forms/" in f"/{lower}" or line_count >= 1000):
            selected.append(path)
    return selected[:8]


def build_insight(repo: Path, source: str, analysis_dir: Path) -> dict[str, Any]:
    methods = load(analysis_dir / "methods.json", [])
    events = load(analysis_dir / "events.json", [])
    event_flows = load(analysis_dir / "event_flows.json", [])
    source_blocks = load(analysis_dir / "source_blocks.json", [])
    path = repo / source
    text = read_text(path) if path.exists() else ""

    source_methods = [m for m in methods if m.get("source") == source]
    by_name = method_lookup(source_methods)

    workflows = []
    for flow in event_flows:
        if flow.get("source") != source:
            continue
        chain = [str(x) for x in (flow.get("call_chain") or []) if x]
        handler = by_name.get(str(flow.get("handler") or ""))
        body = method_body(text, handler) if handler else ""
        workflows.append({
            "entry": flow.get("entry"),
            "handler": flow.get("handler"),
            "call_chain": chain,
            "summary": action_summary(str(flow.get("handler") or ""), chain, body),
            "source": source,
            "line": flow.get("line"),
            "evidence": f"{source}:{flow.get('line')}",
            "status": "confirmed" if handler else "inferred",
        })

    side_effects = []
    method_details = []
    for method in source_methods:
        body = method_body(text, method)
        effects = side_effects_for(method, body)
        side_effects.extend(effects)
        method_details.append({
            "name": method.get("name"),
            "source": method.get("source"),
            "line_range": {"start": method.get("line"), "end": method.get("end_line")},
            "calls": method.get("calls") or [],
            "called_by": method.get("called_by") or [],
            "params": parse_params(method.get("params")),
            "description": method_description(method, body),
            "logic": method_logic(method, body),
            "side_effects": effects,
            "output": returns_or_creates_object(body),
            "anchor": f"method-{anchor(method.get('name'))}",
            "status": "confirmed",
        })

    regions = [
        {
            "name": b.get("name"),
            "line_range": {"start": b.get("start_line"), "end": b.get("end_line")},
            "source": source,
            "status": "confirmed",
        }
        for b in source_blocks
        if b.get("source") == source and b.get("kind") == "region"
    ]
    state_machines = [
        {
            "kind": "Switch/Case",
            "expression": b.get("name"),
            "line_range": {"start": b.get("start_line"), "end": b.get("end_line")},
            "source": source,
            "status": "confirmed",
        }
        for b in source_blocks
        if b.get("source") == source and b.get("kind") == "switch"
    ]
    ui_events = [
        {
            "control": e.get("control"),
            "event": e.get("event"),
            "handler": e.get("handler"),
            "source": source,
            "line": e.get("line"),
            "status": "confirmed",
        }
        for e in events
        if e.get("source") == source
    ]

    return {
        "version": "0.1",
        "source": source,
        "generated_from": "static source-backed manual insight extractor",
        "confirmed_workflows": workflows,
        "confirmed_side_effects": side_effects,
        "method_details": method_details,
        "regions": regions,
        "state_machines": state_machines,
        "ui_events": ui_events,
        "open_questions": [
            "Confirm operator-facing names and expected pass/fail behavior with equipment owners.",
            "Confirm external device, PLC, and camera semantics when source uses simulator or placeholder methods.",
        ],
    }


def form_chunk_path(repo: Path, source: str) -> Path:
    return repo / "docs" / "chunks" / "forms" / f"{Path(source).stem}.md"


def render_param_table(detail: dict[str, Any]) -> str:
    rows = [["**輸入參數**", "", "", ""]]
    params = detail.get("params") or []
    if params:
        for param in params:
            rows.append([param.get("name"), param.get("type"), param.get("range"), param.get("description")])
    else:
        rows.append(["無", "N/A", "N/A", "此方法未宣告輸入參數。"])
    rows.append(["**輸出參數**", "", "", detail.get("output") or "未偵測到輸出。"])
    return table(["Item", "型態", "數值範圍", "說明"], rows)


def render_method_detail(detail: dict[str, Any]) -> str:
    name = detail.get("name")
    line_range = detail.get("line_range") or {}
    calls = detail.get("calls") or []
    effects = detail.get("side_effects") or []
    notes = [
        f"來源：`{detail.get('source')}:{line_range.get('start')}-{line_range.get('end')}`",
        f"狀態：`{detail.get('status')}`",
    ]
    if calls:
        notes.append("已確認呼叫方法：" + ", ".join(f"`{c}`" for c in calls))
    if effects:
        notes.append("已確認副作用：" + ", ".join(f"`{e.get('effect')}`" for e in effects))
    return (
        f"### {esc(name)}\n\n"
        f"<a id=\"{esc(detail.get('anchor'))}\"></a>\n\n"
        "**方法說明**:\n\n"
        f"{esc(detail.get('description'))}\n\n"
        "**方法邏輯**:\n\n"
        f"{esc(detail.get('logic'))}\n\n"
        "**參數說明**:\n\n"
        + render_param_table(detail)
        + "\n**注意事項**:\n\n"
        + "\n".join(f"- {note}" for note in notes)
        + "\n\n---\n\n"
    )


def render_manual(repo: Path, insight: dict[str, Any]) -> str:
    source = insight.get("source")
    doc = f"# {Path(str(source)).name} Industrial Manual\n\n"
    base_chunk = form_chunk_path(repo, str(source))
    if base_chunk.exists():
        doc += "## Base Form Chunk\n\n"
        doc += f"本文件以 `{base_chunk.relative_to(repo).as_posix()}` 為基礎，並在後續章節補充 source-backed 方法手冊、事件入口與維護資訊。\n\n"
        doc += read_text(base_chunk) + "\n\n"
    doc += "## 1. Document Overview\n\n"
    doc += f"`{source}` 已產生 source-backed 單檔手冊。已確認的說明會附上來源行號；不確定的行為會保留在 Open Questions。\n\n"
    doc += "## 2. 核心流程\n\n"
    doc += table(
        ["Entry", "Handler", "Call Chain", "Summary", "Evidence", "Status"],
        [[w.get("entry"), w.get("handler"), " -> ".join(w.get("call_chain") or []), w.get("summary"), w.get("evidence"), w.get("status")] for w in insight.get("confirmed_workflows", [])],
    )
    details_by_name = {d.get("name"): d for d in insight.get("method_details") or []}
    doc += "\n## 3. Handler Methods\n\n"
    handler_rows = []
    for event in insight.get("ui_events", []):
        detail = details_by_name.get(event.get("handler"))
        link = f"[{event.get('handler')}](#method-{anchor(event.get('handler'))})" if detail else event.get("handler")
        handler_rows.append([
            event.get("control"),
            event.get("event"),
            link,
            detail.get("description") if detail else "N/A",
            event.get("line"),
        ])
    doc += table(["Control", "Event", "Handler Method", "Detailed Summary", "Line"], handler_rows)
    doc += "\n## 4. UI 事件入口\n\n"
    doc += table(
        ["Control", "Event", "Handler", "Line", "Status"],
        [[e.get("control"), e.get("event"), e.get("handler"), e.get("line"), e.get("status")] for e in insight.get("ui_events", [])],
    )
    doc += "\n## 5. 狀態機與 Region\n\n"
    doc += table(
        ["Kind", "Name / Expression", "Line Range", "Status"],
        [["Region", r.get("name"), f"{(r.get('line_range') or {}).get('start')}-{(r.get('line_range') or {}).get('end')}", r.get("status")] for r in insight.get("regions", [])]
        + [[s.get("kind"), s.get("expression"), f"{(s.get('line_range') or {}).get('start')}-{(s.get('line_range') or {}).get('end')}", s.get("status")] for s in insight.get("state_machines", [])],
    )
    doc += "\n## 6. 已確認副作用\n\n"
    doc += table(
        ["Method", "Effect", "Evidence", "Line Range", "Status"],
        [[s.get("method"), s.get("effect"), ", ".join(s.get("evidence") or []), f"{(s.get('line_range') or {}).get('start')}-{(s.get('line_range') or {}).get('end')}", s.get("status")] for s in insight.get("confirmed_side_effects", [])],
    )
    doc += "\n## 7. Method Details\n\n"
    for detail in insight.get("method_details") or []:
        doc += render_method_detail(detail)
    doc += "\n## 8. Open Questions\n\n"
    for q in insight.get("open_questions", []):
        doc += f"- {q}\n"
    return doc


def quality_report(insights: list[dict[str, Any]], docs_dir: Path) -> str:
    docs_text = ""
    for path in docs_dir.glob("*.md"):
        docs_text += path.read_text(encoding="utf-8", errors="replace") + "\n"
    inferred_count = len(re.findall(r"推測|需人工確認|candidate", docs_text, re.I))
    confirmed_workflows = sum(len(i.get("confirmed_workflows") or []) for i in insights)
    confirmed_side_effects = sum(len(i.get("confirmed_side_effects") or []) for i in insights)
    rows = [
        ["Manual insight 檔案數", len(insights)],
        ["已確認流程數", confirmed_workflows],
        ["已確認副作用數", confirmed_side_effects],
        ["頂層文件剩餘推測標記數", inferred_count],
    ]
    doc = "# Manual Insight 品質報告\n\n"
    doc += table(["指標", "數值"], rows)
    doc += "\n## 已檢視檔案\n\n"
    doc += table(["來源", "流程數", "副作用數", "狀態機數", "Region 數"], [
        [
            i.get("source"),
            len(i.get("confirmed_workflows") or []),
            len(i.get("confirmed_side_effects") or []),
            len(i.get("state_machines") or []),
            len(i.get("regions") or []),
        ]
        for i in insights
    ])
    return doc


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: generate_manual_insights.py <project-root> [source-file ...]", file=sys.stderr)
        return 2
    repo = Path(argv[1]).resolve()
    analysis_dir = repo / "exports" / "enterprise_analysis"
    out_dir = repo / "exports" / "manual_insights"
    manuals_dir = repo / "docs" / "manuals"
    docs_dir = repo / "docs"
    source_files = load(analysis_dir / "source_files.json", [])
    selected = select_core_sources(source_files, argv[2:])
    insights = []
    for source in selected:
        insight = build_insight(repo, source, analysis_dir)
        insights.append(insight)
        stem = Path(source).name
        write_json(out_dir / f"{stem}.insights.json", insight)
        manuals_dir.mkdir(parents=True, exist_ok=True)
        (manuals_dir / f"{stem}.md").write_text(render_manual(repo, insight), encoding="utf-8")
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "manual_insight_quality.md").write_text(quality_report(insights, docs_dir), encoding="utf-8")
    print(f"Wrote manual insights for {len(insights)} source file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
