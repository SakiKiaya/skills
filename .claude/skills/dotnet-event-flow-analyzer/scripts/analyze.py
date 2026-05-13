#!/usr/bin/env python3
from pathlib import Path
import runpy, sys
script = Path(__file__).resolve().parents[2] / "dotnet-gui-project-analyzer" / "scripts" / "enterprise_gui_analyzer.py"
if __name__ == "__main__":
    sys.argv = [str(script)] + sys.argv[1:]
    runpy.run_path(str(script), run_name="__main__")
