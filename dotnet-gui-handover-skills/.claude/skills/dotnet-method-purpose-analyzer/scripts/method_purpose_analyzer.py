#!/usr/bin/env python3
"""
dotnet-method-purpose-analyzer v1.0

Usage:
    python method_purpose_analyzer.py <analysis_dir>

Reads:
    methods.json, event_flows.json, events.json, configuration.json, external_dependencies.json

Writes:
    method_purposes.json
"""
from __future__ import annotations

from pathlib import Path
import json
import sys
import re
from typing import Any

DEVICE_WORDS = ["plc", "camera", "grab", "capture", "motion", "serial", "socket", "modbus", "halcon", "opencv", "emgu", "vision", "aoi"]
DB_WORDS = ["sql", "db", "database", "repository", "insert", "update", "delete", "select", "sqlite"]
FILE_WORDS = ["file", "readall", "writeall", "stream", "path", "csv", "json", "xml", "ini", "config"]
UI_WORDS = ["ui", "form", "view", "label", "textbox", "button", "grid", "datagrid", "display", "refresh", "update", "show", "enabled", "visible", "invoke", "begininvoke"]
ASYNC_WORDS = ["async", "await", "task", "thread", "backgroundworker", "timer", "tick", "dispatcher", "sleep", "delay"]
CREATE_WORDS = ["create", "new", "init", "initialize", "build", "factory", "load"]
CONFIG_WORDS = ["config", "setting", "settings", "appsettings", "configurationmanager", "environment", "registry"]
EVENT_WORDS = ["click", "load", "shown", "closing", "tick", "changed", "command", "dowork", "datareceived"]

OPERATION_WORDS = {
    "Start": ["start", "run", "begin", "execute"],
    "Stop": ["stop", "end", "abort", "cancel"],
    "Reset": ["reset", "clear"],
    "Save": ["save", "write", "export"],
    "Load": ["load", "read", "import"],
    "Connect": ["connect", "open"],
    "Disconnect": ["disconnect", "close"],
    "Inspect": ["inspect", "inspection", "aoi", "vision", "process"],
    "Alarm": ["alarm", "error", "fault", "異常", "警報"],
    "Initialize": ["init", "initialize", "startup", "setup"],
}

def load(path: Path, default: Any):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def write(path: Path, data: Any):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def low(x: Any) -> str:
    return str(x or "").lower()

def contains_any(text: str, words: list[str]) -> list[str]:
    t = low(text)
    return [w for w in words if w.lower() in t]

def infer_operation(name: str, text: str) -> tuple[str, list[str]]:
    evidence = []
    for op, words in OPERATION_WORDS.items():
        hits = contains_any(name + " " + text, words)
        if hits:
            evidence.append(f"名稱或呼叫鏈包含 {op} 相關關鍵字: {', '.join(hits)}")
            return op, evidence
    return "General", evidence

def build_event_index(events: list[dict[str, Any]], flows: list[dict[str, Any]]):
    by_handler: dict[str, list[dict[str, Any]]] = {}
    for e in events:
        h = e.get("handler")
        if h:
            by_handler.setdefault(h, []).append({
                "source_type": "event",
                "trigger": f"{e.get('control')}.{e.get('event')}",
                "source": e.get("source"),
                "line": e.get("line"),
            })
    for f in flows:
        h = f.get("handler")
        if h:
            by_handler.setdefault(h, []).append({
                "source_type": "event_flow",
                "trigger": f.get("entry"),
                "source": f.get("source"),
                "line": f.get("line"),
            })
    return by_handler

