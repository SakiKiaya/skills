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

def esc(v):
    if v in (None,''): return 'N/A'
    s=str(v).replace('\n',' ').replace('|','\\|')
    return s[:497]+'...' if len(s)>500 else s

def table(h, rows):
    out=['| '+' | '.join(h)+' |','|'+'|'.join(['---']*len(h))+'|']
    for r in rows: out.append('| '+' | '.join(esc(x) for x in r)+' |')
    return '\n'.join(out)+'\n'

def mermaid_controls(form, controls):
    fname=form.get('form_name'); lines=['```mermaid','flowchart TD']
    rows=[c for c in controls if c.get('form')==fname]
    if not rows: lines.append(f'    {fname}["{fname}"]')
    for c in rows:
        name=c.get('name'); parent=c.get('parent') or fname; typ=c.get('type') or ''
        lines.append(f'    {parent} --> {name}["{name}<br/>{typ}"]')
    lines.append('```'); return '\n'.join(lines)

def mermaid_flow(flow):
    trig=flow.get('trigger') or {}; h=flow.get('handler') or 'Handler'
    lines=['```mermaid','sequenceDiagram','    participant User',f'    participant UI as {trig.get("control") or "UI"}',f'    participant Handler as {h}',f'    User->>UI: {trig.get("event") or "event"}',f'    UI->>Handler: {h}()']
    for c in (flow.get('calls') or [])[:10]:
        callee=(str(c.get('target'))+'.' if c.get('target') else '')+str(c.get('method'))
        lines.append(f'    Handler->>Handler: {callee}()')
    lines.append('```'); return '\n'.join(lines)

