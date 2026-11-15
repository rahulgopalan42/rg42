"""Checks on the finished workbooks (master + 35 sector files). Prints PASS / FAIL per check.  Usage: qc.py"""
import os, re, sys
from collections import Counter
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build, review
from sectors35 import SECTORS, ORDER
from f1links import f1_link
res = []
def check(name, ok, detail=''):
    res.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (' | ' + str(detail) if detail else ''))
wb = load_workbook(build.MASTER, read_only=True)
tabs = wb.sheetnames
want = ['Master Companies'] + [f'{c} {build.TAB[c]}'[:31] for c in ORDER] + ['Top 500 Prospects', 'Verification Required', 'Research Summary']
check('1 master tabs present and in order', tabs == want, [t for t in want if t not in tabs][:5])
def read(ws):
    it = ws.iter_rows(values_only=True); hdr = list(next(it)); return hdr, [list(r) for r in it if r and r[0]]
data = {t: read(wb[t]) for t in tabs if t != 'Research Summary'}
check('2 same 22 columns, in the agreed order, on every data tab', all(h[:len(build.COLS)] == build.COLS for h, _ in data.values()))
M = data['Master Companies'][1]
tk = Counter(r[6] for r in M); nm = Counter(build.re.sub(r'[^a-z0-9]', '', str(r[0]).lower()) + '|' + str(r[1]) for r in M)
check('3 no duplicate ticker or company in Master Companies', max(tk.values()) == 1 and max(nm.values()) == 1, [k for k, v in tk.items() if v > 1][:5] + [k for k, v in nm.items() if v > 1][:5])
sec_rows = {c: data[f'{c} {build.TAB[c]}'[:31]][1] for c in ORDER}
check('4 sector tabs add up to Master Companies and none exceeds 400', sum(len(v) for v in sec_rows.values()) == len(M) and max(len(v) for v in sec_rows.values()) <= build.CAP,
      f'master {len(M)}, sector tabs {sum(len(v) for v in sec_rows.values())}')
check('5 every sector tab holds only its own sector', all(all(r[5] == SECTORS[c]['name'] for r in v) for c, v in sec_rows.items()))
bad = [r[0] for r in M if r[2] not in ('Challenger', 'Mid-level', 'Large', 'To Verify') or r[3] not in ('High', 'Medium', 'Lower') or r[13] not in ('Domestic', 'Regional', 'International', 'Global')
       or r[19] not in ('Strong Evidence', 'Plausible Capacity')]
check('6 category, priority, reach and confidence use only the allowed values', not bad, bad[:5])
bad = [(r[0], len(str(r[4]).split())) for r in M if not 10 <= len(str(r[4]).split()) <= 20]
check('7 every description is one sentence of 10-20 words', not bad, bad[:5])
bad = [(r[0], build.COLS[j]) for r in M for j in range(19) if r[j] in (None, '')]
check('8 no blank cell in the 19 agreed columns', not bad, bad[:5])
bad = [(r[0], f1_link(str(r[0]))[0]) for r in M if f1_link(str(r[0]))[0]]
check('9 no listed company matches the F1 partner roster by name', not bad, bad[:5])
A = build.assemble(); sym = {build.ticker(r['c'], r['f']['gap']): r['sym'] for r in A['rows']}
bad = [r[0] for r in M if sym.get(r[6]) in review.ROSTER_EXTRA or sym.get(r[6]) in review.DROP or review.F1.get(sym.get(r[6]), ('',))[0] == 'exclude']
check('10 no company marked for exclusion in the review table is listed', not bad, bad[:5])
T = data['Top 500 Prospects'][1]; mt = {r[6] for r in M}
check('11 Top 500 has 500 rows, all from the master list, all High priority', len(T) == 500 and all(r[6] in mt for r in T) and all(r[3] == 'High' for r in T), f'{len(T)} rows, {Counter(r[3] for r in T)}')
V = data['Verification Required'][1]
check('12 every Verification Required row is in the master list and says what to check', all(r[6] in mt and r[20] for r in V) and all(r in V for r in M if r[2] == 'To Verify'), len(V))
bad = [(r[0], r[7], r[8]) for r in M if not (isinstance(r[7], (int, float)) or r[7] == 'Not available') or not (isinstance(r[8], (int, float)) or r[8] == 'Not available')]
check('13 revenue and market cap are numbers (or "Not available")', not bad, bad[:5])
miss = []
for c in ORDER:
    p = build.sector_path(c)
    if not os.path.exists(p): miss.append(c + ' missing'); continue
    h, rows = read(load_workbook(p, read_only=True).worksheets[0])
    if h[:len(build.COLS)] != build.COLS or [r[6] for r in rows] != [r[6] for r in sec_rows[c]]: miss.append(c + ' differs from the master tab')
check('14 the sector files exist and match their master tabs', not miss, miss[:5])
print(f"{sum(res)}/{len(res)} checks passed | master {len(M)} companies | priority {dict(Counter(r[3] for r in M))} | category {dict(Counter(r[2] for r in M))} | verification {len(V)}")
