"""Marks, on a copy of the new-brands (private companies) workbook, the brands that have an email template in the
'New Private Companies - Wave 1 (priority order)' package (25 batch folders, built 17 Nov 2026): the brand rows and the
tabs they sit on turn green, and a new column gives the date the latest template for the brand was created.

Usage: templates_mark_private.py <unpacked package dir> <package zip> <source xlsx> <output xlsx> [tracker xlsx] [brands.json.gz]
  the tracker (email branch, f1run/runs/new_private_wave1_17nov/00 Tracker ...xlsx) is optional: it names the brands
  that were on the Wave 1 sheet but had no template built.
  brands.json.gz (brandprofile/data, the parsed copy of the user's 48-tab sheet) is optional: with it the workbook also
  gets the user's own style of marking: a column with "x" for a brand that has a template and blank for the rest, and a
  column that repeats the x marks the user had put on the 48-tab sheet."""
import copy, datetime, glob, gzip, html, json, os, re, sys, unicodedata, zipfile
from collections import Counter, defaultdict
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
GREEN = PatternFill('solid', start_color='FF92D050', end_color='FF92D050'); TAB = 'FF00B050'
COL = 'Latest Template Created'; NOT_TAB = {'All New Brands'}            # the combined tab: rows are marked, the tab keeps its colour
XCOL = 'Template Created - Wave 1 Zip (x)'; UCOL = 'Your x Mark on the 48-Tab Sheet'
def norm(s): return re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower())
def loose(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower().replace('&', ' and ')
    s = re.sub(r'\(.*?\)', ' ', s); s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|plc|sa|ag|se|nv|bv|gmbh|spa|holdings?|group|the)\b', ' ', s)
    return re.sub(r'\s+', '', s)
def read_package(root, zpath):
    """one record per brand in the package: priority, names, batch folder, mail merge, contacts, whether its email is in the batch document, date"""
    zf = zipfile.ZipFile(zpath); zdate = {}
    for i in zf.infolist():
        m = re.search(r'/(Batch (\d+)[^/]*)/Batch \d+ - Emails\.docx$', i.filename)
        if m and '__MACOSX' not in i.filename: zdate[int(m.group(2))] = datetime.date(*i.date_time[:3])
    T = []
    for d in sorted(glob.glob(os.path.join(root, '*', 'Batch *')), key=lambda p: int(re.match(r'Batch (\d+)', os.path.basename(p)).group(1))):
        bn = int(re.match(r'Batch (\d+)', os.path.basename(d)).group(1)); files = [f for f in os.listdir(d) if not f.startswith(('~$', '.'))]
        wb = load_workbook(os.path.join(d, next(f for f in files if f.endswith('Contacts.xlsx'))), read_only=True)
        C = list(wb['Contacts'].iter_rows(values_only=True)); ch = [str(x) for x in C[0]]
        ename = {str(r[ch.index('Brand')]).strip(): str(r[ch.index('Email name')]).strip() for r in C[1:] if r[ch.index('Brand')]}
        merge = {}
        for f in files:
            if 'Merge list' not in f: continue
            R = list(load_workbook(os.path.join(d, f), read_only=True).worksheets[0].iter_rows(values_only=True)); ci = [str(x) for x in R[0]].index('Company')
            kind = 'Mail merge ' + re.search(r'Mail merge (\d+ of \d+ - .*?) - Merge list', f).group(1)
            for r in R[1:]: merge[norm(r[ci])] = kind
        x = zipfile.ZipFile(os.path.join(d, next(f for f in files if f.endswith('Emails.docx')))).read('word/document.xml').decode('utf-8', 'replace')
        heads = {norm(re.sub(r'\s*\((B2B|B2C)[^)]*\)\s*$', '', html.unescape(re.sub(r'<[^>]+>', '', p)))) for p in re.findall(r'<w:p[ >].*?</w:p>', x, re.S)}
        S = list(wb['Summary'].iter_rows(values_only=True)); sh = [str(x) for x in S[0]]
        for r in S[1:]:
            if not r[sh.index('Brand')]: continue
            b = str(r[sh.index('Brand')]).strip(); en = ename.get(b, b)
            T.append({'prio': len(T) + 1, 'brand': b, 'email_name': en, 'batch': bn, 'folder': os.path.basename(d), 'status': str(r[sh.index('Template status')]),
                      'contacts': r[sh.index('Contacts')], 'merge': merge.get(norm(en)) or merge.get(norm(b)) or 'No contacts found: not in a mail merge',
                      'in_doc': norm(b) in heads or norm(en) in heads, 'date': zdate.get(bn)})
    return T
