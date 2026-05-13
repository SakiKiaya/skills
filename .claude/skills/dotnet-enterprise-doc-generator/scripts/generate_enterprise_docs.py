#!/usr/bin/env python3
"""
Generate enterprise GUI handover docs v0.7

Usage:
    python generate_enterprise_docs.py <analysis_dir> <docs_dir>
"""
from pathlib import Path
import json, sys

def load(path, default):
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return default

def esc(v):
    s = "N/A" if v in [None,""] else str(v).replace("\n"," ").replace("|","\\|")
    return s[:1000] + "..." if len(s)>1000 else s

def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"]*len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(x) for x in r) + " |")
    return "\n".join(out) + "\n"

def nid(x):
    return "".join(c if c.isalnum() else "_" for c in str(x or "Unknown"))

def project_graph(projects, deps):
    lines=["```mermaid","graph TD"]
    for p in projects:
        lines.append(f'  P_{nid(p["name"])}["{p["name"]}<br/>{p.get("language","")}"]')
    for d in deps:
        if d.get("type")=="ProjectReference":
            lines.append(f'  P_{nid(d.get("project"))} --> P_{nid(Path(str(d.get("target",""))).stem)}')
    lines.append("```")
    return "\n".join(lines)

def architecture_graph(projects, deps, external):
    lines=["```mermaid","graph TD"]
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
        node=f'P_{nid(p["name"])}'
        if p.get("is_gui"):
            lines.append(f'  UI --> {node}["{p["name"]}"]')
        elif any(x in str(p.get("responsibility_inference","")).lower() for x in ["data"]):
            lines.append(f'  Data --> {node}["{p["name"]}"]')
        else:
            lines.append(f'  Logic --> {node}["{p["name"]}"]')
    for e in external[:12]:
        node=f'E_{nid(e.get("dependency_type") or e.get("name"))}'
        lines.append(f'  Device -.-> {node}["{esc(e.get("dependency_type") or e.get("name"))}"]')
    lines.append("```")
    return "\n".join(lines)

def event_sequence(flow):
    chain = flow.get("call_chain") or []
    lines=["```mermaid","sequenceDiagram","  participant User"]
    if chain:
        lines.append(f'  User->>GUI: {esc(flow.get("entry"))}')
        prev="GUI"
        for i, c in enumerate(chain):
            cur=f"M{i}"
            lines.append(f'  participant {cur} as {esc(c)}')
            lines.append(f'  {prev}->>{cur}: call')
            prev=cur
    lines.append("```")
    return "\n".join(lines)

def workflow_graph(workflows):
    lines=["```mermaid","flowchart TD"]
    if not workflows:
        lines.append('  Start --> Unknown["No workflow candidates detected"]')
    else:
        lines.append("  Start((Start))")
        for i,w in enumerate(workflows[:30]):
            node=f"W{i}"
            lines.append(f'  {node}["{esc(w.get("workflow"))}"]')
            lines.append(f"  Start --> {node}")
    lines.append("```")
    return "\n".join(lines)

