"""QC for the 30 Oct new-brands workbook. Prints PASS/FAIL per check and appends a QC tab."""
import os, re, sys, json
import pandas as pd
from openpyxl import load_workbook
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, H); from match import present, phrase_present
OUT = os.path.join(R, 'reports', 'F1-NEW-BRANDS-200M-FUNDING-OR-100M-LISTED-REVENUE-2026-10-30.xlsx')
x = pd.ExcelFile(OUT); M = x.parse('NEW BRANDS (MASTER)')
res = []
def check(name, ok, detail=''): res.append(['PASS' if ok else 'FAIL', name, detail]); print(res[-1][0], '|', name, '|', detail)
check('Every row meets the money rule (funding > USD 200M, or listed with revenue/ARR >= USD 100M)', M['Qualifies on'].fillna('').str.len().gt(0).all(), f"{int(M['Qualifies on'].fillna('').eq('').sum())} rows without a criterion")
hits = [b for b, w in zip(M['Brand'], M['Website'].fillna('')) if present(b, w) or phrase_present(b)]
check('No brand or website on MASTER REFERENCE OCT or the parent-company workbook', not hits, f"{len(hits)} found: {', '.join(map(str, hits[:5]))}")
nm = M['Brand'].str.lower().str.replace(r'[^a-z0-9]', '', regex=True); ws_ = M['Website'].fillna('').str.lower()
check('No duplicate brands or websites', not nm.duplicated().any() and not ws_[ws_ != ''].duplicated().any(), f"{int(nm.duplicated().sum())} name / {int(ws_[ws_ != ''].duplicated().sum())} website duplicates")
check('Ranked by outreach priority with consecutive ranks', M['Outreach Priority'].tolist() == list(range(1, len(M) + 1)) and M['Priority score'].is_monotonic_decreasing)
check('Every row has HQ country and website', M['HQ Country'].fillna('').ne('').all() and M['Website'].fillna('').ne('').all(), f"{int(M['HQ Country'].fillna('').eq('').sum())} without country, {int(M['Website'].fillna('').eq('').sum())} without website")
check('Total = F1 Fit + Financial Capacity; Fit <= 60; Capacity <= 40', ((M['F1 Fit (/60)'] + M['Financial Capacity (/40)'] - M['Total (/100)']).abs() < 0.11).all() and (M['F1 Fit (/60)'] <= 60).all() and (M['Financial Capacity (/40)'] <= 40).all())
skip = {'SUMMARY', 'NEW BRANDS (MASTER)', 'PARENT ALREADY ON SHEETS', 'CURRENT F1 DEAL (SET ASIDE)', 'CHECKED - LEFT OUT', 'QC'}
cnt, ok = 0, True
for sh in x.sheet_names:
    if sh in skip: continue
    t = x.parse(sh); cnt += len(t)
    if t['Sector Rank'].tolist() != list(range(1, len(t) + 1)) or not t['Outreach Priority'].is_monotonic_increasing: ok = False
check('Every brand sits on exactly one sector tab, ranked 1..N in outreach order', ok and cnt == len(M), f"sector rows {cnt} vs master {len(M)}")
f1 = x.parse('CURRENT F1 DEAL (SET ASIDE)')
check('No current F1 sponsor in the main list', not (set(M['Brand']) & set(f1['Brand'])), f"{len(f1)} set aside")
check('Tiers assigned', M['Tier'].fillna('').ne('').all(), M['Tier'].value_counts().to_dict().__repr__())
wb = load_workbook(OUT)
if 'QC' in wb.sheetnames: del wb['QC']
ws = wb.create_sheet('QC'); ws.append(['Result', 'Check', 'Detail'])
for r in res: ws.append(r)
ws.column_dimensions['A'].width = 8; ws.column_dimensions['B'].width = 90; ws.column_dimensions['C'].width = 60
wb.save(OUT); print(sum(r[0] == 'PASS' for r in res), 'of', len(res), 'checks pass')