def insert_cols(ws, at, cols):
    """cols = [(title, width), ...] inserted from column `at`; widths, the filter and the frozen panes follow"""
    n = ws.max_column; W = {}; k = len(cols)
    for dim in ws.column_dimensions.values():
        for i in range(dim.min or 0, (dim.max or 0) + 1): W[i] = dim.width
    ws.insert_cols(at, k)
    for i in range(n, at - 1, -1):
        if i in W: ws.column_dimensions[get_column_letter(i + k)].width = W[i]
    s = ws.cell(1, 1)
    for j, (title, width) in enumerate(cols):
        ws.column_dimensions[get_column_letter(at + j)].width = width
        h = ws.cell(1, at + j, title); h.font = copy.copy(s.font); h.fill = copy.copy(s.fill); h.alignment = copy.copy(s.alignment); h.border = copy.copy(s.border)
    if ws.auto_filter.ref: ws.auto_filter.ref = f'A1:{get_column_letter(n + k)}{ws.max_row}'
    ws.freeze_panes = ws.cell(2, at + k).coordinate
def main(root, zpath, src, out, tracker=None, brands=None):
    T = read_package(root, zpath)
    U = {}                                                             # the user's own x marks: normalised brand name -> marked on any tab
    if brands and os.path.exists(brands):
        for d in json.load(gzip.open(brands, 'rt', encoding='utf-8')):
            for nm in (d.get('brand'), d.get('orig_brand')):
                if nm: U[norm(nm)] = U.get(norm(nm), False) or bool(d.get('mark'))
    xstyle = bool(U); cols = ([(XCOL, 14)] if xstyle else []) + [(COL, 17)] + ([(UCOL, 13)] if xstyle else []); dj = 3 if xstyle else 2; umark = Counter()
    key = {}; lkey = {}
    for x in T:
        for nm in (x['brand'], x['email_name']): key.setdefault(norm(nm), x); lkey.setdefault(loose(nm), x)
    wb = load_workbook(src); found = defaultdict(list); per = Counter(); viaLoose = []
    for ws in wb.worksheets:
        h1 = ws.cell(1, 1).value
        if not (isinstance(h1, str) and h1.startswith('Company')): continue
        hit = {}                                                      # row number -> template record
        for (v,), i in zip(ws.iter_rows(min_row=2, max_col=1, values_only=True), range(2, ws.max_row + 1)):
            if not v: continue
            x = key.get(norm(v))
            if x is None:
                x = lkey.get(loose(v))
                if x is not None: viaLoose.append((ws.title, v, x['brand']))
            if x is not None: hit[i] = x
        if h1 != 'Company Name' and not hit: continue                 # a side list with no templated brand: left as it is
        insert_cols(ws, 2, cols); n = 0
        if xstyle:
            for i in range(2, ws.max_row + 1):
                v = ws.cell(i, 1).value
                if v and U.get(norm(v)): c = ws.cell(i, 4); c.value = 'x'; c.alignment = Alignment(horizontal='center', vertical='top'); umark[ws.title] += 1
        for i, x in hit.items():
            for c in ws[i]: c.fill = GREEN
            c = ws.cell(i, dj); c.value = x['date']; c.number_format = 'd mmm yyyy'; c.alignment = Alignment(vertical='top'); c.fill = GREEN
            if xstyle:
                c = ws.cell(i, 2); c.value = 'x'; c.alignment = Alignment(horizontal='center', vertical='top'); c.fill = GREEN; ws.cell(i, 4).fill = GREEN
            found[x['prio']].append(ws.title); n += 1
        per[ws.title] = n
        if n and ws.title not in NOT_TAB: ws.sheet_properties.tabColor = TAB
    ws = wb.create_sheet('Templates Created', 0); ws.sheet_properties.tabColor = TAB
    dates = sorted({x['date'] for x in T if x['date']})
    ws.append([f"{len(T)} brands have an email template in the package 'New Private Companies - Wave 1 (priority order)' (25 batches). "
               f"All were created on {' and '.join(d.strftime('%d %b %Y').lstrip('0') for d in dates)}. Green rows and green tabs in this workbook = template created."
               + (f" Column B on every company tab ('{XCOL}') holds an x for a brand with a template and is blank for the rest; column D repeats the x marks from your 48-tab sheet." if xstyle else '')])
    ws.append([])
    hdr = ['Priority', 'Brand', 'Name Used in the Email', COL, 'Batch Folder', 'Mail Merge in That Batch', 'Contacts', 'Tab in This Workbook', "Email Found in the Batch's Emails Document?"] + ([XCOL, UCOL] if xstyle else [])
    ws.append(hdr)
    for c in ws[3]: c.font = Font(bold=True, color='FFFFFFFF'); c.fill = PatternFill('solid', start_color='FF1F3864', end_color='FF1F3864'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for x in T:
        tabs = [t for t in found.get(x['prio'], []) if t not in NOT_TAB]
        ws.append([x['prio'], x['brand'], x['email_name'], x['date'], x['folder'], x['merge'], x['contacts'], '; '.join(dict.fromkeys(tabs)) or 'Not found by name', 'Yes' if x['in_doc'] else 'No']
                  + (['x', 'x' if U.get(norm(x['brand'])) else None] if xstyle else []))
        ws.cell(ws.max_row, 4).number_format = 'd mmm yyyy'
    last = ws.max_row
    if tracker and os.path.exists(tracker):
        R = list(load_workbook(tracker, read_only=True)['Priority order'].iter_rows(values_only=True)); th = [str(x) for x in R[0]]
        nb = [r for r in R[1:] if r[th.index('Brand (your sheet)')] and str(r[th.index('Status')]).startswith('Not built')]
        if nb:
            ws.append([]); ws.append([f'{len(nb)} brands on the Wave 1 sheet have no template in the package (not marked green):']); ws.cell(ws.max_row, 1).font = Font(bold=True)
            ws.append(['', 'Brand', '', COL, '', '', '', 'Tab on the Wave 1 Sheet', 'Why No Template Was Built'])
            for c in ws[ws.max_row]: c.font = Font(bold=True)
            for r in nb: ws.append(['', r[th.index('Brand (your sheet)')], '', 'None', '', '', '', r[th.index('Sheet tab')], re.sub(r'^Not built: ', '', re.sub(r'\s+', ' ', str(r[th.index('Status')])))[:400]])
    for col, w in zip('ABCDEFGHIJK', (9, 30, 28, 17, 44, 34, 9, 44, 30, 11, 13)): ws.column_dimensions[col].width = w
    ws.freeze_panes = 'A4'; ws.auto_filter.ref = f"A3:{'K' if xstyle else 'I'}{last}"
    wb.save(out)
    missing = [x['brand'] for x in T if x['prio'] not in found]
    print('brands in the package', len(T), '| dates', dates, '| email missing from the batch document:', [x['brand'] for x in T if not x['in_doc']])
    print('matched in the workbook', len(T) - len(missing), '| not found', missing)
    print('matched by a looser name:', viaLoose)
    print('rows marked per tab:', {k: v for k, v in per.items() if v})
    print('tabs coloured green:', [w.title for w in wb.worksheets if w.sheet_properties.tabColor is not None and w.sheet_properties.tabColor.rgb == TAB])
    if xstyle: print('rows carrying your own x mark, per tab:', {k: v for k, v in umark.items() if v}, '| total', sum(umark.values()))
if __name__ == '__main__': main(*sys.argv[1:7])
