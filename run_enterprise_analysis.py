#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
analysis = TARGET / "exports" / "enterprise_analysis"
docs = TARGET / "docs"
openspec = TARGET / "openspec"

def run(*args):
    cmd = [sys.executable] + [str(a) for a in args]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)

run(ROOT / ".claude/skills/dotnet-gui-project-analyzer/scripts/enterprise_gui_analyzer.py", TARGET, analysis)
run(ROOT / ".claude/skills/dotnet-enterprise-doc-generator/scripts/generate_enterprise_docs.py", analysis, docs)
run(ROOT / ".claude/skills/dotnet-openspec-generator/scripts/generate_openspec.py", analysis, openspec)
print("Enterprise GUI handover analysis complete.")
