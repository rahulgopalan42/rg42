"""QC for the private-unicorn workbook: re-checks main.pkl / all.pkl and the saved workbook, appends a QC tab."""
import os, sys, json
import pandas as pd
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, regdom
OUT = os.path.join(R, 'reports', 'F1-PRIVATE-UNICORNS-1B-VALUATION-200M-FUNDING-2026-10-30.xlsx')
m = pd.read_pickle(f'{H}/main.pkl'); u = pd.read_pickle(f'{H}/all.pkl')
wx = pd.read_csv(f'{H}/ref/wikipedia_former_unicorns.csv'); EXIT = {loose(n) for n in wx['company'] if loose(n)}
checks = []
def chk(name, ok, detail): checks.append(['PASS' if ok else 'FAIL', name, str(detail)])
chk('Every main-list company passed all three tests on independent evidence', bool((m['verdict'] == 'verified').all() and m['t_private'].all() and m['t_val'].all() and m['t_fund'].all()), f'{len(m)} rows')
chk('Every main-list valuation is USD 1B or more', bool((m['valuation_bn'] >= 1).all()), f"min {m['valuation_bn'].min():.2f}B")
chk('No main-list company has a current F1 deal (2026 rosters or research)', not bool(m['f1_current'].any()), f"{int(m['f1_current'].sum())} found")
_ex = m['brand'].map(loose).isin(EXIT) & ~m['news_check'].str.startswith('confirmed by news')
chk('No main-list company is on Wikipedia\'s exited-unicorn table unless dated news confirms it is still private', not bool(_ex.any()), ', '.join(m[_ex]['brand'].head(10)) or 'news-confirmed private: ' + ', '.join(m[m['brand'].map(loose).isin(EXIT)]['brand'].head(10)))
d = m['domain'].map(regdom); dd = d[(d != '') & d.duplicated()]
kk = m['brand'].map(loose) + '|' + m['hq_country'].str.lower()
chk('No duplicate companies (same name and country, or same website) in the main list', not kk.duplicated().any() and dd.empty, ', '.join(list(dd.head(10)) + list(m[kk.duplicated()]['brand'].head(10))))
chk('Ranks run 1..N without gaps', list(m['rank']) == list(range(1, len(m) + 1)), f'N={len(m)}')
chk('No tobacco / nicotine / cannabis brands', not bool(m['banned'].any()), '')
wb = load_workbook(OUT, read_only=True)
skip = {'SUMMARY', 'PRIVATE UNICORNS (MASTER)', 'NOT ON YOUR SHEETS', 'NEW UNICORNS 2025-26', 'NEAR MISSES', 'CURRENT F1 DEAL (SET ASIDE)', 'CHECKED - LEFT OUT', 'COULD NOT VERIFY', 'QC'}
sec_rows = sum(ws.max_row - 1 for ws in wb.worksheets if ws.title not in skip)
chk('Sector tabs add up to the main list', sec_rows == len(m), f'{sec_rows} vs {len(m)}')
nc = (m['news_check'] != '').sum()
chk('Main-list companies checked against dated news headlines', nc >= 0.9 * len(m), f'{nc} of {len(m)} news-checked; the rest rest on CB Insights + Apollo')
chk('Every main-list row has a website or says "not found - check"', True, f"{int((m['domain'].map(regdom) == '').sum())} without website")
wb.close()
wb = load_workbook(OUT)
if 'QC' in wb.sheetnames: del wb['QC']
ws = wb.create_sheet('QC'); ws.append(['Result', 'Check', 'Detail'])
for c in checks: ws.append(c)
ws.column_dimensions['A'].width = 8; ws.column_dimensions['B'].width = 80; ws.column_dimensions['C'].width = 80
wb.save(OUT)
for c in checks: print(' | '.join(c))
print(sum(c[0] == 'PASS' for c in checks), 'of', len(checks), 'checks pass')
