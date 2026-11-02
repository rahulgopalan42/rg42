"""QC for List A (valuation found) and List B (valuation not found): re-checks mainA.pkl / mainB.pkl and the saved
workbooks, and appends a QC tab to each."""
import os, sys
import pandas as pd
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, regdom
wx = pd.read_csv(f'{H}/ref/wikipedia_former_unicorns.csv'); EXIT = {loose(n) for n, r in zip(wx['company'], wx['exit_reason']) if loose(n) and 'deval' not in str(r).lower()}
BOOKS = {'A': (os.path.join(R, 'reports', 'F1-PRIVATE-200M-FUNDING-WITH-VALUATION-2026-10-30.xlsx'), 'mainA.pkl'),
         'B': (os.path.join(R, 'reports', 'F1-PRIVATE-200M-FUNDING-VALUATION-NOT-FOUND-2026-10-30.xlsx'), 'mainB.pkl')}
SUPPORT = {'SUMMARY', 'NEAR MISSES', 'CURRENT F1 DEAL (SET ASIDE)', 'CHECKED - LEFT OUT', 'COULD NOT VERIFY', 'QC'}
total_fail = 0
for lst, (path, pk) in BOOKS.items():
    m = pd.read_pickle(os.path.join(H, pk)); checks = []
    def chk(name, ok, detail=''): checks.append(['PASS' if ok else 'FAIL', name, str(detail)])
    chk('Every company is verified private and independent with USD 200M+ equity raised (independent evidence)', bool((m['verdict'] == 'verified').all() and m['t_private'].all() and m['t_fund'].all()), f'{len(m)} rows')
    if lst == 'A': chk('Every valuation is backed by CB Insights, a dated news ruling or a sourced report', bool(m['val_found'].all()), m['val_src'].value_counts().to_dict())
    else: chk('No company on this list has a verified valuation (those are on List A)', not bool(m['val_found'].any()), '')
    chk('No brand from the 30 Oct unicorn workbook is repeated', not bool(m['already_sent'].any()), int(m['already_sent'].sum()))
    chk('No company with a current F1 deal (2026 rosters or research)', not bool(m['f1_current'].any()), int(m['f1_current'].sum()))
    ex = m['brand'].map(loose).isin(EXIT) & ~m['news_check'].str.startswith('confirmed by news')
    chk("No company on Wikipedia's exited-unicorn table unless dated news confirms it is still private", not bool(ex.any()), ', '.join(m[ex]['brand'].head(8)))
    d = m['domain'].map(regdom); dd = d[(d != '') & d.duplicated()]; kk = m['brand'].map(loose) + '|' + m['hq_country'].str.lower()
    chk('No duplicate companies (same name and country, or same website)', not kk.duplicated().any() and dd.empty, ', '.join(list(dd.head(8)) + list(m[kk.duplicated()]['brand'].head(8))))
    chk('Ranks run 1..N without gaps', list(m['rank']) == list(range(1, len(m) + 1)), f'N={len(m)}')
    chk('No tobacco / nicotine / cannabis brands', not bool(m['banned'].any()))
    wb = load_workbook(path, read_only=True)
    sec = sum(ws.max_row - 1 for ws in wb.worksheets if ws.title not in SUPPORT); wb.close()
    chk('Every company sits on exactly one sector tab', sec == len(m), f'{sec} on sector tabs vs {len(m)} companies')
    nc = (m['news_check'] != '').sum()
    chk('Companies checked against dated news headlines', nc >= 0.95 * len(m), f'{nc} of {len(m)}')
    wb = load_workbook(path)
    if 'QC' in wb.sheetnames: del wb['QC']
    ws = wb.create_sheet('QC'); ws.append(['Result', 'Check', 'Detail'])
    for c in checks: ws.append(c)
    ws.column_dimensions['A'].width = 8; ws.column_dimensions['B'].width = 90; ws.column_dimensions['C'].width = 80
    wb.save(path)
    print(f'List {lst}:'); [print('  ' + ' | '.join(c)) for c in checks]
    total_fail += sum(c[0] == 'FAIL' for c in checks)
print('failures', total_fail)
