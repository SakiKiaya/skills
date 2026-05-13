---
name: dotnet-chunk-aware-doc-generator
description: Generate final enterprise GUI handover docs by reading analysis chunks and regenerated chunk docs, then merging them into 01-09 documentation.
version: 1.0.0
allowed-tools: Read Write Edit Bash
---

# dotnet-chunk-aware-doc-generator

## Purpose

完成第三個問題的第三步：

1. 已完成：新增 `analysis_chunks` 分割輸出
2. 已完成：支援單一 Form / Project / Event Flow / Method 重新產生
3. 本步驟：docs generator 改成讀取 chunks 後再彙整

## Inputs

```text
exports/enterprise_analysis/
exports/analysis_chunks/
docs/chunks/
```

## Outputs

```text
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
```

## Behavior

The generator should prefer chunk-level information:

1. If `docs/chunks/<type>/<id>.md` exists, use it as high-quality expanded content.
2. If chunk markdown is missing, fall back to `exports/analysis_chunks/<type>/<id>.json`.
3. If chunks are missing, fall back to `exports/enterprise_analysis/*.json`.

## Rules

- Do not simply dump JSON.
- Use chunk docs as curated local explanations.
- Keep final docs readable.
- Include links/references to chunk docs where content is too long.
- Keep Mermaid diagrams.
- Preserve source references.
- Mark inferred content as `推測`.
