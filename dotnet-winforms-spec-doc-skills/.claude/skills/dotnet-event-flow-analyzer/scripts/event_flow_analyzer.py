
from pathlib import Path
import json, sys

def load(path):
    p = Path(path)
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else []

def main(norm_dir, out_dir):
    norm = Path(norm_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    flows = load(norm / 'event_flows.json')

    startup = []
    backend = []

    for f in flows:
        name = (f.get('flow_name') or '').lower()

        if 'load' in name:
            startup.append(f)

        backend.append({
            'flow': f.get('flow_name'),
            'calls': f.get('called_methods', [])
        })

    (out / 'startup_flow.json').write_text(json.dumps(startup, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'ui_backend_flows.json').write_text(json.dumps(backend, ensure_ascii=False, indent=2), encoding='utf-8')

    print('event flow analysis complete')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
