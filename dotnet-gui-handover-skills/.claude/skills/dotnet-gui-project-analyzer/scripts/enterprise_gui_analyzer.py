#!/usr/bin/env python3
"""
dotnet-gui enterprise reverse engineering analyzer v0.7.1

Usage:
    python enterprise_gui_analyzer.py <repo_root> <out_dir>

Produces:
    enterprise_analysis.json
    projects.json
    dependencies.json
    classes.json
    methods.json
    source_files.json
    source_blocks.json
    events.json
    event_flows.json
    configuration.json
    external_dependencies.json
    user_workflows.json
    risks.json
    schema_validation.json
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any

IGNORE = {".git", ".vs", "bin", "obj", "packages", "node_modules", ".claude", "exports", "docs", "openspec"}
CODE_EXTS = {".cs", ".vb", ".xaml", ".axaml"}
CONFIG_EXTS = {".config", ".settings", ".json", ".xml", ".ini", ".yaml", ".yml"}

PROJECT_EXTS = {".csproj", ".vbproj", ".vcxproj", ".fsproj"}

CS_METHOD = re.compile(r'(?P<mod>public|private|protected|internal|static|async|virtual|override|sealed|\s)+\s+(?P<ret>[\w<>\[\],\s\?\.]+?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<params>[^)]*)\)\s*\{', re.M)
VB_METHOD = re.compile(r'^\s*(?P<mod>(?:Public|Private|Friend|Protected|Shared|Overrides|Overridable|Async|\s)*)\s*(?P<kind>Sub|Function)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<params>[^)]*)\)(?P<handles>[^\n]*Handles\s+[^\n]+)?', re.I | re.M)
CLASS_RE = re.compile(r'\b(class|interface|enum|struct|Class|Interface|Enum|Structure|Module)\s+([A-Za-z_][A-Za-z0-9_]*)', re.I)
CS_SWITCH = re.compile(r'\bswitch\s*\((?P<expr>[^)]*)\)\s*\{', re.M)
VB_SELECT_CASE = re.compile(r'^\s*Select\s+Case\s+(?P<expr>.+)$', re.I | re.M)
CALL_RE = re.compile(r'(?:(?P<target>[A-Za-z_][A-Za-z0-9_]*)\.)?(?P<method>[A-Za-z_][A-Za-z0-9_]*)\s*\(')
EVENT_CS = re.compile(r'(?P<control>[A-Za-z_][A-Za-z0-9_]*)\.(?P<event>Click|Load|Shown|Closing|FormClosing|Tick|DoWork|DataReceived|SelectedIndexChanged|TextChanged|CheckedChanged|CellClick|Command)\s*\+=\s*(?:new\s+[\w\.]+\()?(?:this\.)?(?P<handler>[A-Za-z_][A-Za-z0-9_]*)', re.I)
EVENT_VB = re.compile(r'(?:AddHandler\s+)?(?P<control>[A-Za-z_][A-Za-z0-9_]*)\.(?P<event>Click|Load|Shown|Closing|Tick|DoWork|DataReceived|SelectedIndexChanged|TextChanged|CheckedChanged|CellClick|Command).*?(?:AddressOf\s+)?(?P<handler>[A-Za-z_][A-Za-z0-9_]*)', re.I)
XAML_EVENT = re.compile(r'\b(?P<event>Click|Loaded|Command|SelectionChanged|TextChanged|Checked|Unchecked)="(?P<handler>[^"]+)"', re.I)
XAML_BINDING = re.compile(r'\{Binding\s+(?P<path>[^,\}]+)', re.I)
COMMAND_BINDING = re.compile(r'Command\s*=\s*"\{Binding\s+(?P<command>[^,\}]+)', re.I)

CONFIG_PATTERNS = [
    ("ConfigurationManager.AppSettings", re.compile(r"ConfigurationManager\.AppSettings(?:\[[^\]]+\])?", re.I)),
    ("ConfigurationManager.ConnectionStrings", re.compile(r"ConfigurationManager\.ConnectionStrings(?:\[[^\]]+\])?", re.I)),
    ("Settings.Default", re.compile(r"\bSettings\.Default\.[A-Za-z_][A-Za-z0-9_]*", re.I)),
    ("My.Settings", re.compile(r"\bMy\.Settings\.[A-Za-z_][A-Za-z0-9_]*", re.I)),
    ("Environment.GetEnvironmentVariable", re.compile(r"Environment\.GetEnvironmentVariable\s*\((?P<args>[^;\n]+)\)", re.I)),
    ("Registry", re.compile(r"\bRegistry(?:Key)?\.", re.I)),
    ("HardcodedPath", re.compile(r'"(?:[A-Za-z]:\\|\\\\|/[^"]+?/)[^"]+"')),
]

DEVICE_KEYWORDS = {
    "PLC": ["plc", "mitsubishi", "mcprotocol", "modbus", "writebit", "readbit"],
    "Camera SDK": ["camera", "grab", "capture", "basler", "hikvision", "cognex"],
    "Vision SDK": ["halcon", "opencv", "emgu", "vision", "aoi", "inspect"],
    "Motion SDK": ["motion", "axis", "servo", "home"],
    "DB Driver": ["sql", "sqlite", "mysql", "oracle", "database"],
    "COM / ActiveX": ["comreference", "activex", "interop"],
    "Serial / Socket": ["serialport", "socket", "tcp", "udp"],
}

RISK_KEYWORDS = {
    "static abuse": ["static "],
    "singleton abuse": ["singleton", "instance"],
    "hardcoded path": ["c:\\", "\\\\", "d:\\"],
    "cross-thread UI risk": ["invoke", "begininvoke", "control.invoke", "dispatcher"],
    "async deadlock risk": [".result", ".wait()"],
    "event leak risk": ["+=", "addhandler"],
    "blocking UI risk": ["thread.sleep", "task.delay", "waitone"],
}

ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "projects",
        "dependencies",
        "classes",
        "methods",
        "source_files",
        "source_blocks",
        "events",
        "event_flows",
        "configuration",
        "external_dependencies",
        "user_workflows",
        "risks",
    ],
    "properties": {
        "projects": {"type": "array", "items": {"type": "object", "required": ["name", "path", "language"]}},
        "dependencies": {"type": "array", "items": {"type": "object", "required": ["type", "project", "target"]}},
        "classes": {"type": "array", "items": {"type": "object", "required": ["name", "kind", "source", "line"]}},
        "methods": {"type": "array", "items": {"type": "object", "required": ["name", "source", "line", "called_by", "calls"]}},
        "source_files": {
            "type": "array",
            "items": {"type": "object", "required": ["path", "line_count", "method_count", "class_count"]},
        },
        "source_blocks": {
            "type": "array",
            "items": {"type": "object", "required": ["kind", "source", "start_line", "end_line"]},
        },
        "events": {"type": "array", "items": {"type": "object", "required": ["source", "line", "event", "handler"]}},
        "event_flows": {"type": "array", "items": {"type": "object", "required": ["entry", "handler", "call_chain", "confidence"]}},
        "configuration": {
            "type": "object",
            "required": ["files", "code_references"],
            "properties": {
                "files": {"type": "array"},
                "code_references": {"type": "array"},
            },
        },
        "external_dependencies": {"type": "array"},
        "user_workflows": {"type": "array"},
        "risks": {"type": "array"},
    },
}

FILE_SCHEMAS: dict[str, dict[str, Any]] = {
    "projects": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["projects"]["items"]},
    "dependencies": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["dependencies"]["items"]},
    "classes": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["classes"]["items"]},
    "methods": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["methods"]["items"]},
    "source_files": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["source_files"]["items"]},
    "source_blocks": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["source_blocks"]["items"]},
    "events": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["events"]["items"]},
    "event_flows": {"type": "array", "items": ANALYSIS_SCHEMA["properties"]["event_flows"]["items"]},
    "configuration": ANALYSIS_SCHEMA["properties"]["configuration"],
    "external_dependencies": {"type": "array"},
    "user_workflows": {"type": "array"},
    "risks": {"type": "array"},
}

TYPE_CHECKS = {
    "array": list,
    "object": dict,
    "string": str,
    "number": (int, float),
    "boolean": bool,
}

def read_text(path: Path) -> str:
    for enc in ["utf-8-sig", "utf-8", "cp950", "big5", "shift_jis"]:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    try:
        return path.read_text(errors="replace")
    except Exception:
        return ""

def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except Exception:
        return path.as_posix()

def ignored(path: Path) -> bool:
    return any(p.lower() in IGNORE for p in path.parts)

def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1

def line_count(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + 1

def find_matching_brace(text: str, open_pos: int) -> int | None:
    if open_pos < 0 or open_pos >= len(text) or text[open_pos] != "{":
        return None
    depth = 0
    in_line_comment = False
    in_block_comment = False
    in_string = False
    string_quote = ""
    escape = False
    i = open_pos
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
        elif in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == string_quote:
                in_string = False
        elif ch == "/" and nxt == "/":
            in_line_comment = True
            i += 1
        elif ch == "/" and nxt == "*":
            in_block_comment = True
            i += 1
        elif ch in {"\"", "'"}:
            in_string = True
            string_quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None

def find_vb_end_line(text: str, start_pos: int, end_pattern: str) -> int:
    match = re.search(end_pattern, text[start_pos:], re.I | re.M)
    if not match:
        return line_count(text)
    return line_no(text, start_pos + match.end())

def load_xml(path: Path):
    try:
        return ET.parse(path).getroot()
    except Exception:
        return None

def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag

def validate_json_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type:
        check = TYPE_CHECKS.get(expected_type)
        if check and not isinstance(value, check):
            return [f"{path}: expected {expected_type}, got {type(value).__name__}"]
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key '{key}'")
        properties = schema.get("properties") or {}
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_json_schema(value[key], child_schema, f"{path}.{key}"))
    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        for i, item in enumerate(value):
            errors.extend(validate_json_schema(item, item_schema, f"{path}[{i}]"))
    return errors

def validate_analysis(data: dict[str, Any]) -> dict[str, Any]:
    checks = {"enterprise_analysis.json": validate_json_schema(data, ANALYSIS_SCHEMA)}
    for name, value in data.items():
        schema = FILE_SCHEMAS.get(name)
        if schema:
            checks[f"{name}.json"] = validate_json_schema(value, schema)
    errors = [err for file_errors in checks.values() for err in file_errors]
    return {
        "valid": not errors,
        "errors": errors,
        "checked_files": sorted(checks.keys()),
    }

def analyze_projects(repo: Path):
    projects = []
    deps = []
    for pf in repo.rglob("*"):
        if ignored(pf) or pf.suffix.lower() not in PROJECT_EXTS:
            continue
        text = read_text(pf)
        root = load_xml(pf)
        lang = "C#" if pf.suffix.lower()==".csproj" else "VB.NET" if pf.suffix.lower()==".vbproj" else "C++/Other"
        project = {
            "name": pf.stem,
            "path": rel(pf, repo),
            "language": lang,
            "target_framework": None,
            "output_type": None,
            "is_gui": False,
            "project_references": [],
            "references": [],
            "nuget_packages": [],
            "responsibility_inference": [],
        }
        if root is not None:
            for e in root.iter():
                tag = strip_ns(e.tag)
                val = (e.text or "").strip()
                if tag in ["TargetFramework", "TargetFrameworkVersion"] and val:
                    project["target_framework"] = val
                if tag == "OutputType" and val:
                    project["output_type"] = val
                if tag == "UseWPF" and val.lower()=="true":
                    project["is_gui"] = True
                if tag == "UseWindowsForms" and val.lower()=="true":
                    project["is_gui"] = True
                if tag == "ProjectReference":
                    inc = e.attrib.get("Include")
                    project["project_references"].append(inc)
                    deps.append({"type":"ProjectReference","project":pf.stem,"target":inc,"source":rel(pf,repo)})
                if tag == "Reference":
                    inc = e.attrib.get("Include")
                    project["references"].append(inc)
                    deps.append({"type":"Reference","project":pf.stem,"target":inc,"source":rel(pf,repo)})
                if tag == "PackageReference":
                    inc = e.attrib.get("Include")
                    ver = e.attrib.get("Version")
                    project["nuget_packages"].append({"id":inc,"version":ver})
                    deps.append({"type":"PackageReference","project":pf.stem,"target":inc,"version":ver,"source":rel(pf,repo)})
        if project["output_type"] and project["output_type"].lower() == "winexe":
            project["is_gui"] = True
        lname = pf.stem.lower()
        if any(x in lname for x in ["ui","view","form","client"]):
            project["responsibility_inference"].append("UI Layer 推測")
        if any(x in lname for x in ["service","business","core"]):
            project["responsibility_inference"].append("Service / Business Layer 推測")
        if any(x in lname for x in ["data","repo","dal"]):
            project["responsibility_inference"].append("Data Access Layer 推測")
        projects.append(project)
    return projects, deps

def analyze_code(repo: Path):
    classes, methods, events, configs, risks = [], [], [], [], []
    source_files = []
    source_blocks = []
    method_names = set()
    method_entries = []
    for path in repo.rglob("*"):
        if ignored(path) or path.suffix.lower() not in CODE_EXTS:
            continue
        text = read_text(path)
        lang = "C#" if path.suffix.lower()==".cs" else "VB.NET" if path.suffix.lower()==".vb" else "XAML"
        file_classes = list(CLASS_RE.finditer(text))
        file_methods = []
        if path.suffix.lower() in [".cs", ".vb"]:
            rx = CS_METHOD if path.suffix.lower()==".cs" else VB_METHOD
            file_methods = list(rx.finditer(text))
        source_files.append({
            "path": rel(path, repo),
            "language": lang,
            "extension": path.suffix.lower(),
            "line_count": line_count(text),
            "method_count": len(file_methods),
            "class_count": len(file_classes),
        })
        for m in file_classes:
            start_line = line_no(text,m.start())
            end_line = line_count(text)
            if path.suffix.lower() in [".cs", ".xaml", ".axaml"]:
                open_pos = text.find("{", m.end())
                close_pos = find_matching_brace(text, open_pos)
                if close_pos is not None:
                    end_line = line_no(text, close_pos)
            elif path.suffix.lower() == ".vb":
                end_line = find_vb_end_line(text, m.end(), r"^\s*End\s+(Class|Interface|Enum|Structure|Module)\b")
            class_entry = {"name":m.group(2), "kind":m.group(1), "language":lang, "source":rel(path,repo), "line":start_line, "end_line":end_line}
            classes.append(class_entry)
            source_blocks.append({
                "kind": "class",
                "name": m.group(2),
                "source": rel(path, repo),
                "language": lang,
                "start_line": start_line,
                "end_line": end_line,
            })
        if path.suffix.lower() in [".cs", ".vb"]:
            for m in file_methods:
                name = m.group("name")
                method_names.add(name)
                start_line = line_no(text,m.start())
                end_line = line_count(text)
                if path.suffix.lower() == ".cs":
                    close_pos = find_matching_brace(text, m.end() - 1)
                    if close_pos is not None:
                        end_line = line_no(text, close_pos)
                else:
                    end_line = find_vb_end_line(text, m.end(), r"^\s*End\s+(Sub|Function)\b")
                entry = {
                    "name": name, "language": lang, "source": rel(path,repo),
                    "line": start_line, "end_line": end_line, "params": m.groupdict().get("params"),
                    "called_by": [], "calls": [], "purpose": "", "side_effects": [], "risks": []
                }
                source_blocks.append({
                    "kind": "method",
                    "name": name,
                    "source": rel(path, repo),
                    "language": lang,
                    "start_line": start_line,
                    "end_line": end_line,
                })
                method_entries.append((entry, text[m.end():m.end()+3000]))
            if path.suffix.lower() == ".cs":
                for s in CS_SWITCH.finditer(text):
                    close_pos = find_matching_brace(text, s.end() - 1)
                    source_blocks.append({
                        "kind": "switch",
                        "name": (s.group("expr") or "switch").strip()[:120],
                        "source": rel(path, repo),
                        "language": lang,
                        "start_line": line_no(text, s.start()),
                        "end_line": line_no(text, close_pos) if close_pos is not None else line_count(text),
                    })
            if path.suffix.lower() == ".vb":
                for s in VB_SELECT_CASE.finditer(text):
                    source_blocks.append({
                        "kind": "switch",
                        "name": (s.group("expr") or "Select Case").strip()[:120],
                        "source": rel(path, repo),
                        "language": lang,
                        "start_line": line_no(text, s.start()),
                        "end_line": find_vb_end_line(text, s.end(), r"^\s*End\s+Select\b"),
                    })
            erx = EVENT_CS if path.suffix.lower()==".cs" else EVENT_VB
            for e in erx.finditer(text):
                events.append({"source":rel(path,repo),"line":line_no(text,e.start()),"control":e.group("control"),"event":e.group("event"),"handler":e.group("handler"),"framework":"WinForms/VB"})
            for name, rx in CONFIG_PATTERNS:
                for c in rx.finditer(text):
                    configs.append({"type":name,"source":rel(path,repo),"line":line_no(text,c.start()),"expression":c.group(0)})
            low = text.lower()
            for risk, words in RISK_KEYWORDS.items():
                for w in words:
                    if w in low:
                        risks.append({"risk_type":risk,"source":rel(path,repo),"evidence":w,"confidence":0.55})
        if path.suffix.lower() in [".xaml", ".axaml"]:
            for e in XAML_EVENT.finditer(text):
                events.append({"source":rel(path,repo),"line":line_no(text,e.start()),"control":"XAML element","event":e.group("event"),"handler":e.group("handler"),"framework":"WPF/Avalonia/MAUI"})
            for b in XAML_BINDING.finditer(text):
                configs.append({"type":"DataBinding","source":rel(path,repo),"line":line_no(text,b.start()),"expression":b.group(0)})
            for c in COMMAND_BINDING.finditer(text):
                events.append({"source":rel(path,repo),"line":line_no(text,c.start()),"control":"CommandBinding","event":"Command","handler":c.group("command"),"framework":"WPF/Avalonia/MAUI"})
    # calls
    for entry, body in method_entries:
        calls = []
        for c in CALL_RE.finditer(body):
            name = c.group("method")
            if name in method_names and name != entry["name"]:
                calls.append(name)
        entry["calls"] = sorted(set(calls))
        text = (entry["name"] + " " + " ".join(calls)).lower()
        if any(x in text for x in ["save","write","insert","update","delete"]):
            entry["side_effects"].append("Persistence or write operation candidate 推測")
        if any(x in text for x in ["camera","plc","serial","socket","motion","grab"]):
            entry["side_effects"].append("External device/API interaction candidate 推測")
        if any(x in text for x in ["invoke","begininvoke","dispatcher"]):
            entry["side_effects"].append("UI thread update candidate 推測")
        if any(x in entry["name"].lower() for x in ["click","load","command","tick"]):
            entry["purpose"] = "Event handler / UI operation entry candidate 推測"
        methods.append(entry)
    for m in methods:
        for callee in m["calls"]:
            for target in methods:
                if target["name"] == callee:
                    target["called_by"].append(m["name"])
    return classes, methods, source_files, source_blocks, events, configs, risks

def analyze_configs(repo: Path):
    files = []
    for p in repo.rglob("*"):
        if ignored(p) or not p.is_file():
            continue
        if p.suffix.lower() in CONFIG_EXTS or p.name.lower() in ["app.config","web.config","settings.settings","appsettings.json","settings.json"]:
            files.append({"path":rel(p,repo), "extension":p.suffix.lower(), "kind":"configuration_candidate"})
    return files

def detect_dependencies(projects, deps, methods, classes):
    external = []
    text = json.dumps({"projects":projects,"deps":deps,"methods":methods,"classes":classes}, ensure_ascii=False).lower()
    for dep_type, words in DEVICE_KEYWORDS.items():
        hits = [w for w in words if w in text]
        if hits:
            external.append({"dependency_type":dep_type,"matched_keywords":hits,"purpose":"External integration candidate 推測","risk":"Initialization, deployment, license, architecture, or runtime failure risk 推測","confidence":min(0.9,0.45+0.1*len(hits))})
    for d in deps:
        external.append({"dependency_type":d.get("type"),"name":d.get("target"),"project":d.get("project"),"purpose":"Referenced dependency","risk":"Version or deployment mismatch risk","confidence":0.75})
    return external

def build_event_flows(events, methods):
    idx = {m["name"]:m for m in methods}
    flows = []
    for e in events:
        h = e.get("handler")
        m = idx.get(h)
        calls = m.get("calls") if m else []
        flows.append({"entry":f"{e.get('control')}.{e.get('event')}","handler":h,"source":e.get("source"),"line":e.get("line"),"call_chain":[h]+calls if h else calls,"side_effects":m.get("side_effects") if m else [],"confidence":0.75 if m else 0.45})
    return flows

def build_workflows(events, methods):
    flows = build_event_flows(events, methods)
    workflows = []
    for f in flows:
        name = (f.get("entry","")+" "+str(f.get("handler",""))).lower()
        if any(x in name for x in ["start","login","save","open","load","stop","reset","command","click"]):
            workflows.append({"workflow":f.get("entry"),"steps":f.get("call_chain"),"success_path":"Handler completes without exception 推測","failure_path":"Exception, validation failure, device/config dependency failure 推測","confidence":f.get("confidence")})
    return workflows

def main(repo_arg: str, out_arg: str):
    repo = Path(repo_arg).resolve()
    out = Path(out_arg).resolve()
    out.mkdir(parents=True, exist_ok=True)
    projects, deps = analyze_projects(repo)
    classes, methods, source_files, source_blocks, events, code_configs, code_risks = analyze_code(repo)
    config_files = analyze_configs(repo)
    event_flows = build_event_flows(events, methods)
    workflows = build_workflows(events, methods)
    external = detect_dependencies(projects, deps, methods, classes)

    # Additional risks
    risks = list(code_risks)
    for c in classes:
        class_methods = [m for m in methods if m["source"] == c["source"]]
        if len(class_methods) >= 40:
            risks.append({"risk_type":"God Object / Giant Form candidate","source":c["source"],"evidence":f"{len(class_methods)} methods in file","confidence":0.7})
    for p in projects:
        if len(p.get("references",[])) + len(p.get("project_references",[])) >= 20:
            risks.append({"risk_type":"High coupling candidate","source":p["path"],"evidence":"many references","confidence":0.65})

    data = {
        "projects":projects,
        "dependencies":deps,
        "classes":classes,
        "methods":methods,
        "source_files":source_files,
        "source_blocks":source_blocks,
        "events":events,
        "event_flows":event_flows,
        "configuration":{"files":config_files,"code_references":code_configs},
        "external_dependencies":external,
        "user_workflows":workflows,
        "risks":risks,
    }
    validation = validate_analysis(data)

    for k,v in data.items():
        (out / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "enterprise_analysis.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "schema_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    if not validation["valid"]:
        print(f"JSON schema validation failed; see {out / 'schema_validation.json'}")
        raise SystemExit(1)
    print(f"Wrote enterprise analysis to {out}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: enterprise_gui_analyzer.py <repo_root> <out_dir>")
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2])
