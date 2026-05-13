#!/usr/bin/env python3
"""Enhanced C#/VB.NET WinForms normalizer v0.3.

Usage: python normalize_project.py <repo_root> <out_dir>

Adds:
- method signatures and approximate line ranges
- event handler mapping from Designer / AddHandler / VB Handles
- event_flows.json: UI event -> handler -> detected calls
- call_graph.json: caller -> callee candidates
"""
from __future__ import annotations
import json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

IGNORED={'.git','bin','obj','.vs','packages','node_modules'}
CONFIG_EXTS={'.config','.settings','.json','.xml'}
CS_NS=re.compile(r'\bnamespace\s+([A-Za-z_][\w.]*)')
VB_NS=re.compile(r'^\s*Namespace\s+([A-Za-z_][\w.]*)',re.I|re.M)
CS_CLASS=re.compile(r'\b(?P<kind>class|interface|enum|struct)\s+(?P<name>[A-Za-z_]\w*)')
VB_CLASS=re.compile(r'^\s*(?:Public|Private|Friend|Protected|Partial|MustInherit|NotInheritable|\s)*\s*(?P<kind>Class|Interface|Enum|Structure|Module)\s+(?P<name>[A-Za-z_]\w*)',re.I|re.M)
CS_METHOD=re.compile(r'(?P<prefix>^\s*(?:public|private|protected|internal|static|async|virtual|override|sealed|partial|extern|new|\s)+)(?P<ret>[\w<>\[\],\s\?\.]+?)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^;{}]*)\)\s*(?:where\s+[^{}]+)?\{',re.M)
VB_METHOD=re.compile(r'^\s*(?P<prefix>(?:Public|Private|Friend|Protected|Shared|Overrides|Overridable|Async|Static|Partial|\s)*)\s*(?P<kind>Sub|Function)\s+(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^)]*)\)\s*(?P<handles>Handles\s+[^\n]+)?(?P<returns>\s+As\s+[\w\.\(\)]+)?',re.I|re.M)
CS_DECL=re.compile(r'(?:private|protected|public|internal)\s+(?P<type>[\w\.]+(?:<[^>]+>)?)\s+(?P<name>[A-Za-z_]\w*)\s*;')
VB_DECL=re.compile(r'(?:Friend|Private|Protected|Public)\s+WithEvents\s+(?P<name>[A-Za-z_]\w*)\s+As\s+(?P<type>[\w\.]+)',re.I)
CS_NEW=re.compile(r'(?:this\.)?(?P<name>[A-Za-z_]\w*)\s*=\s*new\s+(?P<type>[\w\.]+)')
VB_NEW=re.compile(r'(?:Me\.)?(?P<name>[A-Za-z_]\w*)\s*=\s*New\s+(?P<type>[\w\.]+)',re.I)
CS_TEXT=re.compile(r'(?:this\.)?(?P<name>[A-Za-z_]\w*)\.Text\s*=\s*"(?P<text>(?:[^"\\]|\\.)*)"')
VB_TEXT=re.compile(r'(?:Me\.)?(?P<name>[A-Za-z_]\w*)\.Text\s*=\s*"(?P<text>[^"]*)"',re.I)
CS_PARENT=re.compile(r'(?:this\.)?(?P<parent>[A-Za-z_]\w*)\.Controls\.Add\((?:this\.)?(?P<child>[A-Za-z_]\w*)\)')
VB_PARENT=re.compile(r'(?:Me\.)?(?P<parent>[A-Za-z_]\w*)\.Controls\.Add\((?:Me\.)?(?P<child>[A-Za-z_]\w*)\)',re.I)
CS_EVENT=re.compile(r'(?:this\.)?(?P<control>[A-Za-z_]\w*)\.(?P<event>[A-Za-z_]\w*)\s*\+=\s*(?:new\s+[\w\.]+\()?(?:this\.)?(?P<handler>[A-Za-z_]\w*)(?:\))?')
VB_ADDHANDLER=re.compile(r'AddHandler\s+(?:Me\.)?(?P<control>[A-Za-z_]\w*)\.(?P<event>[A-Za-z_]\w*),\s*AddressOf\s+(?P<handler>[A-Za-z_]\w*)',re.I)
VB_HANDLES_TARGET=re.compile(r'(?P<control>[A-Za-z_]\w*)\.(?P<event>[A-Za-z_]\w*)',re.I)
CALL=re.compile(r'(?:(?P<target>[A-Za-z_]\w*)\.)?(?P<method>[A-Za-z_]\w*)\s*\(')
SKIP={'if','for','foreach','while','switch','catch','using','lock','return','sizeof','typeof','nameof','new','base','this','Me','DirectCast','CType','TryCast','GetType','InitializeComponent'}
WIN={'Button','TextBox','Label','Panel','GroupBox','TabControl','TabPage','DataGridView','PictureBox','ComboBox','CheckBox','RadioButton','ListBox','MenuStrip','ToolStrip','SplitContainer','Timer','BackgroundWorker','SerialPort','NumericUpDown','RichTextBox','TreeView','ListView'}

