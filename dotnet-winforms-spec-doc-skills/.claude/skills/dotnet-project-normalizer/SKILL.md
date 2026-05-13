---
name: dotnet-project-normalizer
description: Normalize C# and VB.NET WinForms source files into structured JSON IR, including classes, methods, forms, controls, events, configs, and diagnostics.
version: 0.3.0
allowed-tools: Read Write Edit Bash
---

# dotnet-project-normalizer

## Purpose

Convert C# / VB.NET WinForms projects into normalized JSON that AI Agents and documentation generators can consume.

## Input

- `*.cs`
- `*.vb`
- `*.Designer.cs`
- `*.Designer.vb`
- `*.resx`
- `*.config`
- `*.settings`

## Output

```text
exports/normalized/
  forms.json
  controls.json
  events.json
  classes.json
  methods.json
  configs.json
  resources.json
  diagnostics.json
```

## Script

Run from repository root:

```bash
python .claude/skills/dotnet-project-normalizer/scripts/normalize_project.py . exports/normalized
```

## Important Rules

- Support both C# and VB.NET.
- Merge Designer files with logic files.
- Preserve UI tree where possible.
- Preserve control names and event bindings.
- Preserve `source_file`, `line_range`, and `language`.
- Do not only summarize; create reusable normalized IR.

## v0.3 Method and Event Analysis

- Generates `event_flows.json`.
- Generates `call_graph.json`.
- Maps Designer/AddHandler/VB Handles events to handler methods.
- Extracts approximate method line ranges and static call candidates.
