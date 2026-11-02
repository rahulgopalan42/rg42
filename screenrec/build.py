"""Build the F1 prospect workbook from the Crunchbase screen recordings.

Inputs: <ocr dir>/*.rows.json written by parse.py (one per recording or recording part).
Steps: funding-range coverage and page completeness check -> dedupe across pages / ranges / recordings -> HQ country
-> sector (48 sectors) with the Crunchbase industries as subsector -> current F1 sponsors set aside on their own tab
-> overlaps with earlier lists flagged (kept) -> F1 priority score and tiers -> workbook.
Usage: build.py <ocr dir> <out.xlsx>"""
import json, os, re, sys, glob, difflib, datetime
from collections import defaultdict
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(R, 'brands200'))
from geo import country_of
from sectors_cb import sector_of, FIT, CONSUMER, industries
from sectors_v3 import NAMES, OTHER
from match import loose, present, regdom
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OCR, OUT = sys.argv[1], sys.argv[2]
# recording part -> (file shown to the user, offset of the part in the video, seconds)
PARTS = {'6a': ('6.mov', 0), '6b': ('6.mov', 845)}
LOWCONF = 0.85

def fmt_m(v):
    if v is None: return ''
    return f'USD {v / 1000:g}B' if v >= 1000 else f'USD {v:g}M'
def band_txt(lo, hi): return f'{fmt_m(lo)} - {fmt_m(hi)}'
def mmss(s): s = int(s); return f'{s // 60}:{s % 60:02d}'

# ---------- load ----------
rows, pages = [], []
for f in sorted(glob.glob(os.path.join(OCR, '*.rows.json'))):
    part = os.path.basename(f).replace('.rows.json', '')
    if part.startswith('old') or part.startswith('t'): continue
    rec, off = PARTS.get(part, (part + '.mov', 0))
    d = json.load(open(f))
    for r in d['rows']: rows.append(dict(r, rec=rec, at=r['t'] + off))
    for p in d['pages']: pages.append(dict(p, rec=rec, at=p['t'] + off))
print('raw rows', len(rows), 'pages', len(pages))

# ---------- ranges and pages ----------
bands = defaultdict(lambda: {'recs': set(), 'results': defaultdict(int), 'pages': {}, 'rows': 0})
for p in pages:
    b = (p['band'][0], p['band'][1]); B = bands[b]; B['recs'].add(p['rec']); B['results'][p['results']] += 1
    k = p['start']
    if k not in B['pages'] or p['rows'] > B['pages'][k]['rows']: B['pages'][k] = p
for b, B in bands.items():
    B['n_results'] = max(B['results'], key=B['results'].get)
    B['rows'] = sum(p['rows'] for p in B['pages'].values())
band_list = sorted(bands, key=lambda b: (b[0], b[1]))

# ---------- dedupe ----------
def tot_digits(r): return re.sub(r'[^0-9]', '', str(r.get('total', '')))
def clean_name(n):
    n = re.sub(r'\s+', ' ', str(n or '')).strip()
    n = re.sub(r'^[^A-Za-z0-9一-鿿]+', '', n)
    return n
for r in rows:
    r['name'] = clean_name(r.get('name'))
    r['country'] = country_of(r.get('hq', ''))
    r['band'] = (r['band_lo'], r['band_hi'])
rows = [r for r in rows if len(r['name']) >= 2]
groups = []                     # union by (loose name, country) or (similar name, same total funding)
idx_name = defaultdict(list); idx_tot = defaultdict(list)
for r in sorted(rows, key=lambda r: -(r.get('name_conf') or 0)):
    ln = loose(r['name']) or r['name'].lower(); td = tot_digits(r); hit = None
    for g in idx_name.get(ln, []):
        if not r['country'] or not g['country'] or g['country'] == r['country']: hit = g; break
    if hit is None and td:
        for g in idx_tot.get(td, []):
            if difflib.SequenceMatcher(None, r['name'].lower(), g['name'].lower()).ratio() >= 0.85: hit = g; break
    if hit is None:
        hit = {'name': r['name'], 'country': r['country'], 'obs': []}; groups.append(hit)
        idx_name[ln].append(hit)
        if td: idx_tot[td].append(hit)
    hit['obs'].append(r)
print('companies after dedupe', len(groups))

def pick(obs, f):
    v = defaultdict(float)
    for o in obs:
        if o.get(f): v[o[f]] += (o.get(f + '_conf') or 0.5) * o.get('seen', 1)
    return max(v, key=v.get) if v else ''

def year_of(d):
    m = re.search(r'(19|20)\d\d', str(d or '')); return int(m.group(0)) if m else None

