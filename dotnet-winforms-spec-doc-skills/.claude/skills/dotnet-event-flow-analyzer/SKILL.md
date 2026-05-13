---
name: dotnet-event-flow-analyzer
description: Analyze WinForms operational flows, startup sequence, UI-to-backend mappings, threading/timer risks, and possible device-control paths from normalized .NET project IR.
version: 0.5.0
allowed-tools: Read Write Edit Bash
---

# dotnet-event-flow-analyzer

## Purpose

Convert normalized event/call graph data into higher-level semantic flow analysis.

## Inputs

```text
exports/normalized/
  event_flows.json
  call_graph.json
  methods.json
  events.json
  controls.json
```

## Outputs

```text
exports/semantic/
  operation_flows.json
  startup_flow.json
  risk_points.json
  ui_backend_flows.json
  threading_flows.json
  timer_flows.json
  device_control_flows.json
```

## v0.5 Analysis Targets

- Startup sequence candidates
- UI operation flows
- Handler → internal method call chains
- Timer / BackgroundWorker / Task / Thread / async-await candidates
- UI blocking risk candidates
- Device-control call candidates: PLC, Camera, Vision, Motion, Serial, Socket, Modbus
- Critical operation flows: Start, Stop, Reset, Alarm, Emergency, Home

## Rules

- Treat all flow inference as best-effort static analysis.
- Every inferred item must include confidence.
- Do not claim execution order unless directly observed from call sequence.
- Preserve source references from normalized IR whenever available.
