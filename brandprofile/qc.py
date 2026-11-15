"""Checks on the finished brand workbook. Prints PASS / FAIL per check.  Usage: qc.py"""
import gzip, json, os, re, sys
from collections import Counter
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as build
for p in ('public35',): sys.path.insert(0, os.path.join(os.path.dirname(H), p))
from f1links import f1_link
res = []
def check(name, ok, detail=''):
    res.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (' | ' + str(detail) if detail else ''))
B = json.load(gzip.open(os.path.join(H, 'data', 'brands.json.gz'), 'rt', encoding='utf-8'))
wb = load_workbook(build.OUTFILE, read_only=True); tabs = wb.sheetnames
user_tabs = []
for r in B:
    if r['sector'] not in user_tabs: user_tabs.append(r['sector'])
want = ['Master Brands'] + [t[:31] for t in user_tabs] + ['Top 500 Prospects', 'Verification Required', 'Current F1 Partners', 'Research Summary', 'Key']
check('1 tabs present and in order (Master, your 48 sector tabs, Top 500, Verification, F1 partners, Summary, Key)', tabs == want, [t for t in want if t not in tabs][:5])
def read(ws):
    it = ws.iter_rows(values_only=True); hdr = list(next(it)); return hdr, [list(r) for r in it if r and r[0]]
data = {t: read(wb[t]) for t in tabs if t not in ('Research Summary', 'Key', 'Current F1 Partners')}
check('2 same columns in the same order on every data tab; the first 22 are the listed-company columns', all(h == build.COLS for h, _ in data.values()) and build.COLS[:22] == build.pb.COLS)
M = data['Master Brands'][1]; F = read(wb['Current F1 Partners'])[1]
key = lambda name, tab: (str(name), str(tab))
got = Counter(key(r[24], r[25]) for r in M) + Counter(key(r[4], r[1]) for r in F); exp = Counter(key(r['brand'], r['sector']) for r in B)
check('3 every brand on your 48 tabs is in the workbook exactly once (Master + F1 partners tab)', got == exp, f'yours {sum(exp.values())}, workbook {sum(got.values())}, missing {list((exp - got).items())[:4]}, extra {list((got - exp).items())[:4]}')
sec = {t: data[t[:31]][1] for t in user_tabs}
check('4 sector tabs add up to Master and each holds only the brands of your tab', sum(len(v) for v in sec.values()) == len(M) and all(all(r[25] == t for r in v) for t, v in sec.items()),
      f'master {len(M)}, sector tabs {sum(len(v) for v in sec.values())}')
bad = [r[0] for r in M if r[2] not in ('Challenger', 'Mid-level', 'Large', 'To Verify') or r[3] not in ('High', 'Medium', 'Lower') or r[13] not in ('Domestic', 'Regional', 'International', 'Global')
       or r[19] not in ('Strong Evidence', 'Plausible Capacity', 'Not Established') or r[22] not in ('High', 'Medium', 'Low')]
check('5 category, priority, reach and confidence use only the allowed values', not bad, bad[:5])
bad = [(r[0], len(str(r[4]).split())) for r in M if not 10 <= len(str(r[4]).split()) <= 20]
check('6 every description is 10-20 words', not bad, (len(bad), bad[:5]))
bad = [(r[0], build.COLS[j]) for r in M for j in range(22) if r[j] in (None, '')]
check('7 no blank cell in the 22 profile columns', not bad, (len(bad), bad[:5]))
import bp_review
decided = {key(r['brand'], r['sector']) for r in B if bp_review.F1.get(r['id'], ('',))[0] in ('clear', 'note')}     # looked at by hand: not the roster company, or a link that is noted
bad = [(r[0], f1_link(str(r[0]))[0] or f1_link(str(r[24]))[0]) for r in M if (f1_link(str(r[0]))[0] or f1_link(str(r[24]))[0]) and key(r[24], r[25]) not in decided]
check('8 no brand in the lists matches the F1 partner roster by name (apart from the names reviewed by hand)', not bad, bad[:5])
T = data['Top 500 Prospects'][1]; mk = {key(r[24], r[25]) for r in M}
check('9 Top 500 has 500 rows, all from the master list, all High priority', len(T) == 500 and all(key(r[24], r[25]) in mk for r in T) and all(r[3] == 'High' for r in T), f'{len(T)} rows, {dict(Counter(r[3] for r in T))}')
V = data['Verification Required'][1]
check('10 every Verification Required row is in the master list, is High or Medium, and says what to check', all(key(r[24], r[25]) in mk and r[20] and r[3] != 'Lower' for r in V), len(V))
bad = [(r[0], r[7], r[8]) for r in M if not (isinstance(r[7], (int, float)) or str(r[7]).startswith('Not ')) or not (isinstance(r[8], (int, float)) or str(r[8]).startswith('Not '))]
check('11 revenue and market value are numbers or say why they are not shown', not bad, bad[:5])
x_in = sum(r['mark'] for r in B); x_out = sum(1 for r in M if r[23] == 'x') + sum(1 for r in F if r[3] == 'x')
check('12 your x marks are all carried over', x_in == x_out, f'yours {x_in}, workbook {x_out}')
bad = [r[0] for r in M if r[2] != 'To Verify' and r[19] == 'Not Established'] + [r[0] for r in M if r[3] == 'High' and (r[2] == 'To Verify' or r[22] == 'Low')]
check('13 a category always has supporting evidence; High priority always has a category and is not a low-confidence profile', not bad, bad[:5])
bad = [r[0] for r in M if isinstance(r[7], (int, float)) and ' / ' not in str(r[6])]
check('14 figures are shown only for brands matched to a stock ticker', not bad, bad[:5])
print(f"{sum(res)}/{len(res)} checks passed | {len(M)} brands | priority {dict(Counter(r[3] for r in M))} | category {dict(Counter(r[2] for r in M))} | verification {len(V)} | F1 tab {len(F)}")
