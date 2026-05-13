#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()

analysis = TARGET / "exports" / "enterprise_analysis"
chunks = TARGET / "exports" / "analysis_chunks"
docs_chunks = TARGET / "docs" / "chunks"
docs = TARGET / "docs"

cmd = [
    sys.executable,
    str(ROOT / ".claude/skills/dotnet-chunk-aware-doc-generator/scripts/generate_chunk_aware_docs.py"),
    str(analysis),
    str(chunks),
    str(docs_chunks),
    str(docs),
]
print("+", " ".join(cmd))
subprocess.check_call(cmd)
print("Chunk-aware final docs generated.")
