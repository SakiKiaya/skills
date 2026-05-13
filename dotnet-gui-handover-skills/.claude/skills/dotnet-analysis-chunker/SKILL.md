---
name: dotnet-analysis-chunker
description: Split enterprise .NET GUI analysis output into project, form, event-flow, method, dependency, source-file, and semantic large-file task chunks for incremental documentation.
version: 0.8.5
allowed-tools: Read Write Edit Bash
---

# dotnet-analysis-chunker

## Purpose

Split normalized enterprise GUI analysis output into smaller JSON chunks that can be reviewed, regenerated, and merged incrementally.

This skill reads:

```text
exports/enterprise_analysis/*.json
```

and writes:

```text
exports/analysis_chunks/
  index.json
  projects/
  forms/
  event_flows/
  methods/
  dependencies/
  configs/
  risks/
  source_files/
  large_file_tasks/
```

## Why

Large GUI systems often contain giant forms, long event handlers, and mixed responsibilities. Chunking the analysis lets a maintainer or AI agent work on bounded units without loading the entire project context at once.

## Input

```text
exports/enterprise_analysis/
  projects.json
  dependencies.json
  source_files.json
  source_blocks.json
  methods.json
  method_purposes.json
  events.json
  event_flows.json
  configuration.json
  external_dependencies.json
  user_workflows.json
  risks.json
```

## Output

```text
exports/analysis_chunks/
  index.json
  projects/*.json
  forms/*.json
  event_flows/*.json
  methods/*.json
  dependencies/*.json
  configs/*.json
  risks/*.json
  source_files/*.json
  large_file_tasks/*.json
```

## Large File Task Rule

When a source file has more than 1000 lines, this skill creates `large_file_task` chunks.

Large-file tasks prefer semantic splitting before line-window fallback:

1. Split by class blocks.
2. If a class is still too large, split by method blocks.
3. If a method is still too large, split by switch or Select Case blocks.
4. If no semantic block is available, use bounded line windows of about 800 lines.

Each task includes:

- source file metadata
- line range
- context line range with up to 10 lines before and after the task range
- semantic blocks used for the split
- methods that overlap the range
- events declared inside that range
- related risks
- review goals for targeted follow-up analysis

Use these chunks when a single source file is too large to analyze or document in one pass.

## Context Rule

`line_range` is the ownership range for the task.

`context_line_range` is the reading range. It includes up to 10 lines before and after the task range so downstream reviewers can see nearby declarations, braces, comments, and transition points.

The chunker does not split raw source text by character count, so it does not cut words. Semantic task ranges are chosen from class, method, switch, or line boundaries.

## Rules

- Every chunk must include `chunk_type`, `chunk_id`, `title`, `summary`, `source_refs`, `data`, and `related_chunks`.
- Preserve source references whenever possible.
- Do not write final handover documents from this skill.
- Write only chunk JSON and `index.json`.
- Keep chunk IDs stable so regenerated documentation can link back to prior analysis.
