#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any

def load(b:Path,n:str,d:Any):
    p=b/n
    if p.exists():
        try: return json.loads(p.read_text(encoding='utf-8'))
        except Exception: return d
    return d

def write(p:Path,t:str):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(t,encoding='utf-8')
def esc(v): return 'N/A' if v in (None,'') else str(v)
def req(title, body, scenario=None):
    s=f'### Requirement: {title}\n\n{body.strip()}\n'
    if scenario: s+=f'\n#### Scenario: {title}\n\n{scenario.strip()}\n'
    return s+'\n'

def main(norm_arg, openspec_arg):
    norm=Path(norm_arg); out=Path(openspec_arg); (out/'changes').mkdir(parents=True,exist_ok=True)
    solution=load(norm,'solution.json',{'solution':{}}).get('solution',{})
    projects=load(norm,'projects.json',[]); deps=load(norm,'dependencies.json',[])
    forms=load(norm,'forms.json',[]); controls=load(norm,'controls.json',[])
    flows=load(norm,'event_flows.json',[]); methods=load(norm,'methods.json',[]); graph=load(norm,'call_graph.json',[]); configs=load(norm,'configs.json',[])
    write(out/'project.md',f'''# OpenSpec Project

## Purpose

This OpenSpec workspace describes current .NET / WinForms behavior for AI Agent consumption.

## Source

- Solution: `{esc(solution.get('name'))}`
- Solution Path: `{esc(solution.get('path'))}`

## Specs

- `specs/solution-architecture/spec.md`
- `specs/ui-forms/spec.md`
- `specs/event-flow/spec.md`
- `specs/business-logic/spec.md`
- `specs/configuration/spec.md`
- `specs/dependencies/spec.md`

## AI Agent Rules

- Treat `openspec/specs/` as current-state behavior only when backed by source references.
- Treat assumptions as non-authoritative.
- Do not modify behavior without creating a change proposal under `openspec/changes/`.
''')
    sol='# Solution Architecture Specification\n\n## Requirements\n\n'
    sol+=req('Solution project inventory',f'The system SHALL contain {len(projects)} detected project(s).','\n'.join([f"- THEN project `{esc(p.get('name'))}` SHALL be documented with language `{esc(p.get('language'))}` and target `{esc(p.get('target_framework'))}`" for p in projects]) or '- THEN no projects were detected')
    sol+='\n## Project Inventory\n\n'+'\n'.join([f"- `{esc(p.get('name'))}`: `{esc(p.get('language'))}`, `{esc(p.get('project_file'))}`, WinForms=`{esc(p.get('is_winforms'))}`" for p in projects])+'\n'
    write(out/'specs/solution-architecture/spec.md',sol)
    ui='# UI Forms Specification\n\n## Requirements\n\n'
    for f in forms:
        fname=esc(f.get('form_name'))
        ui+=req(f'{fname} form structure',f'The system SHALL define the `{fname}` WinForms screen based on `{esc(f.get("designer_file"))}`.',f'- GIVEN the application loads `{fname}`\n- THEN the form SHALL expose detected controls and event bindings.')
    ui+='\n## Detected Controls\n\n'
    for c in controls:
        ui+=f"- `{esc(c.get('form'))}.{esc(c.get('name'))}` SHALL exist as `{esc(c.get('type'))}`"
        if c.get('parent'): ui+=f" under `{esc(c.get('parent'))}`"
        ui+='.'+'\n'
    write(out/'specs/ui-forms/spec.md',ui)
    ev='# Event Flow Specification\n\n## Requirements\n\n'
    for fl in flows:
        tr=fl.get('trigger') or {}
        ev+=req(f"{esc(fl.get('handler'))} handles {esc(tr.get('control'))}.{esc(tr.get('event'))}",f"The system SHALL invoke `{esc(fl.get('handler'))}` when `{esc(tr.get('control'))}.{esc(tr.get('event'))}` is triggered.",f"- GIVEN form `{esc(fl.get('form'))}` is active\n- WHEN `{esc(tr.get('control'))}.{esc(tr.get('event'))}` occurs\n- THEN the system SHALL execute handler `{esc(fl.get('handler'))}`\n- AND the handler SHALL follow detected call candidates: `{', '.join(fl.get('called_methods') or []) or 'N/A'}`")
    if not flows: ev+='No confirmed event flows were detected.\n'
    write(out/'specs/event-flow/spec.md',ev)
    logic='# Business Logic Specification\n\n## Requirements\n\n'
    logic+=req('Method inventory',f'The system SHALL expose {len(methods)} detected method(s) for AI Agent navigation and impact analysis.','- WHEN an AI Agent modifies code\n- THEN it MUST review related method inventory and call graph entries before making changes.')
    logic+='\n## Event Handlers\n\n'
    for m in methods:
        if m.get('is_event_handler'): logic+=f"- `{esc(m.get('name'))}` SHALL act as an event handler for `{esc(m.get('event_sources'))}` from `{esc(m.get('source_file'))}`.\n"
    logic+='\n## Method Inventory\n\n'
    for m in methods[:1000]:
        logic+=f"- `{esc(m.get('name'))}` from `{esc(m.get('source_file'))}` lines `{esc(m.get('line_range'))}`"
        if m.get('called_methods'): logic+=f"; calls `{', '.join(m.get('called_methods'))}`"
        logic+='\n'
    logic+='\n## Call Graph\n\n'
    for edge in graph[:2000]:
        caller=edge.get('caller') or {}; callee=edge.get('callee') or {}
        prefix=(esc(callee.get('target'))+'.') if callee.get('target') else ''
        logic+=f"- `{esc(caller.get('method'))}` SHALL have detected call candidate `{prefix}{esc(callee.get('method'))}`.\n"
    write(out/'specs/business-logic/spec.md',logic)
    cfg='# Configuration Specification\n\n## Requirements\n\n'+req('Configuration source inventory','The system SHALL keep detected configuration files documented for build, deployment, and runtime review.','\n'.join([f"- THEN `{esc(c.get('source_file'))}` SHALL be reviewed as `{esc(c.get('kind'))}`" for c in configs]) or '- THEN no configuration files were detected.')
    write(out/'specs/configuration/spec.md',cfg)
    dep='# Dependencies Specification\n\n## Requirements\n\n'+req('Dependency inventory','The system SHALL document project, assembly, and NuGet dependencies detected from project metadata.','\n'.join([f"- THEN dependency `{esc(d.get('include') or d.get('id'))}` SHALL be associated with project `{esc(d.get('project'))}`" for d in deps[:200]]) or '- THEN no dependencies were detected.')
    dep+='\n## Dependencies\n\n'
    for d in deps:
        dep+=f"- `{esc(d.get('type'))}`: `{esc(d.get('project'))}` -> `{esc(d.get('include') or d.get('id'))}`"
        if d.get('version'): dep+=f" version `{esc(d.get('version'))}`"
        if d.get('hint_path'): dep+=f" hint `{esc(d.get('hint_path'))}`"
        dep+='\n'
    write(out/'specs/dependencies/spec.md',dep)
    print(f'Wrote OpenSpec v0.3 files to {out}')
if __name__=='__main__':
    if len(sys.argv)!=3: print('Usage: generate_openspec.py <normalized_dir> <openspec_dir>',file=sys.stderr); raise SystemExit(2)
    main(sys.argv[1],sys.argv[2])
