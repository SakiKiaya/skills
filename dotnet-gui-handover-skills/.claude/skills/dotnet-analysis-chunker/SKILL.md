---
name: dotnet-analysis-chunker
description: Split enterprise .NET GUI analysis output into per-project, per-form, per-event-flow, per-method, and dependency chunks for incremental high-quality documentation.
version: 0.8.3
allowed-tools: Read Write Edit Bash
---

# dotnet-analysis-chunker

## Purpose

新增 `analysis_chunks` 分割輸出，解決大型 GUI 專案因上下文限制導致文件品質下降的問題。

此 Skill 不取代全專案分析，而是將：

```text
exports/enterprise_analysis/*.json
```

分割成：

```text
exports/analysis_chunks/
  projects/
  forms/
  event_flows/
  methods/
  dependencies/
  configs/
  risks/
  index.json
```

## Why

後續可以針對單一 Form、單一 Project、單一 Event Flow、單一 Method 進行重新分析與文件補強。

## Input

```text
exports/enterprise_analysis/
  projects.json
  dependencies.json
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
```

## Rules

- 每個 chunk 必須自包含。
- 每個 chunk 必須保留 source references。
- 每個 chunk 必須包含 `chunk_type`、`chunk_id`、`title`、`related_chunks`。
- 不在此階段產生最終 docs。
- 不改動既有 `docs/` 輸出。