def read(p:Path)->str:
    for e in ['utf-8-sig','utf-8','cp950','big5','shift_jis']:
        try: return p.read_text(encoding=e)
        except UnicodeDecodeError: pass
    return p.read_text(errors='replace')
def rel(p:Path,b:Path)->str:
    try: return p.relative_to(b).as_posix()
    except ValueError: return p.as_posix()
def lang(p:Path)->str: return 'C#' if p.suffix.lower()=='.cs' else 'VB.NET' if p.suffix.lower()=='.vb' else 'Unknown'
def line(t:str,pos:int)->int: return t.count('\n',0,pos)+1
def ns(t:str,l:str):
    m=(CS_NS if l=='C#' else VB_NS).search(t); return m.group(1) if m else None
def norm_type(t):
    if not t: return None
    s=t.strip(); return 'System.Windows.Forms.'+s if '.' not in s and s in WIN else s

def brace_block(t,pos):
    depth=0; ins=False; esc=False
    for i,ch in enumerate(t[pos:],pos):
        if ins:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='"': ins=False
        else:
            if ch=='"': ins=True
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0: return t[pos+1:i], i
    return t[pos+1:], len(t)-1

def vb_block(t,start,kind):
    pat=r'^\s*End\s+'+('Sub' if kind.lower()=='sub' else 'Function')+r'\b'
    m=re.search(pat,t[start:],re.I|re.M)
    if not m: return t[start:], len(t)-1
    return t[start:start+m.start()], start+m.end()

def purpose(name,event=None):
    n=(name or '').lower()
    if event:
        ev=event.get('event'); ctl=event.get('control')
        if ev=='Click': return f'Handles user click from `{ctl}`.'
        if ev=='Tick': return f'Handles timer tick from `{ctl}`.'
        if ev in ('Load','Shown'): return 'Handles form initialization/display lifecycle.'
        if ev=='DataReceived': return f'Handles incoming data from `{ctl}`.'
    if 'click' in n: return 'Likely handles UI click event. 推測'
    if 'load' in n: return 'Likely initializes form/runtime state. 推測'
    if 'connect' in n: return 'Likely handles connection setup. 推測'
    if 'start' in n: return 'Likely starts a workflow. 推測'
    if 'stop' in n: return 'Likely stops a workflow. 推測'
    if 'save' in n: return 'Likely persists data/configuration. 推測'
    if 'read' in n: return 'Likely reads data. 推測'
    if 'write' in n: return 'Likely writes data. 推測'
    return ''

def calls(body,known):
    out=[]; seen=set()
    for m in CALL.finditer(body):
        method=m.group('method'); target=m.group('target')
        if method in SKIP: continue
        if method and method[0].islower() and method not in known: continue
        k=(target,method)
        if k in seen: continue
        seen.add(k); out.append({'target':target,'method':method,'known_internal_method':method in known})
    return out

