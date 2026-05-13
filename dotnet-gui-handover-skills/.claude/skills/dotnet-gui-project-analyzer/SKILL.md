---
name: dotnet-gui-project-analyzer
description: Analyze enterprise .NET GUI projects and emit normalized static-analysis JSON for downstream documentation skills.
version: 0.7.1
allowed-tools: Read Write Edit Bash
---

# dotnet-gui-project-analyzer

## Role

Act as a senior software architect specializing in .NET GUI reverse engineering, enterprise handover documentation, static analysis, and event-flow analysis.

## Purpose

Analyze a .NET GUI repository and write normalized JSON files under:

```text
exports/enterprise_analysis/
```

The analyzer is designed as the upstream data producer for chunking, document generation, OpenSpec generation, and README generation.

## Outputs

```text
exports/enterprise_analysis/
  enterprise_analysis.json
  projects.json
  dependencies.json
  classes.json
  methods.json
  source_files.json
  source_blocks.json
  events.json
  event_flows.json
  configuration.json
  external_dependencies.json
  user_workflows.json
  risks.json
  schema_validation.json
```

## Source File Metadata

`source_files.json` records one entry per scanned source file:

```json
{
  "path": "relative/path/File.cs",
  "language": "C#",
  "extension": ".cs",
  "line_count": 1200,
  "method_count": 35,
  "class_count": 2
}
```

Downstream skills use this metadata to identify files over 1000 lines and create targeted large-file analysis tasks.

## Source Block Metadata

`source_blocks.json` records class, method, and switch-like blocks with source ranges:

```json
{
  "kind": "method",
  "name": "SaveData",
  "source": "relative/path/File.cs",
  "language": "C#",
  "start_line": 120,
  "end_line": 180
}
```

Downstream skills use these ranges to split large files by semantic boundaries before falling back to fixed line windows.

## Quality Bar

- Do not produce a simple code index.
- Produce architecture-level facts and candidates suitable for technical leads, maintainers, and new engineers.
- Preserve source references and line numbers wherever possible.
- Separate confirmed facts from inference.
- Mark inferred behavior clearly as candidate data.
- Include risk and maintenance notes.
- Treat output as enterprise GUI handover analysis, not final documentation.

## Required Style For Downstream Docs

- Use Markdown.
- Use Mermaid diagrams when generating documents.
- Explain behavior and responsibility.
- Preserve source references.
- Include risk and maintenance notes.

## Must Read

- `references/enterprise_gui_doc_goal.md`
- `references/required_docs.md`
