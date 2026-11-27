"""Clean copy of the user's master workbook holding only the brands marked x, cross-referenced with the Filtered Wave 1 sheet.
Usage: xmarked_clean.py <master.xlsx> <filtered.xlsx> <output.xlsx> [tracker.xlsx]
The x that counts is column B of the master (the template mark, as edited by the user). Column D (the x carried over from the
48-tab sheet) is kept in every row as it is but does not select rows. Category tabs keep the master's columns, widths and order."""
import copy, os, re, sys, unicodedata
from collections import Counter, OrderedDict
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
def norm(s): return re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower())
isx = lambda v: isinstance(v, str) and v.strip().lower() == 'x'
SIDE = {'Templates Created', 'Summary', 'Key', 'Capacity To Confirm', 'Clay Leads (Unconfirmed)', 'Deals Announced - Watch', 'Left Out'}
REPEAT = {'All New Brands', 'Changes Since 18 Nov', 'On Your Sheet - Now Unlisted'}       # the same brands again: every x-marked brand on these is also on a category tab
SPECIAL = {'Funding Talks - Update', 'New Since 18 Nov'}
# on the Filtered sheet, no template built (reasons as recorded in the Wave 1 tracker)
NOT_BUILT = {'Alkira': 'No template built: bought by Lumen Technologies (agreed 5 May 2026) and absorbed.',
             'ECI Telecom': 'No template built: merged into Ribbon Communications (agreed Nov 2019); its products are sold under the Ribbon brand.',
             'Uptake Technologies': 'No template built: being bought by Bosch (announced 19 Mar 2026) and absorbed.',
             'Onfido': 'No template built: bought by Entrust (completed Apr 2024) and absorbed.',
             'Exela Technologies': 'No template built: absorbed after Chapter 11; now part of XBP Global.'}
HEAD = PatternFill('solid', start_color='FF1F3864'); HFONT = Font(bold=True, color='FFFFFFFF'); WRAP = Alignment(wrap_text=True, vertical='top')
def filtered(path):
    wb = load_workbook(path, read_only=True); F = OrderedDict()
    for ws in wb.worksheets:
        R = [list(r) for r in ws.iter_rows(values_only=True) if r and any(c is not None for c in r)]
        if not R: continue
        has_header = any(isinstance(c, str) and c.strip() == 'Company Name' for c in R[0][:4])        # two tabs have no header row: their first row is a brand
        F[ws.title] = [(r[1], r[0]) for r in (R[1:] if has_header else R) if r[1] is not None]
    return F
def copy_tab(src, dst, rows, keep_fill=False):
    for key, dim in src.column_dimensions.items():
        for i in range(dim.min or 1, (dim.max or dim.min or 1) + 1):
            d = dst.column_dimensions[get_column_letter(i)]; d.width = dim.width; d.hidden = dim.hidden
    dst.freeze_panes = src.freeze_panes
    for out_i, src_i in enumerate([1] + rows, 1):
        if src.row_dimensions[src_i].height: dst.row_dimensions[out_i].height = src.row_dimensions[src_i].height
        for c in src[src_i]:
            n = dst.cell(out_i, c.column, c.value)
            if c.has_style:
                n.font = copy.copy(c.font); n.alignment = copy.copy(c.alignment); n.border = copy.copy(c.border); n.number_format = c.number_format
                if src_i == 1 or keep_fill: n.fill = copy.copy(c.fill)
    dst.auto_filter.ref = f'A1:{get_column_letter(src.max_column)}{max(len(rows) + 1, 2)}'
def table(ws, cols, widths, data):
    for j, (c, w) in enumerate(zip(cols, widths), 1):
        x = ws.cell(1, j, c); x.font = HFONT; x.fill = HEAD; x.alignment = Alignment(wrap_text=True, vertical='center'); ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[1].height = 34
    for i, r in enumerate(data, 2):
        for j, v in enumerate(r, 1): ws.cell(i, j, v).alignment = WRAP
    ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{max(len(data) + 1, 2)}'
