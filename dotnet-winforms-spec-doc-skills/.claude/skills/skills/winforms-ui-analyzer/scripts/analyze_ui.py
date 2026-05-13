#!/usr/bin/env python3
"""
Thin wrapper for WinForms UI analysis.

Usage:
    python analyze_ui.py <repo_root> <out_dir>

This delegates to dotnet-project-normalizer's normalize_project.py because
Designer.cs / Designer.vb parsing is shared with project normalization.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NORMALIZER = HERE.parents[2] / "dotnet-project-normalizer" / "scripts" / "normalize_project.py"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: analyze_ui.py <repo_root> <out_dir>", file=sys.stderr)
        raise SystemExit(2)
    sys.argv = [str(NORMALIZER), sys.argv[1], sys.argv[2]]
    runpy.run_path(str(NORMALIZER), run_name="__main__")
