# Source File: Forms/MainForm.vb

## File Summary

| Item | Value |
|---|---|
| Path | Forms/MainForm.vb |
| Language | VB.NET |
| Extension | .vb |
| Line Count | 2017 |
| Method Count | 9 |
| Class Count | 1 |

## Semantic Blocks

| Kind | Name | Start Line | End Line |
|---|---|---|---|
| class | MainForm | 6 | 2016 |
| method | New | 12 | 18 |
| method | btnStart_Click | 19 | 23 |
| method | btnSave_Click | 24 | 28 |
| method | StartInspection | 29 | 35 |
| method | EvaluateResult | 36 | 1991 |
| switch | mode | 38 | 916 |
| region | inspection branch filler 0 | 833 | 846 |
| region | inspection branch filler 1 | 883 | 892 |
| region | inspection branch filler 2 | 894 | 901 |
| region | PLC and Camera Simulation | 1993 | 2002 |
| method | ConnectPlc | 1994 | 1997 |
| method | CaptureCameraImage | 1998 | 2001 |
| method | SaveRecipe | 2003 | 2007 |
| method | UpdateStatus | 2008 | 2015 |
| if | Me.InvokeRequired | 2010 | 2013 |

## Methods

| Method | Start Line | End Line | Calls | Called By |
|---|---|---|---|---|
| New | 12 | 18 | [] | [] |
| btnStart_Click | 19 | 23 | ['StartInspection', 'UpdateStatus'] | [] |
| btnSave_Click | 24 | 28 | ['SaveRecipe', 'UpdateStatus'] | [] |
| StartInspection | 29 | 35 | ['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult'] | ['btnStart_Click'] |
| EvaluateResult | 36 | 1991 | [] | ['StartInspection'] |
| ConnectPlc | 1994 | 1997 | [] | ['StartInspection'] |
| CaptureCameraImage | 1998 | 2001 | [] | ['StartInspection'] |
| SaveRecipe | 2003 | 2007 | [] | ['btnSave_Click'] |
| UpdateStatus | 2008 | 2015 | [] | ['btnStart_Click', 'btnSave_Click'] |

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
