#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()

args = sys.argv[2:]
if not args:
    print("Usage:")
    print("  python run_regenerate_chunk_doc.py /path/to/repo --chunk-id <id>")
    print("  python run_regenerate_chunk_doc.py /path/to/repo --chunk-type form")
    print("  python run_regenerate_chunk_doc.py /path/to/repo --all")
    raise SystemExit(2)

cmd = [
    sys.executable,
    str(ROOT / ".claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py"),
    str(TARGET / "exports" / "analysis_chunks"),
    str(TARGET / "docs" / "chunks"),
    *args,
]
print("+", " ".join(cmd))
subprocess.check_call(cmd)
