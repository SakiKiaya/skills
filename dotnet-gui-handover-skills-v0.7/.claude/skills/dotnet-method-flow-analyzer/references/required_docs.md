# Required Documentation Structure

至少產生：

```text
docs/
  01_solution_structure.md
  02_architecture.md
  03_project_dependencies.md
  04_event_flow.md
  05_method_flow.md
  06_configuration.md
  07_user_workflow.md
  08_external_dependencies.md
  09_risk_analysis.md
```

每個文件必須：

- 使用 Markdown
- 使用 Mermaid
- 具備目錄
- 有清楚標題
- 有模組說明
- 有風險說明
- 有資料流說明

## 分析深度

不要只列出：

- 類別名稱
- 方法名稱
- 資料夾名稱

而是要分析：

- 為什麼存在
- 誰呼叫它
- 它影響誰
- UI 如何與它互動
- 是否跨執行緒
- 是否有副作用
- 是否耦合過高
- 是否難以測試
