---
name: dotnet-openspec-generator
description: Generate OpenSpec-compatible specs for AI Agents from normalized .NET WinForms IR, including solution architecture, UI forms, business logic, configuration, and dependencies.
version: 0.2.0
allowed-tools: Read Write Edit Bash
---

# dotnet-openspec-generator

## Purpose

Generate AI-Agent-readable OpenSpec files from normalized project IR.

## Output

```text
openspec/
  project.md
  specs/
    solution-architecture/spec.md
    ui-forms/spec.md
    business-logic/spec.md
    configuration/spec.md
    dependencies/spec.md
  changes/
```

## Script

Run from repository root:

```bash
python .claude/skills/dotnet-openspec-generator/scripts/generate_openspec.py exports/normalized openspec
```

## Rules

- Use `SHALL` / `MUST` wording for confirmed behavior.
- Include Scenario sections where event flow or behavior is known.
- Separate confirmed behavior from assumptions.
- Do not convert guesses into requirements.
- Preserve source references.
