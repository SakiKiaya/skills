# Skills Workspace

這個 workspace 用來存放自己開發的通用 AI Skills，目標是讓 Claude、Gemini CLI，以及其他能讀取 skill 說明與本地腳本的 agent 工具共用同一套工作流程。

目前主要包含兩套正在開發中的 skills kit：

```text
dotnet-gui-handover-skills/
plc-skills-kit/
```

## dotnet-gui-handover-skills

`dotnet-gui-handover-skills` 是針對企業 .NET GUI 專案的反向分析與交接文件產生工具。

主要用途：

- 分析 WinForms、WPF、Avalonia、MAUI-style XAML、C#、VB.NET 專案。
- 產生 `exports/enterprise_analysis/` 靜態分析 JSON。
- 將大型專案拆成 `exports/analysis_chunks/`，支援 project、form、event-flow、method、dependency、config、risk、source-file、large-file-task 等 chunk。
- 對超過 1000 行的原始檔產生語意切分任務，優先依 class、method、switch / Select Case 拆分，並保留 overlap context。
- 產生企業交接文件 `docs/01_*` 到 `docs/09_*`。
- 產生 AI agent 可讀的 OpenSpec 規格。
- 產生目標專案的 `docs/README.md`。

快速執行：

```bash
python dotnet-gui-handover-skills/run_v09_full_pipeline.py /path/to/dotnet-gui-project
```

`run_v09_full_pipeline.py` 檔名保留相容性，目前輸出為 v1.0。

## plc-skills-kit

`plc-skills-kit` 是針對 PLC 專案資料整理、標準化與文件化的 skills kit，主要面向 GX Works 匯出的資料。

目前包含：

- `plc-export-advisor`：協助規劃 GX Works 匯出哪些資料。
- `plc-project-normalizer`：將 raw exports 標準化成 JSON。
- `plc-doc-generator`：由 normalized JSON 產生 Markdown 文件。
- `plc-parameter-explainer`：協助解釋 PLC 參數與設定。
- `plc-structure-analyzer`：分析 ST / mnemonic 程式結構。

典型資料流程：

```text
exports/raw/
  -> exports/normalized/
  -> docs/
```

範例資料位於：

```text
plc-skills-kit/examples/sample_exports/
```

## Repository Layout

```text
.
├─dotnet-gui-handover-skills/
│  ├─.claude/skills/
│  ├─docs/
│  ├─exports/
│  ├─openspec/
│  └─examples/
└─plc-skills-kit/
   ├─.claude/skills/
   ├─docs/
   ├─examples/
   └─exports/
```

## Usage Style

這些 skills 都盡量保持為「可被 agent 閱讀的 `SKILL.md` + 可直接執行的 scripts」。

使用方式可以是：

- 讓 Claude / Gemini CLI 讀取 `.claude/skills/<skill-name>/SKILL.md` 後協助執行。
- 直接執行各 skill 的 Python script。
- 將某個 kit 複製到目標專案內，作為專案本地的分析與文件產生工具。

## Status

這個 workspace 是開發中的 skills 集合。`dotnet-gui-handover-skills` 目前整理到 v1.0；`plc-skills-kit` 仍在早期開發與資料格式整理階段。
