"""Marks in blue, on the user's copy of the New Brands workbook, every brand that also appears in the Private Sheet Batch 1 workbook
or the Public Companies Master workbook. Usage: mark.py <input folder> <output file>"""
import sys, re, unicodedata, copy
from collections import defaultdict, Counter
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
D, OUT = sys.argv[1], sys.argv[2]
BLUE = PatternFill('solid', start_color='FF9DC3E6', end_color='FF9DC3E6')
FORMS = re.compile(r'(?i)\b(groupe?|gruppo|grupo|holding|holdings|technology|technologies|international|company|companies|corporation|corp|enterprises|industries|limited|ltd|inc|llc|gmbh|kgaa|kg|se|ag|co|cie|sa|spa|bv|nv|as|ab|asa|pty|plc|lp|the|and|mbh)\b')
def fold(s): return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
def key(n):
    n = fold(str(n)).lower(); n = re.sub(r'\(.*?\)', ' ', n); n = re.sub(r'\b(b\.v\.?|n\.v\.?|s\.a\.?|s\.p\.a\.?|l\.p\.?|a/s)(?=\s|,|$)', ' ', n)
    k = re.sub(r'[^a-z0-9]', '', FORMS.sub(' ', n))
    return k or re.sub(r'[^a-z0-9]', '', n)
# same name, different company (read one by one): not repeats
NAMESAKE = {('HUB International', 'pub'), ('POET', 'pub'), ('Zip', 'priv'), ('Zip', 'pub'), ('Alight', 'pub'), ('Bird', 'priv'), ('Humana', 'pub')}
UMBRELLA = {'Master Brands', 'Master Companies'}
def names(path):
    wb = load_workbook(path, read_only=True); out = defaultdict(lambda: [None, []])
    for ws in wb.worksheets:
        ci = None
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                hdr = [str(c) if c is not None else '' for c in row]
                if 'Company Name' not in hdr: break
                ci = hdr.index('Company Name'); continue
            if ci < len(row) and row[ci]:
                e = out[key(row[ci])]; e[0] = e[0] or str(row[ci]).strip()
                if ws.title not in e[1]: e[1].append(ws.title)
    return out
P = names(D + '/private_batch1.xlsx'); U = names(D + '/public_master.xlsx')
def where(name):
    k = key(name); parts = []
    for tag, lab, O in (('priv', 'Private Sheet - Batch 1', P), ('pub', 'Public Companies Master', U)):
        if k in O and (name.strip(), tag) not in NAMESAKE:
            tabs = [t for t in O[k][1] if t not in UMBRELLA] or O[k][1]
            parts.append(f"{lab} (tab: {', '.join(tabs)})")
    return '; '.join(parts)
wb = load_workbook(D + '/new_brands.xlsx')
stats = Counter(); listing = {}
for ws in wb.worksheets:
    hdr = [str(c.value) if c.value is not None else '' for c in ws[1]]
    col = 'Company Name' if 'Company Name' in hdr else 'Company (on your sheet)' if 'Company (on your sheet)' in hdr else None
    if not col: continue
    ci = hdr.index(col) + 1; ncol = ws.max_column; new = ncol + 1; hits = []
    for r in range(2, ws.max_row + 1):
        v = ws.cell(r, ci).value
        if not v: continue
        w = where(str(v))
        if w: hits.append((r, str(v).strip(), w))
    if not hits: continue
    h = ws.cell(1, new, 'Repeated In (Other Workbooks)'); src = ws.cell(1, ncol)
    h.font = copy.copy(src.font); h.fill = copy.copy(src.fill); h.alignment = copy.copy(src.alignment); h.border = copy.copy(src.border)
    ws.column_dimensions[get_column_letter(new)].width = 62
    for r, v, w in hits:
        for c in range(1, ncol + 1):
            cell = ws.cell(r, c)
            if cell.fill is None or cell.fill.fill_type in (None, 'none'): cell.fill = BLUE          # status colours already on the row are kept
        ws.cell(r, ci).fill = BLUE
        x = ws.cell(r, new, w); x.fill = BLUE; x.alignment = Alignment(wrap_text=True, vertical='top')
        stats[ws.title] += 1; listing.setdefault(v, [w, []])[1].append(ws.title)
    if ws.auto_filter and ws.auto_filter.ref: ws.auto_filter.ref = f"A1:{get_column_letter(new)}{ws.max_row}"
# one list of everything marked, at the end of the workbook
ls = wb.create_sheet('Repeats - Marked Blue')
ls.append(['Brand', 'Tab(s) in This Workbook', 'Also Appears In'])
for c in ls[1]: c.font = Font(bold=True, color='FFFFFFFF'); c.fill = PatternFill('solid', start_color='FF1F3864', end_color='FF1F3864')
for v in sorted(listing, key=str.lower):
    ls.append([v, ', '.join(listing[v][1]), listing[v][0]])
    for c in ls[ls.max_row]: c.fill = BLUE
for j, wd in enumerate((38, 46, 80), 1): ls.column_dimensions[get_column_letter(j)].width = wd
ls.freeze_panes = 'A2'
wb.save(OUT)
both = sum(1 for v in listing.values() if 'Private' in v[0] and 'Public' in v[0])
print('rows marked per tab:', dict(stats))
print('brands marked:', len(listing), '| in Private Batch 1:', sum(1 for v in listing.values() if 'Private' in v[0]), '| in Public Master:', sum(1 for v in listing.values() if 'Public' in v[0]), '| in both:', both)
print('public master ones:', sorted(v for v, w in listing.items() if 'Public' in w[0]))
