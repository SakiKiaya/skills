# Large File Task: Forms/MainForm.vb lines 1126-1129

## Task Scope

| Item | Value |
|---|---|
| Source File | Forms/MainForm.vb |
| Language | VB.NET |
| Task Number | 12 |
| Task Line Range | 1126-1129 |
| Context Line Range | 1116-1139 |
| Context Before Lines | 10 |
| Context After Lines | 10 |
| Task Strategy | method_aware |
| Split Reason | File has 1143 lines, exceeding the 1000-line threshold. |

## Semantic Boundary

| Kind | Name | Start Line | End Line |
|---|---|---|---|
| method | CaptureCameraImage | 1126 | 1129 |

## Methods In Scope

| Method | Start Line | End Line | Calls | Side Effects |
|---|---|---|---|---|
| CaptureCameraImage | 1126 | 1129 | ['SaveRecipe', 'UpdateStatus'] | ['Persistence or write operation candidate 推測', 'External device/API interaction candidate 推測'] |

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
