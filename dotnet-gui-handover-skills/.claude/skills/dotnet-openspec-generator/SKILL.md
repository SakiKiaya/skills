---
name: dotnet-openspec-generator
description: Generate OpenSpec-compatible specifications for AI Agents from enterprise GUI analysis, analysis chunks, and regenerated chunk docs.
version: 1.0.0
allowed-tools: Read Write Edit Bash
---

# dotnet-openspec-generator

## Purpose

產生 AI Agent 可理解的 OpenSpec 規格文件。

v1.0 reads:

```text
exports/enterprise_analysis/
exports/analysis_chunks/
docs/chunks/
```

並輸出：

```text
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
  changes/
```

## Rules

- `openspec/specs/` 描述目前系統行為。
- `openspec/changes/` 保留給未來變更使用。
- 使用 `SHALL` / `MUST` 描述可確認的行為。
- 推測內容必須放入 `Assumptions` 或標示 `推測`。
- 不可把命名推測寫成確定規格。
- 優先引用 `docs/chunks/` 的人工或 Agent 深化內容。
