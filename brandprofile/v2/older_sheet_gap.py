"""Usage: older_sheet_gap.py <all-sector list.xlsx> <output.xlsx>
Brands that are on the user's older 48-tab sheet, qualified on the 23 Nov all-sector list, and are NOT on the master,
not in a delivered batch and not current F1 partners. One tab per sector, public-company column order, plus where each
brand sits on the older sheet and whether the user marked it x. These were scored under the 16-18 Nov rules, not the new method.
Brands that already have a template on the user's trackers (templates.py) are flagged in the last column and their rows are
filled green; a tab that holds a green row gets a green tab colour (user's request of 28 Nov 2026)."""
import os, re, sys
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from openpyxl import Workbook, load_workbook
import gzip, json
from openpyxl.styles import PatternFill
import build as B, check as C, public_format as P, templates as TP
GREEN = PatternFill('solid', start_color='FF92D050', end_color='FF92D050'); TABGREEN = 'FF00B050'; TCOL = 'Template Already Built? (Your Trackers)'
from older import MARKED_TABS, marking, sheet_tabs          # the user's marks and how to read them: older.py
src, out = sys.argv[1], sys.argv[2]
ws = load_workbook(src, read_only=True)['Prospects - All Sectors']; rows = ws.iter_rows(values_only=True); h = list(next(rows))
COLS = h[:22] + ['Tab in Your Older Sheet', 'Your Marking on the Older Sheet', TCOL]; xi = h.index('Marked "x" in Your Sheet'); ti = h.index('Tab in Your Sheet'); ni = h.index('Company Name'); bi = h.index('Brand Name in Your Sheet')
PR = {'High': 0, 'Medium': 1, 'To Verify': 2}; seen = set(); tabs = defaultdict(list); st = Counter()
for r in rows:
    if not r[ni]: continue
    nm = str(r[ni]).strip()
    if nm.lower() in seen: continue
    seen.add(nm.lower()); s, disp, sr, hits = C.lookup(nm, batch='older')
    k = 'delivered in batch 1 or 2' if s == 'dup' and sr.startswith('delivered') else {'dup': 'on the master', 'f1': 'current F1 partner'}.get(s, 'not on the master')
    st[k] += 1
    if k != 'not on the master': continue
    sec = B.SECKEY.get(B.norm(str(r[5] or '').split(':')[0])) or 'Diversified & Other'
    mk = marking([r[bi], nm], r[ti])
    if str(r[xi] or '').strip().lower() in ('x', 'yes', 'true'): mk = 'x: template wanted'
    tabs[sec].append(list(r[:22]) + [sheet_tabs([r[bi], nm], r[ti]), mk, TP.note(nm)])
P.COLS = COLS; P.WIDTH = P.WIDTH + [30, 40, 48]
wb = Workbook(); n = 0; made = []; green = Counter()
for s in B.SECTORS:
    L = sorted(tabs.get(s, []), key=lambda r: (PR.get(r[3], 3), -(r[21] if isinstance(r[21], (int, float)) else 0), str(r[0]).lower()))
    if not L: continue
    n += 1; t = f'{n:02d} {P.SHORT.get(s, s)}'; ws = P.sheet(wb, t, L, first=(n == 1)); made.append((t[:31], len(L)))
    for i, r in enumerate(L, 2):
        if not r[24]: continue
        ws.cell(i, 25).alignment = P.WRAP
        if r[24].startswith('Yes'):
            green[t[:31]] += 1
            for j in range(1, len(COLS) + 1): ws.cell(i, j).fill = GREEN
    if green[t[:31]]: ws.sheet_properties.tabColor = TABGREEN
wb.save(out)
print(dict(st)); print(out, sum(k for t, k in made), 'brands', len(made), 'tabs', round(os.path.getsize(out) / 1024), 'KB')
allr = [r for L in tabs.values() for r in L]
print('green rows (template built):', sum(green.values()), 'on', len([t for t in green if green[t]]), 'tabs;', 'on a tracker but not built:', [r[0] for r in allr if r[24].startswith('No')])
print('green by tab', green.most_common()); print('green by marking', Counter(r[23][:22] for r in allr if r[24].startswith('Yes')).most_common(), '| x-marked with no template:', sum(1 for r in allr if r[23].startswith('x') and not r[24].startswith('Yes')))
print('marking', Counter(r[23] for r in allr).most_common())
bt = defaultdict(Counter)
for r in allr:
    for t in r[22].split('; '): bt[t][r[23][:5]] += 1
print('marked tabs:', {t: dict(c) for t, c in bt.items() if t in MARKED_TABS})
print('tabs not gone through:', len([t for t in bt if t not in MARKED_TABS]), sum(sum(c.values()) for t, c in bt.items() if t not in MARKED_TABS))
print('biggest tabs', sorted(made, key=lambda x: -x[1])[:8])
print('top tabs on the older sheet', Counter(r[22] for r in allr).most_common(8))
