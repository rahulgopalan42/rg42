"""Usage: validate.py <workbook.xlsx> <batch> [master.xlsx]
Checks a delivered workbook: same columns on every main tab, ranks contiguous, no company twice, nothing on the master or in an earlier batch."""
import json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from openpyxl import load_workbook
import check as C
path, batch = sys.argv[1], sys.argv[2]; master = sys.argv[3] if len(sys.argv) > 3 else None
wb = load_workbook(path, read_only=True); print(len(wb.sheetnames), 'tabs')
skip = {'Summary', 'Research Coverage', 'Supporting Research', 'Methodology', 'Backtest', 'Backtest - Sponsors', 'Research Record', 'Excluded', 'Key', 'Discovered - To Assess', 'Discovery Register'}
side = {'Verification Watchlist', 'Clay Leads (Unconfirmed)'}
hdr0 = None; names = {}; bad = 0; cnt = {}; cons = set()
for ws in wb.worksheets:
    if ws.title in skip: continue
    rows = list(ws.iter_rows(values_only=True)); h = rows[0]
    if hdr0 is None: hdr0 = h
    if h != hdr0: print('HEADER DIFFERS', ws.title); bad += 1
    ns = [r[0] for r in rows[1:] if r[0]]; cnt[ws.title] = len(ns)
    if ws.title == 'Consolidated Ranking':
        ri = h.index('Outreach Rank (All Sectors)'); rk = [r[ri] for r in rows[1:] if r[0]]; si = h.index('Overall Score (0-100)'); sc = [r[si] for r in rows[1:] if r[0]]; pi = h.index('Outreach Priority')
        print('consolidated', len(rk), '| ranks contiguous', rk == list(range(1, len(rk) + 1)), '| scores descending', all(sc[i] >= sc[i + 1] for i in range(len(sc) - 1)), '| columns', len(h))
        print('priority', dict(Counter(r[pi] for r in rows[1:] if r[0]))); cons = set(ns); continue
    if ws.title not in side and ws.title != 'Domestic':
        ri = h.index('Outreach Rank (Sector)'); rk = [r[ri] for r in rows[1:] if r[0]]
        if rk != list(range(1, len(rk) + 1)): print('RANK NOT CONTIGUOUS', ws.title); bad += 1
    for n in ns:
        if n in names: print('TWICE', n, names[n], ws.title); bad += 1
        names[n] = ws.title
sidenames = {n for n, t in names.items() if t in side}
print('ranked', len(cons), '| watchlist', cnt.get('Verification Watchlist', 0), '| Clay leads', cnt.get('Clay Leads (Unconfirmed)', 0), '| domestic tab', cnt.get('Domestic', 0), '| problems', bad, '| consolidated equals the sector tabs:', cons == set(names) - sidenames)
st = Counter(); hits = []
for n in names:
    s, disp, src, _ = C.lookup(n, batch=batch); st[s] += 1
    if s in ('dup', 'f1'): hits.append((n, s, src[:60]))
print('register check of every name in the workbook:', dict(st), hits[:10])
if master:
    m = load_workbook(master, read_only=True); mn = set()
    for ws in m.worksheets:
        if ws.title in ('Summary', 'Key', 'Templates Created'): continue
        for r in ws.iter_rows(min_row=2, max_col=1, values_only=True):
            if r[0]: mn.add(re.sub(r'[^a-z0-9]', '', str(r[0]).lower()))
    print('exact-name hits against the master file itself:', [n for n in names if re.sub(r'[^a-z0-9]', '', n.lower()) in mn][:20])
for p in sorted(os.listdir(os.path.join(H, 'delivered'))):
    if p[:-5] == batch: continue
    prev = {re.sub(r'[^a-z0-9]', '', x[0].lower()) for x in json.load(open(os.path.join(H, 'delivered', p), encoding='utf-8'))}
    print('exact-name hits against', p, ':', [n for n in names if re.sub(r'[^a-z0-9]', '', n.lower()) in prev][:20])
print('largest tabs:', sorted(cnt.items(), key=lambda x: -x[1])[:10])
