---
name: dotnet-industrial-vb-manual-writer
description: Deep-analysis and technical-manual writing workflow for industrial automation VB.NET WinForms systems. Use when analyzing legacy or messy VB.NET projects that include PLC communication, BackgroundWorker or multithreading, timers, state machines, socket handshakes, MES or SOAP integration, barcode readers, INI files, permissions, DataGridView rendering, or when producing handover-grade documentation for files such as frmMain.vb.
---

# dotnet-industrial-vb-manual-writer

## Role

Act as a senior industrial automation architect and technical documentation specialist.

Analyze VB.NET WinForms systems that combine PLC communication, asynchronous execution, device handshaking, state machines, MES/barcode integration, INI persistence, and operator UI logic. Convert messy source code into handover-grade technical manuals.

## Required Inputs

Start from the target file requested by the user, usually a core form such as:

```text
frmMain.vb
MainForm.vb
```

When available, use existing analysis artifacts from:

```text
exports/enterprise_analysis/
exports/analysis_chunks/
docs/chunks/
```

If those artifacts are missing or insufficient, read the source files directly.

## Deep-Dive Workflow

Follow the four phases in order. Record confirmed facts separately from inferred behavior.

### Phase 1: Async Monitoring & HAL

Focus on:

- `BackgroundWorker_DoWork`
- `PLC_Monitor`
- background polling loops
- PLC read/write wrappers
- hardware abstraction functions such as `TrayPick`, `CarrierPlace`, motion, camera, barcode, and PLC helpers

Produce:

- The system heartbeat: which loop or timer keeps the machine alive.
- PLC bit monitoring table, especially M-bits and edge-trigger logic.
- Coordinate calculation notes for core hardware actions.
- Thread-safety notes for cross-thread UI updates, reconnect logic, and exception recovery.

### Phase 2: State Machines & Handshaking

Focus on:

- `Timer_Tick`
- variables such as `Step_EU`, `Step_*`, `State_*`, `Mode_*`
- `Select Case` / `Case` logic
- AGV, conveyor, robot, socket, or peripheral handshakes

Produce:

- State machine diagrams or step tables.
- Handshake flow such as `Ask -> EXE -> Finish`.
- Automatic lot-change and remote-clear chains from UI event to PLC bit/register changes.
- PLC alarm diagnosis flow: how D-register codes become operator-facing troubleshooting guidance.

### Phase 3: External Integration & Consistency

Focus on:

- SOAP / Web Service / MES calls
- upload queues and retry buffers
- barcode readers
- INI or local file persistence
- recipe, lot, tray, carrier, and product identity data

Produce:

- Data-flow map from scan/input to memory, file, queue, and external upload.
- MES queue behavior: buffering, async processing, retry, failure handling.
- Barcode trigger timing and temporary storage locations.
- INI source-of-truth analysis for power-loss recovery and data consistency.

### Phase 4: Lifecycle, Safety & Maintenance

Focus on:

- `Form_Load`, `Shown`, `Closing`, `FormClosing`
- permission checks and role levels
- control `Enabled`, `Visible`, or authorization logic
- `DataGridView`, tray map, carrier map, alarm map, or status rendering
- resource cleanup

Produce:

- Startup warm-up sequence and safety interlocks.
- Shutdown/resource-release sequence.
- UI map rendering algorithm.
- Permission-level to UI-control mapping.
- Maintenance notes for hardcoded paths, model-specific exceptions, race conditions, blocking calls, and deployment risks.

## Search Heuristics

Always search for these patterns before writing the manual:

```text
#Region
BackgroundWorker
DoWork
Timer
Tick
Step_
State_
Select Case
Case
M\d+
D\d+
LastM
CurrentM
ReadBit
WriteBit
ReadWord
WriteWord
Socket
SOAP
WebService
Barcode
Queue
INI
DataGridView
Invoke
BeginInvoke
Permission
Enabled
Form_Load
FormClosing
```

## Cross-File Tracking

When the target file calls modules or helpers, inspect them before finalizing conclusions.

Common examples:

```text
modFunction.vb
modPLC.vb
modSocket.vb
modINI.vb
clsPLC.vb
clsBarcode.vb
clsMES.vb
```

Trace calls across files when they affect:

- PLC address meaning
- state transitions
- hardware motion
- MES upload behavior
- barcode data ownership
- INI persistence
- alarm explanation

## Edge Trigger Rule

Treat comparisons or assignments such as these as critical PLC edge-trigger logic:

```vb
If CurrentM200 AndAlso Not LastM200 Then
LastM200 = CurrentM200
```

Explain:

- the monitored bit
- rising/falling edge behavior
- the action triggered by the edge
- where the previous state is stored
- race-condition or missed-edge risks

## Output Standard

For each analyzed file, write a Markdown manual named:

```text
docs/<FileName>.vb.md
```

Use the required structure from `references/manual_standard.md`.

If the user asks for a full system manual, also create an index document that links the per-file manuals and summarizes cross-file flows.

## Quality Rules

- Prefer source-backed statements with file and line references.
- Mark uncertain behavior as inference.
- Include Mermaid diagrams when they clarify workflows or state machines.
- Keep PLC addresses, register names, and UI control names exact.
- Do not hide messy code. Document risk, coupling, and maintenance traps directly.
- Avoid generic enterprise filler. Every section should help a maintainer operate, debug, or modify the machine.
