#!/usr/bin/env python3
"""
Normalize C# / VB.NET WinForms projects into JSON IR.

Usage:
    python normalize_project.py <repo_root> <out_dir>

Outputs:
    forms.json, controls.json, events.json, classes.json, methods.json,
    configs.json, resources.json, diagnostics.json
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

CS_CLASS_RE = re.compile(r'\b(?P<kind>class|interface|enum|struct)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)')
VB_CLASS_RE = re.compile(r'^\s*(?:Public|Private|Friend|Protected|Partial|\s)*\s*(?P<kind>Class|Interface|Enum|Structure|Module)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)', re.I | re.M)

CS_METHOD_RE = re.compile(
    r'^\s*(?:public|private|protected|internal|static|async|virtual|override|sealed|partial|\s)+\s*'
    r'(?:[\w<>\[\],\s\?]+\s+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^;{}]*\)\s*(?:\{|$)',
    re.M,
)
VB_METHOD_RE = re.compile(r'^\s*(?:Public|Private|Friend|Protected|Shared|Overrides|Overridable|Async|\s)*\s*(?:Sub|Function)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(', re.I | re.M)

CS_NAMESPACE_RE = re.compile(r'\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)')
VB_NAMESPACE_RE = re.compile(r'^\s*Namespace\s+([A-Za-z_][A-Za-z0-9_.]*)', re.I | re.M)

CS_CONTROL_DECL_RE = re.compile(r'(?:private|protected|public|internal)\s+(?P<type>[\w\.]+(?:<[^>]+>)?)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*;')
VB_CONTROL_DECL_RE = re.compile(r'(?:Friend|Private|Protected|Public)\s+WithEvents\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+As\s+(?P<type>[\w\.]+)', re.I)

CS_NEW_RE = re.compile(r'this\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*new\s+(?P<type>[\w\.]+)')
VB_NEW_RE = re.compile(r'Me\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*New\s+(?P<type>[\w\.]+)', re.I)

CS_TEXT_RE = re.compile(r'this\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\.Text\s*=\s*"(?P<text>(?:[^"\\]|\\.)*)"')
VB_TEXT_RE = re.compile(r'Me\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\.Text\s*=\s*"(?P<text>[^"]*)"', re.I)

CS_EVENT_RE = re.compile(r'this\.(?P<control>[A-Za-z_][A-Za-z0-9_]*)\.(?P<event>[A-Za-z_][A-Za-z0-9_]*)\s*\+=\s*new\s+[\w\.]+\((?:this\.)?(?P<handler>[A-Za-z_][A-Za-z0-9_]*)\)')
CS_EVENT_RE2 = re.compile(r'this\.(?P<control>[A-Za-z_][A-Za-z0-9_]*)\.(?P<event>[A-Za-z_][A-Za-z0-9_]*)\s*\+=\s*(?:this\.)?(?P<handler>[A-Za-z_][A-Za-z0-9_]*)')
VB_EVENT_RE = re.compile(r'AddHandler\s+Me\.(?P<control>[A-Za-z_][A-Za-z0-9_]*)\.(?P<event>[A-Za-z_][A-Za-z0-9_]*),\s*AddressOf\s+(?P<handler>[A-Za-z_][A-Za-z0-9_]*)', re.I)
VB_HANDLES_RE = re.compile(r'(?:Sub|Function)\s+(?P<handler>[A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\).*?Handles\s+Me\.(?P<event>[A-Za-z_][A-Za-z0-9_]*)', re.I)

CS_PARENT_RE = re.compile(r'this\.(?P<parent>[A-Za-z_][A-Za-z0-9_]*)\.Controls\.Add\(this\.(?P<child>[A-Za-z_][A-Za-z0-9_]*)\)')
VB_PARENT_RE = re.compile(r'Me\.(?P<parent>[A-Za-z_][A-Za-z0-9_]*)\.Controls\.Add\(Me\.(?P<child>[A-Za-z_][A-Za-z0-9_]*)\)', re.I)

CONFIG_EXTS = {".config", ".settings", ".json", ".xml"}


def read_text(path: Path) -> str:
    for enc in ["utf-8-sig", "utf-8", "cp950", "big5", "shift_jis"]:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def language(path: Path) -> str:
    return "C#" if path.suffix.lower() == ".cs" else "VB.NET" if path.suffix.lower() == ".vb" else "Unknown"


def find_namespace(text: str, lang: str) -> str | None:
    rx = CS_NAMESPACE_RE if lang == "C#" else VB_NAMESPACE_RE
    m = rx.search(text)
    return m.group(1) if m else None


def normalize_type(t: str) -> str:
    if "." not in t and t in {"Button","TextBox","Label","Panel","GroupBox","TabControl","TabPage","DataGridView","PictureBox","ComboBox","CheckBox","RadioButton","ListBox","MenuStrip","ToolStrip","SplitContainer","Timer"}:
        return "System.Windows.Forms." + t
    return t


def parse_code_file(path: Path, repo: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text = read_text(path)
    lang = language(path)
    ns = find_namespace(text, lang)
    classes = []
    methods = []

    class_rx = CS_CLASS_RE if lang == "C#" else VB_CLASS_RE
    method_rx = CS_METHOD_RE if lang == "C#" else VB_METHOD_RE

    for m in class_rx.finditer(text):
        classes.append({
            "name": m.group("name"),
            "namespace": ns,
            "language": lang,
            "kind": m.group("kind"),
            "source_file": rel(path, repo),
            "line_range": [line_no(text, m.start()), None],
        })

    for m in method_rx.finditer(text):
        name = m.group("name")
        if name in {"if", "for", "while", "switch", "catch", "using"}:
            continue
        methods.append({
            "name": name,
            "namespace": ns,
            "language": lang,
            "source_file": rel(path, repo),
            "line_range": [line_no(text, m.start()), None],
            "calls": [],
            "notes": [],
        })

    return classes, methods


def parse_designer(path: Path, repo: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    text = read_text(path)
    lang = language(path)
    form_name = path.name.replace(".Designer.cs", "").replace(".Designer.vb", "")
    ns = find_namespace(text, lang)
    logic_file = path.with_name(form_name + (".cs" if lang == "C#" else ".vb"))
    resx_file = path.with_name(form_name + ".resx")

    controls: dict[str, dict[str, Any]] = {}

    for rx in ([CS_CONTROL_DECL_RE, CS_NEW_RE] if lang == "C#" else [VB_CONTROL_DECL_RE, VB_NEW_RE]):
        for m in rx.finditer(text):
            name = m.group("name")
            typ = normalize_type(m.group("type"))
            controls.setdefault(name, {
                "form": form_name,
                "name": name,
                "type": typ,
                "parent": None,
                "text": None,
                "events": {},
                "source_file": rel(path, repo),
            })
            controls[name]["type"] = typ

    for m in (CS_TEXT_RE if lang == "C#" else VB_TEXT_RE).finditer(text):
        if m.group("name") in controls:
            controls[m.group("name")]["text"] = m.group("text")

    parent_rx = CS_PARENT_RE if lang == "C#" else VB_PARENT_RE
    for m in parent_rx.finditer(text):
        parent, child = m.group("parent"), m.group("child")
        controls.setdefault(child, {
            "form": form_name, "name": child, "type": None, "parent": None, "text": None, "events": {}, "source_file": rel(path, repo)
        })
        controls[child]["parent"] = parent

    events = []
    event_matches = []
    if lang == "C#":
        event_matches = list(CS_EVENT_RE.finditer(text)) + list(CS_EVENT_RE2.finditer(text))
    else:
        event_matches = list(VB_EVENT_RE.finditer(text))
    for m in event_matches:
        control, event, handler = m.group("control"), m.group("event"), m.group("handler")
        controls.setdefault(control, {
            "form": form_name, "name": control, "type": None, "parent": None, "text": None, "events": {}, "source_file": rel(path, repo)
        })
        controls[control]["events"][event] = handler
        events.append({
            "form": form_name,
            "control": control,
            "event": event,
            "handler": handler,
            "language": lang,
            "source_file": rel(path, repo),
            "line": line_no(text, m.start()),
        })

    form = {
        "form_name": form_name,
        "namespace": ns,
        "language": lang,
        "logic_file": rel(logic_file, repo) if logic_file.exists() else None,
        "designer_file": rel(path, repo),
        "resx_file": rel(resx_file, repo) if resx_file.exists() else None,
        "controls": sorted(controls.keys()),
        "events": events,
    }
    return form, list(controls.values()), events


def parse_config(path: Path, repo: Path) -> dict[str, Any]:
    item: dict[str, Any] = {"source_file": rel(path, repo), "kind": path.suffix.lower().lstrip("."), "entries": []}
    if path.suffix.lower() in {".config", ".settings", ".xml"}:
        try:
            root = ET.parse(path).getroot()
            for e in root.iter():
                tag = e.tag.split("}", 1)[-1]
                if tag in {"add", "setting", "connectionString"}:
                    item["entries"].append({"tag": tag, "attributes": dict(e.attrib), "text": (e.text or "").strip()})
        except Exception as exc:
            item["error"] = repr(exc)
    return item


def main(repo_arg: str, out_arg: str) -> int:
    repo = Path(repo_arg).resolve()
    out = Path(out_arg).resolve()
    out.mkdir(parents=True, exist_ok=True)

    forms, controls, events, classes, methods, configs, resources, diagnostics = [], [], [], [], [], [], [], []

    ignored_parts = {".git", "bin", "obj", ".vs", "packages", "node_modules"}
    source_files = [p for p in list(repo.rglob("*.cs")) + list(repo.rglob("*.vb")) if not any(part in ignored_parts for part in p.parts)]

    for path in sorted(source_files):
        try:
            if ".Designer." in path.name:
                form, ctrl, evs = parse_designer(path, repo)
                forms.append(form)
                controls.extend(ctrl)
                events.extend(evs)
            cls, meth = parse_code_file(path, repo)
            classes.extend(cls)
            methods.extend(meth)
        except Exception as exc:
            diagnostics.append({"level": "error", "source_file": rel(path, repo), "message": repr(exc)})

    for path in sorted(repo.rglob("*")):
        if not path.is_file() or any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix.lower() in CONFIG_EXTS and path.name not in {"packages.config"}:
            configs.append(parse_config(path, repo))
        if path.suffix.lower() == ".resx":
            resources.append({"source_file": rel(path, repo), "name": path.stem})

    # Deduplicate controls by form/name
    seen = {}
    for c in controls:
        seen[(c.get("form"), c.get("name"))] = c
    controls = list(seen.values())

    outputs = {
        "forms.json": forms,
        "controls.json": controls,
        "events.json": events,
        "classes.json": classes,
        "methods.json": methods,
        "configs.json": configs,
        "resources.json": resources,
    }
    for filename, data in outputs.items():
        (out / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    diag_path = out / "diagnostics.json"
    old = []
    if diag_path.exists():
        try:
            old = json.loads(diag_path.read_text(encoding="utf-8"))
        except Exception:
            old = []
    diag_path.write_text(json.dumps(old + diagnostics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote project normalized IR to {out}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: normalize_project.py <repo_root> <out_dir>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
