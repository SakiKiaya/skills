#!/usr/bin/env python3
"""Starter normalizer for PLC exported files.

Usage:
    python normalize_exports.py exports/raw exports/normalized

This script is intentionally conservative. It preserves source data and writes
best-effort JSON without pretending to understand proprietary GX Works files.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

ENCODINGS = ["utf-8-sig", "utf-8", "cp932", "shift_jis", "big5"]
DEVICE_RE = re.compile(r"\b(?:X|Y|M|L|B|D|W|R|ZR|T|C|S|SM|SD)[0-9A-F]+\b", re.I)


def read_text(path: Path) -> tuple[str, str]:
    for enc in ENCODINGS:
        try:
            return path.read_text(encoding=enc), enc
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace"), "unknown-replace"


def read_csv(path: Path) -> tuple[list[dict[str, Any]], str]:
    text, enc = read_text(path)
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
    return rows, enc


def lower_keys(row: dict[str, Any]) -> dict[str, Any]:
    return {str(k).strip().lower(): v for k, v in row.items() if k is not None}


def pick(row: dict[str, Any], names: list[str]) -> Any:
    r = lower_keys(row)
    for n in names:
        if n.lower() in r and r[n.lower()] not in (None, ""):
            return r[n.lower()]
    return None


def classify(path: Path) -> str:
    p = str(path).lower()
    if "label" in p:
        return "labels"
    if "comment" in p or "device" in p:
        return "devices"
    if "parameter" in p or "param" in p:
        return "parameters"
    if "module" in p:
        return "modules"
    if "network" in p or "ethernet" in p or "cc-link" in p:
        return "networks"
    if "cross" in p or "xref" in p or "reference" in p:
        return "cross_reference"
    if path.suffix.lower() in [".st", ".txt", ".mnemonic"] or "program" in p:
        return "programs"
    return "unknown"


def main(raw_dir: str, out_dir: str) -> int:
    raw = Path(raw_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    result: dict[str, list[dict[str, Any]]] = {
        "labels": [], "devices": [], "programs": [], "parameters": [],
        "modules": [], "networks": [], "cross_reference": [], "diagnostics": []
    }
    project_sources = []

    for path in sorted(raw.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(raw))
        project_sources.append(rel)
        kind = classify(path)
        ext = path.suffix.lower()
        try:
            if ext in [".csv", ".tsv"]:
                rows, enc = read_csv(path)
                for row in rows:
                    item = {"source_file": rel, "raw": row}
                    if kind == "labels":
                        item.update({
                            "name": pick(row, ["name", "label", "label name", "variable"]),
                            "scope": pick(row, ["scope", "class"]) or "unknown",
                            "program": pick(row, ["program", "pou"]),
                            "address": pick(row, ["address", "device", "assign device"]),
                            "data_type": pick(row, ["data type", "type", "datatype"]),
                            "comment": pick(row, ["comment", "description", "remark"]),
                        })
                    elif kind == "devices":
                        item.update({
                            "device": pick(row, ["device", "address"]),
                            "comment": pick(row, ["comment", "description", "remark"]),
                        })
                    elif kind == "parameters":
                        item.update({
                            "category": "unknown",
                            "parameter_name": pick(row, ["parameter", "parameter name", "name", "item"]),
                            "value": pick(row, ["value", "setting", "set value"]),
                            "unit": pick(row, ["unit"]),
                            "module": pick(row, ["module", "model"]),
                            "station": pick(row, ["station", "station no"]),
                        })
                    result.get(kind, result["diagnostics"]).append(item)
                result["diagnostics"].append({"source_file": rel, "message": f"parsed csv as {kind}", "encoding": enc, "rows": len(rows)})
            else:
                text, enc = read_text(path)
                devices = sorted(set(DEVICE_RE.findall(text)))
                if kind == "programs":
                    result["programs"].append({
                        "name": path.stem,
                        "language": "ST" if ext == ".st" else "TXT_OR_MNEMONIC",
                        "source_file": rel,
                        "calls": [],
                        "devices_read": devices,
                        "devices_written": [],
                        "raw_summary": {"line_count": len(text.splitlines()), "encoding": enc}
                    })
                else:
                    result["diagnostics"].append({"source_file": rel, "message": f"unstructured file classified as {kind}", "encoding": enc})
        except Exception as exc:
            result["diagnostics"].append({"source_file": rel, "error": repr(exc)})

    (out / "project.json").write_text(json.dumps({"project": {"name": None, "plc_series": None, "cpu_model": None, "software": None, "exported_at": None, "source_files": project_sources}}, ensure_ascii=False, indent=2), encoding="utf-8")
    for key in ["labels", "devices", "programs", "parameters", "modules", "networks", "cross_reference", "diagnostics"]:
        (out / f"{key}.json").write_text(json.dumps(result[key], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote normalized files to {out}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: normalize_exports.py exports/raw exports/normalized", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
