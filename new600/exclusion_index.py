"""Every brand already in this project: all delivered workbooks (every tab), Rahul's sheets, research pools and the
screen-recording list. Writes new600/excluded.json {names: [loose names], domains: [...]}."""
import json, os, sys, glob, re
import pandas as pd
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, regdom
names, doms = set(), set()
NAMECOL = re.compile(r'brand|company|organi[sz]ation|^name$|parent|legal', re.I); DOMCOL = re.compile(r'website|domain|url', re.I)
for f in sorted(glob.glob(os.path.join(R, 'reports', '*.xlsx'))):
    try: wb = load_workbook(f, read_only=True)
    except Exception as e: print('skip', f, e); continue
    for ws in wb.worksheets:
        hdr = None
        for row in ws.iter_rows(values_only=True):
            if hdr is None:
                if row and sum(1 for c in row if isinstance(c, str)) >= 2: hdr = [str(c or '') for c in row]
                continue
            for h, v in zip(hdr, row):
                if not isinstance(v, str) or not v.strip() or len(v) > 90: continue
                if NAMECOL.search(h) and not re.search(r'contact|person|ceo|founder', h, re.I): names.add(loose(v))
                elif DOMCOL.search(h): doms.add(regdom(v))
    wb.close()
for f in glob.glob(os.path.join(R, 'reports', '*.csv')):
    try:
        df = pd.read_csv(f, dtype=str)
        for c in df.columns:
            if NAMECOL.search(c): names |= set(df[c].dropna().map(loose))
            elif DOMCOL.search(c): doms |= set(df[c].dropna().map(regdom))
    except Exception: pass
ex = json.load(open(os.path.join(R, 'brands200', 'exclusion.json'))); names |= set(ex['names']); doms |= set(ex['domains'])
for pk in ('unicorns/all.pkl', 'brands200/new_brands.pkl'):
    df = pd.read_pickle(os.path.join(R, pk))
    for c in ('brand', 'legal_name', 'parent'):
        if c in df: names |= set(df[c].dropna().astype(str).map(loose))
    if 'domain' in df: doms |= set(df['domain'].dropna().astype(str).map(regdom))
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):   # screen-recording build output (the workbook in reports/ is read above anyway)
    b = json.load(open(sys.argv[1]))
    for c in b['main'] + b['f1']: names.add(loose(c['brand']))
for f in glob.glob(os.path.join(R, 'screenrec', 'data', '*.rows.json.gz')):
    import gzip
    for r in json.load(gzip.open(f))['rows']: names.add(loose(r.get('name', '')))
names.discard(''); doms.discard('')
json.dump({'names': sorted(names), 'domains': sorted(doms)}, open(os.path.join(H, 'excluded.json'), 'w'))
print('excluded names', len(names), 'domains', len(doms))
