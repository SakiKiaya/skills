---
name: mitsubishi-plc-parameter-explainer
description: Explain Mitsubishi PLC CPU, module, network, and I/O parameters from normalized JSON or exported parameter reports. Use when the user wants detailed parameter documentation, risks, and check points. 解析並說明 Mitsubishi PLC 專案中的 CPU parameter、module parameter、network parameter、I/O parameter。
version: 0.3.0
---

# Mitsubishi PLC Parameter Explainer

## Purpose

Create detailed parameter explanations for Mitsubishi PLC projects based on exported GX Works parameter files or normalized JSON.

## Input

Prefer:

```text
exports/normalized/parameters.json
exports/normalized/modules.json
exports/normalized/networks.json
```

Fallback:

```text
exports/raw/parameters/
exports/raw/module_config/
exports/raw/network/
```

## Output

Write or update:

```text
docs/02_cpu_parameters.md
docs/03_module_parameters.md
docs/04_network_parameters.md
```

## Explanation format

For each parameter, include:

| Field | Meaning |
|---|---|
| Parameter | Original parameter name |
| Value | Original value |
| Function | What this setting controls |
| Impact | Possible system behavior impact |
| Risk | Possible risk if misconfigured |
| Check Point | What engineer should verify |
| Source | Source file |

## Rules

1. Preserve original parameter name and value.
2. If the exact Mitsubishi definition is unknown, write `需查手冊`.
3. Do not pretend generic PLC knowledge is vendor-specific Mitsubishi definition.
4. Separate CPU, module, and network parameters when possible.
5. Mark inferred explanations with `推測`.
6. Prioritize safety, communication, watchdog, I/O refresh, station number, IP address, and module assignment parameters.

## Common categories to identify

- CPU execution / scan / watchdog
- I/O assignment
- module slot configuration
- Ethernet IP / subnet / gateway
- CC-Link / fieldbus station number
- refresh device mapping
- error handling and diagnostic behavior
- retentive/latch memory settings

## 參數說明格式 (Parameter Explanation Format)

每個參數需包含以下內容：

| 項目 | 說明 |
|------|------|
| 功能 | 該設定控制的功能 |
| 對系統的影響 | 可能的系統行為影響 |
| 可能風險 | 誤設定時的風險 |
| 建議確認方式 | 工程師應該驗證的方式 |

## 解析規則 (Parsing Rules)

- 每個參數需保留原始名稱與原始值。
- 若無法確認 Mitsubishi 官方定義，標記為「需查手冊」。
- 不可把通用 PLC 參數說明硬套到特定模組。
- 推測的說明必須標記為 `推測`。
