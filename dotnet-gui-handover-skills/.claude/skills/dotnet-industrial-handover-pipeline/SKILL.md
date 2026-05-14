---
name: dotnet-industrial-handover-pipeline
description: Orchestrate the full industrial VB.NET WinForms handover workflow: run the standard pipeline, select core files, generate source-backed manual insights, refresh docs, and report remaining inferred items.
---

# dotnet-industrial-handover-pipeline

## Role

Run the complete handover-document workflow for industrial VB.NET WinForms projects.

This skill coordinates the broad static-analysis pipeline with file-level deep analysis from `dotnet-industrial-vb-manual-writer`. The goal is to move documentation from weak keyword-based `推測` toward source-backed, confirmed statements.

## Use When

Use this skill when the user asks to:

- run the complete conversion / handover pipeline
- reduce `推測` in generated docs
- produce industrial automation manuals from VB.NET WinForms code
- combine project-level docs with detailed analysis of `frmMain.vb`, `MainForm.vb`, or other large Form files

## Workflow

1. Run the standard project pipeline:

```powershell
python run_v09_full_pipeline.py <project-root>
```

2. Generate file-level manual insights:

```powershell
python .claude/skills/dotnet-industrial-handover-pipeline/scripts/run_industrial_handover_pipeline.py <project-root>
```

The skill may be installed in any of these locations:

```text
<repo>/.claude/skills/
<repo>/.gemini/skills/
~/.claude/skills/
~/.gemini/skills/
```

The runner locates sibling skills from its own installed skill folder. When `run_v09_full_pipeline.py` is not available from the current repository checkout, it calls each sibling skill script directly.

3. Inspect the generated outputs:

```text
exports/manual_insights/*.insights.json
docs/manuals/*.md
docs/manual_insight_quality.md
```

4. Use insights to refresh the generated docs. The orchestrator does this automatically after insights are created.

## Output Contract

The tool produces:

- `exports/manual_insights/<FileName>.insights.json`
- `docs/manuals/<FileName>.md`
- `docs/manual_insight_quality.md`

Each insight JSON should separate:

- `confirmed_workflows`
- `confirmed_side_effects`
- `state_machines`
- `regions`
- `ui_events`
- `open_questions`

Generated documents should prefer confirmed insight data over generic inferred text.

## Language Policy

Unless the user explicitly requests another output language, files written under `docs/` should be written primarily in Traditional Chinese.

This applies to:

- top-level handover documents
- `docs/manuals/*.md`
- `docs/manual_insight_quality.md`
- generated workflow, method, risk, and maintenance explanations

Keep exact code identifiers, method names, class names, file paths, PLC/register names, UI control names, and configuration keys unchanged. English technical terms may be kept when they are standard API or framework terms, but explanatory prose should default to Traditional Chinese.

## Quality Rules

- Do not remove `推測` blindly. Replace it only when source evidence exists.
- Confirmed statements must include file path and line range.
- Keep uncertain behavior as `推測` or `需人工確認`.
- Large or high-risk files should receive file-level manuals before claiming system-level certainty.