def main(analysis_dir, docs_dir):
    a=Path(analysis_dir); d=Path(docs_dir); d.mkdir(parents=True, exist_ok=True)
    projects=load(a/"projects.json",[])
    deps=load(a/"dependencies.json",[])
    methods=load(a/"methods.json",[])
    events=load(a/"events.json",[])
    event_flows=load(a/"event_flows.json",[])
    config=load(a/"configuration.json",{"files":[],"code_references":[]})
    external=load(a/"external_dependencies.json",[])
    workflows=load(a/"user_workflows.json",[])
    risks=load(a/"risks.json",[])

    (d/"README.md").write_text("""# Enterprise GUI Project Handover Documentation

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

    doc="# 01 Solution Structure\n\n## Table of Contents\n\n- [Solution Overview](#solution-overview)\n- [Project Dependency Graph](#project-dependency-graph)\n- [Module Responsibility Table](#module-responsibility-table)\n\n## Solution Overview\n\n"
    doc += table(["Project","Language","Target","GUI","Responsibility Inference"], [[p.get("name"),p.get("language"),p.get("target_framework"),p.get("is_gui"),p.get("responsibility_inference")] for p in projects])
    doc += "\n## Project Dependency Graph\n\n" + project_graph(projects,deps) + "\n\n## Module Responsibility Table\n\n"
    doc += table(["Module","Purpose / Work Allocation","Reason"], [[p.get("name"),p.get("responsibility_inference") or "需人工確認", "Based on project metadata/name/references 推測"] for p in projects])
    (d/"01_solution_structure.md").write_text(doc, encoding="utf-8")

    doc="# 02 Architecture\n\n## Table of Contents\n\n- [Architecture Overview](#architecture-overview)\n- [Block Architecture Diagram](#block-architecture-diagram)\n- [Layer Explanation](#layer-explanation)\n- [Data and Control Flow](#data-and-control-flow)\n\n## Architecture Overview\n\nThis document explains how GUI, logic, configuration, external dependencies, and data/device integrations interact.\n\n## Block Architecture Diagram\n\n"
    doc += architecture_graph(projects,deps,external)
    doc += "\n\n## Layer Explanation\n\n"
    doc += table(["Layer","Responsibility","Typical Risk"], [
        ["GUI Layer","Forms / Windows / UserControls, user events, UI updates","UI and business logic coupling"],
        ["Application / Service Layer","Business workflow, command orchestration, inspection logic","God service, hard-to-test logic"],
        ["Data / Repository Layer","Database, file persistence, result storage","Connection/config failure"],
        ["External Device / SDK Layer","Camera, PLC, motion, SDK, native DLL","Deployment/runtime/device timeout risk"],
        ["Configuration","App.config, Settings, hardcoded paths, environment/registry","Hardcoded or environment-specific behavior"],
    ])
    doc += "\n## Data and Control Flow\n\n- User actions enter through GUI event handlers.\n- Event handlers call service/application methods.\n- Service methods may call repository, device SDK, or configuration sources.\n- External side effects must be reviewed for timeout, exception handling, and UI feedback.\n"
    (d/"02_architecture.md").write_text(doc, encoding="utf-8")

    doc="# 03 Project Dependencies\n\n## Project / Assembly Dependency Graph\n\n" + project_graph(projects,deps)
    doc += "\n\n## Dependency Table\n\n" + table(["Project","Type","Target","Source"], [[x.get("project"),x.get("type"),x.get("target"),x.get("source")] for x in deps])
    (d/"03_project_dependencies.md").write_text(doc, encoding="utf-8")

    doc="# 04 Event Flow\n\n## Event Flow Overview\n\n"
    doc += table(["Entry","Handler","Call Chain","Side Effects","Source"], [[f.get("entry"),f.get("handler")," -> ".join(f.get("call_chain") or []),f.get("side_effects"),f.get("source")] for f in event_flows])
    for f in event_flows[:50]:
        doc += f"\n## {esc(f.get('handler'))}\n\n"
        doc += table(["Item","Value"], [["Entry",f.get("entry")],["Call Chain"," -> ".join(f.get("call_chain") or [])],["Side Effects",f.get("side_effects")],["Confidence",f.get("confidence")]])
        doc += "\n" + event_sequence(f) + "\n"
    (d/"04_event_flow.md").write_text(doc, encoding="utf-8")

    doc="# 05 Method Flow\n\n## Method Chain Table\n\n"
    doc += table(["Method","Called By","Calls","Purpose","Side Effects","Risks","Source"], [[m.get("name"),m.get("called_by"),m.get("calls"),m.get("purpose"),m.get("side_effects"),m.get("risks"),m.get("source")] for m in methods])
    (d/"05_method_flow.md").write_text(doc, encoding="utf-8")

    doc="# 06 Configuration\n\n## Configuration Sources\n\n"
    doc += table(["Path","Kind"], [[f.get("path"),f.get("kind")] for f in config.get("files",[])])
    doc += "\n## In-code Configuration Usage\n\n" + table(["Type","Source","Line","Expression"], [[r.get("type"),r.get("source"),r.get("line"),r.get("expression")] for r in config.get("code_references",[])])
    doc += "\n## Risk Notes\n\n- Hardcoded paths and environment-specific settings require deployment review.\n- Generated Skill files are intentionally ignored.\n"
    (d/"06_configuration.md").write_text(doc, encoding="utf-8")

    doc="# 07 User Workflow\n\n## Workflow Graph\n\n" + workflow_graph(workflows)
    doc += "\n\n## Workflow Candidates\n\n" + table(["Workflow","Steps","Success Path","Failure Path","Confidence"], [[w.get("workflow")," -> ".join(w.get("steps") or []),w.get("success_path"),w.get("failure_path"),w.get("confidence")] for w in workflows])
    (d/"07_user_workflow.md").write_text(doc, encoding="utf-8")

    doc="# 08 External Dependencies\n\n## External Dependency Overview\n\n"
    doc += table(["Type/Name","Matched Keywords","Project","Purpose","Failure Risk","Confidence"], [[e.get("dependency_type") or e.get("name"),e.get("matched_keywords"),e.get("project"),e.get("purpose"),e.get("risk"),e.get("confidence")] for e in external])
    doc += "\n## Review Guidance\n\n- Verify SDK runtime installation.\n- Verify x86/x64 compatibility.\n- Verify license/runtime availability.\n- Verify initialization and failure handling.\n"
    (d/"08_external_dependencies.md").write_text(doc, encoding="utf-8")

    doc="# 09 Risk Analysis\n\n## Risk Summary\n\n"
    doc += table(["Risk Type","Source","Evidence","Confidence"], [[r.get("risk_type"),r.get("source"),r.get("evidence"),r.get("confidence")] for r in risks])
    doc += "\n## Required Review Areas\n\n- God Object / Giant Form\n- UI and logic coupling\n- static / Singleton abuse\n- hardcoded configuration\n- cross-thread UI update\n- event leak\n- circular dependency\n- async deadlock\n"
    (d/"09_risk_analysis.md").write_text(doc, encoding="utf-8")
    print(f"Wrote enterprise docs to {d}")

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: generate_enterprise_docs.py <analysis_dir> <docs_dir>")
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2])
