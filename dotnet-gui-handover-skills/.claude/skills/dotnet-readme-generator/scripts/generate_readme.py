#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json
import sys
from typing import Any


def load(path: Path, default: Any):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def load_chunks(folder: Path):
    if not folder.exists():
        return []
    out = []
    for p in sorted(folder.glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return out


def esc(v: Any) -> str:
    if v in (None, ""):
        return "N/A"
    s = str(v).replace("\n", " ").replace("|", "\\|")
    return s[:800] + "..." if len(s) > 800 else s


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(out) + "\n"


def infer_project_name(projects):
    return projects[0].get("name") if projects else "Unknown Project"


def infer_frameworks(projects):
    vals = []
    for p in projects:
        for k in ["language", "target_framework"]:
            if p.get(k): vals.append(p[k])
        if p.get("is_gui"): vals.append("GUI Project")
    return sorted(set(vals)) or ["需人工確認"]


def tech_stack(projects, external, config):
    text = json.dumps([projects, external, config], ensure_ascii=False).lower()
    hardware, network, storage = [], [], []
    if any(k in text for k in ["plc", "modbus", "mitsubishi", "mcprotocol"]):
        if any(k in text for k in ["tcp", "socket", "ethernet"]): hardware.append(["PLC", "TCP/IP 推測"])
        elif any(k in text for k in ["serial", "com", "rs232", "rs485"]): hardware.append(["PLC", "COM / Serial 推測"])
        else: hardware.append(["PLC", "通訊方式需人工確認"])
    if any(k in text for k in ["camera", "basler", "hikvision", "cognex", "grab"]): hardware.append(["Camera SDK", "相機控制 / 取像 推測"])
    if any(k in text for k in ["motion", "axis", "servo"]): hardware.append(["Motion Controller", "運動控制 推測"])
    if any(k in text for k in ["serialport", "rs232", "rs485", "comport"]): hardware.append(["SerialPort", "COM / RS232 / RS485 推測"])
    if any(k in text for k in ["socket", "tcp", "udp"]): network.append(["Socket", "TCP/UDP 通訊 推測"])
    if any(k in text for k in ["http", "rest", "api"]): network.append(["HTTP / REST API", "網路 API 推測"])
    if any(k in text for k in ["sql", "database", "sqlite", "mysql", "oracle"]): storage.append(["Database", "DB 儲存 推測"])
    if "csv" in text: storage.append(["CSV", "檔案儲存 推測"])
    if "xml" in text: storage.append(["XML", "設定或資料檔 推測"])
    if "json" in text: storage.append(["JSON", "設定或資料檔 推測"])
    if "registry" in text: storage.append(["Registry", "Windows Registry 推測"])
    return hardware or [["需人工確認", "未偵測到明確硬體通訊"]], network or [["需人工確認", "未偵測到明確網路通訊"]], storage or [["需人工確認", "未偵測到明確資料儲存"]]


def project_tree(projects):
    lines = ["```text", "project-root/", "├── docs/                 # 企業級交接文件", "├── openspec/             # AI Agent 可理解規格", "├── exports/", "│   ├── enterprise_analysis/ # 全專案分析資料", "│   └── analysis_chunks/     # 分割分析 chunks"]
    for p in projects[:20]:
        path = p.get("path") or p.get("project_file")
        if path: lines.append(f"├── {path}  # {p.get('language') or 'Project'}")
    lines.append("```")
    return "\n".join(lines)


def app_flow_diagram(forms, event_flows):
    lines = ["```mermaid", "graph TD", '  Entry["Entry Point / Program.cs / App.xaml"]']
    if forms:
        for i, c in enumerate(forms[:20]):
            data = c.get("data") or {}; name = data.get("form_name") or c.get("title") or f"Form{i}"; node = f"F{i}"
            lines.append(f'  {node}["{esc(name)}"]')
            lines.append(f"  {'Entry' if i == 0 else 'F0'} --> {node}")
    else:
        lines.append('  Entry --> MainUI["Main UI 需人工確認"]')
    for i, c in enumerate(event_flows[:20]):
        data = c.get("data") or {}; f = data.get("event_flow") or {}; entry = f.get("entry") or c.get("title") or f"Event{i}"; node = f"E{i}"
        lines.append(f'  {node}["{esc(entry)}"]')
        lines.append(f"  {'F0' if forms else 'MainUI'} --> {node}")
    lines.append("```")
    return "\n".join(lines)


def form_table(forms):
    rows=[]
    for c in forms[:50]:
        data=c.get("data") or {}; form=data.get("form_name") or c.get("title"); events=data.get("events") or []
        rows.append([form, "GUI 畫面 / 操作入口 推測", ", ".join(str(e.get("control")) for e in events[:5] if isinstance(e, dict)) or "需人工確認", ", ".join(str(e.get("handler")) for e in events[:5] if isinstance(e, dict)) or "需人工確認"])
    return table(["表單名稱", "用途", "主要控制項", "從哪裡開啟此表單"], rows)


def form_event_notes(forms):
    out=[]
    for c in forms[:10]:
        data=c.get("data") or {}; form=data.get("form_name") or c.get("title"); events=data.get("events") or []
        out.append(f"> [!NOTE]\n> **{esc(form)} 事件處理摘要（UI Deep Dive）**")
        if not events: out.append("> - **事件名稱**：未偵測到事件，需人工確認")
        for e in events[:12]:
            if isinstance(e, dict): out.append(f"> - **{esc(e.get('control'))}.{esc(e.get('event'))}**：呼叫 `{esc(e.get('handler'))}`，用途需依事件流程確認。推測")
        out.append("")
    return "\n".join(out)


def legacy_module_table(method_chunks):
    rows=[]
    for c in method_chunks[:80]:
        data=c.get("data") or {}; m=data.get("method") or {}; name=m.get("name") or c.get("title"); source=m.get("source"); calls=m.get("calls") or []
        text=(str(name)+" "+str(source)).lower(); kind="Service / Manager / Utility 推測"
        if "service" in text: kind="Service"
        elif "repo" in text or "database" in text: kind="Repository"
        elif "manager" in text: kind="Manager"
        elif "viewmodel" in text: kind="ViewModel"
        elif "util" in text or "helper" in text: kind="Utility"
        rows.append([source or name, kind, f"呼叫 {len(calls)} 個方法；實際職責需參考 05_method_flow.md。推測"])
    return table(["類型", "職責", "說明"], rows)


def module_table(method_chunks):
    grouped={}
    for c in method_chunks:
        data=c.get("data") or {}; m=data.get("method") or {}
        source=m.get("source") or "Unknown"
        module_name=Path(source).stem if source != "Unknown" else str(m.get("name") or c.get("title") or "Unknown")
        key=(source, module_name)
        item=grouped.setdefault(key, {"source":source, "module":module_name, "methods":set(), "calls":set(), "kind":"Service / Manager / Utility"})
        name=m.get("name")
        if name:
            item["methods"].add(str(name))
        for call in m.get("calls") or []:
            item["calls"].add(str(call))
        text=(str(module_name)+" "+str(source)+" "+str(name)).lower()
        if "form" in text:
            item["kind"]="Form / UI"
        elif "service" in text:
            item["kind"]="Service"
        elif "repo" in text or "database" in text:
            item["kind"]="Repository"
        elif "manager" in text:
            item["kind"]="Manager"
        elif "viewmodel" in text:
            item["kind"]="ViewModel"
        elif "util" in text or "helper" in text:
            item["kind"]="Utility"
    rows=[]
    for item in sorted(grouped.values(), key=lambda x: (x["source"], x["module"]))[:80]:
        rows.append([
            item["source"],
            item["module"],
            item["kind"],
            len(item["methods"]),
            len(item["calls"]),
            "See docs/05_method_flow.md and docs/chunks/methods/ for method details.",
        ])
    return table(["文件", "類別/模組", "角色推測", "方法數", "呼叫方法數", "說明"], rows)


def config_table(config_chunks):
    rows=[]
    for c in config_chunks[:80]:
        data=c.get("data") or {}; path=data.get("path") or data.get("source") or data.get("expression") or c.get("title")
        modify="外部修改 推測"
        if "settings" in str(path).lower(): modify="可能由 UI 或 Visual Studio Settings 修改 推測"
        rows.append([path, data.get("default") or "需人工確認", modify])
    return table(["檔案位置", "預設值", "修改方式（UI修改還是外部修改）"], rows)


def risk_notes(risks):
    if not risks: return "- 未偵測到明確風險；仍需人工確認巨型 Form、UI 耦合、hardcoded path 等問題。\n"
    rows=[]
    for c in risks[:50]:
        data=c.get("data") or {}; rows.append([data.get("risk_type"), data.get("source"), data.get("evidence"), data.get("confidence")])
    return table(["問題", "位置", "證據", "信心度"], rows)


def main(repo_arg: str) -> int:
    repo=Path(repo_arg).resolve(); docs=repo/"docs"; docs.mkdir(parents=True, exist_ok=True)
    analysis=repo/"exports"/"enterprise_analysis"; chunks=repo/"exports"/"analysis_chunks"
    projects=load(analysis/"projects.json", []); external=load(analysis/"external_dependencies.json", []); config=load(analysis/"configuration.json", {"files":[],"code_references":[]})
    form_chunks=load_chunks(chunks/"forms"); event_chunks=load_chunks(chunks/"event_flows"); method_chunks=load_chunks(chunks/"methods"); config_chunks=load_chunks(chunks/"configs"); risk_chunks=load_chunks(chunks/"risks")
    project_name=infer_project_name(projects); frameworks=infer_frameworks(projects); hardware, network, storage=tech_stack(projects, external, config)
    readme=f"""# {project_name}

## 概述

此專案為 .NET GUI 應用程式。根據目前靜態分析結果，系統包含 GUI 畫面、事件流程、方法呼叫鏈、設定檔與外部相依項目。

本 README 是企業級交接入口，供新進工程師、維護工程師與 AI Agent 快速理解專案。若內容標示為「推測」或「需人工確認」，代表該結論來自靜態分析或命名推測，尚未經人工驗證。

## 技術棧

### 語言/架構

{table(['項目'], [[x] for x in frameworks])}

### 硬體通訊

{table(['類型', '用途'], hardware)}

### 網路通訊

{table(['類型', '用途'], network)}

### 資料儲存

{table(['類型', '用途'], storage)}

## 專案結構

{project_tree(projects)}

## 應用程式流程

程式進入點需從 `Program.cs`、`App.xaml` 或專案啟動設定確認。以下流程圖根據表單與事件 chunks 推測產生。

{app_flow_diagram(form_chunks, event_chunks)}

## 表單清單

{form_table(form_chunks) if form_chunks else '目前未產生 form chunks，請先執行 analysis_chunker。'}

{form_event_notes(form_chunks) if form_chunks else ''}

## 類別與模組清單

以下列出非 Form 相關程式碼的初步職責推測。詳細內容請參考 `docs/05_method_flow.md` 與 `docs/chunks/methods/`。

{module_table(method_chunks) if method_chunks else '目前未產生 method chunks，請先執行 analysis_chunker。'}

## 參數設定指南

{config_table(config_chunks) if config_chunks else '目前未產生 config chunks，請先執行 analysis_chunker。'}

## 常見操作

### 1. 建置執行

- 使用 Visual Studio 或對應 .NET SDK 開啟 solution / project。
- 確認 NuGet、SDK、Native DLL、COM 元件與 x86/x64 平台設定。
- 若有設備連線，需先確認 PLC / Camera / Motion / DB 設定。

### 2. 查閱 Log

- 搜尋專案中的 `Log`、`logger`、`NLog`、`log4net`、`Serilog`、`WriteLine`。
- 若 Log 路徑來自設定檔，請參考 `docs/06_configuration.md`。
- 若 Log 路徑為硬編碼，請列入 `docs/09_risk_analysis.md`。

### 3. 權限切換

- 若系統存取 Registry、Program Files、設備 SDK、COM 或網路磁碟，需確認執行權限。
- 若使用 Windows 服務或系統管理員權限，需確認部署帳號與 UAC 設定。
- 實際權限流程需人工確認。

### 4. SDK 初始化

- 檢查 Camera / PLC / Motion / Vision SDK 初始化流程。
- 確認 runtime、license、driver、x86/x64 相容性。
- 相關風險請參考 `docs/08_external_dependencies.md`。

### 5. 設定修改

- App.config / settings.json / ini / xml 通常屬於外部修改。
- Settings.settings 可能由 UI 或 Visual Studio Settings 修改。
- 若設定由程式寫入，請確認寫入位置與權限。

## 已知注意事項

{risk_notes(risk_chunks)}

## 相關文件

- `docs/01_solution_structure.md`
- `docs/02_architecture.md`
- `docs/03_project_dependencies.md`
- `docs/04_event_flow.md`
- `docs/05_method_flow.md`
- `docs/06_configuration.md`
- `docs/07_user_workflow.md`
- `docs/08_external_dependencies.md`
- `docs/09_risk_analysis.md`
- `openspec/project.md`
"""
    (docs/"README.md").write_text(readme, encoding="utf-8")
    print(f"Wrote {docs/'README.md'}")
    return 0

if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    raise SystemExit(main(repo))
