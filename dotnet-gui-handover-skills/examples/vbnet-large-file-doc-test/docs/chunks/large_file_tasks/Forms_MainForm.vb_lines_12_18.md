# Large File Task: Forms/MainForm.vb lines 12-18

## Task Scope

| Item | Value |
|---|---|
| Source File | Forms/MainForm.vb |
| Language | VB.NET |
| Task Number | 3 |
| Task Line Range | 12-18 |
| Context Line Range | 2-28 |
| Context Before Lines | 10 |
| Context After Lines | 10 |
| Task Strategy | method_aware |
| Split Reason | File has 2017 lines, exceeding the 1000-line threshold. |

## Semantic Boundary

| Kind | Name | Start Line | End Line |
|---|---|---|---|
| method | New | 12 | 18 |

## Methods In Scope

| Method | Start Line | End Line | Calls | Side Effects |
|---|---|---|---|---|
| New | 12 | 18 | [] | [] |

## Events In Scope

| Control | Event | Handler | Line |
|---|---|---|---|
| btnStart | Click | btnStart_Click | 16 |
| btnSave | Click | btnSave_Click | 17 |

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
