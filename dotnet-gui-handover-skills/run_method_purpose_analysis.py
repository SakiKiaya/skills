#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
analysis = TARGET / "exports" / "enterprise_analysis"
docs = TARGET / "docs"

def run(script, *args):
    cmd = [sys.executable, str(script), *map(str, args)]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)

run(ROOT / ".claude/skills/dotnet-method-purpose-analyzer/scripts/method_purpose_analyzer.py", analysis)
run(ROOT / ".claude/skills/dotnet-enterprise-doc-generator/scripts/generate_enterprise_docs.py", analysis, docs)
print("Method purpose analysis and docs generation complete.")
