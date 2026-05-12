---
name: plc-structure-analyzer
description: Analyze PLC program structure, label/device usage, cross references, alarm/interlock candidates, and produce Mermaid diagrams from normalized JSON or exported source files. 分析 PLC 專案的程式結構、Label 使用關係、Device 使用關係與 Cross Reference，產生架構文件與 Mermaid 圖。
version: 0.3.0
---

# PLC Structure Analyzer

## Purpose

Analyze project structure from normalized PLC data and produce program maps, dependency summaries, device usage tables, and Mermaid diagrams.

## Input

Prefer:

```text
exports/normalized/programs.json
exports/normalized/labels.json
exports/normalized/devices.json
exports/normalized/cross_reference.json
```

Fallback:

```text
exports/raw/programs/
exports/raw/cross_reference/
```

## Output

Write or update:

```text
docs/05_program_structure.md
docs/09_cross_reference.md
docs/diagrams/program_structure.md
```

## Analysis tasks

1. List programs, POU, FB, and functions if available.
2. Summarize source language: Ladder mnemonic, ST, FBD, SFC, unknown.
3. Extract visible calls from ST or text when possible.
4. Extract device usage from source and cross reference.
5. Classify device usage as read/write only when source data proves it.
6. Identify alarm candidates from device comments containing `alarm`, `error`, `異常`, `警報`, `故障`.
7. Identify interlock candidates from comments containing `interlock`, `lock`, `禁止`, `互鎖`, `條件`.

## Mermaid rules

Only draw confirmed relationships. If relationships are incomplete, label the diagram as `partial`.

Example:

```mermaid
flowchart TD
    MAIN[MAIN]
    AUTO[AUTO_MODE]
    ALARM[ALARM_HANDLER]
    MAIN --> AUTO
    MAIN --> ALARM
```

## Do not

- Do not guess call relationships that are not present.
- Do not claim a device is written unless cross reference or source proves write usage.
- Do not infer safety logic without evidence.

## 分析工具 (Analysis Tools)

包含的 scripts：

- `scripts/parse_st.py`: 解析 Structured Text 程式檔案
- `scripts/parse_mnemonic.py`: 解析 ladder 助記碼 CSV 檔案

執行方式：

```bash
# Parse ST files
python .claude/skills/plc-structure-analyzer/scripts/parse_st.py exports/raw/programs exports/normalized

# Parse mnemonic files
python .claude/skills/plc-structure-analyzer/scripts/parse_mnemonic.py exports/raw/programs exports/normalized
```

## 分析任務 (Analysis Tasks)

1. 列出 programs, POU, FB, functions 清單（若有）
2. 摘要程式語言類型：Ladder mnemonic, ST, FBD, SFC
3. 從 ST 或文本中提取可見的函數呼叫
4. 從原始碼和 cross reference 提取 device 使用情況
5. 根據 device comments 中的關鍵字識別 alarm 候選項（alarm, error, 異常, 警報, 故障）
6. 根據 comments 識別 interlock 候選項（interlock, lock, 禁止, 互鎖, 條件）
