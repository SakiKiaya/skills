#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path, default: Any):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def val(x: Any) -> str:
    return "N/A" if x in (None, "") else str(x).replace("\n", " ")


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(val(c) for c in row) + " |")
    return "\n".join(out) + "\n"


def main(norm_dir: str, docs_dir: str) -> int:
    norm = Path(norm_dir)
    docs = Path(docs_dir)
    docs.mkdir(parents=True, exist_ok=True)

    project = load(norm / "project.json", {"project": {}}).get("project", {})
    programs = load(norm / "programs.json", [])
    labels = load(norm / "labels.json", [])
    devices = load(norm / "devices.json", [])
    params = load(norm / "parameters.json", [])
    modules = load(norm / "modules.json", [])
    networks = load(norm / "networks.json", [])
    xref = load(norm / "cross_reference.json", [])
    diagnostics = load(norm / "diagnostics.json", [])

    index = """# PLC Project Documentation

Generated from exported GX Works text files.

## Index

- [00 Project Overview](00_project_overview.md)
- [01 System Configuration](01_system_configuration.md)
- [02 CPU Parameters](02_cpu_parameters.md)
- [03 Module Parameters](03_module_parameters.md)
- [04 Network Parameters](04_network_parameters.md)
- [05 Program Structure](05_program_structure.md)
- [06 Labels](06_labels.md)
- [07 Device Comments](07_device_comments.md)
- [08 Alarm List](08_alarm_list.md)
- [09 Cross Reference](09_cross_reference.md)
- [10 Diagnostics](10_diagnostics.md)
"""
    (docs / "README.md").write_text(index, encoding="utf-8")

    overview_rows = [[k, v] for k, v in project.items() if k != "source_files"]
    src_rows = [[s] for s in project.get("source_files", [])]
    (docs / "00_project_overview.md").write_text("# Project Overview\n\n" + table(["Field", "Value"], overview_rows) + "\n## Source Files\n\n" + table(["Path"], src_rows), encoding="utf-8")

    (docs / "01_system_configuration.md").write_text("# System Configuration\n\n## Modules\n\n" + table(["Source", "Raw"], [[m.get("source_file"), m.get("raw", {})] for m in modules]) + "\n## Networks\n\n" + table(["Source", "Raw"], [[n.get("source_file"), n.get("raw", {})] for n in networks]), encoding="utf-8")

    param_rows = [[p.get("category"), p.get("module") or p.get("station"), p.get("parameter_name"), p.get("value"), "需查手冊", "需確認", "確認與實機設定一致", p.get("source_file")] for p in params]
    (docs / "02_cpu_parameters.md").write_text("# CPU Parameters\n\n" + table(["Category", "Module/Station", "Parameter", "Value", "Meaning", "Risk", "Check Point", "Source"], param_rows), encoding="utf-8")
    (docs / "03_module_parameters.md").write_text("# Module Parameters\n\n" + table(["Category", "Module/Station", "Parameter", "Value", "Meaning", "Risk", "Check Point", "Source"], param_rows), encoding="utf-8")
    (docs / "04_network_parameters.md").write_text("# Network Parameters\n\n" + table(["Category", "Module/Station", "Parameter", "Value", "Meaning", "Risk", "Check Point", "Source"], param_rows), encoding="utf-8")

    prog_rows = [[p.get("name"), p.get("language"), ", ".join(p.get("calls", [])), ", ".join(p.get("devices_read", [])[:20]), p.get("source_file")] for p in programs]
    (docs / "05_program_structure.md").write_text("# Program Structure\n\n" + table(["Program", "Language", "Calls", "Devices Used", "Source"], prog_rows), encoding="utf-8")

    label_rows = [[l.get("scope"), l.get("program"), l.get("name"), l.get("address"), l.get("data_type"), l.get("comment"), l.get("source_file")] for l in labels]
    (docs / "06_labels.md").write_text("# Labels\n\n" + table(["Scope", "Program", "Name", "Address", "Type", "Comment", "Source"], label_rows), encoding="utf-8")

    device_rows = [[d.get("device"), d.get("comment"), d.get("source_file")] for d in devices]
    (docs / "07_device_comments.md").write_text("# Device Comments\n\n" + table(["Device", "Comment", "Source"], device_rows), encoding="utf-8")

    alarms = [d for d in devices if "alarm" in str(d.get("comment", "")).lower() or "異常" in str(d.get("comment", ""))]
    (docs / "08_alarm_list.md").write_text("# Alarm List\n\n" + table(["Device", "Comment", "Source"], [[d.get("device"), d.get("comment"), d.get("source_file")] for d in alarms]), encoding="utf-8")

    (docs / "09_cross_reference.md").write_text("# Cross Reference\n\n" + table(["Source", "Raw"], [[x.get("source_file"), x.get("raw", {})] for x in xref]), encoding="utf-8")
    (docs / "10_diagnostics.md").write_text("# Diagnostics\n\n" + table(["Source", "Message/Error", "Detail"], [[d.get("source_file"), d.get("message") or d.get("error"), d] for d in diagnostics]), encoding="utf-8")
    print(f"Wrote docs to {docs}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_docs.py exports/normalized docs", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
