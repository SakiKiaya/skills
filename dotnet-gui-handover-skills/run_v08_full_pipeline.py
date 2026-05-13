#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()

def run(script, *args):
    cmd = [sys.executable, str(script), *map(str, args)]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)

analysis = TARGET / "exports" / "enterprise_analysis"
chunks = TARGET / "exports" / "analysis_chunks"
docs_chunks = TARGET / "docs" / "chunks"
docs = TARGET / "docs"
openspec = TARGET / "openspec"

run(ROOT / ".claude/skills/dotnet-gui-project-analyzer/scripts/enterprise_gui_analyzer.py", TARGET, analysis)
run(ROOT / ".claude/skills/dotnet-method-purpose-analyzer/scripts/method_purpose_analyzer.py", analysis)
run(ROOT / ".claude/skills/dotnet-analysis-chunker/scripts/analysis_chunker.py", analysis, chunks)
run(ROOT / ".claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py", chunks, docs_chunks, "--all")
run(ROOT / ".claude/skills/dotnet-chunk-aware-doc-generator/scripts/generate_chunk_aware_docs.py", analysis, chunks, docs_chunks, docs)
run(ROOT / ".claude/skills/dotnet-openspec-generator/scripts/generate_openspec.py", analysis, chunks, docs_chunks, openspec)
print("v1.0 full pipeline complete.")
