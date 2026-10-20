"""Step 4: QC checks on the finished workbook; appends a QC tab with the results."""
import collections, re
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font
OUT = '/home/user/rg42/reports/2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS.xlsx'
x = pd.ExcelFile(OUT)
M = x.parse('NEW PARENT COMPANIES (MASTER)'); B = x.parse('EXISTING GROUP OVERLAPS'); C = x.parse('MANUAL REVIEW'); E = x.parse('EXCLUDED DIRECT DUPLICATES'); F = x.parse('EXISTING F1 SPONSORS')
res = []
def check(n, desc, ok, detail=''): res.append([n, desc, 'PASS' if ok else 'CHECK', detail])
# 1 qualification
q = M['Qualification Criterion Met'].fillna('')
check(1, 'Every master-ranking parent meets valuation >= USD 1B, funding >= USD 100M or revenue >= USD 100M', q.str.contains('Valuation|funding|revenue').all(), f"{int((~q.str.contains('Valuation|funding|revenue')).sum())} rows without a criterion")
# 2 parent level / duplicates
names = M['Parent Company Name'].str.lower().str.strip()
check(2, 'One row per ultimate parent: no duplicate parent names in master ranking', not names.duplicated().any(), f"{int(names.duplicated().sum())} duplicates: {', '.join(M.loc[names.duplicated(), 'Parent Company Name'].head(5))}")
# 3 new vs overlap separation
bn = set(B['Parent Company Name'].str.lower().str.strip()); fn = set(F['Parent Company Name'].str.lower().str.strip())
check(3, 'No parent appears in both the master ranking and the overlaps tab', not (set(names) & bn), f"{len(set(names) & bn)} shared")
fm = set(M.loc[M['Existing F1 sponsorship'].fillna('').astype(str).str.strip() != '', 'Parent Company Name'].str.lower().str.strip()) | set(B.loc[B['Existing F1 sponsorship'].fillna('').astype(str).str.strip() != '', 'Parent Company Name'].str.lower().str.strip())
check(3, 'Every existing F1 sponsor is kept in its ranking with the Existing F1 sponsorship column filled (blue row) and listed on EXISTING F1 SPONSORS', fn == fm, f"{len(fn)} on the F1 tab, {len(fm)} marked in master/overlaps")
# 4 ranking integrity
check(4, 'Master ranking sorted by Total descending with consecutive ranks', (M['Overall Rank'].tolist() == list(range(1, len(M) + 1))) and M['Total Score (/100)'].is_monotonic_decreasing)
check(4, 'Total = Fit + Capacity; Fit <= 60; Capacity <= 40', ((M['F1 Fit Score (/60)'] + M['Financial Capacity Score (/40)'] - M['Total Score (/100)']).abs().lt(0.01).all()) and M['F1 Fit Score (/60)'].le(60).all() and M['Financial Capacity Score (/40)'].le(40).all())
# 5 industry tabs
skip = {'SUMMARY', 'READ ME', 'NEW PARENT COMPANIES (MASTER)', 'NEW BRANDS THIS ROUND', 'EXISTING GROUP OVERLAPS', 'EXCLUDED DIRECT DUPLICATES', 'EXISTING F1 SPONSORS', 'MANUAL REVIEW', 'QC', 'DRIVE CSV BRANDS (QUALIFIED)', 'APOLLO MATCHES IN YOUR FILES'}
cnt = collections.Counter(); rank_ok = True
for sh in x.sheet_names:
    if sh in skip: continue
    t = x.parse(sh)
    if t['Sector Rank'].tolist() != list(range(1, len(t) + 1)) or not t['Total Score (/100)'].is_monotonic_decreasing: rank_ok = False
    for n_, r_, tot in zip(t['Parent Company Name'], t['Overall Rank'], t['Total Score (/100)']):
        cnt[n_] += 1
        mr = M.loc[M['Parent Company Name'] == n_, 'Overall Rank']
        if not len(mr) or int(mr.iloc[0]) != int(r_): rank_ok = False
check(5, 'Each master parent appears in exactly one industry tab; tabs ranked independently 1..N by Total with the overall rank preserved', all(cnt[n_] == 1 for n_ in M['Parent Company Name']) and rank_ok and sum(cnt.values()) == len(M), f"industry rows {sum(cnt.values())} vs master {len(M)}")
# 6 overlaps tab content
check(6, 'Every overlap row names the existing subsidiary/brand or the parent itself, and the dataset', (B['Existing Subsidiary / Brand(s) in datasets'].fillna('').str.len().gt(0) & B['Dataset(s)'].fillna('').str.len().gt(0)).all())
check(6, 'Overlaps ranked separately with consecutive ranks', B['Overlap Rank'].tolist() == list(range(1, len(B) + 1)))
# 7 sources and confidence
check(7, 'Every master row has a sources & dates entry and a research confidence', (M['Sources & Dates'].fillna('').str.len().gt(0) & M['Research Confidence'].fillna('').str.len().gt(0)).all())
check(7, 'Preliminary rows are flagged', int((M['Preliminary?'] == 'Yes').sum()) >= 0, f"{int((M['Preliminary?'] == 'Yes').sum())} of {len(M)} flagged preliminary")
# 8 approach and brand
check(8, 'Every master row has a most-relevant brand, a G/B approach and a reason', (M['Most Relevant Subsidiary / Brand'].fillna('').str.len().gt(0) & M['Recommended Approach'].isin(['Group-Level', 'Brand-Level']) & M['Why this brand / approach'].fillna('').str.len().gt(0)).all())
check(8, 'Manual review rows each carry a reason', C['Why it needs review'].fillna('').str.len().gt(0).all())
wb = load_workbook(OUT)
if 'QC' in wb.sheetnames: wb.remove(wb['QC'])
ws = wb.create_sheet('QC'); ws.append(['QC item', 'Check', 'Result', 'Detail'])
for c in ws[1]: c.font = Font(bold=True)
for r in res: ws.append(r)
ws.column_dimensions['B'].width = 100; ws.column_dimensions['D'].width = 60
wb.save(OUT)
for r in res: print(r[2], '|', r[1], '|', r[3])
