# README Generation Rules

README.md 不可只是 GitHub 專案介紹。

README 必須是：

- 新人交接入口
- GUI 專案總覽
- 系統架構摘要
- 操作指南
- 維護入口

README 必須包含：

1. 專案名稱
2. 概述
3. 技術棧
4. 專案結構
5. 應用程式流程
6. 表單清單
7. 類別與模組清單
8. 參數設定指南
9. 常見操作
10. 已知注意事項

README 必須包含 Mermaid `graph TD`。

推測內容必須標記「推測」或「需人工確認」。

若 `docs/chunks/` 存在，README Generator 必須優先讀取 Form chunks、Event Flow chunks、Method chunks、Project chunks。
