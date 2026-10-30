"""Wave 16 final step 1: index every brand in the old Drive files and every earlier-wave file, all worksheets.
Each row keeps its file | sheet and a category so exclusions can be explained. Writes old_v2.pkl."""
import glob, os, re, sys
import openpyxl, pandas as pd
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
R = '/home/user/rg42'
NAMEX = ('brand', 'company', 'company name', 'brand name', 'name', 'key_brand', 'brand / company', 'account name',
         'organization', 'organisation', 'prospect', 'brand (new file)', 'new brand')
NOTNAME = ('parent', 'type', 'size', 'ultimate', 'holding', 'owner', 'sector', 'industry', 'count', 'status', 'source')
rows = []   # name, domain, linkedin, source, category

def cols(h):
    hl = [str(x or '').strip().lower() for x in h]
    ci = next((i for i, x in enumerate(hl) if x in NAMEX), None)
    if ci is None:
        ci = next((i for i, x in enumerate(hl) if ('brand' in x or 'company' in x) and not any(k in x for k in NOTNAME)), None)
    di = next((i for i, x in enumerate(hl) if 'domain' in x or 'website' in x or x in ('url', 'site', 'web')), None)
    li = next((i for i, x in enumerate(hl) if 'linkedin' in x), None)
    return ci, di, li

def add_rows(it, src, cat, loose):
    head = []
    for r in it:                      # header = first of the first 15 rows with a name-like column
        head.append(r)
        ci, di, li = cols(r)
        if ci is not None or di is not None: break
        if len(head) >= 15: break
    else:
        return
    if ci is None and di is None:
        if not loose: return
        ci, di, li = 0, None, None
        it = iter(head + list(it))   # no header: first column holds names
    for r in it:
        g = lambda i: (r[i] if i is not None and i < len(r) else None)
        nm, dm, ln = g(ci), g(di), g(li)
        if isinstance(nm, (int, float)): nm = None
        nm = str(nm).strip() if nm else ''
        dm = str(dm).strip() if dm else ''
        ln = str(ln).strip() if ln else ''
        if nm or dm or ln: rows.append((nm, dm, ln, src, cat))

def category(fname, sheet):
    if 'Database-Sweep-UNCHECKED' in fname:
        return 'Wave 15 database sweep - auto-removed' if re.search(r'^99|removed', sheet, re.I) else 'Wave 15 database sweep (unchecked)'
    if re.search(r'drop|reject|removed|excluded|not ?new|duplicate', sheet, re.I): return 'Earlier wave - dropped/rejected list'
    return 'Earlier wave'

drive = [('master.xlsx', 'MASTER REFERENCE OCT (Drive)'), ('upload_11oct.xlsx', 'Upload 11 Oct (Drive)'),
         ('to_upload_oct11.xlsx', 'To Upload Oct 11 (Drive)'), ('wave14_v4.xlsx', 'Wave 14 V4 (Drive)')]
books = [(f'{S}/old/{f}', name, True) for f, name in drive]
books += [(f, os.path.basename(f)[:-5], False) for f in sorted(glob.glob(f'{R}/reports/*.xlsx')) if 'Wave16' not in f]
log = []
for f, src, is_drive in books:
    wb = openpyxl.load_workbook(f, read_only=True)
    for ws in wb.worksheets:
        n0 = len(rows)
        cat = 'Old master files (Drive)' if is_drive else category(os.path.basename(f), ws.title)
        loose = not re.search(r'read ?me|summary|^00|notes|method', ws.title, re.I)
        add_rows(ws.iter_rows(values_only=True), f'{src} | {ws.title}', cat, loose)
        log.append((src, ws.title, cat, len(rows) - n0))
    print(src, sum(n for s, _, _, n in log if s == src), flush=True)
for f in sorted(glob.glob(f'{R}/reports/*.csv')):
    src = os.path.basename(f)[:-4]
    try: d = pd.read_csv(f, dtype=str, keep_default_na=False, encoding_errors='replace')
    except Exception as e: print('skip', f, e); continue
    n0 = len(rows)
    add_rows(iter([list(d.columns)] + d.values.tolist()), f'{src} | csv', 'Earlier wave', True)
    log.append((src, 'csv', 'Earlier wave', len(rows) - n0))
old = pd.DataFrame(rows, columns=['name', 'domain', 'linkedin', 'source', 'category'])
old.to_pickle(f'{S}/old_v2.pkl')
pd.DataFrame(log, columns=['file', 'sheet', 'category', 'rows indexed']).to_pickle(f'{S}/old_v2_log.pkl')
print('rows', len(old), old['category'].value_counts().to_dict())
print('sheets scanned', len(log), 'with rows', sum(1 for l in log if l[3]))
