"""Writes the brand workbook (streaming writer: about a million cells)."""
import os, re
from collections import Counter
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
HEAD = PatternFill('solid', fgColor='1F3864'); HFONT = Font(bold=True, color='FFFFFF'); HALIGN = Alignment(wrap_text=True, vertical='center')
WRAP = Alignment(wrap_text=True, vertical='top'); TOP = Alignment(vertical='top'); BOLD = Font(bold=True)
FILLS = {'High': PatternFill('solid', fgColor='C6EFCE'), 'Medium': PatternFill('solid', fgColor='FFEB9C'), 'Lower': PatternFill('solid', fgColor='EDEDED'),
         'To Verify': PatternFill('solid', fgColor='FCE4D6'), 'Plausible Capacity': PatternFill('solid', fgColor='FFF2CC'), 'Not Established': PatternFill('solid', fgColor='EDEDED'),
         'Low': PatternFill('solid', fgColor='FCE4D6')}
MONEY = '[>=1000000000]$#,##0.00,,,"B";[>=1000000]$#,##0,,"M";$#,##0'
LONG = {5, 6, 11, 12, 13, 15, 16, 17, 18, 19, 21}
def sheet(wb, title, cols, width, data):
    ws = wb.create_sheet(title[:31])
    for j, w in enumerate(width, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{max(len(data) + 1, 2)}'
    ws.row_dimensions[1].height = 44
    hdr = []
    for c in cols:
        x = WriteOnlyCell(ws, value=c); x.font = HFONT; x.fill = HEAD; x.alignment = HALIGN; hdr.append(x)
    ws.append(hdr)
    for i, row in enumerate(data, 2):
        ws.row_dimensions[i].height = 62
        out = []
        for j, v in enumerate(row, 1):
            x = WriteOnlyCell(ws, value=v); x.alignment = WRAP if j in LONG else TOP
            if j in (8, 9) and isinstance(v, (int, float)): x.number_format = MONEY
            elif j == 10 and isinstance(v, (int, float)): x.number_format = '0.0%'
            elif j == 22: x.number_format = '0.0'
            if j in (3, 4, 20, 23) and v in FILLS: x.fill = FILLS[v]
            out.append(x)
        ws.append(out)
    return ws
def text_sheet(wb, title, lines, widths=(34, 120)):
    ws = wb.create_sheet(title)
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    for ln in lines:
        out = []
        for j, v in enumerate(ln if isinstance(ln, (list, tuple)) else [ln]):
            x = WriteOnlyCell(ws, value=v); x.alignment = WRAP if (j == len(widths) - 1 and len(widths) == 2) else TOP
            if isinstance(ln, tuple): x.font = BOLD
            out.append(x)
        ws.append(out)
    return ws
def write(A, path, COLS, WIDTH, cells):
    import summary
    rows = A['rows']; data = {id(x): cells(x) for x in rows}
    wb = Workbook(write_only=True)
    sheet(wb, 'Master Brands', COLS, WIDTH, [data[id(x)] for x in rows])
    tabs = []
    for r in A['B']:
        if r['sector'] not in tabs: tabs.append(r['sector'])
    for i, t in enumerate(tabs, 1):
        sheet(wb, re.sub(r'[\\/*?:\[\]]', ' ', t), COLS, WIDTH, [data[id(x)] for x in rows if x['r']['sector'] == t])
    sheet(wb, 'Top 500 Prospects', COLS, WIDTH, [data[id(x)] for x in rows[:500]])
    sheet(wb, 'Verification Required', COLS, WIDTH, [data[id(x)] for x in rows if x['verify']])
    fx = sorted(A['f1x'], key=lambda d: (d['r']['sector'], d['name'].lower()))
    fcols = ['Brand', 'Tab in Your Sheet', 'Current Formula 1 Link (why it is not a prospect)', 'Marked "x" in Your Sheet', 'Brand Name in Your Sheet']
    ws = wb.create_sheet('Current F1 Partners')
    for j, w in enumerate((32, 30, 110, 12, 30), 1): ws.column_dimensions[get_column_letter(j)].width = w
    hdr = []
    for c in fcols:
        x = WriteOnlyCell(ws, value=c); x.font = HFONT; x.fill = HEAD; x.alignment = HALIGN; hdr.append(x)
    ws.append(hdr)
    for d in fx:
        out = []
        for v in (d['name'], d['r']['sector'], d['why'], 'x' if d['r']['mark'] else '', d['r']['brand']):
            x = WriteOnlyCell(ws, value=v); x.alignment = WRAP; out.append(x)
        ws.append(out)
    text_sheet(wb, 'Research Summary', summary.lines(A, tabs), widths=summary.WIDTHS)
    text_sheet(wb, 'Key', summary.KEY)
    wb.save(path)