f1 = json.load(open(os.path.join(R, 'unicorns', 'ref', 'f1_sponsors_2026.json')))
F1N = defaultdict(list)
for x in f1:
    k = loose(x[0])
    if k and len(k) >= 3: F1N[k].append(f'{x[2]}: {x[3]} ({x[4]})')
sent_u = {loose(n) for n, _ in json.load(open(os.path.join(R, 'unicorns', 'ref', 'sent_unicorns_30oct.json')))} - {''}
try:
    import pandas as pd
    nb = pd.read_pickle(os.path.join(R, 'brands200', 'new_brands.pkl')); NB = set(nb['brand'].map(loose)) - {''}
except Exception: NB = set()
TIER_A = {'United States', 'United Kingdom', 'United Arab Emirates', 'Saudi Arabia', 'Qatar', 'Netherlands', 'Germany', 'Switzerland', 'Japan', 'Singapore',
          'France', 'Italy', 'Spain', 'Monaco', 'China', 'Hong Kong', 'Australia', 'Canada', 'Brazil', 'Mexico', 'India', 'Bahrain', 'Azerbaijan', 'Austria', 'Belgium', 'Hungary'}
TIER_B = {'Sweden', 'Norway', 'Denmark', 'Finland', 'Ireland', 'Israel', 'South Korea', 'Taiwan', 'Luxembourg', 'Portugal', 'Poland', 'Turkey', 'Indonesia',
          'Malaysia', 'Thailand', 'Kuwait', 'Oman', 'Argentina', 'Chile', 'Colombia', 'New Zealand', 'South Africa', 'Czech Republic', 'Estonia', 'Greece', 'Cyprus', 'Malta'}

def cap_pts(m):
    for lim, pts in ((5000, 25), (2000, 22), (1000, 19), (600, 16), (400, 13), (250, 10), (150, 7)):
        if m >= lim: return pts
    return 4
def rec_pts(y):
    if y is None: return 3
    return {2026: 20, 2025: 18, 2024: 15, 2023: 12, 2022: 9}.get(y, 6 if y >= 2020 else 3 if y >= 2015 else 0)

out = []
for g in groups:
    obs = g['obs']; best = max(obs, key=lambda o: (o.get('seen', 1), o.get('name_conf') or 0))
    c = {'brand': pick(obs, 'name') or g['name']}
    for f in ('total', 'date', 'ind', 'hq', 'desc', 'ipo'): c[f] = pick(obs, f)
    c['country'] = country_of(c['hq']) or g['country']
    bset = sorted({o['band'] for o in obs}); c['bands'] = bset
    c['band_lo'] = min(b[0] for b in bset); c['band_hi'] = max(b[1] or b[0] for b in bset)
    c['mid'] = (c['band_lo'] + c['band_hi']) / 2
    c['src'] = '; '.join(sorted({f"{o['rec']} @ {mmss(o['at'])}" for o in obs})[:3])
    c['name_conf'] = max((o.get('name_conf') or 0) for o in obs); c['seen'] = sum(o.get('seen', 1) for o in obs)
    c['sector'] = sector_of(c['ind'], c['brand'], c['desc'])
    c['subsector'] = ', '.join(industries(c['ind']))
    c['year'] = year_of(c['date'])
    ln = loose(c['brand'])
    c['f1'] = '; '.join(sorted(set(F1N.get(ln, []))))
    flags = []
    on = present(c['brand'])
    if on in ('name', 'website'): flags.append('already on your sheets')
    elif on: flags.append('possible match on your sheets (' + on + ')')
    if ln in sent_u: flags.append('on the 30 Oct unicorn list')
    if ln in NB: flags.append('on the 30 Oct new-brands list')
    if len(bset) > 1: flags.append('shown in two funding ranges (boundary)')
    if str(c['ipo']).lower().startswith('public'): flags.append('listed (IPO status: public)')
    if c['year'] is not None and c['year'] < 2015: flags.append(f'last funding {c["year"]}: check it is still independent and operating')
    if c['name_conf'] < LOWCONF: flags.append('name read with low OCR confidence: check spelling')
    if c['sector'] == 'Tobacco & Nicotine': flags.append('tobacco / nicotine / cannabis: F1 advertising restrictions')
    c['flags'] = '; '.join(flags)
    fit = FIT[c['sector']]
    consumer = bool(CONSUMER.search(c['ind'] + ' ' + c['desc']))
    geo = 8 if c['country'] in TIER_A else 5 if c['country'] in TIER_B else 3
    c['score'] = round(fit * 4 + cap_pts(c['mid']) + rec_pts(c['year']) + geo + (7 if consumer else 0), 1)
    why = [f"{c['sector']} (F1 fit {fit}/10)", f"raised {band_txt(c['band_lo'], c['band_hi'])}"]
    if c['year']: why.append(f"last round {c['date']}")
    if c['country']: why.append(f"HQ {c['country']}")
    if consumer: why.append('consumer-facing')
    c['why'] = '; '.join(why)
    out.append(c)

