#!/usr/bin/env python3
"""
Generate OpenSpec-style specs from normalized IR.

Usage:
    python generate_openspec.py <normalized_dir> <openspec_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def load(base: Path, name: str, default: Any):
    p = base / name
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def esc(v: Any) -> str:
    return "N/A" if v in (None, "") else str(v)


def requirement(title: str, body: str, scenario: str | None = None) -> str:
    s = f"### Requirement: {title}\n\n{body.strip()}\n"
    if scenario:
        s += f"\n#### Scenario: {title}\n\n{scenario.strip()}\n"
    return s + "\n"


def main(norm_arg: str, openspec_arg: str) -> int:
    norm = Path(norm_arg)
    out = Path(openspec_arg)
    (out / "changes").mkdir(parents=True, exist_ok=True)

    solution_obj = load(norm, "solution.json", {"solution": {}})
    solution = solution_obj.get("solution", solution_obj)
    projects = load(norm, "projects.json", [])
    deps = load(norm, "dependencies.json", [])
    forms = load(norm, "forms.json", [])
    controls = load(norm, "controls.json", [])
    events = load(norm, "events.json", [])
    classes = load(norm, "classes.json", [])
    methods = load(norm, "methods.json", [])
    configs = load(norm, "configs.json", [])

    project_md = f"""# OpenSpec Project

## Purpose

This OpenSpec workspace describes the current behavior and structure of the .NET / WinForms project for AI Agent consumption.

## Source

- Solution: `{esc(solution.get("name"))}`
- Solution Path: `{esc(solution.get("path"))}`

## Specs

- `specs/solution-architecture/spec.md`
- `specs/ui-forms/spec.md`
- `specs/business-logic/spec.md`
- `specs/configuration/spec.md`
- `specs/dependencies/spec.md`

## Rules for AI Agents

- Treat `openspec/specs/` as confirmed current-state behavior when backed by source references.
- Treat `Assumptions` and `Open Questions` as non-authoritative.
- Do not modify behavior without creating a change proposal under `openspec/changes/`.
"""
    write(out / "project.md", project_md)

    sol = "# Solution Architecture Specification\n\n## Requirements\n\n"
    sol += requirement(
        "Solution project inventory",
        f"The system SHALL contain {len(projects)} detected project(s) based on static solution/project file analysis.",
        "\n".join([f"- THEN project `{esc(p.get('name'))}` SHALL be documented with language `{esc(p.get('language'))}` and target `{esc(p.get('target_framework'))}`" for p in projects]) or "- THEN no projects were detected"
    )
    sol += "\n## Project Inventory\n\n"
    for p in projects:
        sol += f"- `{esc(p.get('name'))}`: `{esc(p.get('language'))}`, `{esc(p.get('project_file'))}`, WinForms=`{esc(p.get('is_winforms'))}`\n"
    write(out / "specs" / "solution-architecture" / "spec.md", sol)

    ui = "# UI Forms Specification\n\n## Requirements\n\n"
    for f in forms:
        fname = esc(f.get("form_name"))
        ui += requirement(
            f"{fname} form structure",
            f"The system SHALL define the `{fname}` WinForms screen based on `{esc(f.get('designer_file'))}`.",
            f"- GIVEN the application loads `{fname}`\n- THEN the form SHALL expose its detected controls and event bindings as documented in normalized IR."
        )
    ui += "\n## Detected Controls\n\n"
    for c in controls:
        ui += f"- `{esc(c.get('form'))}.{esc(c.get('name'))}` SHALL exist as `{esc(c.get('type'))}`"
        if c.get("parent"):
            ui += f" under `{esc(c.get('parent'))}`"
        ui += ".\n"
    write(out / "specs" / "ui-forms" / "spec.md", ui)

    logic = "# Business Logic Specification\n\n## Requirements\n\n"
    for e in events:
        logic += requirement(
            f"{esc(e.get('handler'))} handles {esc(e.get('control'))}.{esc(e.get('event'))}",
            f"The system SHALL bind `{esc(e.get('control'))}.{esc(e.get('event'))}` to handler `{esc(e.get('handler'))}`.",
            f"- GIVEN form `{esc(e.get('form'))}` is active\n- WHEN `{esc(e.get('control'))}.{esc(e.get('event'))}` occurs\n- THEN the system SHALL invoke `{esc(e.get('handler'))}`."
        )
    if not events:
        logic += "No confirmed event bindings were detected.\n"
    logic += "\n## Method Inventory\n\n"
    for m in methods[:500]:
        logic += f"- `{esc(m.get('name'))}` from `{esc(m.get('source_file'))}`\n"
    write(out / "specs" / "business-logic" / "spec.md", logic)

    cfg = "# Configuration Specification\n\n## Requirements\n\n"
    cfg += requirement(
        "Configuration source inventory",
        "The system SHALL keep detected configuration files documented for build, deployment, and runtime review.",
        "\n".join([f"- THEN `{esc(c.get('source_file'))}` SHALL be reviewed as `{esc(c.get('kind'))}`" for c in configs]) or "- THEN no configuration files were detected."
    )
    write(out / "specs" / "configuration" / "spec.md", cfg)

    dep = "# Dependencies Specification\n\n## Requirements\n\n"
    dep += requirement(
        "Dependency inventory",
        "The system SHALL document project, assembly, and NuGet dependencies detected from project metadata.",
        "\n".join([f"- THEN dependency `{esc(d.get('include') or d.get('id'))}` SHALL be associated with project `{esc(d.get('project'))}`" for d in deps[:200]]) or "- THEN no dependencies were detected."
    )
    dep += "\n## Dependencies\n\n"
    for d in deps:
        dep += f"- `{esc(d.get('type'))}`: `{esc(d.get('project'))}` -> `{esc(d.get('include') or d.get('id'))}`"
        if d.get("version"):
            dep += f" version `{esc(d.get('version'))}`"
        if d.get("hint_path"):
            dep += f" hint `{esc(d.get('hint_path'))}`"
        dep += "\n"
    write(out / "specs" / "dependencies" / "spec.md", dep)

    print(f"Wrote OpenSpec files to {out}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_openspec.py <normalized_dir> <openspec_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
