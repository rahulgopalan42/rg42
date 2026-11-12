"""Sector coverage review workbook: for each of the 17 priority sectors, which brands the delivered lists already
hold (and at what level of research), and which well-known names are missing.
Inputs: result.json.gz (classify.py --save) and notes.py (verdict and note per sector).  Usage: report.py <out.xlsx>"""
import gzip, json, os, sys
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
try: from notes import NOTES
except ImportError: NOTES = {}
OUT = sys.argv[1] if len(sys.argv) > 1 else None
res = json.load(gzip.open(os.path.join(H, 'result.json.gz'), 'rt'))
STATUS = {'good': 'On a researched prospect list', 'rec': 'Only in the screen-recordings list', 'low': 'Only in a database list (never researched)',
          'rejected': 'Looked at earlier and rejected', 'f1': 'Current F1 sponsor', 'index': 'Named only under a parent company or in a research pool',
          'none': 'On no list'}
ORD = ['good', 'rec', 'low', 'rejected', 'f1']
summ = []
for r in res:
    lv = Counter(x[3] for x in r['rows']); sd = Counter(x[1] for x in r['seeds']); n = len(r['seeds'])
    summ.append({'id': r['id'], 'name': r['name'], 'group': r['group'], 'good': lv['good'], 'rec': lv['rec'], 'low': lv['low'], 'rej': lv['rejected'],
                 'seeds': n, 's_good': sd['good'], 's_other': sd['rec'] + sd['low'], 's_index': sd['index'] + sd['rejected'], 's_none': sd['none'],
                 'share': sd['good'] / n if n else 0})
if not OUT:
    for s in summ: print(f"{s['id']} {s['name'][:44]:44s} researched {s['good']:5d} rec {s['rec']:4d} db {s['low']:5d} | names {s['seeds']:3d}: res {s['s_good']:3d} ({s['share']:.0%}) rec/db {s['s_other']:3d} parent/pool {s['s_index']:3d} none {s['s_none']:3d}")
    for r in res:
        print('\n' + r['id'], r['name']); 
        for k in ('none', 'index', 'low', 'rec'): print(f'  {k}:', ', '.join(x[0] for x in r['seeds'] if x[1] == k)[:1400])
    sys.exit()
HDR = Font(bold=True, color='FFFFFF'); HFILL = PatternFill('solid', fgColor='1F3864'); WRAP = Alignment(wrap_text=True, vertical='top')
VFILL = {'Created': 'C6EFCE', 'Created - top up': 'FFEB9C', 'Thin - start generating': 'F8CBAD', 'Not created - start generating': 'F4B084'}
wb = Workbook(); ws = wb.active; ws.title = 'SUMMARY'
intro = ['SECTOR COVERAGE REVIEW: have brands been created for the 17 priority sectors?',
         'Checked: every tab of every workbook delivered so far (44 workbooks, 338,525 different brands). A brand counts for a sector if its category or '
         'description on those lists matches the sector, or it is one of the sector\'s well-known names.',
         'Three levels: (1) on a researched prospect list = someone looked at the company (verdict Yes / Stretch, verified ranking, unicorn / parent / new-brand '
         'lists); (2) only in the screen-recordings list = Crunchbase, USD 150M+ funding, described and ranked but not qualified one by one; (3) only in a '
         'database list = pulled from Clay / Apollo with a revenue estimate, never researched (Wave 16 preliminary ranking, Wave 15 "Low-value", raw sweeps).',
         '"Well-known names" = a checklist I wrote from my own knowledge for each sector (100-370 names). It is not exhaustive and the names were not checked '
         'for affordability; it measures how much of each sector the lists already hold. Counts by keyword are approximate (roughly 10-15% noise).',
         'Verdict = share of the well-known names that are on a researched list: 65% or more = Created; 55-64% = Created - top up; under 55% = Thin - start '
         'generating. No sector is empty. "On no list" can include product brands whose parent company is listed. Names to generate are on the NAMES TO ADD tab.', '']
for t in intro:
    ws.append([t]); ws.cell(ws.max_row, 1).alignment = WRAP
ws.cell(1, 1).font = Font(bold=True, size=13)
for i in range(2, 6): ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=12); ws.row_dimensions[i].height = 48
cols = [('#', 5), ('Sector', 40), ('Group', 14), ('Brands on researched lists', 12), ('Only in screen recordings', 12), ('Only in database lists (never researched)', 14),
        ('Well-known names checked', 11), ('...on researched lists', 11), ('...only in recordings / database', 12), ('...only under a parent or in a pool, or rejected', 14),
        ('...on no list', 9), ('Verdict', 22), ('Note: what to generate', 90)]
ws.append([c for c, _ in cols]); h = ws.max_row
for i, (c, w) in enumerate(cols, 1):
    x = ws.cell(h, i); x.font = HDR; x.fill = HFILL; x.alignment = WRAP; ws.column_dimensions[x.column_letter].width = w
for s in summ:
    v, note = NOTES.get(s['id'], ('', ''))
    ws.append([s['id'], s['name'], s['group'], s['good'], s['rec'], s['low'], s['seeds'], f"{s['s_good']} ({s['share']:.0%})", s['s_other'], s['s_index'], s['s_none'], v, note])
    ws.cell(ws.max_row, 13).alignment = WRAP; ws.cell(ws.max_row, 2).alignment = WRAP
    if v in VFILL: ws.cell(ws.max_row, 12).fill = PatternFill('solid', fgColor=VFILL[v])
ws.freeze_panes = ws.cell(h + 1, 3)
# names to add
wn = wb.create_sheet('NAMES TO ADD'); wn.append(['Sector', 'Company', 'Status', 'Found on the lists as'])
for r in res:
    for nm, lv, as_ in sorted(r['seeds'], key=lambda x: (['none', 'index', 'low', 'rec', 'rejected', 'good', 'f1'].index(x[1]), x[0].lower())):
        if lv in ('good', 'f1'): continue
        wn.append([f"{r['id']} {r['name']}", nm, STATUS[lv], as_ if as_ and as_ != nm else ''])
for i, w in enumerate((48, 36, 50, 40), 1):
    x = wn.cell(1, i); x.font = HDR; x.fill = HFILL; wn.column_dimensions[x.column_letter].width = w
wn.freeze_panes = 'A2'; wn.auto_filter.ref = wn.dimensions
# one tab per sector
SC = [('Brand', 34), ('HQ', 18), ('Website', 22), ('Status', 40), ('Current F1 sponsor tab', 10), ('Where it appears (workbook > tab)', 70), ('Category / what it does', 90), ('Matched by', 12)]
for r in res:
    t = wb.create_sheet(f"{r['id']} {r['name']}"[:31].replace('/', '-')); t.append([c for c, _ in SC])
    for i, (c, w) in enumerate(SC, 1):
        x = t.cell(1, i); x.font = HDR; x.fill = HFILL; t.column_dimensions[x.column_letter].width = w
    for nm, ctry, web, lv, f1, where, txt, hit in sorted(r['rows'], key=lambda x: (ORD.index(x[3]), x[0].lower())):
        t.append([nm, ctry, web, STATUS[lv], 'yes' if f1 else '', where, txt, hit])
    t.freeze_panes = 'B2'; t.auto_filter.ref = t.dimensions
wb.save(OUT); print('saved', OUT, [(s['id'], s['good']) for s in summ])
