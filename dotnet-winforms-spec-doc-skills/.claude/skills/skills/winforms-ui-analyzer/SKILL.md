---
name: winforms-ui-analyzer
description: Analyze WinForms Designer.cs and Designer.vb files to extract forms, controls, UI hierarchy, event binding, layout hints, and Mermaid diagrams.
version: 0.2.0
allowed-tools: Read Write Edit Bash
---

# winforms-ui-analyzer

## Purpose

Analyze WinForms UI structure from Designer files and normalized IR.

## Input

- `*.Designer.cs`
- `*.Designer.vb`
- `*.resx`
- `exports/normalized/forms.json`
- `exports/normalized/controls.json`

## Output

```text
exports/normalized/forms.json
exports/normalized/controls.json
exports/normalized/events.json
docs/03_forms_ui_structure.md
openspec/specs/ui-forms/spec.md
```

## Script

The UI parser is included in:

```bash
python .claude/skills/dotnet-project-normalizer/scripts/normalize_project.py . exports/normalized
```

For docs generation:

```bash
python .claude/skills/dotnet-docs-generator/scripts/generate_docs.py exports/normalized docs
```

## Rules

- Parse `InitializeComponent()`.
- Preserve event binding.
- Preserve parent-child hierarchy.
- Preserve Dock/Anchor/Layout when detectable.
- Detect custom controls.
- Generate Mermaid diagrams from known parent-child relationships only.
