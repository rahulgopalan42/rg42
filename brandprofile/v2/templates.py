"""Usage: templates.py "<tracker label>=<tracker.xlsx>" ["<label>=<xlsx>" ...]
Reads the user's template trackers (every tab with a 'Brand (your sheet)' header) and stores brand, batch and status in
templates_built.json. note(name) then says whether a template was built for that company.
Trackers received on 28 Nov 2026: '00_Tracker - F1 Private Sheet - Batch 1' (765 brands) and
'00_Tracker - New Private Companies - Wave 1 priority order' (271 brands, all of them on the master).
Matching is on the exact name only (letters and digits, accents removed) against 'Brand (your sheet)' and 'Email name'.
Looser alias matching was tried and gave false pairs (Apex, the satellite maker, with Apex Group; Aura Holdings with Aura),
so anything beyond an exact name goes in SAME after a check by hand."""
import json, os, re, sys, unicodedata
H = os.path.dirname(os.path.abspath(__file__)); STORE = os.path.join(H, 'templates_built.json')
# same company under another name on the older sheet: file name -> tracker name (checked by hand, 28 Nov 2026)
SAME = {'Silk (formerly Kaminario)': 'Silk'}
def key(s):
    s = unicodedata.normalize('NFKD', str(s or '')); return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if not unicodedata.combining(c)).lower())
def built(status): return str(status or '').lower().startswith(('template', 'done'))
def read(path, label):
    from openpyxl import load_workbook
    out = []
    for ws in load_workbook(path, read_only=True).worksheets:
        rows = ws.iter_rows(values_only=True); h = [str(c or '').strip() for c in next(rows, [])]
        if 'Brand (your sheet)' not in h: continue
        for r in rows:
            d = {k: re.sub(r'\s+', ' ', str(v)).strip() if v is not None else '' for k, v in zip(h, r)}
            if d.get('Brand (your sheet)'):
                out.append({'tracker': label, 'batch': d.get('Batch', ''), 'tab': d.get('Sheet tab', ''), 'brand': d['Brand (your sheet)'], 'email': d.get('Email name', ''), 'status': d.get('Status', '')})
    return out
_IX = None
def index():
    global _IX
    if _IX is None:
        _IX = {}
        for t in (json.load(open(STORE, encoding='utf-8')) if os.path.exists(STORE) else []):
            for k in {key(t['brand']), key(t['email'])} - {''}:
                if k not in _IX or (built(t['status']) and not built(_IX[k]['status'])): _IX[k] = t
    return _IX
def find(name): return index().get(key(SAME.get(str(name).strip(), name)))
def note(name):
    """Text for the 'Template Already Built?' column: starts with Yes when a template exists, No when the tracker says it was not built."""
    t = find(name)
    if not t: return ''
    aka = '' if key(t['brand']) == key(name) or key(t['email']) == key(name) else f' under the name {t["brand"]}'
    if built(t['status']):
        extra = '' if t['status'] == 'Template + contacts' else f'. Tracker status: {t["status"]}'
        return f'Yes: template built{aka} ({t["batch"]}, {t["tracker"]} tracker){extra}'
    why = re.sub(r'^Not built:\s*', '', t['status'])
    return f'No: on the {t["tracker"]} tracker but no template was built. {why[:260]}'
if __name__ == '__main__':
    T = []
    for a in sys.argv[1:]:
        label, path = a.split('=', 1); T += read(path, label)
    json.dump(T, open(STORE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    from collections import Counter
    print(len(T), 'tracker rows', dict(Counter(t['tracker'] for t in T)), 'built', sum(built(t['status']) for t in T))
