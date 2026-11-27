"""The tabs of the user's master workbook that carry no x mark, copied whole in the master's format so they can be reviewed and labelled.
Usage: unmarked_tabs.py <master.xlsx> <output.xlsx>
Group 1: no x anywhere on the tab. Group 2: no x in column B (the template column the user labels in), but some rows carry the older x
from the 48-tab sheet in column D. Tabs with any x in column B are left out. Side lists without an x column are listed, not copied."""
import os, sys
from collections import Counter
from openpyxl import Workbook, load_workbook
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xmarked_clean import copy_tab, isx, table
NOT_BRANDS = {'Templates Created', 'Summary', 'Key'}
SIDE_LISTS = {'Capacity To Confirm': 'Companies whose capacity or ownership could not be shown from a public page', 'Clay Leads (Unconfirmed)': 'Unverified leads from Clay',
              'Deals Announced - Watch': 'Companies still listed, with a deal announced', 'Left Out': 'Companies left off the list, with the reason'}
def main(mpath, out):
    wb = load_workbook(mpath); new = Workbook(); new.remove(new.active)
    idx = []; keep = []
    for ws in wb.worksheets:
        if ws.title in NOT_BRANDS: continue
        hdr = [c.value for c in ws[1]]
        if ws.title in SIDE_LISTS:
            idx.append([ws.title, 'Side list: no x column', sum(1 for i in range(2, ws.max_row + 1) if ws.cell(i, 1).value is not None), '', '', '', SIDE_LISTS[ws.title] + '. Not copied into this workbook.']); continue
        if not (isinstance(hdr[0], str) and hdr[0].startswith('Company')): continue
        oi = hdr.index('On Your Sheet?') if 'On Your Sheet?' in hdr else None
        rows = [i for i in range(2, ws.max_row + 1) if ws.cell(i, 1).value is not None]
        xb = sum(1 for i in rows if isx(ws.cell(i, 2).value)); xd = sum(1 for i in rows if isx(ws.cell(i, 4).value))
        newb = sum(1 for i in rows if str(ws.cell(i, oi + 1).value or '').startswith('No')) if oi is not None else ''
        if xb: continue                                                   # the tab has x marks in the template column: not part of this check
        grp = 'No x anywhere' if not xd else 'No x in column B; older x from your 48-tab sheet in column D'
        note = ''
        if ws.title == 'New Since 18 Nov': note = 'These 32 brands also appear on their own category tab or on Domestic.'
        if ws.title == 'Domestic': note = 'New brands that sell in essentially one country; they are on this tab only.'
        if xd: note = f'{xd} of the {len(rows)} rows are brands already on your 48-tab sheet that you had marked x there.'
        idx.append([ws.title, grp, len(rows), newb, xb, xd, note]); keep.append((ws, rows))
    order = {'No x anywhere': 0, 'No x in column B; older x from your 48-tab sheet in column D': 1, 'Side list: no x column': 2}
    ws = new.create_sheet('Tabs With No Markings')
    table(ws, ['Tab in the Master', 'Markings', 'Brands on the Tab', 'Of Which New (not on your 48-tab sheet)', 'x in Column B (template)', 'x in Column D (your 48-tab sheet)', 'Note'], [36, 46, 12, 16, 12, 14, 80],
          sorted(idx, key=lambda r: order[r[1]]))
    for src, rows in keep: copy_tab(src, new.create_sheet(src.title), rows, keep_fill=True)
    new.save(out)
    return idx, keep
if __name__ == '__main__':
    idx, keep = main(sys.argv[1], sys.argv[2])
    print(Counter(r[1] for r in idx), '| tabs copied', len(keep), '| rows copied', sum(len(r) for _, r in keep))
    for r in idx: print('  ', r[:6])
