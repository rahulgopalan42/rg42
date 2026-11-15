"""Reads the user's workbook (F1-SCREEN-RECORDINGS-ALL-BRANDS-RANKED-2026-11-02-2.xlsx, downloaded from Drive on 15 Nov 2026)
and writes data/brands.json.gz: one record per brand on the 48 sector tabs, in the user's tab and row order.
The user has edited the sheet (moved or removed columns on some tabs, marked rows with an x, added brands), so each
field is located by its header on that tab and missing fields are filled from the original workbook in reports/.
Usage: prep.py <user workbook.xlsx>"""
import gzip, json, os, re, sys
from collections import Counter
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
ORIG = os.path.join(R, 'reports', 'F1-SCREEN-RECORDINGS-ALL-BRANDS-RANKED-2026-11-02.xlsx')
SKIP = {'SUMMARY', 'RANGES CHECK', 'PAGE CHECK', 'ALL PROSPECTS (RANKED)', 'ALREADY F1 SPONSORS', 'QC'}
def sheets(p):
    wb = load_workbook(p, read_only=True)
    return {ws.title: [[c for c in r] for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
def s(x): return re.sub(r'\s+', ' ', str(x)).strip() if x is not None else ''
U = sheets(sys.argv[1]); O = sheets(ORIG)
oh = [s(x) for x in O['ALL PROSPECTS (RANKED)'][0]]
orig = {}; by_about = {}
for r in O['ALL PROSPECTS (RANKED)'][1:]:
    d = {h: r[i] for i, h in enumerate(oh)}
    orig.setdefault(s(d['Brand']), d); by_about.setdefault(s(d['About the company'])[:160], d)
otabs = [t for t in O if t not in SKIP]; utabs = [t for t in U if t not in SKIP]
assert len(otabs) == len(utabs) == 48
out = []; stat = Counter()
for ti, (ut, ot) in enumerate(zip(utabs, otabs), 1):
    sector = s(O[ot][1][oh.index('Sector')])                       # full sector name (tab titles are cut at 31 characters)
    rows = U[ut]; hd = [s(x) for x in rows[0]]
    def last(name): 
        ix = [i for i, h in enumerate(hd) if h == name]; return ix[-1] if ix else None
    col = {k: last(k) for k in ('Rank', 'Tier', 'Brand', 'Subsector (Crunchbase industries)', 'HQ country', 'HQ location (Crunchbase)', 'About the company', 'About: confidence',
                                'Description (Crunchbase)', 'Total funding (as shown)', 'Funding range filter (USD)', 'Last funding date', 'Flags', 'Search', 'Seen in recording')}
    b = col['Brand']; n = 0
    for ri, r in enumerate(rows[1:], 2):
        brand = s(r[b]) if b < len(r) else ''
        if not brand: continue
        n += 1
        g = lambda k: s(r[col[k]]) if col[k] is not None and col[k] < len(r) else ''
        mark = any(s(c).lower() in ('x', 'xx') for c in r[:b])
        about = g('About the company')
        o = orig.get(brand); renamed = ''
        if o is None and about and about[:160] in by_about:               # the user retyped the brand cell: keep the data row, restore or note the name
            o = by_about[about[:160]]; renamed = s(o['Brand']); stat['brand cell changed by user'] += 1
        if o is None: stat['brand not in the original workbook'] += 1
        if o is not None and s(o['Sector']) != sector: stat['on a different tab than in the original'] += 1
        og = lambda k: s(o[k]) if o is not None else ''
        rec = {'id': f'{ti:02d}-{n:04d}', 'tab': ut.strip(), 'sector': sector, 'row': ri, 'brand': brand, 'orig_brand': renamed, 'mark': mark,
               'tier': next((s(c) for c in r[:b] if s(c).startswith('Tier')), '') or og('Tier'), 'rank': og('Rank'), 'old_score': og('Priority score (/100)'),
               'subsector': g('Subsector (Crunchbase industries)') or og('Subsector (Crunchbase industries)'), 'country': g('HQ country') or og('HQ country'),
               'loc': g('HQ location (Crunchbase)') or og('HQ location (Crunchbase)'), 'about': about or og('About the company'), 'about_conf': g('About: confidence') or og('About: confidence'),
               'cb_desc': g('Description (Crunchbase)') or og('Description (Crunchbase)'), 'funding': g('Total funding (as shown)') or og('Total funding (as shown)'),
               'range': g('Funding range filter (USD)') or og('Funding range filter (USD)'), 'last': g('Last funding date') or og('Last funding date'),
               'flags': g('Flags') or og('Flags'), 'search': g('Search') or og('Search'), 'seen': g('Seen in recording') or og('Seen in recording'), 'user_added': o is None and not about}
        if len(brand) < 2 and renamed: rec['brand'] = renamed; rec['orig_brand'] = ''; rec['note'] = f'brand cell in your sheet reads "{brand}" (typing slip); original name restored'
        out.append(rec)
    stat['tabs'] += 1
json.dump(out, gzip.open(os.path.join(H, 'data', 'brands.json.gz'), 'wt', encoding='utf-8'), ensure_ascii=False)
print(len(out), 'brands |', dict(stat), '| marked x:', sum(r['mark'] for r in out), '| added by user:', sum(r['user_added'] for r in out))
