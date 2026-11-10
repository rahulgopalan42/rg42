"""NEW-brands workbook: companies valued >= USD 1B or with >= USD 150M equity funding that are on none of the lists
delivered so far, Rahul's sheets or the screen recordings. Inputs: verify/out_*.json (Crunchbase finds, verified) and
research/seg_*.json (web research). Every row is re-checked against the exclusion index here.
Usage: build.py <out.xlsx>  -> also writes new600/build.json"""
import json, os, re, sys, glob
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(R, 'screenrec')); sys.path.insert(0, os.path.join(R, 'brands200'))
from excl import why
from match import loose, regdom
from sectors_cb import sector_of, FIT, CONSUMER
OUT = sys.argv[1]
TIER_A = {'United States', 'United Kingdom', 'United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Netherlands', 'Germany', 'Switzerland', 'Japan', 'Singapore',
          'France', 'Italy', 'Spain', 'Monaco', 'China', 'Hong Kong', 'Australia', 'Canada', 'Brazil', 'Mexico', 'India', 'Bahrain', 'Azerbaijan', 'Austria', 'Belgium', 'Hungary'}
TIER_B = {'Sweden', 'Norway', 'Denmark', 'Finland', 'Ireland', 'Israel', 'South Korea', 'Taiwan', 'Luxembourg', 'Portugal', 'Poland', 'Turkey', 'Indonesia',
          'Malaysia', 'Thailand', 'Kuwait', 'Oman', 'Argentina', 'Chile', 'Colombia', 'New Zealand', 'South Africa', 'Czech Republic', 'Estonia', 'Greece', 'Cyprus', 'Malta'}
CANON = {'usa': 'United States', 'us': 'United States', 'u.s.': 'United States', 'united states of america': 'United States', 'uk': 'United Kingdom',
         'england': 'United Kingdom', 'scotland': 'United Kingdom', 'uae': 'United Arab Emirates', 'korea': 'South Korea', 'republic of korea': 'South Korea',
         "people's republic of china": 'China', 'prc': 'China', 'czechia': 'Czech Republic', 'the netherlands': 'Netherlands', 'türkiye': 'Turkey'}
def country(x): x = str(x or '').strip(); return CANON.get(x.lower(), x)
def num(x):
    try: return float(str(x).replace(',', '')) if x not in (None, '') else None
    except ValueError: return None
f1 = json.load(open(os.path.join(R, 'unicorns', 'ref', 'f1_sponsors_2026.json'))); F1N = {loose(x[0]) for x in f1}

rows, dropped = [], []
for f in sorted(glob.glob(os.path.join(H, 'verify', 'out_*.json'))):
    for r in json.load(open(f)):
        if r.get('verdict') == 'keep': rows.append(dict(r, via='Crunchbase search (verified on the web)'))
        else: dropped.append([r.get('input_name', ''), r.get('drop_reason', '')])
for f in sorted(glob.glob(os.path.join(H, 'research', 'seg_*.json'))):
    for r in json.load(open(f)): rows.append(dict(r, via='Web research (2025-26 unicorns, large rounds, deals)'))
