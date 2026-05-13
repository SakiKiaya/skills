#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, re, sys, xml.etree.ElementTree as ET
from typing import Any

IGNORE_PARTS = {'.git','.vs','bin','obj','packages','node_modules','.claude','exports','docs','openspec'}
CONFIG_DIR_NAMES = {'settings','setting','config','configs','configuration','properties','my project'}
CONFIG_EXTS = {'.config','.settings','.ini','.xml','.json','.yaml','.yml','.toml'}
CODE_EXTS = {'.cs','.vb'}
PATTERNS = [
    ('ConfigurationManager.AppSettings', re.compile(r'ConfigurationManager\.AppSettings(?:\[[^\]]+\])?', re.I)),
    ('ConfigurationManager.ConnectionStrings', re.compile(r'ConfigurationManager\.ConnectionStrings(?:\[[^\]]+\])?', re.I)),
    ('Settings.Default', re.compile(r'\bSettings\.Default\.[A-Za-z_][A-Za-z0-9_]*', re.I)),
    ('My.Settings', re.compile(r'\bMy\.Settings\.[A-Za-z_][A-Za-z0-9_]*', re.I)),
    ('Path.Combine', re.compile(r'\bPath\.Combine\s*\((?P<args>[^;\n]+)\)', re.I)),
    ('File.ReadAllText', re.compile(r'\bFile\.ReadAllText\s*\((?P<args>[^;\n]+)\)', re.I)),
    ('File.ReadAllLines', re.compile(r'\bFile\.ReadAllLines\s*\((?P<args>[^;\n]+)\)', re.I)),
    ('File.WriteAllText', re.compile(r'\bFile\.WriteAllText\s*\((?P<args>[^;\n]+)\)', re.I)),
    ('XDocument.Load', re.compile(r'\bXDocument\.Load\s*\((?P<args>[^;\n]+)\)', re.I)),
    ('XmlDocument.Load', re.compile(r'\bXmlDocument\.Load\s*\((?P<args>[^;\n]+)\)', re.I)),
    ('JsonConvert.DeserializeObject', re.compile(r'\bJsonConvert\.DeserializeObject\s*(?:<[^>]+>)?\s*\((?P<args>[^;\n]+)\)', re.I)),
]
STRING_LITERAL_RE = re.compile(r'"([^"]+\.(?:json|xml|ini|config|yaml|yml|txt|csv|db|sqlite))"', re.I)

def is_ignored(path: Path) -> bool:
    return any(part.lower() in IGNORE_PARTS for part in path.parts)

def rel(path: Path, root: Path) -> str:
    try: return path.relative_to(root).as_posix()
    except Exception: return path.as_posix()

def line_no(text: str, pos: int) -> int:
    return text.count('\n', 0, pos) + 1

def read_text(path: Path) -> str:
    for enc in ['utf-8-sig','utf-8','cp950','big5','shift_jis']:
        try: return path.read_text(encoding=enc)
        except UnicodeDecodeError: continue
        except Exception: break
    try: return path.read_text(errors='replace')
    except Exception: return ''

def parse_settings_file(path: Path) -> list[dict[str, Any]]:
    settings=[]
    try:
        root=ET.parse(path).getroot()
        for s in root.iter():
            tag=s.tag.split('}',1)[-1]
            if tag.lower()=='setting':
                settings.append({'name':s.attrib.get('Name') or s.attrib.get('name'),'type':s.attrib.get('Type') or s.attrib.get('type'),'scope':s.attrib.get('Scope') or s.attrib.get('scope'),'raw_attributes':dict(s.attrib)})
    except Exception: pass
    return settings

def classify_config_file(path: Path) -> str:
    parts=[p.lower() for p in path.parts]
    name=path.name.lower()
    if name in {'app.config','web.config'} or name.endswith('.exe.config') or name.endswith('.dll.config'):
        return 'runtime_config'
    if name=='settings.settings': return 'settings_settings'
    if any(p in CONFIG_DIR_NAMES for p in parts): return 'settings_or_config_folder'
    if path.suffix.lower() in CONFIG_EXTS: return 'project_config_candidate'
    return 'unknown'

def extract_code_refs(path: Path, repo: Path) -> list[dict[str, Any]]:
    text=read_text(path); refs=[]
    for ref_type,rx in PATTERNS:
        for m in rx.finditer(text):
            refs.append({'reference_type':ref_type,'source_file':rel(path,repo),'line':line_no(text,m.start()),'expression':m.group(0).strip(),'args':m.groupdict().get('args'),'confidence':0.85 if ref_type.startswith('ConfigurationManager') or ref_type in {'Settings.Default','My.Settings'} else 0.65})
    for m in STRING_LITERAL_RE.finditer(text):
        refs.append({'reference_type':'string_literal_config_path_candidate','source_file':rel(path,repo),'line':line_no(text,m.start()),'expression':m.group(1),'args':None,'confidence':0.55})
    return refs

def main(repo_arg: str, out_arg: str) -> int:
    repo=Path(repo_arg).resolve(); out=Path(out_arg).resolve(); out.mkdir(parents=True, exist_ok=True)
    config_files=[]; code_refs=[]
    for path in repo.rglob('*'):
        if not path.is_file() or is_ignored(path): continue
        suffix=path.suffix.lower(); name=path.name.lower()
        if suffix in CONFIG_EXTS or name in {'app.config','web.config','settings.settings'}:
            kind=classify_config_file(path)
            config_files.append({'path':rel(path,repo),'name':path.name,'kind':kind,'extension':suffix,'settings':parse_settings_file(path) if name=='settings.settings' else [],'confidence':0.9 if kind in {'runtime_config','settings_settings','settings_or_config_folder'} else 0.6})
        if suffix in CODE_EXTS:
            code_refs.extend(extract_code_refs(path, repo))
    data={'config_files':config_files,'code_config_references':code_refs,'ignored_generated_folders':sorted(IGNORE_PARTS),'notes':['Generated skill intermediate files are intentionally ignored.','String literal paths are candidates and require engineer review.']}
    (out/'config_sources.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {out / "config_sources.json"}')
    return 0
if __name__=='__main__':
    if len(sys.argv)!=3:
        print('Usage: configuration_analyzer.py <repo_root> <normalized_out_dir>', file=sys.stderr); raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
