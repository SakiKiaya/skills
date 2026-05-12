# Skill: mitsubishi-plc-doc-generator

## Purpose
根據 Mitsubishi PLC 專案的 normalized JSON，產生 GitHub 風格 Markdown 技術文件。

## Required input
- plc_project_normalized/*.json

## Output
產生 docs/*.md 文件。

## Documentation sections
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

## Rules
- 不要編造專案不存在的資訊。
- 若欄位缺失，標記為 `N/A`。
- 若推測用途，必須標記為 `推測`。
- Device comment 優先於 LLM 推測。
- 參數說明需包含：原始值、解析值、可能影響、建議確認項目。