#!/usr/bin/env python3
"""
Generate enterprise GUI handover docs v0.8-problem2.

Focus:
- 05_method_flow.md now uses method_purposes.json when available.
- No blank method purpose sections.
- Method explanations include purpose, evidence, triggers, responsibility, side effects, and maintenance notes.

Usage:
    python generate_enterprise_docs.py <analysis_dir> <docs_dir>
"""
from pathlib import Path
import json
import sys

def load(p, default):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def esc(v):
    s = "N/A" if v in [None, ""] else str(v).replace("\n", " ").replace("|", "\\|")
    return s[:1000] + "..." if len(s) > 1000 else s

def bullet(items):
    if not items:
        return "- N/A\n"
    if isinstance(items, str):
        items = [items]
    return "".join(f"- {esc(x)}\n" for x in items)

def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(out) + "\n"

def nid(x):
    return "".join(c if c.isalnum() else "_" for c in str(x or "Unknown"))

def project_graph(projects, deps):
    lines = ["```mermaid", "graph TD"]
    for p in projects:
        lines.append(f'  P_{nid(p["name"])}["{p["name"]}<br/>{p.get("language","")}"]')
    for d in deps:
        if d.get("type") == "ProjectReference":
            lines.append(f'  P_{nid(d.get("project"))} --> P_{nid(Path(str(d.get("target",""))).stem)}')
    lines.append("```")
    return "\n".join(lines)

def architecture_graph(projects, deps, external):
    lines = ["```mermaid", "graph TD"]
    lines += [
        '  User["User / Operator"]',
        '  UI["GUI Layer<br/>Forms / Windows / UserControls"]',
        '  Logic["Application / Service Layer"]',
        '  Data["Data / Repository Layer"]',
        '  Device["External Device / SDK Layer"]',
        '  Config["Configuration"]',
        '  User --> UI',
        '  UI --> Logic',
        '  Logic --> Data',
        '  Logic --> Device',
        '  UI --> Config',
        '  Logic --> Config',
    ]
    for p in projects:
        node = f'P_{nid(p["name"])}'
        if p.get("is_gui"):
            lines.append(f'  UI --> {node}["{p["name"]}"]')
        elif any(x in str(p.get("responsibility_inference","")).lower() for x in ["data"]):
            lines.append(f'  Data --> {node}["{p["name"]}"]')
        else:
            lines.append(f'  Logic --> {node}["{p["name"]}"]')
    for e in external[:12]:
        node = f'E_{nid(e.get("dependency_type") or e.get("name"))}'
        lines.append(f'  Device -.-> {node}["{esc(e.get("dependency_type") or e.get("name"))}"]')
    lines.append("```")
    return "\n".join(lines)

def classify_call(call_name):
    name = str(call_name or "").lower()
    if any(k in name for k in ["plc", "camera", "grab", "capture", "motion", "serial", "socket", "modbus", "halcon", "opencv", "emgu"]):
        return "Device"
    if any(k in name for k in ["sql", "db", "database", "save", "load", "read", "write", "file", "config"]):
        return "Storage"
    if any(k in name for k in ["update", "refresh", "display", "show", "settext", "view"]):
        return "UI"
    return "Logic"

def simplified_event_sequence(flow):
    entry = flow.get("entry") or "UI Event"
    handler = flow.get("handler") or "Handler"
    chain = flow.get("call_chain") or []
    internal_calls = [c for c in chain if c and c != handler]

    lines = [
        "```mermaid",
        "sequenceDiagram",
        "  participant User",
        "  participant UI",
        "  participant Handler",
        "  participant Logic",
        "  participant Device",
        "  participant Storage",
        f"  User->>UI: {esc(entry)}",
        f"  UI->>Handler: {esc(handler)}()",
    ]
    if not internal_calls:
        lines.append("  Handler-->>UI: complete")
    else:
        for call in internal_calls[:30]:
            target = classify_call(call)
            if target == "UI":
                lines.append(f"  Handler->>UI: {esc(call)}()")
            elif target == "Device":
                lines.append(f"  Handler->>Device: {esc(call)}()")
                lines.append("  Device-->>Handler: result/status")
            elif target == "Storage":
                lines.append(f"  Handler->>Storage: {esc(call)}()")
                lines.append("  Storage-->>Handler: data/result")
            else:
                lines.append(f"  Handler->>Logic: {esc(call)}()")
                lines.append("  Logic-->>Handler: result")
        if len(internal_calls) > 30:
            lines.append(f"  Note over Handler,Logic: {len(internal_calls) - 30} additional calls omitted; see method chain table")
        lines.append("  Handler-->>UI: update status/result")
    side_effects = flow.get("side_effects") or []
    if side_effects:
        lines.append(f"  Note over Handler,Device: Side effects: {esc(side_effects)}")
    lines.append("```")
    return "\n".join(lines)

