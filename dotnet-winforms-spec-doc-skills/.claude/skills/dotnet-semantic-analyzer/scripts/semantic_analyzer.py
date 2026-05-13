#!/usr/bin/env python3
"""
dotnet-semantic-analyzer v0.5

Usage:
    python semantic_analyzer.py exports/normalized exports/semantic
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
from typing import Any

LAYER_KEYWORDS = {
    "UI Layer": ["form", "dialog", "view", "screen", "ui"],
    "PLC Layer": ["plc", "mcprotocol", "mitsubishi", "modbus"],
    "Vision Layer": ["vision", "aoi", "inspect", "inspection", "halcon", "opencv", "emgu"],
    "Camera Layer": ["camera", "grab", "trigger", "capture"],
    "Motion Layer": ["motion", "axis", "servo", "home"],
    "Database Layer": ["sql", "database", "db"],
    "Communication Layer": ["socket", "tcp", "udp", "serial", "comport"],
    "Utility Layer": ["util", "helper", "common"],
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
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def low(v: Any) -> str:
    return str(v or "").lower()


def hits(text: str, words: list[str]) -> list[str]:
    t = low(text)
    return [w for w in words if w.lower() in t]


def conf(n: int) -> float:
    return min(0.95, 0.45 + 0.15 * n)


def main(norm_dir: str, semantic_dir: str) -> int:
    norm = Path(norm_dir)
    out = Path(semantic_dir)
    out.mkdir(parents=True, exist_ok=True)

    projects = load(norm / "projects.json", [])
    forms = load(norm / "forms.json", [])
    controls = load(norm / "controls.json", [])
    methods = load(norm / "methods.json", [])
    operation_flows = load(out / "operation_flows.json", [])
    device_control_flows = load(out / "device_control_flows.json", [])
    threading_flows = load(out / "threading_flows.json", [])

    architecture_layers = []
    for p in projects:
        text = " ".join([str(p.get("name")), str(p.get("project_file")), str(p.get("references")), str(p.get("nuget_packages"))])
        for layer, words in LAYER_KEYWORDS.items():
            h = hits(text, words)
            if h:
                architecture_layers.append({
                    "source_type": "project",
                    "source": p.get("name"),
                    "layer": layer,
                    "matched_keywords": h,
                    "confidence": conf(len(h)),
                    "inference": True,
                })

    for m in methods:
        text = " ".join([str(m.get("name")), str(m.get("source_file")), str(m.get("called_methods")), str(m.get("purpose_hint"))])
        for layer, words in LAYER_KEYWORDS.items():
            h = hits(text, words)
            if h:
                architecture_layers.append({
                    "source_type": "method",
                    "source": m.get("name"),
                    "source_file": m.get("source_file"),
                    "layer": layer,
                    "matched_keywords": h,
                    "confidence": conf(len(h)),
                    "inference": True,
                })

    ui_responsibilities = []
    for f in forms:
        fname = f.get("form_name")
        form_controls = [c for c in controls if c.get("form") == fname]
        form_flows = [op for op in operation_flows if op.get("form") == fname]
        role_candidates = []
        text = " ".join([str(fname), str(form_controls), str(form_flows)])
        for layer, words in LAYER_KEYWORDS.items():
            h = hits(text, words)
            if h:
                role_candidates.append({
                    "role": layer,
                    "matched_keywords": h,
                    "confidence": conf(len(h)),
                })
        if "main" in low(fname):
            role_candidates.append({"role": "Main Control UI", "matched_keywords": ["main"], "confidence": 0.7})
        ui_responsibilities.append({
            "form": fname,
            "role_candidates": role_candidates,
            "control_count": len(form_controls),
            "operation_count": len(form_flows),
            "confidence": max([r["confidence"] for r in role_candidates], default=0.4),
            "inference": True,
        })

    critical_operations = []
    for c in controls:
        text = " ".join([str(c.get("name")), str(c.get("text")), str(c.get("events"))])
        for kind, words in CRITICAL_KEYWORDS.items():
            h = hits(text, words)
            if h:
                critical_operations.append({
                    "source_type": "control",
                    "form": c.get("form"),
                    "control": c.get("name"),
                    "operation_type": kind,
                    "matched_keywords": h,
                    "confidence": conf(len(h)),
                    "inference": True,
                })
    for op in operation_flows:
        for cand in op.get("criticality_candidates") or []:
            critical_operations.append({
                "source_type": "operation_flow",
                "operation_name": op.get("operation_name"),
                "operation_type": cand.get("category"),
                "matched_keywords": cand.get("matched_keywords"),
                "confidence": cand.get("confidence"),
                "inference": True,
            })

    backend_mappings = []
    for op in operation_flows:
        backend_mappings.append({
            "operation": op.get("operation_name"),
            "handler": op.get("handler"),
            "direct_called_methods": op.get("direct_called_methods"),
            "expanded_call_chain": op.get("expanded_call_chain"),
            "device_candidates": op.get("device_candidates"),
            "confidence": op.get("confidence"),
        })

    device_topology = []
    for df in device_control_flows:
        device_topology.append({
            "device_type": df.get("device_type"),
            "flow": df.get("flow"),
            "handler": df.get("handler"),
            "matched_keywords": df.get("matched_keywords"),
            "confidence": df.get("confidence"),
            "inference": True,
        })

    threading_model = []
    for tf in threading_flows:
        threading_model.append({
            "source": tf.get("flow") or tf.get("method"),
            "source_file": tf.get("source_file"),
            "line_range": tf.get("line_range"),
            "reason": tf.get("reason"),
            "confidence": tf.get("confidence"),
            "inference": True,
        })

    write(out / "architecture_layers.json", architecture_layers)
    write(out / "ui_responsibilities.json", ui_responsibilities)
    write(out / "critical_operations.json", critical_operations)
    write(out / "backend_mappings.json", backend_mappings)
    write(out / "device_topology.json", device_topology)
    write(out / "threading_model.json", threading_model)

    print(f"Semantic analysis complete: {out}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: semantic_analyzer.py <normalized_dir> <semantic_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