def main(norm_arg, docs_arg):
    norm=Path(norm_arg); docs=Path(docs_arg); (docs/'diagrams').mkdir(parents=True,exist_ok=True)
    solution=load(norm,'solution.json',{'solution':{}}).get('solution',{})
    projects=load(norm,'projects.json',[]); deps=load(norm,'dependencies.json',[])
    forms=load(norm,'forms.json',[]); controls=load(norm,'controls.json',[]); events=load(norm,'events.json',[]); flows=load(norm,'event_flows.json',[])
    classes=load(norm,'classes.json',[]); methods=load(norm,'methods.json',[]); graph=load(norm,'call_graph.json',[]); configs=load(norm,'configs.json',[]); diags=load(norm,'diagnostics.json',[])
    (docs/'README.md').write_text('# Project Documentation\n\n- [00 Solution Overview](00_solution_overview.md)\n- [01 Project Structure](01_project_structure.md)\n- [02 Architecture](02_architecture.md)\n- [03 Forms UI Structure](03_forms_ui_structure.md)\n- [04 Event Flow](04_event_flow.md)\n- [05 Class Method Reference](05_class_method_reference.md)\n- [06 Configuration](06_configuration.md)\n- [07 Dependencies](07_dependencies.md)\n- [08 Call Graph](08_call_graph.md)\n- [10 Learning Path for New Engineers](10_learning_path_for_new_engineers.md)\n',encoding='utf-8')
    (docs/'00_solution_overview.md').write_text('# Solution Overview\n\n'+table(['Item','Value'],[['Solution',solution.get('name')],['Path',solution.get('path')],['Projects',len(projects)],['Forms',len(forms)],['Methods',len(methods)],['Event Flows',len(flows)]]),encoding='utf-8')
    (docs/'01_project_structure.md').write_text('# Project Structure\n\n'+table(['Project','Language','File','Target','Output','WinForms','Platforms'],[[p.get('name'),p.get('language'),p.get('project_file'),p.get('target_framework'),p.get('output_type'),p.get('is_winforms'),', '.join(p.get('platforms',[]))] for p in projects]),encoding='utf-8')
    (docs/'02_architecture.md').write_text('# Architecture\n\n## Dependency Candidates\n\n'+table(['Type','Project','Include/ID','Hint/Version'],[[d.get('type'),d.get('project'),d.get('include') or d.get('id'),d.get('hint_path') or d.get('version')] for d in deps]),encoding='utf-8')
    ui='# Forms UI Structure\n\n'
    for f in forms:
        ui+=f"## {esc(f.get('form_name'))}\n\n"+table(['Item','Value'],[['Namespace',f.get('namespace')],['Language',f.get('language')],['Logic',f.get('logic_file')],['Designer',f.get('designer_file')],['Resx',f.get('resx_file')]])
        fc=[c for c in controls if c.get('form')==f.get('form_name')]
        ui+='\n### Controls\n\n'+table(['Name','Type','Parent','Text','Events','Source'],[[c.get('name'),c.get('type'),c.get('parent'),c.get('text'),c.get('events'),c.get('source_file')] for c in fc])+'\n### UI Diagram\n\n'+mermaid_controls(f,controls)+'\n\n'
    (docs/'03_forms_ui_structure.md').write_text(ui,encoding='utf-8')
    ev='# Event Flow\n\n## Event Binding Table\n\n'+table(['Form','Control','Event','Handler','Binding','Language','Source','Line'],[[e.get('form'),e.get('control'),e.get('event'),e.get('handler'),e.get('binding'),e.get('language'),e.get('source_file'),e.get('line')] for e in events])+'\n## Event Flow Details\n\n'
    for fl in flows:
        ev+=f"### {esc(fl.get('flow_name'))}\n\n"+table(['Item','Value'],[['Handler',fl.get('handler')],['Handler Source',fl.get('handler_source')],['Handler Lines',fl.get('handler_line_range')],['Confidence',fl.get('confidence')],['Purpose',fl.get('purpose_hint')],['Called Methods',', '.join(fl.get('called_methods') or [])]])+'\n'+mermaid_flow(fl)+'\n\n'
    (docs/'04_event_flow.md').write_text(ev,encoding='utf-8')
    cm='# Class and Method Reference\n\n## Classes\n\n'+table(['Name','Namespace','Kind','Language','Source','Line'],[[c.get('name'),c.get('namespace'),c.get('kind'),c.get('language'),c.get('source_file'),(c.get('line_range') or [None])[0]] for c in classes])+'\n## Methods\n\n'
    cm+=table(['Name','Namespace','Language','Source','Lines','Event Handler','Events','Purpose','Calls'],[[m.get('name'),m.get('namespace'),m.get('language'),m.get('source_file'),m.get('line_range'),m.get('is_event_handler'),m.get('event_sources'),m.get('purpose_hint'),', '.join(m.get('called_methods') or [])] for m in methods])
    (docs/'05_class_method_reference.md').write_text(cm,encoding='utf-8')
    (docs/'06_configuration.md').write_text('# Configuration\n\n'+table(['Source','Kind','Entries/Error'],[[c.get('source_file'),c.get('kind'),c.get('entries') or c.get('error')] for c in configs]),encoding='utf-8')
    (docs/'07_dependencies.md').write_text('# Dependencies\n\n'+table(['Type','Project','Include/ID','Version','Hint Path','Source'],[[d.get('type'),d.get('project'),d.get('include') or d.get('id'),d.get('version'),d.get('hint_path'),d.get('source_file')] for d in deps]),encoding='utf-8')
    (docs/'08_call_graph.md').write_text('# Call Graph\n\n'+table(['Caller','Caller Source','Callee Target','Callee Method','Known Internal'],[[(e.get('caller') or {}).get('method'),(e.get('caller') or {}).get('source_file'),(e.get('callee') or {}).get('target'),(e.get('callee') or {}).get('method'),e.get('known_internal_method')] for e in graph]),encoding='utf-8')
    learn='# Learning Path for New Engineers\n\n1. Read `00_solution_overview.md`.\n2. Read `01_project_structure.md`.\n3. Read `03_forms_ui_structure.md`.\n4. Read `04_event_flow.md`.\n5. Read `05_class_method_reference.md`.\n6. Read `08_call_graph.md`.\n7. Read config/dependency docs.\n\n## Diagnostics\n\n'+table(['Level','Source','Message'],[[d.get('level'),d.get('source_file'),d.get('message')] for d in diags])
    (docs/'10_learning_path_for_new_engineers.md').write_text(learn,encoding='utf-8')
    print(f'Wrote docs v0.3 to {docs}')
if __name__=='__main__':
    if len(sys.argv)!=3: print('Usage: generate_docs.py <normalized_dir> <docs_dir>',file=sys.stderr); raise SystemExit(2)
    main(sys.argv[1],sys.argv[2])
