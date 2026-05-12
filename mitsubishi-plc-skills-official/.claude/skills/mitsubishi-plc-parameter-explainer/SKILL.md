---
name: mitsubishi-plc-parameter-explainer
description: Explain Mitsubishi PLC CPU, module, network, and I/O parameters from normalized JSON or exported parameter reports. Use when the user wants detailed parameter documentation, risks, and check points.
version: 0.2.0
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
