"""Marks, on a copy of the public-companies master workbook, the brands that had an email template built from it
(Public Companies Wave 1, 15 Nov 2026, kept on the email branch under f1run/runs/wave1_15nov) and the sector tabs they sit on.
Usage: templates_mark.py <folder with bNN_rows.json> <source xlsx> <output xlsx>"""
import glob, json, os, re, sys
from collections import Counter, defaultdict
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
RED = PatternFill('solid', start_color='FFFF7C80', end_color='FFFF7C80'); TAB = 'FFFF0000'
ALIAS = {'butterfieldgroup': ('butterfield', 'bankofntbutterfield')}       # template name -> fragments of the name used in the workbook
def norm(s): return re.sub(r'[^a-z0-9]+', '', str(s).lower())
def main(src_dir, src, out):
    T = []
    for f in sorted(glob.glob(os.path.join(src_dir, 'b*_rows.json'))):
        for x in json.load(open(f, encoding='utf-8')): x['_batch'] = int(os.path.basename(f)[1:3]); T.append(x)
    keys = {}
    for x in T:
        for n in (x.get('_user'), x.get('user_name'), x.get('brand'), x.get('legal_name')):
            if n: keys.setdefault(norm(n), x)
    wb = load_workbook(src); found = defaultdict(list); per = Counter()
    for ws in wb.worksheets:
        hdr = [c.value for c in ws[1]]
        if 'Company Name' not in hdr: continue
        ci = hdr.index('Company Name') + 1; n = 0
        for row in ws.iter_rows(min_row=2):
            v = row[ci - 1].value
            if not v: continue
            k = norm(v); x = keys.get(k)
            if x is None:
                x = next((keys[a] for a, frags in ALIAS.items() if a in keys and any(k.startswith(fr) for fr in frags)), None)
            if x is None: continue
            for c in row: c.fill = RED
            found[id(x)].append(ws.title); n += 1
        per[ws.title] = n
        if n and re.match(r'^\d\d ', ws.title): ws.sheet_properties.tabColor = TAB
    ws = wb.create_sheet('Templates Created', 0); ws.sheet_properties.tabColor = TAB
    ws.append(['Brand (as in the template)', 'Sector Tab in This Workbook', 'Template Batch', 'Date Built', 'Version', 'Proposed Designation'])
    for c in ws[1]: c.font = Font(bold=True); c.alignment = Alignment(wrap_text=True, vertical='top')
    rows = []
    for x in T:
        tabs = [t for t in found.get(id(x), []) if re.match(r'^\d\d ', t)]
        rows.append((tabs[0] if tabs else 'Not found by name', x.get('user_name') or x.get('brand'), x['_batch'], x.get('variant', ''), x.get('designation', '')))
    for tab, nm, bt, var, des in sorted(rows, key=lambda r: (r[0], r[2], r[1].lower())): ws.append([nm, tab, bt, '15 Nov 2026', var, des])
    for col, w in zip('ABCDEF', (38, 34, 12, 14, 10, 44)): ws.column_dimensions[col].width = w
    ws.freeze_panes = 'A2'
    wb.save(out)
    missing = [x.get('user_name') for x in T if id(x) not in found]
    print('templates', len(T), '| matched', len(T) - len(missing), '| not found', missing)
    print('rows marked per tab:', {k: v for k, v in per.items() if v})
    print('tabs coloured red:', [w.title for w in wb.worksheets if w.sheet_properties.tabColor is not None and w.sheet_properties.tabColor.rgb == TAB])
if __name__ == '__main__': main(*sys.argv[1:4])
