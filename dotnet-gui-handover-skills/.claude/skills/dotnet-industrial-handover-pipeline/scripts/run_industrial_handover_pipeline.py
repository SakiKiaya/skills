#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).resolve()


def find_skills_root() -> Path:
    for parent in SCRIPT.parents:
        if (
            (parent / "dotnet-gui-project-analyzer").exists()
            and (parent / "dotnet-analysis-chunker").exists()
            and (parent / "dotnet-chunk-aware-doc-generator").exists()
        ):
            return parent
    raise RuntimeError("Cannot locate skills root. Expected sibling skills such as dotnet-gui-project-analyzer.")


def find_repo_root(target: Path) -> Path | None:
    candidates = [Path.cwd().resolve(), *Path.cwd().resolve().parents, target.resolve(), *target.resolve().parents, *SCRIPT.parents]
    for candidate in candidates:
        if (candidate / "run_v09_full_pipeline.py").exists() and (candidate / ".claude" / "skills").exists():
            return candidate
    return None


def run(script: Path, *args: Path | str):
    cmd = [sys.executable, str(script), *map(str, args)]
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: run_industrial_handover_pipeline.py <project-root> [core-source-file ...]", file=sys.stderr)
        return 2

    target = Path(argv[1]).resolve()
    requested_sources = argv[2:]
    skills_root = find_skills_root()
    repo_root = find_repo_root(target)
    analysis = target / "exports" / "enterprise_analysis"
    chunks = target / "exports" / "analysis_chunks"
    docs_chunks = target / "docs" / "chunks"
    docs = target / "docs"
    openspec = target / "openspec"

    if repo_root and (repo_root / "run_v09_full_pipeline.py").exists():
        run(repo_root / "run_v09_full_pipeline.py", target)
    else:
        run(skills_root / "dotnet-gui-project-analyzer/scripts/enterprise_gui_analyzer.py", target, analysis)
        run(skills_root / "dotnet-method-purpose-analyzer/scripts/method_purpose_analyzer.py", analysis)
        run(skills_root / "dotnet-analysis-chunker/scripts/analysis_chunker.py", analysis, chunks)
        run(skills_root / "dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py", chunks, docs_chunks, "--all")
        run(skills_root / "dotnet-chunk-aware-doc-generator/scripts/generate_chunk_aware_docs.py", analysis, chunks, docs_chunks, docs)
        run(skills_root / "dotnet-openspec-generator/scripts/generate_openspec.py", analysis, chunks, docs_chunks, openspec)
        run(skills_root / "dotnet-readme-generator/scripts/generate_readme.py", target)
    run(SCRIPT.parent / "generate_manual_insights.py", target, *requested_sources)

    # Refresh docs that can consume manual insights.
    run(skills_root / "dotnet-chunk-aware-doc-generator/scripts/generate_chunk_aware_docs.py", analysis, chunks, docs_chunks, docs)
    run(skills_root / "dotnet-openspec-generator/scripts/generate_openspec.py", analysis, chunks, docs_chunks, openspec)
    run(skills_root / "dotnet-readme-generator/scripts/generate_readme.py", target)
    run(SCRIPT.parent / "generate_manual_insights.py", target, *requested_sources)

    print("industrial handover pipeline complete.")
    print(f"- Manual insights: {target / 'exports' / 'manual_insights'}")
    print(f"- File manuals: {target / 'docs' / 'manuals'}")
    print(f"- Quality report: {target / 'docs' / 'manual_insight_quality.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
