# Method: CaptureCameraImage

**用途：**
執行 Start 類型流程。推測

**推測依據：**
- 被其他方法呼叫: New, btnStart_Click, btnSave_Click, StartInspection, ConnectPlc
- 名稱或呼叫鏈包含 Start 相關關鍵字: start
- 呼叫方法: SaveRecipe, UpdateStatus

**觸發來源：**
- 未偵測到明確 GUI 事件觸發來源。推測

**主要責任：**
- 作為內部流程中的被呼叫方法
- 協調或委派後續方法呼叫

**副作用：**
- 可能存取外部設備 / SDK: plc, camera, capture
- 可能存取 DB 或資料儲存: update
- 可能更新 UI 狀態或顯示內容: form, update
- 可能建立新物件或初始化流程: new
- Persistence or write operation candidate 推測
- External device/API interaction candidate 推測

**維護注意事項：**
- 檢查設備呼叫是否有 timeout、重試、例外處理與安全狀態
- 檢查資料庫連線、交易、例外處理與設定來源
- 若此方法可能在背景執行，需檢查 UI thread Invoke / Dispatcher
- 檢查物件生命週期、Dispose、資源釋放與重複初始化風險

## Method Metadata

| Item | Value |
|---|---|
| Source | Forms/MainForm.vb |
| Line | 1126 |
| Called By | ['New', 'btnStart_Click', 'btnSave_Click', 'StartInspection', 'ConnectPlc'] |
| Calls | ['SaveRecipe', 'UpdateStatus'] |
| Existing Purpose | N/A |
| Existing Side Effects | ['Persistence or write operation candidate 推測', 'External device/API interaction candidate 推測'] |

## Event Triggers

| Trigger | Source | Line |
|---|---|---|

## Related Event Flows

| Entry | Handler | Call Chain |
|---|---|---|
