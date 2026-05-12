---
name: plc-doc-generator
description: Generate Markdown documentation for PLC projects from normalized JSON. Use after exports/normalized exists and the user wants project overview, structure, labels, devices, parameters, or GitHub-style docs. 根據 PLC 專案的 normalized JSON，產生 GitHub 風格 Markdown 技術文件。
version: 0.3.0
allowed-tools: Read Write Edit Bash
---

# PLC Doc Generator

## Purpose

Generate GitHub-style Markdown documentation from normalized PLC JSON files.

## Input

Read:

```text
exports/normalized/
  project.json
  programs.json
  labels.json
  devices.json
  parameters.json
  modules.json
  networks.json
  cross_reference.json
  diagnostics.json
```

## Output

Write:

```text
docs/
  README.md
  00_project_overview.md
  01_system_configuration.md
  02_cpu_parameters.md
  03_module_parameters.md
  04_network_parameters.md
  05_program_structure.md
  06_labels.md
  07_device_comments.md
  08_alarm_list.md
  09_cross_reference.md
  10_diagnostics.md
```

## Rules

1. Do not invent missing values.
2. Use `N/A` when a field is absent.
3. If meaning is inferred from name/comment, label it as `推測`.
4. Prefer device comments and label comments over language model guesses.
5. Preserve source file paths in tables where useful.
6. Generate Mermaid diagrams only from known relationships.
7. Put parse warnings and missing data in `10_diagnostics.md`.

## Script

A starter script is included:

```bash
python .claude/skills/plc-doc-generator/scripts/generate_docs.py exports/normalized docs
```

## References

- See `references/doc_template.md` for document layout.

## 文檔章節 (Documentation Sections)

1. 專案總覽
2. PLC 型號與 CPU 資訊
3. 模組組態
4. CPU 參數
5. 網路參數
6. 程式結構
7. Program / POU / FB / Function 清單
8. Global Label / Local Label
9. Device Comment
10. Cross Reference
11. Alarm / Interlock / Safety / Manual / Auto mode 關聯
12. 未解析項目與人工確認清單

## 產出規則 (Output Rules)

- 不要編造專案不存在的資訊。
- 若欄位缺失，標記為 `N/A`。
- 若推測用途，必須標記為 `推測`。
- Device comment 優先於 LLM 推測。
- 參數說明需包含：原始值、解析值、可能影響、建議確認項目。
