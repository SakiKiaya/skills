#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, sys
from typing import Any

def load(path: Path, default: Any):
    if path.exists():
        try: return json.loads(path.read_text(encoding='utf-8'))
        except Exception: return default
    return default

def esc(v: Any) -> str:
    s='N/A' if v in (None,'') else str(v).replace('\n',' ').replace('|','\\|')
    return s[:1000]+'...' if len(s)>1000 else s

def table(headers: list[str], rows: list[list[Any]]) -> str:
    out=['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
    for row in rows:
        out.append('| '+' | '.join(esc(c) for c in row)+' |')
    return '\n'.join(out)+'\n'

def node_id(name: Any) -> str:
    return ''.join(ch if ch.isalnum() else '_' for ch in str(name or 'Unknown'))

def infer_responsibility(project: dict[str, Any], layers: list[dict[str, Any]]) -> str:
    text=' '.join([str(project.get('name') or ''),str(project.get('project_file') or ''),str(project.get('references') or ''),str(project.get('nuget_packages') or '')]).lower()
    candidates=[]
    if project.get('is_winforms'): candidates.append('UI / WinForms application entry or screen layer')
    if any(k in text for k in ['plc','modbus','mcprotocol','mitsubishi']): candidates.append('PLC communication / equipment control')
    if any(k in text for k in ['camera','grab','basler','hikvision']): candidates.append('Camera acquisition')
    if any(k in text for k in ['vision','aoi','halcon','opencv','emgu']): candidates.append('Vision inspection / image processing')
    if any(k in text for k in ['sql','database','sqlite','db']): candidates.append('Database / persistence')
    if any(k in text for k in ['socket','tcp','serial','communication']): candidates.append('Communication / protocol integration')
    if any(k in text for k in ['common','util','helper']): candidates.append('Shared utility / common library')
    for layer in [l.get('layer') for l in layers if l.get('source') == project.get('name')]:
        candidates.append(f'{layer} 推測')
    return '; '.join(dict.fromkeys(candidates)) if candidates else '需人工確認：未從專案名稱、引用或語意資料判斷出明確責任'

def architecture_diagram(projects, deps) -> str:
    lines=['```mermaid','flowchart TD','    User["Operator / User"]','    UI["WinForms UI Layer"]','    Service["Service / Business Logic"]','    Device["Device / External Integration"]','    Config["Configuration"]','    User --> UI','    UI --> Service','    Service --> Device','    UI --> Config','    Service --> Config']
    for p in projects:
        pid='P_'+node_id(p.get('name')); label=f"{p.get('name')}<br/>{p.get('language') or ''}"
        lines.append(f'    {pid}["{label}"]')
        lines.append(f"    {'UI' if p.get('is_winforms') else 'Service'} --> {pid}")
    for d in deps:
        if d.get('type')=='ProjectReference':
            src='P_'+node_id(d.get('project')); dst_name=d.get('name') or d.get('include')
            if dst_name:
                dst='P_'+node_id(Path(str(dst_name)).stem)
                lines.append(f'    {src} -. ProjectReference .-> {dst}')
    lines.append('```')
    return '\n'.join(lines)

def project_reference_diagram(projects, deps) -> str:
    lines=['```mermaid','flowchart LR']
    for p in projects:
        lines.append(f'    P_{node_id(p.get("name"))}["{p.get("name")}"]')
    for d in deps:
        if d.get('type')=='ProjectReference':
            src='P_'+node_id(d.get('project')); target=d.get('name') or Path(str(d.get('include') or '')).stem
            lines.append(f'    {src} --> P_{node_id(target)}')
    lines.append('```')
    return '\n'.join(lines)

def external_dependency_diagram(deps) -> str:
    lines=['```mermaid','flowchart LR','    App["Application Projects"]']; added=set()
    for d in [x for x in deps if x.get('type') in {'Reference','PackageReference','packages.config'}][:80]:
        name=d.get('include') or d.get('id')
        if not name or name in added: continue
        added.add(name); eid='E_'+node_id(name); label=str(name).split(',')[0]
        lines.append(f'    {eid}["{label}"]'); lines.append(f'    App -. uses .-> {eid}')
    lines.append('```')
    return '\n'.join(lines)

def generate_architecture(norm: Path, sem: Path, docs: Path) -> None:
    projects=load(norm/'projects.json',[]); deps=load(norm/'dependencies.json',[])
    layers=load(sem/'architecture_layers.json',[]); topology=load(sem/'device_topology.json',[]); backend=load(sem/'backend_mappings.json',[])
    doc='# Architecture\n\n本文件用於協助新進工程師理解系統模組之間的關係、各模組責任，以及外部相依關係。\n\n'
    doc+='## 1. Overall Block Architecture\n\n'+architecture_diagram(projects,deps)+'\n\n'
    doc+='## 2. Project / Module Reference Diagram\n\n'+project_reference_diagram(projects,deps)+'\n\n'
    doc+='## 3. External Dependency Diagram\n\n'+external_dependency_diagram(deps)+'\n\n'
    doc+='## 4. Module Responsibility Allocation\n\n'
    doc+=table(['Module / Project','Language','Project File','Target','WinForms','Responsibility'],[[p.get('name'),p.get('language'),p.get('project_file'),p.get('target_framework'),'Yes' if p.get('is_winforms') else 'No',infer_responsibility(p,layers)] for p in projects])
    doc+='\n## 5. Layer Assignment Candidates\n\n以下內容包含語意推測，需由工程師確認。\n\n'
    doc+=table(['Source Type','Source','Layer','Keywords','Confidence'],[[l.get('source_type'),l.get('source'),l.get('layer'),l.get('matched_keywords'),l.get('confidence')] for l in layers])
    doc+='\n## 6. Project References\n\n'
    doc+=table(['Project','Reference Type','Target / Include','Hint / Version','Source'],[[d.get('project'),d.get('type'),d.get('name') or d.get('include') or d.get('id'),d.get('hint_path') or d.get('version'),d.get('source_file')] for d in deps])
    doc+='\n## 7. External Device / Backend Interaction Candidates\n\n'
    doc+=table(['Device Type','Flow','Handler','Keywords','Confidence'],[[t.get('device_type'),t.get('flow'),t.get('handler'),t.get('matched_keywords'),t.get('confidence')] for t in topology])
    doc+='\n## 8. Backend Mapping Summary\n\n'
    doc+=table(['Operation','Handler','Direct Calls','Device Candidates','Confidence'],[[b.get('operation'),b.get('handler'),b.get('direct_called_methods'),b.get('device_candidates'),b.get('confidence')] for b in backend])
    doc+='\n## 9. Review Notes\n\n- `推測` 表示根據命名、引用或靜態分析結果推斷，尚未經人工確認。\n- ProjectReference 代表專案層級引用，Reference / PackageReference 代表外部 assembly 或 NuGet 相依。\n- 若架構圖中出現孤立模組，代表目前未從專案檔或分析資料中取得明確引用關係。\n'
    (docs/'02_architecture.md').write_text(doc, encoding='utf-8')

def generate_configuration(norm: Path, docs: Path) -> None:
    config=load(norm/'config_sources.json',{}); files=config.get('config_files',[]); refs=config.get('code_config_references',[])
    doc='# Configuration\n\n本文件只整理目標專案本身的設定來源，刻意忽略 Skill 產生的中繼文件，例如 `.claude/`、`exports/`、`docs/`、`openspec/`。\n\n'
    doc+='## 1. Confirmed Project Configuration Files\n\n'
    doc+=table(['Path','Kind','Extension','Settings Count','Confidence'],[[f.get('path'),f.get('kind'),f.get('extension'),len(f.get('settings') or []),f.get('confidence')] for f in files])
    settings=[]
    for f in files:
        for s in f.get('settings') or []:
            settings.append([f.get('path'),s.get('name'),s.get('type'),s.get('scope'),s.get('raw_attributes')])
    doc+='\n## 2. Settings.settings Entries\n\n'+table(['File','Setting','Type','Scope','Raw'],settings)
    doc+='\n## 3. In-code Configuration References\n\n'
    doc+=table(['Type','Source','Line','Expression / Path','Args','Confidence'],[[r.get('reference_type'),r.get('source_file'),r.get('line'),r.get('expression'),r.get('args'),r.get('confidence')] for r in refs])
    doc+='\n## 4. Review Guidance\n\n- `runtime_config` 通常代表 App.config / Web.config / exe.config 類型設定。\n- `settings_settings` 通常代表 Visual Studio Settings.settings。\n- `string_literal_config_path_candidate` 是從程式碼字串推測的設定檔路徑，需人工確認。\n- 建議新進工程師優先確認 App.config、Settings.settings、ConnectionStrings、AppSettings，以及 File/XDocument/JsonConvert 載入的外部檔案。\n'
    (docs/'06_configuration.md').write_text(doc, encoding='utf-8')

def main(norm_dir: str, semantic_dir: str, docs_dir: str) -> int:
    norm=Path(norm_dir); sem=Path(semantic_dir); docs=Path(docs_dir); docs.mkdir(parents=True, exist_ok=True)
    generate_architecture(norm,sem,docs); generate_configuration(norm,docs)
    print(f'Wrote enhanced architecture/config docs to {docs}')
    return 0
if __name__=='__main__':
    if len(sys.argv)!=4:
        print('Usage: generate_architecture_docs.py <normalized_dir> <semantic_dir> <docs_dir>', file=sys.stderr); raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
