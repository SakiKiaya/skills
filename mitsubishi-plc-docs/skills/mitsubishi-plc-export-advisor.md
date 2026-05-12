# Skill: mitsubishi-plc-export-advisor

## Purpose
協助使用者規劃三菱 Mitsubishi PLC 專案的文本化匯出流程，目標是讓 GX Works2 / GX Works3 專案可以被 Git 版本控制，並作為後續文件產生與差異分析的輸入。

## When to use
當使用者提到：
- GX Works2 / GX Works3
- 三菱 PLC 專案版本控制
- 匯出 PLC 程式為文字
- 產生 PLC 文件
- 分析 PLC 專案結構
- PLC label / device comment / parameter / ST / ladder / mnemonic

## Required input
- PLC 系列：FX / Q / L / iQ-F / iQ-R
- 使用軟體：GX Developer / GX Works2 / GX Works3
- 專案是否包含 ST / Ladder / FBD / SFC / FB / Function
- 使用者目前能匯出的檔案格式

## Output
產生一份建議匯出清單，例如：

```
exports/
  project_info/
  program/
  labels/
  device_comments/
  parameters/
  module_config/
  network/
  cross_reference/
  build_report/
```

## Rules

* 不要假設可以直接解析 .gx3 / .gxw / .gppw 等 proprietary project file。
* 優先要求使用者從 GX Works 匯出 CSV / XML / TXT / ST / mnemonic / report。
* 若資料不足，先給出通用匯出架構。
* 對於無法匯出的資料，標記為 manual-export 或 screenshot-required。