def event_flow_graph(flow):
    entry = flow.get("entry") or "UI Event"
    handler = flow.get("handler") or "Handler"
    chain = [c for c in (flow.get("call_chain") or []) if c]
    lines = ["```mermaid", "flowchart TD"]
    lines.append(f'  User["User"] --> UI["{esc(entry)}"]')
    lines.append(f'  UI --> Handler["{esc(handler)}"]')
    prev = "Handler"
    for i, call in enumerate([c for c in chain if c != handler][:40]):
        node = f"C{i}"
        lines.append(f'  {prev} --> {node}["{esc(call)}"]')
        prev = node
    if len(chain) > 40:
        lines.append(f'  {prev} --> More["... {len(chain)-40} more calls"]')
    lines.append("```")
    return "\n".join(lines)

def workflow_graph(workflows):
    lines = ["```mermaid", "flowchart TD"]
    if not workflows:
        lines.append('  Start --> Unknown["No workflow candidates detected"]')
    else:
        lines.append("  Start((Start))")
        for i, w in enumerate(workflows[:30]):
            node = f"W{i}"
            lines.append(f'  {node}["{esc(w.get("workflow"))}"]')
            lines.append(f"  Start --> {node}")
    lines.append("```")
    return "\n".join(lines)

def method_section(purpose):
    name = purpose.get("method")
    lines = [f"## {esc(name)}", ""]
    lines.append("**用途：**")
    lines.append(esc(purpose.get("inferred_purpose") or "用途需人工確認。推測"))
    lines.append("")
    lines.append("**推測依據：**")
    lines.append(bullet(purpose.get("evidence")))
    lines.append("**觸發來源：**")
    triggers = purpose.get("triggers") or []
    trigger_text = [t.get("trigger") if isinstance(t, dict) else str(t) for t in triggers]
    if not trigger_text:
        trigger_text = ["未偵測到明確 GUI 事件觸發來源，可能由內部方法、初始化流程或外部框架呼叫。推測"]
    lines.append(bullet(trigger_text))
    lines.append("**主要責任：**")
    lines.append(bullet(purpose.get("main_responsibility")))
    lines.append("**副作用：**")
    lines.append(bullet(purpose.get("side_effects")))
    lines.append("**維護注意事項：**")
    lines.append(bullet(purpose.get("maintenance_notes")))
    lines.append("**分析來源：**")
    src = purpose.get("analysis_inputs") or {}
    lines.append(table(["Item", "Value"], [
        ["Source", purpose.get("source")],
        ["Line", purpose.get("line")],
        ["Class/File", purpose.get("class_or_file")],
        ["Called By", purpose.get("called_by")],
        ["Calls", purpose.get("calls")],
        ["存取 Config", src.get("has_config_candidate")],
        ["存取 DB", src.get("has_db_candidate")],
        ["存取 File", src.get("has_file_candidate")],
        ["存取 Device", src.get("has_device_candidate")],
        ["更新 UI", src.get("has_ui_update_candidate")],
        ["Async/Thread/Timer", src.get("has_async_thread_timer_candidate")],
        ["產生新物件", src.get("has_object_creation_candidate")],
        ["Confidence", purpose.get("confidence")],
    ]))
    return "\n".join(lines) + "\n"

