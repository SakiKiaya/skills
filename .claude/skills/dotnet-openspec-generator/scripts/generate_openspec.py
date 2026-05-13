#!/usr/bin/env python3
"""
Generate OpenSpec specs from enterprise analysis.

Usage:
    python generate_openspec.py <analysis_dir> <openspec_dir>
"""
from pathlib import Path
import json, sys

def load(p, default):
    p=Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def req(title, body, scenario=""):
    s=f"### Requirement: {title}\n\n{body}\n"
    if scenario:
        s += f"\n#### Scenario: {title}\n\n{scenario}\n"
    return s+"\n"

def main(analysis_dir, openspec_dir):
    a=Path(analysis_dir); o=Path(openspec_dir)
    projects=load(a/"projects.json",[])
    event_flows=load(a/"event_flows.json",[])
    methods=load(a/"methods.json",[])
    risks=load(a/"risks.json",[])
    config=load(a/"configuration.json",{"files":[],"code_references":[]})
    external=load(a/"external_dependencies.json",[])
    workflows=load(a/"user_workflows.json",[])
    write(o/"project.md", "# Enterprise GUI Project OpenSpec\n\nThis OpenSpec describes current-state GUI architecture and behavior for AI Agent consumption.\n")
    txt="# Solution Architecture Spec\n\n## Requirements\n\n"
    for p in projects:
        txt += req(f"Project {p.get('name')} responsibility", f"The system SHALL document project `{p.get('name')}` as `{p.get('language')}` with responsibility candidates `{p.get('responsibility_inference')}`.")
    write(o/"specs/solution-architecture/spec.md", txt)
    txt="# Event Flow Spec\n\n## Requirements\n\n"
    for f in event_flows:
        txt += req(f"{f.get('entry')} invokes {f.get('handler')}", f"The system SHALL route `{f.get('entry')}` to `{f.get('handler')}`.", f"- GIVEN user triggers `{f.get('entry')}`\n- THEN handler `{f.get('handler')}` SHALL execute\n- AND call chain candidate SHALL be `{f.get('call_chain')}`")
    write(o/"specs/event-flow/spec.md", txt)
    txt="# Method Flow Spec\n\n## Requirements\n\n"
    for m in methods[:500]:
        txt += req(f"Method {m.get('name')} impact", f"The method `{m.get('name')}` SHALL be considered with callers `{m.get('called_by')}`, callees `{m.get('calls')}`, and side effects `{m.get('side_effects')}`.")
    write(o/"specs/method-flow/spec.md", txt)
    txt="# Configuration Spec\n\n## Requirements\n\n"
    txt += req("Configuration inventory", f"The system SHALL maintain configuration sources `{config.get('files')}` and in-code usage `{config.get('code_references')}`.")
    write(o/"specs/configuration/spec.md", txt)
    txt="# External Dependencies Spec\n\n## Requirements\n\n"
    for e in external:
        txt += req(f"External dependency {e.get('dependency_type') or e.get('name')}", f"The system SHALL review dependency `{e}` for initialization and deployment risk.")
    write(o/"specs/external-dependencies/spec.md", txt)
    txt="# User Workflow Spec\n\n## Requirements\n\n"
    for w in workflows:
        txt += req(f"Workflow {w.get('workflow')}", f"The system SHALL document workflow `{w.get('workflow')}` with steps `{w.get('steps')}`.", f"- GIVEN the user performs `{w.get('workflow')}`\n- THEN the expected success path is `{w.get('success_path')}`\n- AND failure path is `{w.get('failure_path')}`")
    write(o/"specs/user-workflow/spec.md", txt)
    txt="# Risk Analysis Spec\n\n## Requirements\n\n"
    for r in risks:
        txt += req(f"Review risk {r.get('risk_type')}", f"The system MUST review `{r.get('risk_type')}` in `{r.get('source')}` with evidence `{r.get('evidence')}`.")
    write(o/"specs/risk-analysis/spec.md", txt)
    print(f"Wrote OpenSpec to {o}")

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: generate_openspec.py <analysis_dir> <openspec_dir>")
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2])