main = [c for c in out if not c['f1']]; f1rows = [c for c in out if c['f1']]
main.sort(key=lambda c: (-c['score'], -c['mid'], c['brand'].lower()))
for i, c in enumerate(main, 1):
    c['rank'] = i
    c['tier'] = 'Tier 1' if c['score'] >= 72 else 'Tier 2' if c['score'] >= 60 else 'Tier 3' if c['score'] >= 48 else 'Tier 4'
f1rows.sort(key=lambda c: -c['score'])
print('main', len(main), 'current F1', len(f1rows))

# ---------- workbook ----------
HDR = Font(bold=True, color='FFFFFF'); HFILL = PatternFill('solid', fgColor='1F3864'); BOLD = Font(bold=True)
TFILL = {'Tier 1': 'C6EFCE', 'Tier 2': 'FFEB9C', 'Tier 3': 'F2F2F2', 'Tier 4': 'FFFFFF'}
COLS = [('Rank', 7, 'rank'), ('Tier', 8, 'tier'), ('Priority score (/100)', 10, 'score'), ('Brand', 30, 'brand'), ('Sector', 26, 'sector'),
        ('Subsector (Crunchbase industries)', 34, 'subsector'), ('HQ country', 16, 'country'), ('HQ location (Crunchbase)', 30, 'hq'),
        ('Description (Crunchbase)', 60, 'desc'), ('Total funding (as shown)', 18, 'total'), ('Funding range filter (USD)', 22, 'range'),
        ('Last funding date', 14, 'date'), ('Why this rank', 60, 'why'), ('Flags', 50, 'flags'), ('Seen in recording', 26, 'src')]
def sheet(wb, title, data, cols=COLS, tier=True):
    ws = wb.create_sheet(title[:31])
    ws.append([h for h, _, _ in cols])
    for i, (h, w, _) in enumerate(cols, 1):
        cl = ws.cell(1, i); cl.font = HDR; cl.fill = HFILL; cl.alignment = Alignment(wrap_text=True, vertical='center')
        ws.column_dimensions[get_column_letter(i)].width = w
    for c in data:
        c['range'] = ' | '.join(band_txt(*b) for b in c['bands'])
        ws.append([c.get(k, '') for _, _, k in cols])
        if tier and c.get('tier'):
            ws.cell(ws.max_row, 2).fill = PatternFill('solid', fgColor=TFILL[c['tier']])
    ws.freeze_panes = 'E2'; ws.auto_filter.ref = ws.dimensions
    return ws

wb = Workbook(); ws = wb.active; ws.title = 'SUMMARY'
n_t = defaultdict(int)
for c in main: n_t[c['tier']] += 1
lines = [
    ('F1 sponsorship prospects from your Crunchbase screen recordings', BOLD),
    (f'Built {datetime.date.today():%d %b %Y} from {len({p["rec"] for p in pages})} recordings: every company shown in the results tables was read frame by frame (OCR).', None),
    ('', None),
    (f'Companies captured (after removing repeats): {len(out)}', BOLD),
    (f'  Ranked prospects: {len(main)}  (Tier 1: {n_t["Tier 1"]}, Tier 2: {n_t["Tier 2"]}, Tier 3: {n_t["Tier 3"]}, Tier 4: {n_t["Tier 4"]})', None),
    (f'  Already F1 sponsors / partners in 2026 (own tab): {len(f1rows)}', None),
    (f'  Also on earlier lists (kept, flagged in the Flags column): {sum(1 for c in out if "list" in c["flags"] or "sheets" in c["flags"])}', None),
    ('', None),
    ('Funding ranges in the recordings: see RANGES CHECK (gaps, overlaps, pages captured per range).', BOLD),
    ('', None),
    ('Priority score (/100) = sector F1 fit x4 (40) + funding raised (25) + recency of last round (20) + HQ market (8) + consumer-facing (7).', None),
    ('Tier 1 >= 72, Tier 2 60-71, Tier 3 48-59, Tier 4 < 48.', None),
    ('Sector: same 48 sectors as the earlier lists, chosen from the Crunchbase industries, name and description. Subsector = the Crunchbase industries shown.', None),
    ('Country: from the Crunchbase HQ location (the table cuts long locations short; the state / province decides when the country is cut off).', None),
    ('', None),
    ('Read before outreach', BOLD),
    ('- The Crunchbase searches were not limited to active, independent companies: many older names (last round before 2015) have since been', None),
    ('  acquired, listed or closed. They are kept (you asked for every brand) but flagged and ranked lower.', None),
    ('- Names and figures were read by OCR from video. Rows with low read confidence are flagged; spot-check those against Crunchbase.', None),
    ('- Total funding is shown as Crunchbase displays it (local currency for some companies); the range filter column is the USD range.', None),
]
for t, f_ in lines:
    ws.append([t]);
    if f_: ws.cell(ws.max_row, 1).font = f_
