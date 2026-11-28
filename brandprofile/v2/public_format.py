"""Usage: public_format.py <batch> <output.xlsx>
The new brands of a batch in the format of the public-company master (reports/F1-PUBLIC-COMPANIES-MASTER-2026-11-15.xlsx):
the same 22 columns in the same order, the same header, widths, row heights and frozen pane, one tab per sector, rows by score.
Tabs: All New Brands, one numbered tab per sector, Verification Required (the watchlist)."""
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
import build as B
COLS = ['Company Name', 'Headquarters – City and country', 'F1 Investment Category', 'Outreach Priority', 'Company Description', 'Sector / Industry', 'Stock Ticker / Exchange', 'Annual Revenue (USD)',
        'Market Capitalization (USD)', 'Revenue Growth (YoY)', 'EBITDA / Operating Profit', 'Free Cash Flow / Liquidity', 'Marketing Expenditure (if disclosed)', 'Geographic Reach',
        'Main Customer Markets & International Expansion', 'F1 Sponsorship Rationale', 'Latest Financial Reporting Period', 'Financial & Corporate Sources', 'F1 Sponsorship Verification Source',
        'Financial Capacity Confidence', 'Verification Notes', 'Priority Score (0-100)']
WIDTH = [30, 24, 26, 11, 50, 30, 22, 14, 14, 11, 42, 42, 42, 13, 50, 55, 36, 60, 60, 16, 50, 10]          # as the public master; column C widened for the tier wording
SHORT = {'Industrial Machinery & Equipment': 'Industrial Machinery', 'Media, Entertainment & Publishing': 'Media & Entertainment', 'Shipping, Maritime & Shipbuilding': 'Shipping & Maritime',
         'Professional & Business Services': 'Professional Services', 'Environmental & Waste Services': 'Environmental & Waste', 'Financial Services & Payments': 'Financial Services',
         'Building Products & Materials': 'Building Products', 'Medical Devices & Diagnostics': 'Medical Devices'}
FILLS = {k: PatternFill('solid', fgColor=v) for k, v in {'High': 'C6EFCE', 'Medium': 'FFEB9C', 'Watchlist': 'FCE4D6', 'Low': 'EDEDED', 'To Verify': 'FCE4D6', 'Confirmed capacity': 'C6EFCE',
                                                          'Indicative capacity': 'FFF2CC', 'Unverified capacity': 'FCE4D6'}.items()}
HEAD = PatternFill('solid', fgColor='1F3864'); WRAP = Alignment(wrap_text=True, vertical='top'); TOP = Alignment(vertical='top')
MONEY = '[>=1000000000]$#,##0.00,,,"B";[>=1000000]$#,##0,,"M";$#,##0'; LONG = {5, 11, 12, 13, 15, 16, 17, 18, 19, 21}
IDX = {c: B.COLS.index(c) for c in COLS if c in B.COLS}
def cells(d, watch=False):
    r = B.row(d, watch=watch); a = d['A']; M = a['M']; out = []
    for c in COLS:
        if c == 'Priority Score (0-100)': v = a['total']
        elif c == 'Annual Revenue (USD)': v = round(M['revenue'][0] * 1e6) if 'revenue' in M and M['revenue'][0] else r[IDX[c]]
        elif c == 'F1 Investment Category': v = r[IDX[c]].replace(' (estimate)', '')
        elif c == 'Geographic Reach': v = r[IDX[c]] if r[IDX[c]] in ('Global', 'International', 'Regional', 'Domestic') else 'Not recorded'
        else: v = r[IDX[c]]
        out.append(v)
    return out
def sheet(wb, title, rows, first=False):
    ws = wb.active if first else wb.create_sheet(); ws.title = title[:31]; ws.append(COLS)
    for r in rows: ws.append(r)
    for j, w in enumerate(WIDTH, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
        h = ws.cell(1, j); h.font = Font(bold=True, color='FFFFFF'); h.fill = HEAD; h.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[1].height = 44; ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(COLS))}{max(len(rows) + 1, 2)}'
    for i in range(2, len(rows) + 2):
        ws.row_dimensions[i].height = 62
        for j in range(1, len(COLS) + 1): ws.cell(i, j).alignment = WRAP if j in LONG else TOP
        if isinstance(ws.cell(i, 8).value, (int, float)): ws.cell(i, 8).number_format = MONEY
        ws.cell(i, 22).number_format = '0.0'
        for j in (4, 20):
            fl = FILLS.get(ws.cell(i, j).value)
            if fl: ws.cell(i, j).fill = fl
    return ws
def main(batch, path):
    D = B.load(batch); Q, W, I, tab = B.classify(D['recs'])
    wb = Workbook(); sheet(wb, 'All New Brands', [cells(d) for d in Q], first=True)
    n = 0; made = []
    for s in B.SECTORS:
        L = [d for d in Q if d['sector'] == s]                 # every reach in the sector tab, as in the public master; Geographic Reach is its own column
        if not L: continue
        n += 1; t = f'{n:02d} {SHORT.get(s, s)}'; sheet(wb, t, [cells(d) for d in L]); made.append((t[:31], len(L)))
    sheet(wb, 'Verification Required', [cells(d, watch=True) for d in W])
    wb.save(path); print(path, '|', len(Q), 'brands |', len(made), 'sector tabs |', len(W), 'to verify |', round(os.path.getsize(path) / 1024), 'KB'); return made
if __name__ == '__main__':
    for t, k in main(sys.argv[1], sys.argv[2]): print(f'  {t}: {k}')