def parse_code(p,repo,known):
    t=read(p); l=lang(p); namespace=ns(t,l); classes=[]; methods=[]
    for m in (CS_CLASS if l=='C#' else VB_CLASS).finditer(t):
        classes.append({'name':m.group('name'),'namespace':namespace,'language':l,'kind':m.group('kind'),'source_file':rel(p,repo),'line_range':[line(t,m.start()),None]})
    if l=='C#':
        for m in CS_METHOD.finditer(t):
            name=m.group('name')
            if name in SKIP: continue
            ob=t.find('{',m.end()-1); body,end=brace_block(t,ob); cs=calls(body,known)
            methods.append({'name':name,'namespace':namespace,'language':l,'return_type':m.group('ret').strip(),'parameters':m.group('params').strip(),'modifiers':m.group('prefix').split(),'source_file':rel(p,repo),'line_range':[line(t,m.start()),line(t,end)],'calls':cs,'called_methods':[c['method'] for c in cs],'is_event_handler':False,'event_sources':[],'purpose_hint':purpose(name)})
    elif l=='VB.NET':
        for m in VB_METHOD.finditer(t):
            name=m.group('name'); body,end=vb_block(t,m.end(),m.group('kind')); cs=calls(body,known); evs=[]
            handles=m.group('handles')
            if handles:
                for h in VB_HANDLES_TARGET.finditer(handles): evs.append({'control':h.group('control'),'event':h.group('event'),'binding':'VB Handles'})
            methods.append({'name':name,'namespace':namespace,'language':l,'return_type':(m.group('returns') or '').replace('As','',1).strip() or ('void' if m.group('kind').lower()=='sub' else None),'parameters':m.group('params').strip(),'modifiers':m.group('prefix').split(),'source_file':rel(p,repo),'line_range':[line(t,m.start()),line(t,end)],'calls':cs,'called_methods':[c['method'] for c in cs],'is_event_handler':bool(evs),'event_sources':evs,'purpose_hint':purpose(name, evs[0] if evs else None)})
    return classes,methods

def parse_designer(p,repo):
    t=read(p); l=lang(p); form=p.name.replace('.Designer.cs','').replace('.Designer.vb',''); namespace=ns(t,l)
    logic=p.with_name(form+('.cs' if l=='C#' else '.vb')); resx=p.with_name(form+'.resx')
    controls={}; events=[]
    def ensure(n):
        controls.setdefault(n,{'form':form,'name':n,'type':None,'parent':None,'text':None,'events':{},'layout':{},'source_file':rel(p,repo)})
        return controls[n]
    for rx in ([CS_DECL,CS_NEW] if l=='C#' else [VB_DECL,VB_NEW]):
        for m in rx.finditer(t): ensure(m.group('name'))['type']=norm_type(m.group('type'))
    for m in (CS_TEXT if l=='C#' else VB_TEXT).finditer(t): ensure(m.group('name'))['text']=m.group('text')
    for m in (CS_PARENT if l=='C#' else VB_PARENT).finditer(t): ensure(m.group('child'))['parent']=m.group('parent')
    for m in (CS_EVENT if l=='C#' else VB_ADDHANDLER).finditer(t):
        ctl,ev,handler=m.group('control'),m.group('event'),m.group('handler'); ensure(ctl)['events'][ev]=handler
        events.append({'form':form,'control':ctl,'event':ev,'handler':handler,'binding':'Designer' if l=='C#' else 'AddHandler','importance':'high','language':l,'source_file':rel(p,repo),'line':line(t,m.start())})
    return {'form_name':form,'namespace':namespace,'language':l,'logic_file':rel(logic,repo) if logic.exists() else None,'designer_file':rel(p,repo),'resx_file':rel(resx,repo) if resx.exists() else None,'controls':sorted(controls),'events':events}, list(controls.values()), events

def vb_handles(p,repo):
    t=read(p); form=p.stem; evs=[]
    for m in VB_METHOD.finditer(t):
        if not m.group('handles'): continue
        for h in VB_HANDLES_TARGET.finditer(m.group('handles')):
            evs.append({'form':form,'control':h.group('control'),'event':h.group('event'),'handler':m.group('name'),'binding':'VB Handles','importance':'high','language':'VB.NET','source_file':rel(p,repo),'line':line(t,m.start())})
    return evs

def parse_config(p,repo):
    item={'source_file':rel(p,repo),'kind':p.suffix.lower().lstrip('.'),'entries':[]}
    if p.suffix.lower() in {'.config','.settings','.xml'}:
        try:
            r=ET.parse(p).getroot()
            for e in r.iter():
                tag=e.tag.split('}',1)[-1]
                if tag in {'add','setting','connectionString'}: item['entries'].append({'tag':tag,'attributes':dict(e.attrib),'text':(e.text or '').strip()})
        except Exception as ex: item['error']=repr(ex)
    return item

