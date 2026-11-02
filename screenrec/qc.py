"""QC for the screen-recording workbook: re-checks the build output (<out>.json) and the saved workbook, and appends a
QC tab. Also measures how complete the row capture is against an independent full-frame OCR pass of part of one
recording (old3.rows.json: every frame of 3.mov read with text detection, pages 401-900 of USD 284M-326M).
Usage: qc.py <ocr dir> <out.xlsx>"""
import json, os, re, sys, difflib
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(R, 'brands200')); sys.path.insert(0, os.path.join(R, 'parents'))
from match import loose
from sectors_v3 import NAMES
from openpyxl import load_workbook

OCR, OUT = sys.argv[1], sys.argv[2]
d = json.load(open(os.path.join(OCR, 'build.json'))); main, f1 = d['main'], d['f1']
checks = []
def chk(name, ok, detail=''): checks.append(['PASS' if ok else 'FAIL', name, str(detail)])

chk('Ranks run 1..N without gaps', [c['rank'] for c in main] == list(range(1, len(main) + 1)), f'N={len(main)}')
kk = Counter(loose(c['brand']) + '|' + c['country'] for c in main)
dup = [k for k, v in kk.items() if v > 1]
chk('No company listed twice (same name and country)', not dup, ', '.join(dup[:10]))
f1n = {loose(x[0]) for x in json.load(open(os.path.join(R, 'unicorns', 'ref', 'f1_sponsors_2026.json')))}
bad = [c['brand'] for c in main if loose(c['brand']) in f1n and c['brand'] not in ('Paramount Group',)]
chk('No current F1 sponsor / partner on the prospect tabs (2026 rosters)', not bad, f'{len(f1)} on their own tab; Paramount Group kept (name collision with Paramount+) ' + ', '.join(bad[:5]))
chk('Every prospect has a sector from the 48', all(c['sector'] in NAMES for c in main), Counter(c['sector'] for c in main).most_common(3))
nc = [c for c in main if not c['country']]
chk('HQ country found for >= 97% of prospects (the rest: HQ cut off or blank in Crunchbase; HQ location column shows what was on screen)', len(nc) <= 0.03 * len(main), f'{len(nc)} without a country ({len(nc) / len(main):.1%}): ' + '; '.join(c['hq'] for c in nc[:8]))
m1 = [c for c in main if not c['listed']]
chk('Every prospect in the USD 150M+ search has a description', sum(1 for c in m1 if not c['desc']) <= 0.01 * len(m1), f"{sum(1 for c in m1 if not c['desc'])} of {len(m1)} without (8.mov listed-company rows have none: column off screen)")
wb = load_workbook(OUT, read_only=True)
sec = sum(ws.max_row - 1 for ws in wb.worksheets if ws.title[:31] in {n[:31] for n in NAMES})
chk('Every prospect sits on exactly one sector tab', sec == len(main), f'{sec} on sector tabs vs {len(main)} prospects')
wb.close()
# capture completeness vs an independent full-frame OCR of 3.mov
old = os.path.join(OCR, 'old3.rows.json')
if os.path.exists(old):
    o = json.load(open(old))['rows']
    on = {re.sub(r'[^a-z0-9]', '', r['name'].lower()) for r in o if (r.get('page_start') or 0) in range(451, 901) and len(r['name']) > 3}
    allnames = [re.sub(r'[^a-z0-9]', '', c['brand'].lower()) for c in main + f1]
    hit = sum(1 for n in on if difflib.get_close_matches(n, allnames, 1, 0.8))
    chk('Row capture vs independent full-frame OCR of 3.mov (pages 451-900)', hit >= 0.95 * len(on), f'{hit} of {len(on)} names found ({hit / max(len(on), 1):.1%})')
bands = d['bands']
short = [f"{b[0]}: {b[3]} rows of {b[1]}" for b in bands if b[5] and b[3] < 0.9 * b[1]]
chk('Funding ranges: companies read vs results Crunchbase shows (>= 90%)', not short, '; '.join(short[:10]) or 'all ranges >= 90%')

wb = load_workbook(OUT)
if 'QC' in wb.sheetnames: del wb['QC']
ws = wb.create_sheet('QC'); ws.append(['Result', 'Check', 'Detail'])
for c in checks: ws.append(c)
ws.column_dimensions['A'].width = 8; ws.column_dimensions['B'].width = 80; ws.column_dimensions['C'].width = 100
wb.save(OUT)
for c in checks: print(' | '.join(c))
print(sum(c[0] == 'PASS' for c in checks), 'of', len(checks), 'pass')
