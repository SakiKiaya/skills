# Large File Task: Forms/MainForm.vb lines 1143-1143

## Task Scope

| Item | Value |
|---|---|
| Source File | Forms/MainForm.vb |
| Language | VB.NET |
| Task Number | 15 |
| Task Line Range | 1143-1143 |
| Context Line Range | 1133-1143 |
| Context Before Lines | 10 |
| Context After Lines | 0 |
| Task Strategy | class_gap_fallback |
| Split Reason | File has 1143 lines, exceeding the 1000-line threshold. |

## Semantic Boundary

| Kind | Name | Start Line | End Line |
|---|---|---|---|

## Methods In Scope

| Method | Start Line | End Line | Calls | Side Effects |
|---|---|---|---|---|

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
