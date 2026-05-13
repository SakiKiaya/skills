---
name: dotnet-method-purpose-analyzer
description: Infer method purpose, triggers, responsibility, side effects, evidence, and maintenance notes for .NET GUI projects.
version: 0.8.2
allowed-tools: Read Write Edit Bash
---

# dotnet-method-purpose-analyzer

## Purpose

補足 `05_method_flow.md` 中方法用途空白的問題。

此 Skill 會根據下列來源推測方法用途：

- 方法名稱
- 所在 class / source file
- 被哪些事件呼叫
- 呼叫了哪些方法
- 是否存取 config / DB / file / device
- 是否更新 UI
- 是否有 try/catch
- 是否 async / await / Thread / Timer
- 是否產生新物件

## Input

```text
exports/enterprise_analysis/
  methods.json
  event_flows.json
  events.json
  classes.json
  configuration.json
  external_dependencies.json
```

## Output

```text
exports/enterprise_analysis/method_purposes.json
docs/05_method_flow.md
```

## Required Method Explanation Format

每個方法至少要包含：

- 推測用途
- 觸發來源
- 主要責任
- 副作用
- 維護注意事項
- 推測依據

## Rules

- 不允許用途欄位空白。
- 沒有足夠證據時，也要輸出「需人工確認」與推測依據。
- 推測內容必須標記為 `推測`。
- 不能把命名推測當成確定事實。
