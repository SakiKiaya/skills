# Enterprise GUI Project OpenSpec

## Purpose

This OpenSpec workspace describes the current structure and behavior of the analyzed .NET GUI project for AI Agent consumption.

## Source Inputs

- `exports/enterprise_analysis/`
- `exports/analysis_chunks/`
- `docs/chunks/`

## Chunk Counts

```json
{
  "source_file": 1,
  "large_file_task": 15,
  "project": 1,
  "method": 9,
  "event_flow": 2,
  "form": 1,
  "dependency": 7,
  "config": 3,
  "risk": 4
}
```

## Specs

- `specs/solution-architecture/spec.md`
- `specs/ui-forms/spec.md`
- `specs/event-flow/spec.md`
- `specs/method-flow/spec.md`
- `specs/configuration/spec.md`
- `specs/external-dependencies/spec.md`
- `specs/user-workflow/spec.md`
- `specs/risk-analysis/spec.md`

## Agent Rules

- Treat confirmed source-backed items as current behavior.
- Treat `推測`, assumptions, and low-confidence items as review targets.
- Do not change behavior without creating a proposal under `openspec/changes/`.