def main(analysis_dir, docs_dir):
    a = Path(analysis_dir)
    d = Path(docs_dir)
    d.mkdir(parents=True, exist_ok=True)

    projects = load(a / "projects.json", [])
    deps = load(a / "dependencies.json", [])
    methods = load(a / "methods.json", [])
    method_purposes = load(a / "method_purposes.json", [])
    event_flows = load(a / "event_flows.json", [])
    config = load(a / "configuration.json", {"files": [], "code_references": []})
    external = load(a / "external_dependencies.json", [])
    workflows = load(a / "user_workflows.json", [])
    risks = load(a / "risks.json", [])

    (d / "README.md").write_text("""# Enterprise GUI Project Handover Documentation

## Documents

1. [Solution Structure](01_solution_structure.md)
2. [Architecture](02_architecture.md)
3. [Project Dependencies](03_project_dependencies.md)
4. [Event Flow](04_event_flow.md)
5. [Method Flow](05_method_flow.md)
6. [Configuration](06_configuration.md)
7. [User Workflow](07_user_workflow.md)
8. [External Dependencies](08_external_dependencies.md)
9. [Risk Analysis](09_risk_analysis.md)
""", encoding="utf-8")

    doc = "# 01 Solution Structure\n\n## Table of Contents\n\n- [Solution Overview](#solution-overview)\n- [Project Dependency Graph](#project-dependency-graph)\n- [Module Responsibility Table](#module-responsibility-table)\n\n## Solution Overview\n\n"
    doc += table(["Project", "Language", "Target", "GUI", "Responsibility Inference"], [[p.get("name"), p.get("language"), p.get("target_framework"), p.get("is_gui"), p.get("responsibility_inference")] for p in projects])
    doc += "\n## Project Dependency Graph\n\n" + project_graph(projects, deps) + "\n\n## Module Responsibility Table\n\n"
    doc += table(["Module", "Purpose / Work Allocation", "Reason"], [[p.get("name"), p.get("responsibility_inference") or "需人工確認", "Based on project metadata/name/references 推測"] for p in projects])
    (d / "01_solution_structure.md").write_text(doc, encoding="utf-8")

    doc = "# 02 Architecture\n\n## Table of Contents\n\n- [Architecture Overview](#architecture-overview)\n- [Block Architecture Diagram](#block-architecture-diagram)\n- [Layer Explanation](#layer-explanation)\n- [Data and Control Flow](#data-and-control-flow)\n\n## Architecture Overview\n\nThis document explains how GUI, logic, configuration, external dependencies, and data/device integrations interact.\n\n## Block Architecture Diagram\n\n"
    doc += architecture_graph(projects, deps, external)
    doc += "\n\n## Layer Explanation\n\n"
    doc += table(["Layer", "Responsibility", "Typical Risk"], [
        ["GUI Layer", "Forms / Windows / UserControls, user events, UI updates", "UI and business logic coupling"],
        ["Application / Service Layer", "Business workflow, command orchestration, inspection logic", "God service, hard-to-test logic"],
        ["Data / Repository Layer", "Database, file persistence, result storage", "Connection/config failure"],
        ["External Device / SDK Layer", "Camera, PLC, motion, SDK, native DLL", "Deployment/runtime/device timeout risk"],
        ["Configuration", "App.config, Settings, hardcoded paths, environment/registry", "Hardcoded or environment-specific behavior"],
    ])
    doc += "\n## Data and Control Flow\n\n- User actions enter through GUI event handlers.\n- Event handlers call service/application methods.\n- Service methods may call repository, device SDK, or configuration sources.\n- External side effects must be reviewed for timeout, exception handling, and UI feedback.\n"
    (d / "02_architecture.md").write_text(doc, encoding="utf-8")

    doc = "# 03 Project Dependencies\n\n## Project / Assembly Dependency Graph\n\n" + project_graph(projects, deps)
    doc += "\n\n## Dependency Table\n\n" + table(["Project", "Type", "Target", "Source"], [[x.get("project"), x.get("type"), x.get("target"), x.get("source")] for x in deps])
    (d / "03_project_dependencies.md").write_text(doc, encoding="utf-8")

    doc = "# 04 Event Flow\n\n## Diagram Style Note\n\nv0.8 uses simplified fixed-participant sequence diagrams to avoid horizontal expansion.\n\n## Event Flow Overview\n\n"
    doc += table(["Entry", "Handler", "Call Chain", "Side Effects", "Source"], [[f.get("entry"), f.get("handler"), " -> ".join(f.get("call_chain") or []), f.get("side_effects"), f.get("source")] for f in event_flows])
    for f in event_flows[:80]:
        doc += f"\n## {esc(f.get('handler'))}\n\n"
        doc += table(["Item", "Value"], [
            ["Entry", f.get("entry")],
            ["Call Chain", " -> ".join(f.get("call_chain") or [])],
            ["Side Effects", f.get("side_effects")],
            ["Confidence", f.get("confidence")],
        ])
        doc += "\n### Simplified Sequence Diagram\n\n" + simplified_event_sequence(f) + "\n"
        doc += "\n### Event Flow Graph\n\n" + event_flow_graph(f) + "\n"
    (d / "04_event_flow.md").write_text(doc, encoding="utf-8")

    doc = "# 05 Method Flow\n\n"
    doc += "本文件提供方法用途推測、觸發來源、主要責任、副作用與維護注意事項。推測內容需由工程師確認。\n\n"
    doc += "## Method Overview Table\n\n"
    if method_purposes:
        doc += table(["Method", "Purpose", "Triggers", "Side Effects", "Maintenance Notes", "Source"], [
            [
                p.get("method"),
                p.get("inferred_purpose"),
                [t.get("trigger") for t in (p.get("triggers") or []) if isinstance(t, dict)],
                p.get("side_effects"),
                p.get("maintenance_notes"),
                p.get("source"),
            ] for p in method_purposes
        ])
        doc += "\n## Method Details\n\n"
        for p in method_purposes:
            doc += method_section(p) + "\n"
    else:
        doc += "> method_purposes.json not found. Run dotnet-method-purpose-analyzer first.\n\n"
        doc += table(["Method", "Called By", "Calls", "Purpose", "Side Effects", "Risks", "Source"], [[m.get("name"), m.get("called_by"), m.get("calls"), m.get("purpose") or "用途需人工確認。推測", m.get("side_effects"), m.get("risks"), m.get("source")] for m in methods])
    (d / "05_method_flow.md").write_text(doc, encoding="utf-8")

    doc = "# 06 Configuration\n\n## Configuration Sources\n\n"
    doc += table(["Path", "Kind"], [[f.get("path"), f.get("kind")] for f in config.get("files", [])])
    doc += "\n## In-code Configuration Usage\n\n" + table(["Type", "Source", "Line", "Expression"], [[r.get("type"), r.get("source"), r.get("line"), r.get("expression")] for r in config.get("code_references", [])])
    doc += "\n## Risk Notes\n\n- Hardcoded paths and environment-specific settings require deployment review.\n- Generated Skill files are intentionally ignored.\n"
    (d / "06_configuration.md").write_text(doc, encoding="utf-8")

    doc = "# 07 User Workflow\n\n## Workflow Graph\n\n" + workflow_graph(workflows)
    doc += "\n\n## Workflow Candidates\n\n" + table(["Workflow", "Steps", "Success Path", "Failure Path", "Confidence"], [[w.get("workflow"), " -> ".join(w.get("steps") or []), w.get("success_path"), w.get("failure_path"), w.get("confidence")] for w in workflows])
    (d / "07_user_workflow.md").write_text(doc, encoding="utf-8")

    doc = "# 08 External Dependencies\n\n## External Dependency Overview\n\n"
    doc += table(["Type/Name", "Matched Keywords", "Project", "Purpose", "Failure Risk", "Confidence"], [[e.get("dependency_type") or e.get("name"), e.get("matched_keywords"), e.get("project"), e.get("purpose"), e.get("risk"), e.get("confidence")] for e in external])
    doc += "\n## Review Guidance\n\n- Verify SDK runtime installation.\n- Verify x86/x64 compatibility.\n- Verify license/runtime availability.\n- Verify initialization and failure handling.\n"
    (d / "08_external_dependencies.md").write_text(doc, encoding="utf-8")

    doc = "# 09 Risk Analysis\n\n## Risk Summary\n\n"
    doc += table(["Risk Type", "Source", "Evidence", "Confidence"], [[r.get("risk_type"), r.get("source"), r.get("evidence"), r.get("confidence")] for r in risks])
    doc += "\n## Required Review Areas\n\n- God Object / Giant Form\n- UI and logic coupling\n- static / Singleton abuse\n- hardcoded configuration\n- cross-thread UI update\n- event leak\n- circular dependency\n- async deadlock\n"
    (d / "09_risk_analysis.md").write_text(doc, encoding="utf-8")
    print(f"Wrote enterprise docs to {d}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_enterprise_docs.py <analysis_dir> <docs_dir>")
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2])
