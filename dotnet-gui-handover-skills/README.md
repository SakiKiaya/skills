# dotnet-gui-handover-skills


## v0.8

This version only solves problem 1:

- `04_event_flow.md` sequence diagrams now use simplified fixed participants.
- Avoids one participant per method call.
- Keeps diagrams readable for long call chains.


## v0.8

This version solves problem 2:

- Adds `dotnet-method-purpose-analyzer`
- Generates `exports/enterprise_analysis/method_purposes.json`
- Enhances `docs/05_method_flow.md`
- Prevents blank method purpose output
- Adds method explanation sections with:
  - 用途
  - 推測依據
  - 觸發來源
  - 主要責任
  - 副作用
  - 維護注意事項
  - 分析來源

### Usage

```bash
python .claude/skills/dotnet-gui-project-analyzer/scripts/enterprise_gui_analyzer.py . exports/enterprise_analysis
python .claude/skills/dotnet-method-purpose-analyzer/scripts/method_purpose_analyzer.py exports/enterprise_analysis
python .claude/skills/dotnet-enterprise-doc-generator/scripts/generate_enterprise_docs.py exports/enterprise_analysis docs
```

`dotnet-gui-project-analyzer` validates the generated analysis JSON and writes
`exports/enterprise_analysis/schema_validation.json`. A failed validation stops
the pipeline before documentation generation.

`dotnet-enterprise-doc-generator` is now marked as the fallback generator. Prefer
`dotnet-chunk-aware-doc-generator` in the full v0.8/v0.9 pipeline when chunk
outputs are present.

Or:

```bash
python run_method_purpose_analysis.py /path/to/target/repo
```


## v0.8

This version completes step 1 of the third issue:

### Added

- `dotnet-analysis-chunker`
- `exports/analysis_chunks/`
- per-project chunks
- per-form chunks
- per-event-flow chunks
- per-method chunks
- dependency chunks
- config chunks
- risk chunks
- `index.json`

### Usage

```bash
python .claude/skills/dotnet-analysis-chunker/scripts/analysis_chunker.py exports/enterprise_analysis exports/analysis_chunks
```

Or:

```bash
python run_analysis_chunker.py /path/to/target/repo
```

### Purpose

This prepares the pipeline for later steps:

1. Support regenerating a single Form / Project / Event Flow.
2. Make docs generator read chunks and then merge.


## v0.8

This version completes step 2 of the third issue:

### Added

- `dotnet-chunk-regenerator`
- single chunk doc regeneration
- per-project local docs
- per-form local docs
- per-event-flow local docs
- per-method local docs
- dependency/config/risk local docs

### Usage

Regenerate one chunk:

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-id <chunk_id>
```

Regenerate by type:

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-type form
```

Regenerate all chunks:

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --all
```

Wrapper:

```bash
python run_regenerate_chunk_doc.py /path/to/target/repo --chunk-type event_flow
```

### Output

```text
docs/chunks/
  projects/
  forms/
  event_flows/
  methods/
  dependencies/
  configs/
  risks/
```


## v0.8

This version completes step 3 of the third issue:

### Added

- `dotnet-chunk-aware-doc-generator`
- final 01-09 docs can now read:
  - `exports/analysis_chunks/**/*.json`
  - `docs/chunks/**/*.md`
  - `exports/enterprise_analysis/*.json`
- chunk docs are preferred over raw JSON when available.

### Usage

Generate final docs from chunks:

```bash
python .claude/skills/dotnet-chunk-aware-doc-generator/scripts/generate_chunk_aware_docs.py exports/enterprise_analysis exports/analysis_chunks docs/chunks docs
```

Wrapper:

```bash
python run_chunk_aware_docs.py /path/to/target/repo
```

Full chunk pipeline:

```bash
python run_chunk_pipeline.py /path/to/target/repo
```


## v0.8 Integrated OpenSpec Support

This complete v0.8 version restores and upgrades OpenSpec output.

### Generate OpenSpec only

```bash
python .claude/skills/dotnet-openspec-generator/scripts/generate_openspec.py exports/enterprise_analysis exports/analysis_chunks docs/chunks openspec
```

or:

```bash
python run_openspec_generation.py /path/to/target/repo
```

### Full v0.8 Pipeline

```bash
python run_v08_full_pipeline.py /path/to/target/repo
```

## v0.9 README Generator

v0.9 adds `dotnet-readme-generator`.

The generated `docs/README.md` follows the enterprise GUI handover format:

- 專案名稱
- 概述
- 技術棧
- 專案結構
- 應用程式流程
- 表單清單
- 類別與模組清單
- 參數設定指南
- 常見操作
- 已知注意事項

### Generate README only

```bash
python .claude/skills/dotnet-readme-generator/scripts/generate_readme.py /path/to/target/repo
```

### Full v0.9 Pipeline

```bash
python run_v09_full_pipeline.py /path/to/target/repo
```
