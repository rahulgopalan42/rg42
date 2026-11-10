"""QC for the NEW-brands workbook: re-checks build.json and the saved workbook, appends a QC tab.
Usage: qc.py <out.xlsx>"""
import json, os, sys, re
from collections import Counter
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(R, 'brands200'))
from excl import why, why_all
from match import loose, regdom
OUT = sys.argv[1]; d = json.load(open(os.path.join(H, 'build.json'))); main = d['main']
checks = []
def chk(name, ok, detail=''): checks.append(['PASS' if ok else 'FAIL', name, str(detail)])
chk('At least 150 new brands', len(main) >= 150, f'{len(main)} brands')
chk('Ranks run 1..N without gaps', [c['rank'] for c in main] == list(range(1, len(main) + 1)))
kn = Counter(loose(c['brand']) for c in main); kd = Counter(c['web'] for c in main if c['web'])
chk('No company listed twice (name or website)', all(v == 1 for v in kn.values()) and all(v == 1 for v in kd.values()),
    [k for k, v in kn.items() if v > 1] + [k for k, v in kd.items() if v > 1])
bad = [c['brand'] for c in main if why_all(c['brand'], c['former'], c['web'])]
chk('None is on an earlier list, Rahul\'s sheets or the screen recordings (name, former name, variants, website)', not bad, ', '.join(bad))
f1n = {loose(x[0]) for x in json.load(open(os.path.join(R, 'unicorns', 'ref', 'f1_sponsors_2026.json')))}
chk('No current F1 sponsor / partner (2026 rosters)', not [c for c in main if loose(c['brand']) in f1n])
below = [c['brand'] for c in main if not ((c['val'] or 0) >= 1 or (c['fund'] or 0) >= 150)]
chk('Every brand: valuation >= USD 1B or equity funding >= USD 150M', not below, ', '.join(below))
nos = [c['brand'] for c in main if not str(c['src']).startswith('http')]
chk('Every brand has a source URL for its qualifying figure', not nos, ', '.join(nos[:10]))
noc = [c['brand'] for c in main if not c['country']]
chk('Every brand has an HQ country', not noc, ', '.join(noc))
nod = [c['brand'] for c in main if len(c['about']) < 80]
chk('Every brand has a description (80+ characters)', not nod, ', '.join(nod))
wb = load_workbook(OUT, read_only=True)
sec = sum(ws.max_row - 1 for ws in wb.worksheets if ws.title not in ('SUMMARY', 'NEW BRANDS (RANKED)', 'CHECKED AND DROPPED', 'QC'))
chk('Every brand sits on exactly one sector tab', sec == len(main), f'{sec} on sector tabs vs {len(main)}')
wb.close()
wb = load_workbook(OUT)
if 'QC' in wb.sheetnames: del wb['QC']
ws = wb.create_sheet('QC'); ws.append(['Result', 'Check', 'Detail'])
for c in checks: ws.append(c)
ws.column_dimensions['A'].width = 8; ws.column_dimensions['B'].width = 90; ws.column_dimensions['C'].width = 90
wb.save(OUT)
for c in checks: print(' | '.join(c))
print(sum(c[0] == 'PASS' for c in checks), 'of', len(checks), 'pass')