def main(mpath, fpath, out, tracker=None):
    F = filtered(fpath); fkey = {}
    for t, rows in F.items():
        for nm, mk in rows: fkey.setdefault(norm(nm), (nm, t))
    why = {}
    if tracker and os.path.exists(tracker):
        ws = load_workbook(tracker, read_only=True)['Priority order']; it = ws.iter_rows(values_only=True); h = list(next(it))
        for r in it:
            st = str(r[h.index('Status')] or '')
            if st.startswith('Not built'):
                for nm in (r[h.index('Brand (your sheet)')], r[h.index('Email name')]):
                    if nm: why[norm(nm)] = re.split(r'(?<=[a-z\)])\. ', st)[0].rstrip('.') + '.'
    wb = load_workbook(mpath); new = Workbook(); new.remove(new.active)
    tabs = [ws for ws in wb.worksheets if ws.title not in SIDE and isinstance(ws.cell(1, 1).value, str) and ws.cell(1, 1).value.startswith('Company')]
    xrows = OrderedDict(); stats = []; where = {}                       # tab -> row numbers marked x in column B
    for ws in tabs:
        hdr = [c.value for c in ws[1]]; oi = hdr.index('On Your Sheet?') if 'On Your Sheet?' in hdr else None
        n = newb = onf = 0; rows = []; ftabs = Counter()
        for i in range(2, ws.max_row + 1):
            nm = ws.cell(i, 1).value
            if nm is None: continue
            n += 1
            if oi is not None and str(ws.cell(i, oi + 1).value or '').startswith('No'): newb += 1
            f = fkey.get(norm(nm))
            if f: onf += 1; ftabs[f[1]] += 1
            if isx(ws.cell(i, 2).value):
                rows.append(i)
                if ws.title not in REPEAT: where.setdefault(norm(nm), (nm, ws.title, ws.cell(i, 3).value, isx(ws.cell(i, 4).value)))
        xrows[ws.title] = rows; stats.append((ws.title, n, newb if oi is not None else None, len(rows), onf, ftabs))
    # which master tab each Filtered tab was drawn from: the tab that supplies most of its brands
    home = {}
    for ft, rows in F.items():
        c = Counter()
        for nm, mk in rows:
            for t, n, nb, nx, onf, ftabs in stats:
                if t in REPEAT or t in SPECIAL or t == 'Domestic': continue
                ws = wb[t]
                if any(norm(ws.cell(i, 1).value or '') == norm(nm) for i in xrows[t]) or norm(nm) in {norm(wb[t].cell(i, 1).value or '') for i in range(2, wb[t].max_row + 1)}: c[t] += 1; break
        home[ft] = c.most_common(1)[0][0] if c else ''
    added = {v: k for k, v in home.items()}
    # ---- tab 1: cross-reference
    xr = []; odd = {norm(r[0].value) for r in wb['Funding Talks - Update'].iter_rows(min_row=2) if r[0].value and not isx(r[1].value)}
    for k, (nm, tab, date, own) in where.items():
        f = fkey.get(k); talks = tab == 'Funding Talks - Update'
        note = ''
        if k == norm('Cox Automotive (Autotrader)'): note = 'Same template as Cox Enterprises, which is on the Filtered sheet: the email in the package is addressed to Cox Automotive.'
        if k in odd and not talks: note = 'You removed its x on the Funding Talks tab, but it is still marked x on this tab. Left as you have it.'
        xr.append([nm, tab, 'x added by you on the Funding Talks tab' if talks else 'Template created (Wave 1 package)', date.strftime('%d %b %Y') if hasattr(date, 'strftime') else (date or ''),
                   'Yes' if f else 'No', f[1] if f else '', 'x' if own else '', note])
    order = {t.title: i for i, t in enumerate(tabs)}
    xr.sort(key=lambda r: (order[r[1]], str(r[0]).lower()))
    sits = {}
    for src in tabs:
        if src.title in REPEAT or src.title in SPECIAL: continue
        for i in range(2, src.max_row + 1):
            v = src.cell(i, 1).value
            if v is not None: sits.setdefault(norm(v), src.title)
    rest = [[nm, sits.get(k, 'Not in the master'), 'Not marked x', '', 'Yes', t, '', NOT_BUILT.get(nm, 'No template in the Wave 1 package.')] for k, (nm, t) in fkey.items() if k not in where]
    ws = new.create_sheet('Cross-Reference')
    table(ws, ['Brand', 'Tab in the Master', 'How It Is Marked x', 'Latest Template Created', 'On the Filtered Wave 1 Sheet?', 'Tab on the Filtered Sheet', 'Your x on the 48-Tab Sheet', 'Note'],
          [36, 32, 34, 16, 14, 26, 12, 80], xr + rest)
    # ---- tab 2: which master tabs are on the Filtered sheet
    tb = []
    for t, n, nb, nx, onf, ftabs in stats:
        if t in REPEAT: continue
        if t in added: st = 'Added'; fn = added[t]
        elif onf and t not in SPECIAL and t != 'Domestic': st = 'No tab of its own'; fn = '; '.join(f'{v} under "{k}"' for k, v in ftabs.items())
        else: st = 'Not added'; fn = ''
        tb.append([t, st, fn, n, nb if nb is not None else '', nx, onf])
    ws = new.create_sheet('Tabs vs Filtered Sheet')
    table(ws, ['Tab in the Master', 'On the Filtered Wave 1 Sheet?', 'Where on the Filtered Sheet', 'Brands on the Tab', 'Of Which New (not on your 48-tab sheet)', 'Marked x', 'Brands Also on the Filtered Sheet'], [36, 20, 44, 12, 16, 10, 16],
          sorted(tb, key=lambda r: ({'Not added': 0, 'No tab of its own': 1, 'Added': 2}[r[1]], order[r[0]])))
    # ---- the master's own tabs, x-marked rows only
    for src in tabs:
        if src.title in REPEAT or not xrows[src.title]: continue
        copy_tab(src, new.create_sheet(src.title), xrows[src.title])
    new.save(out)
    return xr, rest, tb, stats, F
if __name__ == '__main__':
    xr, rest, tb, stats, F = main(*sys.argv[1:5])
    print('x-marked brands', len(xr), Counter(r[2] for r in xr), '| on the Filtered sheet', Counter(r[4] for r in xr), '| on Filtered, not marked', [r[0] for r in rest])
    print('tabs:', Counter(r[1] for r in tb))
    for r in tb: print('  ', r)
