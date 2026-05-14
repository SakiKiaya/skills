# Large File Task: Forms/MainForm.vb lines 1993-2002

## Task Scope

| Item | Value |
|---|---|
| Source File | Forms/MainForm.vb |
| Language | VB.NET |
| Task Number | 16 |
| Task Line Range | 1993-2002 |
| Context Line Range | 1983-2012 |
| Context Before Lines | 10 |
| Context After Lines | 10 |
| Task Strategy | region_aware |
| Split Reason | File has 2017 lines, exceeding the 1000-line threshold. |

## Semantic Boundary

| Kind | Name | Start Line | End Line |
|---|---|---|---|
| region | PLC and Camera Simulation | 1993 | 2002 |

## Methods In Scope

| Method | Start Line | End Line | Calls | Side Effects |
|---|---|---|---|---|
| ConnectPlc | 1994 | 1997 | [] | ['External device/API interaction candidate 推測'] |
| CaptureCameraImage | 1998 | 2001 | [] | ['External device/API interaction candidate 推測'] |

## Events In Scope

| Control | Event | Handler | Line |
|---|---|---|---|

## Review Goals

- Summarize responsibilities in this line range.
- Identify event handlers, side effects, device/config/database interactions, and maintenance risks.
- Link findings back to related method, event-flow, form, and source-file chunks.

## Risk Candidates

| Risk | Evidence | Confidence |
|---|---|---|
| cross-thread UI risk | invoke | 0.55 |
| cross-thread UI risk | begininvoke | 0.55 |
| event leak risk | addhandler | 0.55 |
| blocking UI risk | thread.sleep | 0.55 |