ws.column_dimensions['A'].width = 140

# ranges check
wr = wb.create_sheet('RANGES CHECK')
wr.append(['Funding range (USD)', 'Recording(s)', 'Results Crunchbase shows', 'Pages of 50 needed', 'Pages captured', 'Pages missing',
           'Companies read', 'Coverage', 'Next range starts at', 'Gap / overlap to next range'])
for i, b in enumerate(band_list):
    B = bands[b]; need = -(-B['n_results'] // 50); have = sorted(B['pages'])
    miss = [f'{s}-{min(s + 49, B["n_results"])}' for s in range(1, B['n_results'] + 1, 50) if s not in B['pages']]
    nxt = band_list[i + 1] if i + 1 < len(band_list) else None
    if nxt is None: gap = 'last range'
    elif b[1] is None: gap = '?'
    elif abs(nxt[0] - b[1]) < 0.01: gap = 'contiguous'
    elif nxt[0] > b[1]: gap = f'GAP: {fmt_m(b[1])} - {fmt_m(nxt[0])} not covered'
    else: gap = f'overlap {fmt_m(nxt[0])} - {fmt_m(min(b[1], nxt[1] or b[1]))}'
    wr.append([band_txt(*b), ', '.join(sorted(B['recs'])), B['n_results'], need, len(have), ', '.join(miss) or 'none', B['rows'],
               f"{B['rows'] / max(B['n_results'], 1):.0%}", fmt_m(nxt[0]) if nxt else '', gap])
for i, w in enumerate([26, 16, 12, 10, 10, 40, 10, 9, 14, 40], 1): wr.column_dimensions[get_column_letter(i)].width = w
for cl in wr[1]: cl.font = HDR; cl.fill = HFILL; cl.alignment = Alignment(wrap_text=True)
wp = wb.create_sheet('PAGE CHECK')
wp.append(['Funding range (USD)', 'Page', 'Companies read', 'Companies on page', 'Recording', 'At (mm:ss)'])
for b in band_list:
    B = bands[b]
    for s in sorted(B['pages']):
        p = B['pages'][s]; exp = min(50, B['n_results'] - s + 1)
        wp.append([band_txt(*b), f'{s}-{s + exp - 1}', p['rows'], exp, p['rec'], mmss(p['at'])])
for i, w in enumerate([26, 12, 10, 10, 12, 10], 1): wp.column_dimensions[get_column_letter(i)].width = w
for cl in wp[1]: cl.font = HDR; cl.fill = HFILL

sheet(wb, 'ALL PROSPECTS (RANKED)', main)
F1COLS = [('Brand', 30, 'brand'), ('Current F1 deal (2026 rosters)', 60, 'f1'), ('Sector', 26, 'sector'), ('Subsector (Crunchbase industries)', 34, 'subsector'),
          ('HQ country', 16, 'country'), ('Description (Crunchbase)', 60, 'desc'), ('Total funding (as shown)', 18, 'total'),
          ('Funding range filter (USD)', 22, 'range'), ('Last funding date', 14, 'date'), ('Seen in recording', 26, 'src')]
sheet(wb, 'ALREADY F1 SPONSORS', f1rows, F1COLS, tier=False)
by_sec = defaultdict(list)
for c in main: by_sec[c['sector']].append(c)
for s in NAMES:
    if by_sec.get(s): sheet(wb, s.replace('/', '-'), by_sec[s])
json.dump({'main': main, 'f1': f1rows, 'bands': [[list(b), bands[b]['n_results'], len(bands[b]['pages']), bands[b]['rows'], sorted(bands[b]['recs'])] for b in band_list]},
          open(OUT.replace('.xlsx', '.json'), 'w'), default=str)
wb.save(OUT)
print('saved', OUT)
for b in band_list:
    B = bands[b]; print(f"  {band_txt(*b):28} results {B['n_results']:5}  pages {len(B['pages']):3}/{-(-B['n_results'] // 50):3}  rows {B['rows']:5}  recs {sorted(B['recs'])}")
