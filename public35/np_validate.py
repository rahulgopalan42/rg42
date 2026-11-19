"""Checks the new-parameters workbook after it is written.  Usage: np_validate.py [path]"""
import os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build
import np_build as nb
from openpyxl import load_workbook
p = sys.argv[1] if len(sys.argv) > 1 else nb.OUT
wb = load_workbook(p, read_only=True); bad = []; names = wb.sheetnames
REQ = ['Company Name', 'Headquarters', 'F1 Investment Category', 'Outreach Priority', 'Short Company Description', 'Annual Revenue', 'Market Capitalization', 'Cash / Profitability',
       'Estimated Sponsorship Capacity', 'Financial Capacity Confidence', 'Geographic Reach', 'Existing Sports / F1 Partnerships', 'Strategic Rationale for F1', 'Buying Signals', 'Sources / Verification Status']
tot = 0; allrows = None; seen = Counter(); part = set()
for n in names:
    if n in ('Summary', 'Key', 'Below Threshold'): continue
    ws = wb[n]; R = list(ws.iter_rows(values_only=True)); hdr = R[0]; body = R[1:]
    for i, r in enumerate(REQ):
        if not str(hdr[i]).startswith(r): bad.append(f'{n}: column {i + 1} is {hdr[i]!r}, expected {r!r}')
    for r in body:
        if any(v is None or str(v).strip() in ('', 'None', 'nan') for v in r[:21]): bad.append(f'{n}: empty cell in {r[0]}')
        if r[2] not in nb.CATS: bad.append(f'{n}: category {r[2]!r} for {r[0]}')
        if r[3] not in ('High', 'Medium', 'Lower'): bad.append(f'{n}: priority {r[3]!r} for {r[0]}')
        if r[9] not in ('High', 'Medium', 'Low'): bad.append(f'{n}: confidence {r[9]!r} for {r[0]}')
        if r[10] not in ('Global', 'International', 'Regional', 'Domestic'): bad.append(f'{n}: reach {r[10]!r} for {r[0]}')
        if not 6 <= len(str(r[4]).split()) <= 26: bad.append(f'{n}: description length for {r[0]}: {r[4]!r}')
        if r[2] == 'Strategic Exception' and 'Strategic Exception because' not in str(r[14]): bad.append(f'{n}: no reason for the exception: {r[0]}')
        if n == 'Current F1 Partners' and not str(r[11]).startswith('CURRENT F1 PARTNER'): bad.append(f'{n}: not flagged: {r[0]}')
        if n not in ('Current F1 Partners',) and str(r[11]).startswith('CURRENT F1 PARTNER'): bad.append(f'{n}: a current partner on a prospect tab: {r[0]}')
    if n == 'All New Brands': allrows = len(body); allkeys = Counter((r[0], r[16]) for r in body)
    elif n == 'Current F1 Partners': part = {(r[0], r[16]) for r in body}
    else:
        tot += len(body)
        for r in body: seen[(r[0], r[16])] += 1
        want = {str(r[15]) for r in body}
        if len(want) != 1: bad.append(f'{n}: more than one sector on the tab: {want}')
if tot != allrows: bad.append(f'sector tabs hold {tot} rows, All New Brands holds {allrows}')
if any(v > 1 for v in seen.values()): bad.append('a company is on two sector tabs: ' + str([k for k, v in seen.items() if v > 1][:5]))
if set(seen) & part: bad.append('a company is on a sector tab and on the partner tab: ' + str(list(set(seen) & part)[:5]))
master = {r['name'] for r in build.assemble()['rows']}
both = [k[0] for k in seen if k[0] in master]
if both: bad.append(f'{len(both)} names are also on the 15 Nov master: {both[:8]}')
print(len(names), 'tabs |', allrows, 'new brands |', len(part), 'current F1 partners |', wb['Below Threshold'].max_row - 1, 'below threshold')
print('OK' if not bad else 'PROBLEMS (%d):\n' % len(bad) + '\n'.join(bad[:40]))
