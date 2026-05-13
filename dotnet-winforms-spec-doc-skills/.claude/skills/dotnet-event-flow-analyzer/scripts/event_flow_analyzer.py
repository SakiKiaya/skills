#!/usr/bin/env python3
"""
dotnet-event-flow-analyzer v0.5

Reads normalized WinForms IR and produces semantic flow analysis.

Usage:
    python event_flow_analyzer.py exports/normalized exports/semantic
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
from typing import Any

THREAD_KEYWORDS = [
    "thread", "task", "backgroundworker", "dowork", "runworker", "async", "await",
    "begininvoke", "invoke", "timer", "tick", "sleep", "delay"
]

TIMER_KEYWORDS = ["timer", "tick", "interval"]

DEVICE_KEYWORDS = {
    "PLC": ["plc", "mcprotocol", "mitsubishi", "modbus", "writebit", "readbit", "writedevice", "readdevice"],
    "Camera": ["camera", "grab", "trigger", "capture", "basler", "hik", "hikvision", "cognex"],
    "Vision": ["vision", "aoi", "inspect", "inspection", "halcon", "opencv", "emgu"],
    "Motion": ["motion", "axis", "servo", "home", "moveabs", "moverel"],
    "Serial": ["serial", "serialport", "comport", "datareceived"],
    "Socket": ["socket", "tcp", "udp", "client", "server"],
    "LightController": ["light", "lighting", "strobe"],
    "Database": ["sql", "database", "db", "insert", "update", "select"],
}

CRITICAL_KEYWORDS = {
    "Start": ["start", "run", "begin"],
    "Stop": ["stop", "end", "abort", "cancel"],
    "Reset": ["reset", "clear"],
    "Alarm": ["alarm", "error", "fault", "異常", "警報"],
    "Emergency": ["emergency", "ems", "estop"],
    "Home": ["home", "origin"],
}


def load(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def low(value: Any) -> str:
    return str(value or "").lower()


def confidence_from_hits(hits: int, base: float = 0.45) -> float:
    return min(0.95, base + hits * 0.15)


def detect_keywords(text: str, keyword_map: dict[str, list[str]]) -> list[dict[str, Any]]:
    t = low(text)
    results = []
    for category, words in keyword_map.items():
        hits = [w for w in words if w.lower() in t]
        if hits:
            results.append({
                "category": category,
                "matched_keywords": hits,
                "confidence": confidence_from_hits(len(hits)),
            })
    return results


def method_index(methods: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    idx = {}
    for m in methods:
        name = m.get("name")
        if name and name not in idx:
            idx[name] = m
    return idx


def expand_call_chain(handler: str, methods_by_name: dict[str, dict[str, Any]], depth: int = 2) -> list[dict[str, Any]]:
    """Best-effort recursive expansion using method names only."""
    chain = []
    visited = set()

    def walk(name: str, level: int):
        if level > depth or name in visited:
            return
        visited.add(name)
        m = methods_by_name.get(name)
        if not m:
            return
        for c in m.get("calls", []) or []:
            callee = c.get("method")
            item = {
                "level": level,
                "caller": name,
                "callee": callee,
                "target": c.get("target"),
                "known_internal_method": c.get("known_internal_method"),
            }
            chain.append(item)
            if callee:
                walk(callee, level + 1)

    walk(handler, 1)
    return chain


def main(norm_dir: str, out_dir: str) -> int:
    norm = Path(norm_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    event_flows = load(norm / "event_flows.json", [])
    call_graph = load(norm / "call_graph.json", [])
    methods = load(norm / "methods.json", [])
    events = load(norm / "events.json", [])
    controls = load(norm / "controls.json", [])

    methods_by_name = method_index(methods)

    operation_flows = []
    startup_flow = []
    risk_points = []
    ui_backend_flows = []
    threading_flows = []
    timer_flows = []
    device_control_flows = []

    # Analyze event flows.
    for flow in event_flows:
        name = flow.get("flow_name") or ""
        handler = flow.get("handler") or ""
        trigger = flow.get("trigger") or {}
        called = flow.get("called_methods") or []
        calls_text = " ".join([name, handler, " ".join(called), str(flow.get("calls") or [])])
        expanded_chain = expand_call_chain(handler, methods_by_name, depth=2)

        critical = detect_keywords(calls_text, CRITICAL_KEYWORDS)
        devices = detect_keywords(calls_text, DEVICE_KEYWORDS)

        op_type = critical[0]["category"] if critical else "General"
        operation = {
            "operation_name": name,
            "operation_type": op_type,
            "form": flow.get("form"),
            "trigger": trigger,
            "handler": handler,
            "handler_source": flow.get("handler_source"),
            "handler_line_range": flow.get("handler_line_range"),
            "direct_called_methods": called,
            "expanded_call_chain": expanded_chain,
            "criticality_candidates": critical,
            "device_candidates": devices,
            "confidence": 0.75 if flow.get("confidence") == "matched-handler" else 0.45,
        }
        operation_flows.append(operation)

        ui_backend_flows.append({
            "ui_trigger": {
                "form": flow.get("form"),
                "control": trigger.get("control"),
                "event": trigger.get("event"),
                "binding": trigger.get("binding"),
            },
            "handler": handler,
            "backend_calls": called,
            "expanded_call_chain": expanded_chain,
            "confidence": operation["confidence"],
        })

        if "load" in low(name) or "shown" in low(name) or low(trigger.get("event")) in ["load", "shown"]:
            startup_flow.append({
                "startup_candidate": name,
                "handler": handler,
                "calls": called,
                "reason": "Form Load/Shown event candidate",
                "confidence": 0.75,
            })

        if any(k in low(calls_text) for k in TIMER_KEYWORDS):
            timer_flows.append({
                "flow": name,
                "handler": handler,
                "calls": called,
                "reason": "Timer/Tick/Interval keyword candidate",
                "confidence": 0.65,
            })

        if any(k in low(calls_text) for k in THREAD_KEYWORDS):
            threading_flows.append({
                "flow": name,
                "handler": handler,
                "calls": called,
                "reason": "Threading/async/timer keyword candidate",
                "confidence": 0.6,
            })

        for d in devices:
            device_control_flows.append({
                "flow": name,
                "handler": handler,
                "device_type": d["category"],
                "matched_keywords": d["matched_keywords"],
                "calls": called,
                "confidence": d["confidence"],
            })

    # Analyze methods not necessarily linked to UI events.
    for m in methods:
        text = " ".join([
            str(m.get("name") or ""),
            str(m.get("source_file") or ""),
            " ".join(m.get("called_methods") or []),
            str(m.get("calls") or []),
            str(m.get("purpose_hint") or ""),
        ])
        if any(k in low(text) for k in THREAD_KEYWORDS):
            threading_flows.append({
                "method": m.get("name"),
                "source_file": m.get("source_file"),
                "line_range": m.get("line_range"),
                "reason": "Method-level threading keyword candidate",
                "confidence": 0.55,
            })
        if any(k in low(text) for k in TIMER_KEYWORDS):
            timer_flows.append({
                "method": m.get("name"),
                "source_file": m.get("source_file"),
                "line_range": m.get("line_range"),
                "reason": "Method-level timer keyword candidate",
                "confidence": 0.55,
            })

    # Risk points.
    for tf in threading_flows:
        risk_points.append({
            "risk_type": "threading_or_async_candidate",
            "item": tf.get("flow") or tf.get("method"),
            "reason": tf.get("reason"),
            "risk": "May update UI from background thread or block UI if used incorrectly.",
            "suggested_review": "Check Invoke/BeginInvoke usage, cancellation, exception handling, and blocking calls.",
            "confidence": tf.get("confidence", 0.5),
        })

    for tf in timer_flows:
        risk_points.append({
            "risk_type": "timer_candidate",
            "item": tf.get("flow") or tf.get("method"),
            "reason": tf.get("reason"),
            "risk": "Timer flow may re-enter, block UI, or overlap device calls.",
            "suggested_review": "Check timer interval, enabled/disabled lifecycle, and whether handler execution can exceed interval.",
            "confidence": tf.get("confidence", 0.5),
        })

    for df in device_control_flows:
        risk_points.append({
            "risk_type": "device_control_candidate",
            "item": df.get("flow"),
            "device_type": df.get("device_type"),
            "risk": "Device control path should be reviewed for timeout, retry, exception handling, and safe-state behavior.",
            "suggested_review": "Check connection state, error handling, and operator feedback.",
            "confidence": df.get("confidence", 0.5),
        })

    write(out / "operation_flows.json", operation_flows)
    write(out / "startup_flow.json", startup_flow)
    write(out / "risk_points.json", risk_points)
    write(out / "ui_backend_flows.json", ui_backend_flows)
    write(out / "threading_flows.json", threading_flows)
    write(out / "timer_flows.json", timer_flows)
    write(out / "device_control_flows.json", device_control_flows)

    print(f"Event flow semantic analysis complete: {out}")
    print(f"- operation_flows: {len(operation_flows)}")
    print(f"- startup_flow: {len(startup_flow)}")
    print(f"- risk_points: {len(risk_points)}")
    print(f"- device_control_flows: {len(device_control_flows)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: event_flow_analyzer.py <normalized_dir> <semantic_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
