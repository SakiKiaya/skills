---
name: dotnet-semantic-analyzer
description: Infer architecture layers, UI responsibilities, critical operations, and device topology from normalized and semantic .NET WinForms IR.
version: 0.5.0
allowed-tools: Read Write Edit Bash
---

# dotnet-semantic-analyzer

## Purpose

Infer semantic architecture information for legacy WinForms reverse engineering.

## Inputs

```text
exports/normalized/
exports/semantic/
```

## Outputs

```text
exports/semantic/
  architecture_layers.json
  ui_responsibilities.json
  critical_operations.json
  device_topology.json
  backend_mappings.json
  threading_model.json
```

## Rules

- Keep confirmed data and inferred data separate.
- All inference must include confidence.
- Naming-based inference must not be treated as guaranteed truth.
