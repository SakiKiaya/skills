---
name: plc-project-normalizer
description: Normalize exported GX Works raw files into JSON. Use when the user has CSV, TXT, XML, ST, mnemonic, label, device comment, parameter, or cross-reference exports under exports/raw. 解析 GX Works2 / GX Works3 匯出的文字檔、CSV、XML、ST、mnemonic CSV，轉換成統一 JSON 結構。
version: 0.3.0
allowed-tools: Read Write Edit Bash
---

# PLC Project Normalizer

## Purpose

Convert GX Works exported text files into stable normalized JSON files for documentation and Git diff.

## Input

Read files from:

```text
exports/raw/
```

Expected categories:

- labels
- device_comments
- programs
- parameters
- module_config
- network
- cross_reference
- reports

## Output

Write normalized files to:

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

## Parsing rules

1. Preserve original values and source file paths.
2. Do not invent missing fields.
3. Put unknown columns under `raw`.
4. If encoding is uncertain, try UTF-8 with BOM, UTF-8, CP932/Shift-JIS, then Big5.
5. Add all parse warnings and unknown formats to `diagnostics.json`.
6. Normalize common fields when possible:
   - name
   - address
   - device
   - data_type
   - scope
   - comment
   - program
   - parameter_name
   - value
   - module
   - station

## Script

A starter script is included at:

```text
scripts/normalize_exports.py
```

Run it from repository root:

```bash
python .claude/skills/plc-project-normalizer/scripts/normalize_exports.py exports/raw exports/normalized
```

## References

- See `references/normalized_schema.md` for expected JSON structure.

## 支援的輸入格式 (Supported Input)

- **CSV**: labels, device comments, parameters, cross reference
- **TXT**: compile report, print report, parameter report
- **ST**: Structured Text program
- **XML**: 若 GX Works 或相關工具可匯出 XML，需保留原始節點與屬性
- **Mnemonic CSV**: Ladder 轉 mnemonic 後的指令表

## 解析規則 (Parsing Rules)

* 保留原始欄位名稱。
* 另外產生標準欄位，例如 name, address, data_type, scope, comment。
* 無法判斷的欄位放入 raw。
* 不要刪除未知欄位。
* 所有解析錯誤需輸出到 diagnostics.json。
