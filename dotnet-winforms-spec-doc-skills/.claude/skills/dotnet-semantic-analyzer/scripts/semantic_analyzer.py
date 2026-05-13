
from pathlib import Path
import json, sys

def load(path):
    p = Path(path)
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else []

def main(norm_dir, out_dir):
    norm = Path(norm_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    forms = load(norm / 'forms.json')
    controls = load(norm / 'controls.json')

    ui = []
    critical = []

    for f in forms:
        roles = []
        name = (f.get('form_name') or '').lower()

        if 'main' in name:
            roles.append('Main Control UI')
        if 'alarm' in name:
            roles.append('Alarm UI')

        ui.append({
            'form': f.get('form_name'),
            'roles': roles,
            'confidence': 0.6
        })

    for c in controls:
        n = (c.get('name') or '').lower()
        if any(x in n for x in ['start','stop','reset','alarm']):
            critical.append({
                'control': c.get('name'),
                'form': c.get('form'),
                'confidence': 0.8
            })

    (out / 'ui_responsibilities.json').write_text(json.dumps(ui, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'critical_operations.json').write_text(json.dumps(critical, ensure_ascii=False, indent=2), encoding='utf-8')

    print('semantic analysis complete')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
