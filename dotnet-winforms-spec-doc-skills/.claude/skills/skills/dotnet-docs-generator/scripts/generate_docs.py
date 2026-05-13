#!/usr/bin/env python3
"""
Generate human-readable docs from normalized IR.

Usage:
    python generate_docs.py <normalized_dir> <docs_dir>
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


def esc(v: Any) -> str:
    if v in (None, ""):
        return "N/A"
    s = str(v).replace("\n", " ").replace("|", "\\|")
    return s


def table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(esc(c) for c in row) + " |")
    return "\n".join(out) + "\n"


def mermaid_controls(form: dict[str, Any], controls: list[dict[str, Any]]) -> str:
    form_name = form.get("form_name")
    rows = [c for c in controls if c.get("form") == form_name]
    lines = ["```mermaid", "flowchart TD"]
    if not rows:
        lines.append(f'    {form_name}["{form_name}"]')
    for c in rows:
        name = c.get("name")
        parent = c.get("parent") or form_name
        label = f'{name}<br/>{c.get("type") or ""}'
        lines.append(f'    {parent} --> {name}["{label}"]')
    lines.append("```")
    return "\n".join(lines)


def main(norm_arg: str, docs_arg: str) -> int:
    norm = Path(norm_arg)
    docs = Path(docs_arg)
    (docs / "diagrams").mkdir(parents=True, exist_ok=True)

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
    diagnostics = load(norm, "diagnostics.json", [])

    (docs / "README.md").write_text("""# Project Documentation

Generated from normalized .NET / WinForms project IR.

## Index

- [00 Solution Overview](00_solution_overview.md)
- [01 Project Structure](01_project_structure.md)
- [02 Architecture](02_architecture.md)
- [03 Forms UI Structure](03_forms_ui_structure.md)
- [04 Event Flow](04_event_flow.md)
- [05 Class Method Reference](05_class_method_reference.md)
- [06 Configuration](06_configuration.md)
- [07 Dependencies](07_dependencies.md)
- [10 Learning Path for New Engineers](10_learning_path_for_new_engineers.md)
""", encoding="utf-8")

    overview = "# Solution Overview\n\n"
    overview += table(["Item", "Value"], [["Solution", solution.get("name")], ["Path", solution.get("path")], ["Project Count", len(projects)], ["Forms", len(forms)]])
    (docs / "00_solution_overview.md").write_text(overview, encoding="utf-8")

    project_rows = [[p.get("name"), p.get("language"), p.get("project_file"), p.get("target_framework"), p.get("output_type"), p.get("is_winforms"), ", ".join(p.get("platforms", []))] for p in projects]
    (docs / "01_project_structure.md").write_text("# Project Structure\n\n" + table(["Project", "Language", "File", "Target", "Output", "WinForms", "Platforms"], project_rows), encoding="utf-8")

    arch = "# Architecture\n\n## High-level Summary\n\n"
    arch += "- This document is generated from static analysis.\n"
    arch += "- Confirmed items are based on solution/project/source files.\n"
    arch += "- Unknown behavior should be verified by engineers.\n\n"
    arch += "## Project Dependency Candidates\n\n"
    arch += table(["Type", "Project", "Include/ID", "Hint/Version"], [[d.get("type"), d.get("project"), d.get("include") or d.get("id"), d.get("hint_path") or d.get("version")] for d in deps])
    (docs / "02_architecture.md").write_text(arch, encoding="utf-8")

    ui_doc = "# Forms UI Structure\n\n"
    for f in forms:
        ui_doc += f"## {esc(f.get('form_name'))}\n\n"
        ui_doc += table(["Item", "Value"], [["Namespace", f.get("namespace")], ["Language", f.get("language")], ["Logic File", f.get("logic_file")], ["Designer File", f.get("designer_file")], ["Resx File", f.get("resx_file")]])
        ui_doc += "\n### Controls\n\n"
        form_controls = [c for c in controls if c.get("form") == f.get("form_name")]
        ui_doc += table(["Name", "Type", "Parent", "Text", "Events", "Source"], [[c.get("name"), c.get("type"), c.get("parent"), c.get("text"), c.get("events"), c.get("source_file")] for c in form_controls])
        ui_doc += "\n### UI Diagram\n\n" + mermaid_controls(f, controls) + "\n\n"
    (docs / "03_forms_ui_structure.md").write_text(ui_doc, encoding="utf-8")

    event_doc = "# Event Flow\n\n"
    event_doc += table(["Form", "Control", "Event", "Handler", "Language", "Source", "Line"], [[e.get("form"), e.get("control"), e.get("event"), e.get("handler"), e.get("language"), e.get("source_file"), e.get("line")] for e in events])
    (docs / "04_event_flow.md").write_text(event_doc, encoding="utf-8")

    class_doc = "# Class and Method Reference\n\n## Classes\n\n"
    class_doc += table(["Name", "Namespace", "Kind", "Language", "Source", "Line"], [[c.get("name"), c.get("namespace"), c.get("kind"), c.get("language"), c.get("source_file"), (c.get("line_range") or [None])[0]] for c in classes])
    class_doc += "\n## Methods\n\n"
    class_doc += table(["Name", "Namespace", "Language", "Source", "Line"], [[m.get("name"), m.get("namespace"), m.get("language"), m.get("source_file"), (m.get("line_range") or [None])[0]] for m in methods])
    (docs / "05_class_method_reference.md").write_text(class_doc, encoding="utf-8")

    config_doc = "# Configuration\n\n"
    config_doc += table(["Source", "Kind", "Entries/Error"], [[c.get("source_file"), c.get("kind"), c.get("entries") or c.get("error")] for c in configs])
    (docs / "06_configuration.md").write_text(config_doc, encoding="utf-8")

    dep_doc = "# Dependencies\n\n"
    dep_doc += table(["Type", "Project", "Include/ID", "Version", "Hint Path", "Source"], [[d.get("type"), d.get("project"), d.get("include") or d.get("id"), d.get("version"), d.get("hint_path"), d.get("source_file")] for d in deps])
    (docs / "07_dependencies.md").write_text(dep_doc, encoding="utf-8")

    learning = "# Learning Path for New Engineers\n\n"
    learning += "1. Read `00_solution_overview.md` to understand the repository scope.\n"
    learning += "2. Read `01_project_structure.md` to identify startup and library projects.\n"
    learning += "3. Read `03_forms_ui_structure.md` to understand screens and controls.\n"
    learning += "4. Read `04_event_flow.md` to follow UI actions and event handlers.\n"
    learning += "5. Read `05_class_method_reference.md` to locate important classes and methods.\n"
    learning += "6. Read `06_configuration.md` and `07_dependencies.md` before building or deploying.\n\n"
    learning += "## Diagnostics\n\n"
    learning += table(["Level", "Source", "Message"], [[d.get("level"), d.get("source_file"), d.get("message")] for d in diagnostics])
    (docs / "10_learning_path_for_new_engineers.md").write_text(learning, encoding="utf-8")

    print(f"Wrote docs to {docs}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_docs.py <normalized_dir> <docs_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