def infer_purpose(method: dict[str, Any], triggers: list[dict[str, Any]]) -> dict[str, Any]:
    name = method.get("name") or "UnknownMethod"
    source = method.get("source")
    class_hint = Path(source).stem if source else ""
    calls = method.get("calls") or []
    called_by = method.get("called_by") or []
    side_effects_existing = method.get("side_effects") or []
    raw_text = " ".join([name, class_hint, " ".join(calls), " ".join(called_by), str(side_effects_existing), str(method)])

    operation, op_evidence = infer_operation(name, raw_text)

    evidence = []
    purpose_parts = []
    responsibilities = []
    side_effects = []
    maintenance_notes = []

    # Triggers
    trigger_texts = [t.get("trigger") for t in triggers if t.get("trigger")]
    if triggers:
        evidence.append("由事件或事件流程觸發: " + ", ".join(trigger_texts))
        responsibilities.append("作為 GUI / 事件流程的入口或處理節點")
    elif called_by:
        evidence.append("被其他方法呼叫: " + ", ".join(map(str, called_by[:10])))
        responsibilities.append("作為內部流程中的被呼叫方法")
    else:
        evidence.append("未偵測到明確觸發來源，需人工確認")
        responsibilities.append("需人工確認此方法在系統中的責任")

    # Method name evidence
    if contains_any(name, EVENT_WORDS):
        evidence.append("方法名稱包含事件處理常見關鍵字")
        purpose_parts.append("處理 GUI 或系統事件")
    if op_evidence:
        evidence.extend(op_evidence)
        if operation != "General":
            purpose_parts.append(f"執行 {operation} 類型流程")

    # Calls
    if calls:
        evidence.append("呼叫方法: " + ", ".join(map(str, calls[:20])))
        responsibilities.append("協調或委派後續方法呼叫")
    else:
        evidence.append("未偵測到明確的內部方法呼叫")
        responsibilities.append("可能是簡單 setter/getter、事件終點、或外部 API 呼叫點，需人工確認")

    # Side effects
    device_hits = contains_any(raw_text, DEVICE_WORDS)
    db_hits = contains_any(raw_text, DB_WORDS)
    file_hits = contains_any(raw_text, FILE_WORDS)
    ui_hits = contains_any(raw_text, UI_WORDS)
    async_hits = contains_any(raw_text, ASYNC_WORDS)
    create_hits = contains_any(raw_text, CREATE_WORDS)
    config_hits = contains_any(raw_text, CONFIG_WORDS)

    if device_hits:
        side_effects.append("可能存取外部設備 / SDK: " + ", ".join(device_hits))
        maintenance_notes.append("檢查設備呼叫是否有 timeout、重試、例外處理與安全狀態")
    if db_hits:
        side_effects.append("可能存取 DB 或資料儲存: " + ", ".join(db_hits))
        maintenance_notes.append("檢查資料庫連線、交易、例外處理與設定來源")
    if file_hits:
        side_effects.append("可能讀寫檔案或外部資料路徑: " + ", ".join(file_hits))
        maintenance_notes.append("檢查檔案路徑是否硬編碼、權限是否足夠、格式是否穩定")
    if ui_hits:
        side_effects.append("可能更新 UI 狀態或顯示內容: " + ", ".join(ui_hits))
        maintenance_notes.append("若此方法可能在背景執行，需檢查 UI thread Invoke / Dispatcher")
    if config_hits:
        side_effects.append("可能讀取設定或環境資訊: " + ", ".join(config_hits))
        maintenance_notes.append("檢查設定來源是否在 06_configuration.md 中有文件化")
    if async_hits:
        side_effects.append("可能涉及非同步、Timer 或背景執行: " + ", ".join(async_hits))
        maintenance_notes.append("檢查 async deadlock、Timer re-entry、BackgroundWorker 例外處理與取消流程")
    if create_hits:
        side_effects.append("可能建立新物件或初始化流程: " + ", ".join(create_hits))
        maintenance_notes.append("檢查物件生命週期、Dispose、資源釋放與重複初始化風險")

    for s in side_effects_existing:
        if s not in side_effects:
            side_effects.append(str(s))

    if not side_effects:
        side_effects.append("未偵測到明確副作用；仍需人工確認是否有外部 API、UI 或狀態變更")

    if not maintenance_notes:
        maintenance_notes.append("需人工確認此方法是否有隱含狀態變更、例外處理或耦合風險")

    # Purpose text
    if not purpose_parts:
        if triggers:
            purpose_parts.append("處理觸發來源對應的操作流程")
        elif calls:
            purpose_parts.append("執行內部流程協調或業務邏輯")
        else:
            purpose_parts.append("用途需人工確認；目前僅能從名稱與所在檔案推測")
    purpose = "；".join(dict.fromkeys(purpose_parts)) + "。推測"

    return {
        "method": name,
        "class_or_file": class_hint,
        "source": source,
        "line": method.get("line"),
        "called_by": called_by,
        "calls": calls,
        "triggers": triggers,
        "inferred_purpose": purpose,
        "main_responsibility": list(dict.fromkeys(responsibilities)),
        "side_effects": list(dict.fromkeys(side_effects)),
        "maintenance_notes": list(dict.fromkeys(maintenance_notes)),
        "evidence": list(dict.fromkeys(evidence)),
        "analysis_inputs": {
            "method_name": name,
            "class_or_file": class_hint,
            "event_triggers": trigger_texts,
            "called_methods": calls,
            "called_by": called_by,
            "has_config_candidate": bool(config_hits),
            "has_db_candidate": bool(db_hits),
            "has_file_candidate": bool(file_hits),
            "has_device_candidate": bool(device_hits),
            "has_ui_update_candidate": bool(ui_hits),
            "has_async_thread_timer_candidate": bool(async_hits),
            "has_object_creation_candidate": bool(create_hits),
        },
        "confidence": 0.75 if triggers or calls or side_effects_existing else 0.45,
    }

def main(analysis_dir: str) -> int:
    base = Path(analysis_dir)
    methods = load(base / "methods.json", [])
    events = load(base / "events.json", [])
    flows = load(base / "event_flows.json", [])
    event_index = build_event_index(events, flows)

    purposes = []
    for m in methods:
        triggers = event_index.get(m.get("name"), [])
        purposes.append(infer_purpose(m, triggers))

    write(base / "method_purposes.json", purposes)
    print(f"Wrote {base / 'method_purposes.json'}")
    print(f"Analyzed methods: {len(purposes)}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: method_purpose_analyzer.py <analysis_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
