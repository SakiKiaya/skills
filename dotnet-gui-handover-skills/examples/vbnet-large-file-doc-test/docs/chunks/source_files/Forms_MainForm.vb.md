# Source File: Forms/MainForm.vb

## File Summary

| Item | Value |
|---|---|
| Path | Forms/MainForm.vb |
| Language | VB.NET |
| Extension | .vb |
| Line Count | 1143 |
| Method Count | 9 |
| Class Count | 1 |

## Semantic Blocks

| Kind | Name | Start Line | End Line |
|---|---|---|---|
| class | MainForm | 6 | 1143 |
| method | New | 12 | 18 |
| method | btnStart_Click | 19 | 23 |
| method | btnSave_Click | 24 | 28 |
| method | StartInspection | 29 | 35 |
| method | EvaluateResult | 36 | 1120 |
| switch | mode | 38 | 45 |
| method | ConnectPlc | 1121 | 1125 |
| method | CaptureCameraImage | 1126 | 1129 |
| method | SaveRecipe | 1130 | 1134 |
| method | UpdateStatus | 1135 | 1142 |

## Methods

| Method | Start Line | End Line | Calls | Called By |
|---|---|---|---|---|
| New | 12 | 18 | ['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult', 'SaveRecipe', 'StartInspection', 'UpdateStatus', 'btnSave_Click', 'btnStart_Click'] | [] |
| btnStart_Click | 19 | 23 | ['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult', 'SaveRecipe', 'StartInspection', 'UpdateStatus', 'btnSave_Click'] | ['New'] |
| btnSave_Click | 24 | 28 | ['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult', 'SaveRecipe', 'StartInspection', 'UpdateStatus'] | ['New', 'btnStart_Click'] |
| StartInspection | 29 | 35 | ['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult'] | ['New', 'btnStart_Click', 'btnSave_Click'] |
| EvaluateResult | 36 | 1120 | [] | ['New', 'btnStart_Click', 'btnSave_Click', 'StartInspection'] |
| ConnectPlc | 1121 | 1125 | ['CaptureCameraImage', 'SaveRecipe', 'UpdateStatus'] | ['New', 'btnStart_Click', 'btnSave_Click', 'StartInspection'] |
| CaptureCameraImage | 1126 | 1129 | ['SaveRecipe', 'UpdateStatus'] | ['New', 'btnStart_Click', 'btnSave_Click', 'StartInspection', 'ConnectPlc'] |
| SaveRecipe | 1130 | 1134 | ['UpdateStatus'] | ['New', 'btnStart_Click', 'btnSave_Click', 'ConnectPlc', 'CaptureCameraImage'] |
| UpdateStatus | 1135 | 1142 | [] | ['New', 'btnStart_Click', 'btnSave_Click', 'ConnectPlc', 'CaptureCameraImage', 'SaveRecipe'] |

## Events

| Control | Event | Handler | Line |
|---|---|---|---|
| btnStart | Click | btnStart_Click | 16 |
| btnSave | Click | btnSave_Click | 17 |

## Risks

| Risk | Evidence | Confidence |
|---|---|---|
| cross-thread UI risk | invoke | 0.55 |
| cross-thread UI risk | begininvoke | 0.55 |
| event leak risk | addhandler | 0.55 |
| blocking UI risk | thread.sleep | 0.55 |
