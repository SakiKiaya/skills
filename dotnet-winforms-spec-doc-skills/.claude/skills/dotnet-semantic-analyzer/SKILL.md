
---
name: dotnet-semantic-analyzer
description: Semantic reverse-engineering analyzer for legacy WinForms systems.
version: 0.4.0
allowed-tools: Read Write Edit Bash
---

# dotnet-semantic-analyzer

## Purpose

Infer:

- architecture layers
- AOI device topology
- UI responsibilities
- critical operations
- backend workflow mappings
- threading models

## Outputs

```text
exports/semantic/
  architecture_layers.json
  ui_responsibilities.json
  device_topology.json
  threading_model.json
  critical_operations.json
  backend_mappings.json
```
