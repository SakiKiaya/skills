#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
cmd = [
    sys.executable,
    str(ROOT / ".claude/skills/dotnet-openspec-generator/scripts/generate_openspec.py"),
    str(TARGET / "exports" / "enterprise_analysis"),
    str(TARGET / "exports" / "analysis_chunks"),
    str(TARGET / "docs" / "chunks"),
    str(TARGET / "openspec"),
]
print("+", " ".join(cmd))
subprocess.check_call(cmd)
print("OpenSpec generation complete.")
