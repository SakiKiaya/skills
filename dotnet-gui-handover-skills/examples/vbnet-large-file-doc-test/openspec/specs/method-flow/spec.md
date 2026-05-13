# Method Flow Specification

## Requirements

### Requirement: Method btnSave_Click shall have impact information

The method `btnSave_Click` SHALL be documented with callers `['New', 'btnStart_Click']`, callees `['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult', 'SaveRecipe', 'StartInspection', 'UpdateStatus']`, inferred purpose `處理 GUI 或系統事件；執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能存取 DB 或資料儲存: update', '可能更新 UI 狀態或顯示內容: ui, form, update', '可能建立新物件或初始化流程: new', 'Persistence or write operation candidate 推測', 'External device/API interaction candidate 推測']`.

#### Scenario: Method btnSave_Click shall have impact information

- WHEN an AI Agent modifies `btnSave_Click`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method btnStart_Click shall have impact information

The method `btnStart_Click` SHALL be documented with callers `['New']`, callees `['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult', 'SaveRecipe', 'StartInspection', 'UpdateStatus', 'btnSave_Click']`, inferred purpose `處理 GUI 或系統事件；執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能存取 DB 或資料儲存: update', '可能更新 UI 狀態或顯示內容: ui, form, update', '可能建立新物件或初始化流程: new', 'Persistence or write operation candidate 推測', 'External device/API interaction candidate 推測']`.

#### Scenario: Method btnStart_Click shall have impact information

- WHEN an AI Agent modifies `btnStart_Click`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method CaptureCameraImage shall have impact information

The method `CaptureCameraImage` SHALL be documented with callers `['New', 'btnStart_Click', 'btnSave_Click', 'StartInspection', 'ConnectPlc']`, callees `['SaveRecipe', 'UpdateStatus']`, inferred purpose `執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能存取 DB 或資料儲存: update', '可能更新 UI 狀態或顯示內容: form, update', '可能建立新物件或初始化流程: new', 'Persistence or write operation candidate 推測', 'External device/API interaction candidate 推測']`.

#### Scenario: Method CaptureCameraImage shall have impact information

- WHEN an AI Agent modifies `CaptureCameraImage`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method ConnectPlc shall have impact information

The method `ConnectPlc` SHALL be documented with callers `['New', 'btnStart_Click', 'btnSave_Click', 'StartInspection']`, callees `['CaptureCameraImage', 'SaveRecipe', 'UpdateStatus']`, inferred purpose `執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能存取 DB 或資料儲存: update', '可能更新 UI 狀態或顯示內容: form, update', '可能建立新物件或初始化流程: new', 'Persistence or write operation candidate 推測', 'External device/API interaction candidate 推測']`.

#### Scenario: Method ConnectPlc shall have impact information

- WHEN an AI Agent modifies `ConnectPlc`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method EvaluateResult shall have impact information

The method `EvaluateResult` SHALL be documented with callers `['New', 'btnStart_Click', 'btnSave_Click', 'StartInspection']`, callees `[]`, inferred purpose `執行 Start 類型流程。推測`, and side effects `['可能更新 UI 狀態或顯示內容: form', '可能建立新物件或初始化流程: new']`.

#### Scenario: Method EvaluateResult shall have impact information

- WHEN an AI Agent modifies `EvaluateResult`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method New shall have impact information

The method `New` SHALL be documented with callers `[]`, callees `['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult', 'SaveRecipe', 'StartInspection', 'UpdateStatus', 'btnSave_Click', 'btnStart_Click']`, inferred purpose `執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能存取 DB 或資料儲存: update', '可能更新 UI 狀態或顯示內容: form, update', '可能建立新物件或初始化流程: new', 'Persistence or write operation candidate 推測', 'External device/API interaction candidate 推測']`.

#### Scenario: Method New shall have impact information

- WHEN an AI Agent modifies `New`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method SaveRecipe shall have impact information

The method `SaveRecipe` SHALL be documented with callers `['New', 'btnStart_Click', 'btnSave_Click', 'ConnectPlc', 'CaptureCameraImage']`, callees `['UpdateStatus']`, inferred purpose `執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能存取 DB 或資料儲存: update', '可能更新 UI 狀態或顯示內容: form, update', '可能建立新物件或初始化流程: new', 'Persistence or write operation candidate 推測']`.

#### Scenario: Method SaveRecipe shall have impact information

- WHEN an AI Agent modifies `SaveRecipe`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method StartInspection shall have impact information

The method `StartInspection` SHALL be documented with callers `['New', 'btnStart_Click', 'btnSave_Click']`, callees `['CaptureCameraImage', 'ConnectPlc', 'EvaluateResult']`, inferred purpose `執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能更新 UI 狀態或顯示內容: form', '可能建立新物件或初始化流程: new', 'External device/API interaction candidate 推測']`.

#### Scenario: Method StartInspection shall have impact information

- WHEN an AI Agent modifies `StartInspection`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`

### Requirement: Method UpdateStatus shall have impact information

The method `UpdateStatus` SHALL be documented with callers `['New', 'btnStart_Click', 'btnSave_Click', 'ConnectPlc', 'CaptureCameraImage', 'SaveRecipe']`, callees `[]`, inferred purpose `執行 Start 類型流程。推測`, and side effects `['可能存取外部設備 / SDK: plc, camera, capture', '可能存取 DB 或資料儲存: update', '可能更新 UI 狀態或顯示內容: form, update', '可能建立新物件或初始化流程: new', 'Persistence or write operation candidate 推測']`.

#### Scenario: Method UpdateStatus shall have impact information

- WHEN an AI Agent modifies `UpdateStatus`
- THEN it MUST inspect callers, callees, trigger sources, side effects, and maintenance notes from the corresponding method chunk.

**Source:** `Forms/MainForm.vb`


## Modification Rule

- AI Agents MUST review method callers and callees before changing method behavior.