def event_flows(events,methods):
    idx={}
    for m in methods: idx.setdefault(m['name'],[]).append(m)
    flows=[]
    for e in events:
        sel=(idx.get(e.get('handler')) or [None])[0]
        flows.append({'flow_name':f"{e.get('form')}.{e.get('control')}.{e.get('event')} -> {e.get('handler')}",'form':e.get('form'),'trigger':{'control':e.get('control'),'event':e.get('event'),'binding':e.get('binding'),'source_file':e.get('source_file'),'line':e.get('line')},'handler':e.get('handler'),'handler_source':sel.get('source_file') if sel else None,'handler_line_range':sel.get('line_range') if sel else None,'calls':sel.get('calls') if sel else [],'called_methods':sel.get('called_methods') if sel else [],'purpose_hint':purpose(e.get('handler'),e),'confidence':'matched-handler' if sel else 'handler-not-found'})
    return flows

def main(repo_arg,out_arg):
    repo=Path(repo_arg).resolve(); out=Path(out_arg).resolve(); out.mkdir(parents=True,exist_ok=True)
    source=[p for p in list(repo.rglob('*.cs'))+list(repo.rglob('*.vb')) if not any(part in IGNORED for part in p.parts)]
    known=set()
    for p in source:
        t=read(p); l=lang(p); rx=CS_METHOD if l=='C#' else VB_METHOD
        for m in rx.finditer(t): known.add(m.group('name'))
    forms=[]; controls=[]; events=[]; classes=[]; methods=[]; configs=[]; resources=[]; diagnostics=[]
    for p in sorted(source):
        try:
            if '.Designer.' in p.name:
                f,c,e=parse_designer(p,repo); forms.append(f); controls+=c; events+=e
            if p.suffix.lower()=='.vb': events+=vb_handles(p,repo)
            c,m=parse_code(p,repo,known); classes+=c; methods+=m
        except Exception as ex: diagnostics.append({'level':'error','source_file':rel(p,repo),'message':repr(ex)})
    byh={}
    for e in events: byh.setdefault(e.get('handler'),[]).append(e)
    for m in methods:
        linked=byh.get(m['name'],[])
        if linked:
            m['is_event_handler']=True; m['event_sources']=[{'form':e.get('form'),'control':e.get('control'),'event':e.get('event'),'binding':e.get('binding')} for e in linked]; m['purpose_hint']=purpose(m['name'],linked[0])
    uniq={}
    for c in controls: uniq[(c.get('form'),c.get('name'))]=c
    controls=list(uniq.values())
    uev={}
    for e in events: uev[(e.get('form'),e.get('control'),e.get('event'),e.get('handler'),e.get('source_file'),e.get('line'))]=e
    events=list(uev.values())
    flows=event_flows(events,methods)
    graph=[]
    for m in methods:
        for c in m.get('calls',[]): graph.append({'caller':{'method':m.get('name'),'namespace':m.get('namespace'),'source_file':m.get('source_file'),'line_range':m.get('line_range')},'callee':c,'known_internal_method':c.get('known_internal_method')})
    for p in sorted(repo.rglob('*')):
        if not p.is_file() or any(part in IGNORED for part in p.parts): continue
        if p.suffix.lower() in CONFIG_EXTS and p.name!='packages.config': configs.append(parse_config(p,repo))
        if p.suffix.lower()=='.resx': resources.append({'source_file':rel(p,repo),'name':p.stem})
    data={'forms.json':forms,'controls.json':controls,'events.json':events,'event_flows.json':flows,'classes.json':classes,'methods.json':methods,'call_graph.json':graph,'configs.json':configs,'resources.json':resources}
    for fn,obj in data.items(): (out/fn).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
    dp=out/'diagnostics.json'; old=[]
    if dp.exists():
        try: old=json.loads(dp.read_text(encoding='utf-8'))
        except Exception: old=[]
    dp.write_text(json.dumps(old+diagnostics,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Wrote project normalized IR v0.3 to {out}')
if __name__=='__main__':
    if len(sys.argv)!=3:
        print('Usage: normalize_project.py <repo_root> <out_dir>',file=sys.stderr); raise SystemExit(2)
    main(sys.argv[1],sys.argv[2])
