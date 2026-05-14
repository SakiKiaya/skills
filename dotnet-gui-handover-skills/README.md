# dotnet-gui-handover-skills v1.0

Skills and scripts for reverse-engineering enterprise .NET GUI projects and generating handover documentation for maintainers, technical leads, and AI agents.

Supported targets include WinForms, WPF, Avalonia, MAUI-style XAML projects, C#, and VB.NET.

## What Is New In v1.0

v1.0 consolidates the earlier analyzer, chunking, documentation, OpenSpec, and README workflows into one full pipeline.

### Analysis Contract

- `dotnet-gui-project-analyzer` now emits validated JSON under `exports/enterprise_analysis/`.
- `source_files.json` records file-level metadata: `path`, `line_count`, `method_count`, and `class_count`.
- `source_blocks.json` records semantic source ranges for classes, methods, and switch / Select Case blocks.
- `schema_validation.json` is written so invalid analysis output stops downstream generation early.

### Large File Handling

- `dotnet-analysis-chunker` now creates `source_file` chunks.
- Files over 1000 lines generate `large_file_task` chunks.
- Large-file tasks prefer semantic boundaries:
  1. class
  2. method
  3. switch / Select Case
  4. line-window fallback
- Every large-file task includes `line_range` plus `context_line_range` with up to 10 lines of overlap before and after the task.

### Chunk-Aware Documentation

- `dotnet-chunk-regenerator` can regenerate one chunk, one chunk type, or all chunk docs.
- `source_file` and `large_file_task` chunk docs are supported.
- `dotnet-chunk-aware-doc-generator` merges chunk docs and analysis JSON into final handover documents.
- `05_method_flow.md` includes source-file and large-file task sections.

### OpenSpec Output

- `dotnet-openspec-generator` writes AI-agent-friendly specs under `openspec/specs/`.
- Chunk excerpts are sanitized before being embedded in OpenSpec files, so GitHub Markdown rendering is not broken by truncated Mermaid or fenced code blocks.

### README Generation

- `dotnet-readme-generator` creates a target-project `docs/README.md` from analysis and chunks.
- The README summarizes architecture, forms, methods, configuration, operations, and known risks.

### Industrial VB.NET Deep Manual Writing

- `dotnet-industrial-vb-manual-writer` provides a deep-dive workflow for industrial automation VB.NET WinForms systems.
- It focuses on PLC monitoring, BackgroundWorker loops, timers, state machines, socket handshakes, MES/SOAP integration, barcode readers, INI source-of-truth behavior, permissions, and DataGridView or tray-map rendering.
- Use it when a core form such as `frmMain.vb` needs a file-level handover manual.
- `dotnet-industrial-handover-pipeline` orchestrates the full flow: run the standard pipeline, generate source-backed manual insights for core VB files, refresh final docs, and write a quality report for remaining inferred content.

## Skill Set

```text
.claude/skills/
  dotnet-gui-project-analyzer/
  dotnet-method-purpose-analyzer/
  dotnet-analysis-chunker/
  dotnet-chunk-regenerator/
  dotnet-chunk-aware-doc-generator/
  dotnet-industrial-vb-manual-writer/
  dotnet-industrial-handover-pipeline/
  dotnet-enterprise-doc-generator/
  dotnet-openspec-generator/
  dotnet-readme-generator/
```

`dotnet-enterprise-doc-generator` is kept as a fallback generator. Prefer the chunk-aware pipeline for v1.0 output.

## Generated Outputs

```text
exports/
  enterprise_analysis/
  analysis_chunks/
  manual_insights/

docs/
  README.md
  01_solution_structure.md
  02_architecture.md
  03_project_dependencies.md
  04_event_flow.md
  05_method_flow.md
  06_configuration.md
  07_user_workflow.md
  08_external_dependencies.md
  09_risk_analysis.md
  manual_insight_quality.md
  manuals/
  chunks/

openspec/
  project.md
  specs/
    solution-architecture/spec.md
    ui-forms/spec.md
    event-flow/spec.md
    method-flow/spec.md
    configuration/spec.md
    external-dependencies/spec.md
    user-workflow/spec.md
    risk-analysis/spec.md
```

## Quick Start

Run the full v1.0 pipeline against a target .NET GUI repository:

```bash
python run_v09_full_pipeline.py /path/to/target/repo
```

The wrapper name is kept for compatibility, but the pipeline now produces v1.0 output.

For industrial VB.NET projects, run the handover orchestrator to add file-level manual insights and refresh docs with confirmed evidence:

```bash
python .claude/skills/dotnet-industrial-handover-pipeline/scripts/run_industrial_handover_pipeline.py /path/to/target/repo
```

Optionally pass one or more source files to force deep insight generation for specific files:

```bash
python .claude/skills/dotnet-industrial-handover-pipeline/scripts/run_industrial_handover_pipeline.py /path/to/target/repo Forms/MainForm.vb
```

## Step-By-Step Pipeline

```bash
python .claude/skills/dotnet-gui-project-analyzer/scripts/enterprise_gui_analyzer.py . exports/enterprise_analysis
python .claude/skills/dotnet-method-purpose-analyzer/scripts/method_purpose_analyzer.py exports/enterprise_analysis
python .claude/skills/dotnet-analysis-chunker/scripts/analysis_chunker.py exports/enterprise_analysis exports/analysis_chunks
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --all
python .claude/skills/dotnet-chunk-aware-doc-generator/scripts/generate_chunk_aware_docs.py exports/enterprise_analysis exports/analysis_chunks docs/chunks docs
python .claude/skills/dotnet-openspec-generator/scripts/generate_openspec.py exports/enterprise_analysis exports/analysis_chunks docs/chunks openspec
python .claude/skills/dotnet-readme-generator/scripts/generate_readme.py .
```

## Regenerate One Chunk

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-id <chunk_id>
```

Regenerate a chunk type:

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-type large_file_task
```

## Example

The repository includes a generated VB.NET large-file test project:

```text
examples/vbnet-large-file-doc-test/
```

Useful files:

- `Forms/MainForm.vb`
- `docs/05_method_flow.md`
- `docs/chunks/source_files/Forms_MainForm.vb.md`
- `docs/chunks/large_file_tasks/`
- `openspec/specs/event-flow/spec.md`

## Notes

This is static analysis. All inferred behavior should be reviewed by engineers before being treated as confirmed system behavior.
