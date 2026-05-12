# Skill: mitsubishi-plc-parameter-explainer

## Purpose
解析並說明 Mitsubishi PLC 專案中的 CPU parameter、module parameter、network parameter、I/O parameter。

## Input
- parameters.json
- modules.json
- networks.json
- raw exported parameter CSV/TXT/XML

## Output
- docs/02_cpu_parameters.md
- docs/03_module_parameters.md
- docs/04_network_parameters.md

## Rules
- 每個參數需保留原始名稱與原始值。
- 說明分成：
  - 功能
  - 對系統的影響
  - 可能風險
  - 建議確認方式
- 若無法確認 Mitsubishi 官方定義，標記為「需查手冊」。
- 不可把通用 PLC 參數說明硬套到特定模組。