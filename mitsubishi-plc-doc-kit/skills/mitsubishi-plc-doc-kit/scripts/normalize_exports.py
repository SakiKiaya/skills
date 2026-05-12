#!/usr/bin/env python3
"""
Minimal starter normalizer for Mitsubishi PLC exported CSV files.
This script is intentionally conservative. Extend column mappings per project.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
RAW = ROOT / "exports" / "raw"
OUT = ROOT / "exports" / "normalized"


def read_csv(path: Path) -> list[dict[str, Any]]:
    encodings = ["utf-8-sig", "cp932", "shift_jis", "big5", "utf-8"]
    last_error: Exception | None = None
    for enc in encodings:
        try:
            with path.open("r", encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except Exception as exc:  # keep trying common GX export encodings
            last_error = exc
    raise RuntimeError(f"Failed to read {path}: {last_error}")


def pick(row: dict[str, Any], candidates: list[str]) -> str:
    lowered = {str(k).strip().lower(): v for k, v in row.items()}
    for c in candidates:
        v = lowered.get(c.lower())
        if v not in (None, ""):
            return str(v).strip()
    return ""


def normalize_labels() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in sorted((RAW / "labels").glob("*.csv")) if (RAW / "labels").exists() else []:
        rows = read_csv(path)
        for i, row in enumerate(rows, start=2):
            results.append({
                "name": pick(row, ["name", "label name", "label", "variable", "變數名稱", "標籤名稱"]),
                "scope": "global" if "global" in path.name.lower() else "local" if "local" in path.name.lower() else "unknown",
                "program": pick(row, ["program", "pou", "program name", "程式"]),
                "data_type": pick(row, ["data type", "type", "datatype", "資料型態"]),
                "address": pick(row, ["device", "address", "assign device", "軟元件", "位址"]),
                "initial_value": pick(row, ["initial value", "init", "初始值"]),
                "comment": pick(row, ["comment", "description", "remark", "註解", "說明"]),
                "source_file": str(path),
                "source_row": i,
                "raw": row,
            })
    return results


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    diagnostics: list[dict[str, Any]] = []

    labels = normalize_labels()
    (OUT / "labels.json").write_text(json.dumps({"labels": labels}, ensure_ascii=False, indent=2), encoding="utf-8")

    if not labels:
        diagnostics.append({
            "level": "warning",
            "source_file": "exports/raw/labels",
            "source_row": 0,
            "message": "No label CSV files were found or parsed.",
            "raw": "",
        })

    (OUT / "diagnostics.json").write_text(json.dumps({"diagnostics": diagnostics}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote normalized output to {OUT}")


if __name__ == "__main__":
    main()
