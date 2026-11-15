"""Reads the user's 'Private' selection sheet (8 tabs of brands picked from the 48-tab sheet) and matches every row to the brand
records in data/brands.json.gz.   Usage: sel_prep.py <private.xlsx>   -> data/selection.json"""
import gzip, json, os, re, sys
from collections import Counter, defaultdict
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__))
TABMAP = {'Software': 'Software, Internet & AI', 'IT Services': 'IT Services & Consulting', 'Investment & Capital': 'Investment & Capital Markets',
          'Financial Services': 'Financial Services & Payments', 'Industrial Machinery': 'Industrial Machinery & Equipment', 'Luxury, Jewellery': 'Luxury, Jewellery & Watches',
          'Beauty & Personal Care': 'Beauty & Personal Care', 'Staffing & HR': 'Staffing & HR'}
B = json.load(gzip.open(os.path.join(H, 'data', 'brands.json.gz'), 'rt', encoding='utf-8'))
norm = lambda t: re.sub(r'[^a-z0-9]', '', str(t or '').lower())
by_tab = defaultdict(list); by_name = defaultdict(list)
for r in B:
    for k in {norm(r['brand']), norm(r.get('orig_brand'))} - {''}: by_tab[(r['sector'], k)].append(r); by_name[k].append(r)
wb = load_workbook(sys.argv[1], read_only=True); out = []; stat = Counter(); used = set()
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True)); hdr = [str(c).strip() if c is not None else '' for c in rows[0]]
    col = lambda name, last=False: ([i for i, h in enumerate(hdr) if h.startswith(name)] or [None])[-1 if last else 0]
    ib = col('Brand'); im = hdr.index('') if '' in hdr else None
    for n, row in enumerate(rows[1:], 2):
        if not row or ib is None or ib >= len(row) or row[ib] in (None, ''): continue
        g = lambda name, last=False: (str(row[col(name, last)]).strip() if col(name, last) is not None and col(name, last) < len(row) and row[col(name, last)] is not None else '')
        brand = str(row[ib]).strip(); sector = TABMAP.get(ws.title.strip(), ws.title.strip())
        c = [r for r in by_tab.get((sector, norm(brand)), []) if r['id'] not in used]; how = 'tab + name'
        if not c: c = [r for r in by_name.get(norm(brand), []) if r['id'] not in used]; how = 'name on another tab'
        if len(c) > 1:                                    # same name twice: take the one with the same country, else the first
            cc = [r for r in c if r['country'] == g('HQ country')]; c = cc or c
        rec = {'tab': ws.title.strip(), 'row': n, 'brand': brand, 'mark': (str(row[im]).strip() if im is not None and im < len(row) and row[im] is not None else ''),
               'tier': g('Tier'), 'rank': g('Rank'), 'country': g('HQ country'), 'loc': g('HQ location'), 'about': g('About the company', True), 'cb_desc': g('Description (Crunchbase)'),
               'funding': g('Total funding (as shown)', True), 'range': g('Funding range'), 'last': g('Last funding date'), 'flags': g('Flags'), 'id': c[0]['id'] if c else None, 'how': how if c else 'no match'}
        if c: used.add(c[0]['id'])
        stat[rec['how']] += 1; out.append(rec)
json.dump(out, open(os.path.join(H, 'data', 'selection.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out), 'brands on', len(wb.worksheets), 'tabs |', dict(stat), '| per tab', dict(Counter(r['tab'] for r in out)))
for r in out:
    if r['how'] != 'tab + name': print('  ', r['how'], '|', r['tab'], '|', r['brand'], '|', r['country'], '|', r['id'])
print('marks:', dict(Counter(r['mark'] for r in out)))
