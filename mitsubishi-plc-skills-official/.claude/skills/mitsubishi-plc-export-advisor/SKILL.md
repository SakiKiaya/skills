---
name: mitsubishi-plc-export-advisor
description: Plan what to export from Mitsubishi GX Works2/GX Works3 projects for Git version control and documentation. Use when the user asks how to export Mitsubishi PLC project data, prepare raw files, or document GX Works projects. 協助使用者規劃三菱 Mitsubishi PLC 專案的文本化匯出流程，目標是讓 GX Works2 / GX Works3 專案可以被 Git 版本控制。
version: 0.3.0
---

# Mitsubishi PLC Export Advisor

## Purpose

Plan a text-based export workflow for Mitsubishi PLC projects so downstream skills can generate project structure and parameter documentation.

## Core rule

Do not assume direct parsing of proprietary GX Works project files such as `.gx3`, `.gxw`, `.gppw`, or packaged project archives. Treat GX Works as the exporter and require text or semi-structured files as input.

## Required questions when information is missing

Ask only for details that materially change the export plan:

- GX Works version: GX Developer, GX Works2, GX Works3
- PLC family: FX, Q, L, iQ-F, iQ-R
- Programming languages used: Ladder, ST, FBD, SFC, FB, Function
- Whether the user needs Git diff only, documentation only, or both

If the user does not know, provide a generic GX Works2/GX Works3 export plan.

## Recommended export folders

Create this structure in the user's repository:

```text
exports/raw/
  project_info/
  programs/
  labels/
  device_comments/
  parameters/
  module_config/
  network/
  cross_reference/
  reports/
exports/normalized/
docs/
```

## Minimum export set

For MVP documentation, request:

1. Global Label CSV
2. Local Label CSV, if local labels are used
3. Device Comment CSV
4. Program source as ST, TXT, or mnemonic CSV
5. CPU parameter report or CSV
6. Module parameter report or CSV
7. Network parameter report or CSV, if communication modules are used
8. Cross Reference CSV, if available
9. Compile/build report, if available

## Output format

Return:

1. Export checklist
2. Target folder path for each export
3. Why the export is needed
4. Which downstream skill consumes it
5. Items requiring manual confirmation

## Downstream skills

- Use `mitsubishi-plc-project-normalizer` after raw files are exported.
- Use `mitsubishi-plc-doc-generator` after normalized JSON exists.
- Use `mitsubishi-plc-parameter-explainer` for CPU/module/network parameter documentation.
- Use `mitsubishi-plc-structure-analyzer` for program tree, cross reference, and Mermaid diagrams.

## 優先級建議 (Priority)

| 優先級 | 資料                        | 用途               | 備註 |
| --- | ------------------------- | ---------------- | --- |
| P0  | Global Label CSV          | 建立變數表            | 必須 |
| P0  | Device Comment CSV        | 建立 Device 說明     | 必須 |
| P0  | Program ST / mnemonic CSV | 建立程式結構           | 必須 |
| P1  | CPU Parameter 匯出          | 產生 CPU 參數文件      | 重要 |
| P1  | Module Parameter 匯出       | 產生模組參數文件         | 重要 |
| P1  | Cross Reference CSV       | 建立變數/Device 使用關係 | 重要 |
| P2  | Compile Report            | 建立品質檢查文件         | 可選 |
| P2  | Network Parameter         | 建立通訊設定文件         | 可選 |