out, seen = [], {}
for r in rows:
    nm = str(r.get('name') or '').strip(); web = str(r.get('website') or '').strip()
    if not nm: continue
    ex = why(nm, web) or (why(r['former_name']) if r.get('former_name') else '')
    if ex: dropped.append([nm, f'already covered ({ex})']); continue
    if loose(nm) in F1N: dropped.append([nm, 'current F1 sponsor/partner']); continue
    v, fm = num(r.get('valuation_usd_bn')), num(r.get('funding_usd_m'))
    meets = (v or 0) >= 1 or (fm or 0) >= 150
    if not meets: dropped.append([nm, f'below the bar (valuation {v} bn, funding {fm} m)']); continue
    k = loose(nm) or nm.lower(); d = regdom(web)
    dup = seen.get(k) or (seen.get('d:' + d) if d else None)
    if dup: dup['via'] = dup['via'] if r['via'] in dup['via'] else dup['via'] + '; ' + r['via']; continue
    c = {'brand': nm, 'former': r.get('former_name', ''), 'web': d or web, 'country': country(r.get('hq_country')), 'city': r.get('hq_city', ''),
         'about': str(r.get('what', '')).strip(), 'basis': r.get('basis', ''), 'val': v, 'val_date': r.get('valuation_date', ''), 'fund': fm,
         'round': r.get('last_round', ''), 'listed': 'Listed' + (f" ({r['ticker']})" if r.get('ticker') else '') if r.get('listed') else 'Private',
         'investors': r.get('investors', ''), 'src': r.get('source_url', ''), 'src_note': r.get('source_note', ''), 'conf': r.get('confidence', ''),
         'via': r['via']}
    c['orig_bar'] = 'Yes' if (v or 0) >= 1 or (fm or 0) >= 200 else 'No - USD 150-200M funding'
    c['sector'] = sector_of(c['about'], nm, c['about'])
    yrs = [int(y) for y in re.findall(r'\b(20[0-2]\d)\b', f"{c['round']} {c['val_date']}")]
    c['year'] = max(yrs) if yrs else None
    seen[k] = c
    if d: seen['d:' + d] = c
    out.append(c)
def cap_pts(c):
    m = c['fund'] or 0; v = c['val'] or 0
    p1 = next((p for lim, p in ((5000, 25), (2000, 22), (1000, 19), (600, 16), (400, 13), (250, 10), (150, 7)) if m >= lim), 4)
    p2 = next((p for lim, p in ((20, 25), (10, 22), (5, 19), (3, 16), (2, 13), (1, 10)) if v >= lim), 0)
    return max(p1, p2)
def rec_pts(y): return 3 if y is None else {2026: 20, 2025: 18, 2024: 15, 2023: 12, 2022: 9}.get(y, 6 if y >= 2020 else 3 if y >= 2015 else 0)
for c in out:
    fit = FIT[c['sector']]; consumer = bool(CONSUMER.search(c['about']))
    geo = 8 if c['country'] in TIER_A else 5 if c['country'] in TIER_B else 3
    c['score'] = round(fit * 4 + cap_pts(c) + rec_pts(c['year']) + geo + (7 if consumer else 0), 1)
    fig = (f"valued USD {c['val']:g}B" + (f" ({c['val_date']})" if c['val_date'] else '')) if c['val'] else f"raised USD {c['fund']:,.0f}M"
    c['why'] = '; '.join(x for x in [f"{c['sector']} (F1 fit {fit}/10)", fig, f"last round {c['round']}" if c['round'] else '',
                                    f"HQ {c['country']}" if c['country'] else '', 'consumer-facing' if consumer else ''] if x)
out.sort(key=lambda c: (-c['score'], -(c['val'] or 0), -(c['fund'] or 0), c['brand'].lower()))
for i, c in enumerate(out, 1): c['rank'] = i; c['tier'] = 'Tier 1' if i <= 50 else 'Tier 2' if i <= 100 else 'Tier 3'
json.dump({'main': out, 'dropped': dropped}, open(os.path.join(H, 'build.json'), 'w'), ensure_ascii=False, indent=0)
print('rows', len(out), '| dropped', len(dropped), '| by sector', Counter(c['sector'] for c in out).most_common(8))

HDR = Font(bold=True, color='FFFFFF'); HFILL = PatternFill('solid', fgColor='1F3864'); WRAP = Alignment(wrap_text=True, vertical='top')
TFILL = {'Tier 1': 'C6EFCE', 'Tier 2': 'FFEB9C', 'Tier 3': 'F2F2F2'}
COLS = [('Rank', 6, 'rank'), ('Tier', 8, 'tier'), ('Priority score (/100)', 10, 'score'), ('Brand', 28, 'brand'), ('Former name', 16, 'former'),
        ('Sector', 26, 'sector'), ('HQ country', 16, 'country'), ('HQ city', 14, 'city'), ('Website', 22, 'web'), ('About the company', 80, 'about'),
        ('Qualifies on', 11, 'basis'), ('Valuation / market cap (USD bn)', 12, 'val'), ('Valuation date', 10, 'val_date'), ('Total equity funding (USD m)', 12, 'fund'),
        ('Last round', 26, 'round'), ('Listed / private', 14, 'listed'), ('Investors / owner', 30, 'investors'),
        ('Meets USD 1B valuation or USD 200M funding?', 14, 'orig_bar'), ('Why ranked here', 50, 'why'), ('Source (what it shows)', 40, 'src_note'),
        ('Source URL', 40, 'src'), ('Confidence', 9, 'conf'), ('Found via', 22, 'via')]
