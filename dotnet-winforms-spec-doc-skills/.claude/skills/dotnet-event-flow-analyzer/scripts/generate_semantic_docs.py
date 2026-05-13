#!/usr/bin/env python3
"""
Generate extra semantic docs from exports/semantic.

Usage:
    python generate_semantic_docs.py exports/semantic docs
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
from typing import Any


def load(path: Path, default: Any):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def esc(v: Any) -> str:
    s = "N/A" if v in (None, "") else str(v).replace("\n", " ").replace("|", "\\|")
    return s[:800] + "..." if len(s) > 800 else s


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(esc(c) for c in row) + " |")
    return "\n".join(out) + "\n"


def main(semantic_dir: str, docs_dir: str) -> int:
    sem = Path(semantic_dir)
    docs = Path(docs_dir)
    docs.mkdir(parents=True, exist_ok=True)

    operation = load(sem / "operation_flows.json", [])
    startup = load(sem / "startup_flow.json", [])
    risks = load(sem / "risk_points.json", [])
    ui_backend = load(sem / "ui_backend_flows.json", [])
    threading = load(sem / "threading_flows.json", [])
    timers = load(sem / "timer_flows.json", [])
    devices = load(sem / "device_control_flows.json", [])
    responsibilities = load(sem / "ui_responsibilities.json", [])
    critical = load(sem / "critical_operations.json", [])

    doc = "# Semantic Architecture and Flow Analysis\n\n"
    doc += "## UI Responsibilities\n\n"
    doc += table(["Form", "Role Candidates", "Control Count", "Operation Count", "Confidence"], [
        [r.get("form"), r.get("role_candidates"), r.get("control_count"), r.get("operation_count"), r.get("confidence")]
        for r in responsibilities
    ])
    doc += "\n## Critical Operations\n\n"
    doc += table(["Source", "Form", "Control/Operation", "Type", "Keywords", "Confidence"], [
        [r.get("source_type"), r.get("form"), r.get("control") or r.get("operation_name"), r.get("operation_type"), r.get("matched_keywords"), r.get("confidence")]
        for r in critical
    ])
    doc += "\n## Operation Flows\n\n"
    doc += table(["Operation", "Type", "Form", "Handler", "Direct Calls", "Devices", "Confidence"], [
        [o.get("operation_name"), o.get("operation_type"), o.get("form"), o.get("handler"), o.get("direct_called_methods"), o.get("device_candidates"), o.get("confidence")]
        for o in operation
    ])
    doc += "\n## Startup Flow Candidates\n\n"
    doc += table(["Startup Candidate", "Handler", "Calls", "Reason", "Confidence"], [
        [s.get("startup_candidate"), s.get("handler"), s.get("calls"), s.get("reason"), s.get("confidence")]
        for s in startup
    ])
    doc += "\n## UI Backend Flows\n\n"
    doc += table(["UI Trigger", "Handler", "Backend Calls", "Expanded Chain", "Confidence"], [
        [u.get("ui_trigger"), u.get("handler"), u.get("backend_calls"), u.get("expanded_call_chain"), u.get("confidence")]
        for u in ui_backend
    ])
    doc += "\n## Threading / Timer Flows\n\n"
    doc += table(["Type", "Item", "Reason", "Confidence"], 
        [["Threading", t.get("flow") or t.get("method"), t.get("reason"), t.get("confidence")] for t in threading] +
        [["Timer", t.get("flow") or t.get("method"), t.get("reason"), t.get("confidence")] for t in timers]
    )
    doc += "\n## Device Control Flow Candidates\n\n"
    doc += table(["Flow", "Handler", "Device", "Keywords", "Calls", "Confidence"], [
        [d.get("flow"), d.get("handler"), d.get("device_type"), d.get("matched_keywords"), d.get("calls"), d.get("confidence")]
        for d in devices
    ])
    doc += "\n## Risk Points\n\n"
    doc += table(["Type", "Item", "Device", "Risk", "Suggested Review", "Confidence"], [
        [r.get("risk_type"), r.get("item"), r.get("device_type"), r.get("risk"), r.get("suggested_review"), r.get("confidence")]
        for r in risks
    ])

    (docs / "09_semantic_flow_analysis.md").write_text(doc, encoding="utf-8")
    print(f"Wrote {docs / '09_semantic_flow_analysis.md'}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_semantic_docs.py exports/semantic docs", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
