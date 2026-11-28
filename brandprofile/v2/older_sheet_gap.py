"""Usage: older_sheet_gap.py <all-sector list.xlsx> <output.xlsx>
Brands that are on the user's older 48-tab sheet, qualified on the 23 Nov all-sector list, and are NOT on the master,
not in a delivered batch and not current F1 partners. One tab per sector, public-company column order, plus where each
brand sits on the older sheet and whether the user marked it x. These were scored under the 16-18 Nov rules, not the new method."""
import os, re, sys
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from openpyxl import Workbook, load_workbook
import build as B, check as C, public_format as P
src, out = sys.argv[1], sys.argv[2]
ws = load_workbook(src, read_only=True)['Prospects - All Sectors']; rows = ws.iter_rows(values_only=True); h = list(next(rows))
COLS = h[:22] + ['Tab in Your Older Sheet', 'Marked "x" in Your Older Sheet']; xi = h.index('Marked "x" in Your Sheet'); ti = h.index('Tab in Your Sheet'); ni = h.index('Company Name')
PR = {'High': 0, 'Medium': 1, 'To Verify': 2}; seen = set(); tabs = defaultdict(list); st = Counter()
for r in rows:
    if not r[ni]: continue
    nm = str(r[ni]).strip()
    if nm.lower() in seen: continue
    seen.add(nm.lower()); s, disp, sr, hits = C.lookup(nm)
    k = 'delivered in batch 1 or 2' if s == 'dup' and sr.startswith('delivered') else {'dup': 'on the master', 'f1': 'current F1 partner'}.get(s, 'not on the master')
    st[k] += 1
    if k != 'not on the master': continue
    sec = B.SECKEY.get(B.norm(str(r[5] or '').split(':')[0])) or 'Diversified & Other'
    tabs[sec].append(list(r[:22]) + [r[ti] or '', 'x' if str(r[xi] or '').strip().lower() in ('x', 'yes', 'true') else ''])
P.COLS = COLS; P.WIDTH = P.WIDTH + [30, 12]
wb = Workbook(); n = 0; made = []
for s in B.SECTORS:
    L = sorted(tabs.get(s, []), key=lambda r: (PR.get(r[3], 3), -(r[21] if isinstance(r[21], (int, float)) else 0), str(r[0]).lower()))
    if not L: continue
    n += 1; t = f'{n:02d} {P.SHORT.get(s, s)}'; P.sheet(wb, t, L, first=(n == 1)); made.append((t[:31], len(L)))
wb.save(out)
print(dict(st)); print(out, sum(k for t, k in made), 'brands', len(made), 'tabs', round(os.path.getsize(out) / 1024), 'KB')
allr = [r for L in tabs.values() for r in L]
print('priority', Counter(r[3] for r in allr).most_common(), '| x-marked', sum(1 for r in allr if r[23] == 'x'), '| reach', Counter(r[13] for r in allr).most_common())
print('biggest tabs', sorted(made, key=lambda x: -x[1])[:8])
print('top tabs on the older sheet', Counter(r[22] for r in allr).most_common(8))
