# 02 Architecture

## Overall Block Architecture

```mermaid
graph TD
  User["User / Operator"]
  UI["GUI Layer"]
  Logic["Application / Service Layer"]
  Data["Data / Repository Layer"]
  Device["External Device / SDK Layer"]
  Config["Configuration"]
  User --> UI
  UI --> Logic
  Logic --> Data
  Logic --> Device
  UI --> Config
  Logic --> Config
  UI --> P_VbLargeFileDocTest["VbLargeFileDocTest"]
  Device -.-> D_PLC["PLC"]
  Device -.-> D_Camera_SDK["Camera SDK"]
  Device -.-> D_Vision_SDK["Vision SDK"]
```

## Layer Explanation

| Layer | Responsibility | Review Focus |
|---|---|---|
| GUI Layer | Forms / Windows / UserControls, user events, UI updates | UI-logic coupling, thread safety |
| Application / Service Layer | Workflow orchestration and business logic | God service, testability |
| Data / Repository Layer | Database/file persistence | connection/config/runtime risk |
| External Device / SDK Layer | Camera, PLC, motion, native SDKs | runtime, timeout, x86/x64, license |
| Configuration | App.config, settings, registry, environment | hardcoded and environment-specific behavior |

## Module Responsibility from Project Chunks

| Project | Responsibility | Sources |
|---|---|---|
| VbLargeFileDocTest | [] | ['VbLargeFileDocTest.vbproj'] |

## Architecture Details from Curated Chunks


### [Project: VbLargeFileDocTest](chunks/projects/VbLargeFileDocTest.md)

# Project: VbLargeFileDocTest

## Summary

Project-level chunk for module responsibility and dependencies.

## Project Metadata

| Item | Value |
|---|---|
| Name | VbLargeFileDocTest |
| Language | VB.NET |
| Path | VbLargeFileDocTest.vbproj |
| Target Framework | net48 |
| GUI Project | True |
| Responsibility Inference | [] |

## Local Dependency Graph

```mermaid
flowchart LR
  P["VbLargeFileDocTest"]
  D0["System.Windows.Forms"]
  P --> D0
  D1["System.Configuration"]
  P --> D1
```

## Dependencies

| Type | Target | Source |
|---|---|---|
| Reference | System.Windows.Forms | VbLargeFileDocTest.vbproj |
| Reference | System.Configuration | VbLargeFileDocTest.vbproj |

## Module Responsibility

- 主要責任：需人工確認。推測
- 維護注意：確認此模組是否同時承擔 UI、業務邏輯、設備控制或資料存取，避免耦合過高。

## Risks

| Risk | Evidence | Confidence |
|---|---|---|