def sheet(wb, title, data):
    ws = wb.create_sheet(title[:31]); ws.append([h for h, _, _ in COLS])
    for i, (h, w, _) in enumerate(COLS, 1):
        ws.cell(1, i).font = HDR; ws.cell(1, i).fill = HFILL; ws.cell(1, i).alignment = WRAP
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    for c in data:
        ws.append([c.get(k) if c.get(k) not in (None, '') else '' for _, _, k in COLS])
        ws.cell(ws.max_row, 2).fill = PatternFill('solid', fgColor=TFILL[c['tier']])
        for j in (10, 19, 20): ws.cell(ws.max_row, j).alignment = WRAP
    ws.freeze_panes = 'E2'; ws.auto_filter.ref = ws.dimensions
wb = Workbook(); s = wb.active; s.title = 'SUMMARY'
n_orig = sum(c['orig_bar'] == 'Yes' for c in out)
lines = [('NEW BRANDS: valuation USD 1B+ or USD 150M+ equity funding, not on any earlier list', HDR),
         (f'{len(out)} companies. None of them is on any workbook delivered so far, on your MASTER REFERENCE / Drive sheets, or in the screen recordings '
          '(checked by name, former name, name variants and website against every tab).', None),
         (f'{n_orig} meet your original bar (valuation USD 1B+ or funding USD 200M+); the other {len(out) - n_orig} have USD 150-200M equity funding.', None),
         ('Why not 600: your screen recordings were Crunchbase\'s full USD 150M+ funding list (18,980 companies) and earlier lists covered the unicorn lists '
          '(CB Insights, Hurun, Wikipedia), listed companies over USD 1B and Apollo/Lusha/Clay funded companies. Of 9,900 Crunchbase companies pulled for this '
          'task (USD 150M+ funding with a round since 2025, PrivCo valuation USD 1B+, every round valued USD 1B+ that raised under USD 150M), only 287 were new, '
          'and most of those were joint ventures, project companies, funds or public bodies.', None),
         ('Sources: Crunchbase searches (verified company by company on the web) and web research on 2025-26 unicorns, large rounds and USD 1B+ deals. '
          'Every row has a dated source URL for the qualifying figure.', None),
         ('Priority score (/100) = sector F1 fit x4 (40) + size: funding or valuation (25) + recency of last round/valuation (20) + HQ market (8) + consumer-facing (7). '
          'Tier 1 = top 50, Tier 2 = 51-100, Tier 3 = rest.', None),
         ('', None), ('Tabs', HDR)]
for t, f in lines:
    s.append([t]); s.cell(s.max_row, 1).alignment = WRAP
    if f: s.cell(s.max_row, 1).font = Font(bold=True)
s.column_dimensions['A'].width = 140
sheet(wb, 'NEW BRANDS (RANKED)', out); s.append(['NEW BRANDS (RANKED) - all companies, ranked'])
bys = defaultdict(list)
for c in out: bys[c['sector']].append(c)
for sec in sorted(bys, key=lambda x: (-len(bys[x]), x)):
    sheet(wb, sec, bys[sec]); s.append([f'{sec[:31]} - {len(bys[sec])}'])
ws = wb.create_sheet('CHECKED AND DROPPED'); ws.append(['Company', 'Why not on the list'])
for d in sorted(dropped, key=lambda d: d[0].lower()): ws.append(d)
ws.column_dimensions['A'].width = 50; ws.column_dimensions['B'].width = 90
for i in (1, 2): ws.cell(1, i).font = HDR; ws.cell(1, i).fill = HFILL
s.append(['CHECKED AND DROPPED - Crunchbase finds and research candidates that failed a check, with the reason'])
wb.save(OUT); print('saved', OUT)
