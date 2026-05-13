# Method Purpose Explanation Format

```markdown
## btnStart_Click

**用途：**
處理 Start 按鈕點擊事件，啟動主要檢測流程。

**推測依據：**
- 方法名稱包含 Start / Click
- 由 btnStart.Click 觸發
- 呼叫 Camera / PLC / Inspection 相關方法

**觸發來源：**
- btnStart.Click

**主要責任：**
- 作為 UI 操作入口
- 協調後端檢測流程

**副作用：**
- 可能啟動相機
- 可能寫入 PLC
- 可能更新 UI 狀態

**維護注意事項：**
- 檢查是否有長時間阻塞 UI 的操作
- 檢查設備呼叫是否有例外與 timeout 處理
```
