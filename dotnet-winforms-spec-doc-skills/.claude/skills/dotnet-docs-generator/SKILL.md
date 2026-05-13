---
name: dotnet-docs-generator
description: Generate human-readable technical documentation for .NET Framework / WinForms C# and VB.NET projects from normalized IR.
version: 0.2.0
allowed-tools: Read Write Edit Bash
---

# dotnet-docs-generator

## Purpose

Generate human-readable technical documentation for new engineers and maintainers.

## Output

```text
docs/
  README.md
  00_solution_overview.md
  01_project_structure.md
  02_architecture.md
  03_forms_ui_structure.md
  04_event_flow.md
  05_class_method_reference.md
  06_configuration.md
  07_dependencies.md
  10_learning_path_for_new_engineers.md
  diagrams/
```

## Script

Run from repository root:

```bash
python .claude/skills/dotnet-docs-generator/scripts/generate_docs.py exports/normalized docs
```

## Rules

- Prefer tables over long paragraphs.
- Generate Mermaid diagrams when data exists.
- Include source file references.
- Separate confirmed behavior from assumptions.
- Explain architecture, Forms/UserControls, event flow, config, dependencies, and onboarding order.
