---
name: dotnet-chunk-regenerator
description: Regenerate documentation for a single analysis chunk, such as one Form, Project, Event Flow, Method, Dependency, Config, or Risk.
version: 0.8.4
allowed-tools: Read Write Edit Bash
---

# dotnet-chunk-regenerator

## Purpose

支援單一 Form / 單一 Project / 單一事件流程 / 單一 Method 重新產生局部文件。

此 Skill 是第三個問題的第二步：

1. 已完成：新增 `analysis_chunks` 分割輸出
2. 本步驟：支援單一 chunk 重新產生
3. 下一步：docs generator 改成讀取 chunks 後再彙整

## Input

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
```

## Output

```text
docs/chunks/
  projects/*.md
  forms/*.md
  event_flows/*.md
  methods/*.md
  dependencies/*.md
  configs/*.md
  risks/*.md
```

## Usage

Regenerate one chunk by id:

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-id <chunk_id>
```

Regenerate one chunk by path:

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-path exports/analysis_chunks/forms/MainForm.json
```

Regenerate all chunks of a type:

```bash
python .claude/skills/dotnet-chunk-regenerator/scripts/regenerate_chunk_doc.py exports/analysis_chunks docs/chunks --chunk-type form
```

## Rules

- Regenerated output must be local to the chunk.
- Do not overwrite final docs 01-09 in this step.
- Preserve source references.
- Mark inference as `推測`.
- Include maintenance notes and risk hints.
