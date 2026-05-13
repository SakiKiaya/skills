# README Generation Specification v1.0

````text
# README Generation Rules

README.md 不可只是 GitHub 專案介紹。

README 必須是：

- 新人交接入口
- GUI 專案總覽
- 系統架構摘要
- 操作指南
- 維護入口

README 必須可讓：

- 新進工程師
- 維護工程師
- AI Agent

快速理解專案。

---

# README 必須包含以下章節

# 專案名稱

自動從：

- solution
- csproj
- vbproj

推測。

若無法確認：

使用：

```text
Unknown Project
````

---

# 概述

說明：

* 專案用途
* GUI 功能
* 設備控制用途
* 系統責任
* 主要工作流程

不要只描述：

```text
這是一個 WinForms 專案
```

必須描述：

```text
此系統為 AOI 檢測 GUI，
負責控制 Camera / PLC，
並提供檢測流程操作介面。
```

---

# 技術棧

必須分析：

## 語言 / 架構

例如：

* .NET Framework
* .NET
* WinForms
* WPF
* Avalonia
* MAUI
* Prism
* MVVM

---

## 硬體通訊

必須特別標示：

* TCP/IP
* COM
* RS232
* RS485
* Modbus
* PLC SDK
* Camera SDK
* Motion SDK

例如：

| 類型     | 用途             |
| ------ | -------------- |
| TCP/IP | PLC 通訊         |
| COM    | Barcode Reader |
| SDK    | Camera 控制      |

---

## 網路通訊

分析：

* Socket
* HTTP
* REST API
* WebSocket
* MQTT

---

## 資料儲存

分析：

* SQL Server
* SQLite
* CSV
* XML
* JSON
* Registry
* Log Files

---

# 專案結構

必須使用：

```text
tree structure
```

並加入簡易說明。

例如：

```text
Services/
  業務邏輯

SDK/
  設備封裝

Forms/
  GUI 畫面
```

---

# 應用程式流程

必須分析：

* Program.cs
* App.xaml
* Main entry
* Startup flow

並建立：

```mermaid
graph TD
```

必須描述：

* 主畫面
* 子畫面
* Dialog
* Workflow

---

# 表單清單

必須使用表格。

至少包含：

| 表單名稱 | 用途 | 主要控制項 | 開啟來源 |

---

# 表單事件摘要

每個重要 Form 必須產生：

```md
> [!NOTE]
> **frmMain 事件處理摘要（UI Deep Dive）**
```

至少包含：

* Start
* Stop
* Save
* Load
* Timer
* BackgroundWorker
* Camera
* PLC
* DB

相關事件。

---

# 類別與模組清單

只列：

* 非 Form 類別
* Service
* Repository
* SDK
* Utility
* Manager
* ViewModel

必須包含：

| 類型 | 職責 |

不要只列檔名。

---

# 參數設定指南

必須分析：

* app.config
* settings.json
* ini/xml/json
* Registry
* Environment Variable

並使用：

| 檔案位置 | 預設值 | 修改方式 |

---

# 常見操作

至少包含：

## 建置執行

## 查閱 Log

## 權限切換

## SDK 初始化

## 設定修改

---

# 已知注意事項

必須包含：

* 巨型 Form
* UI 耦合
* static 濫用
* Singleton 濫用
* Cross-thread UI update
* async deadlock
* hardcoded path

如果有檢測到。

---

# README 品質要求

README 不是：

* API 文件
* 類別索引
* 方法清單

而是：

* 系統總覽
* GUI 操作指南
* 維護入口
* 技術交接文件

---

# Mermaid 要求

README 必須包含：

```mermaid
graph TD
```

不得省略。

---

# 推測規則

若內容為推測：

必須標記：

```text
推測
需人工確認
```

不得將推測內容寫成確定事實。

---

# Chunk-Aware README

若：

```text
docs/chunks/
```

存在：

README Generator 必須：

1. 優先讀取 chunks
2. 優先讀取 Form chunks
3. 優先讀取 Event Flow chunks
4. 優先讀取 Method chunks

不可只依賴：

```text
enterprise_analysis/*.json
```

---

# README Length Policy

README 不可過短。

至少必須：

* 可讓新人理解專案
* 可作為交接入口
* 可作為 AI Agent 首次閱讀入口

---

# 最終目標

README 必須達到：

* 技術主管
* 資深架構師
* GUI 系統維護工程師

會認為：

```text
這份 README 足以讓人開始接手系統
```

```
```
