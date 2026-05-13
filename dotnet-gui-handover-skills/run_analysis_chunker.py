#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
analysis = TARGET / "exports" / "enterprise_analysis"
chunks = TARGET / "exports" / "analysis_chunks"

cmd = [
    sys.executable,
    str(ROOT / ".claude/skills/dotnet-analysis-chunker/scripts/analysis_chunker.py"),
    str(analysis),
    str(chunks),
]
print("+", " ".join(cmd))
subprocess.check_call(cmd)
print("Analysis chunks generated.")
