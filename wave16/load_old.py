"""Wave 16 step 1b: build the 'already have' index from the old master, Upload 11 Oct, Wave 14 and every earlier wave."""
import glob, json, re, os
import openpyxl, pandas as pd
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
R = '/home/user/rg42'
DOM = re.compile(r'^(?:https?://)?(?:www\.)?([a-z0-9-]+(?:\.[a-z0-9-]+)+)', re.I)
rows = []   # (name, domain, source)

def add_sheet(ws, src, max_blank=200):
    it = ws.iter_rows(values_only=True)
    h = next(it, None)
    if not h: return
    hl = [str(x or '').strip().lower() for x in h]
    ci = next((i for i, x in enumerate(hl) if x in ('company', 'brand', 'name', 'key_brand', 'company name')), None)
    di = next((i for i, x in enumerate(hl) if 'domain' in x or x in ('website', 'url')), None)
    if ci is None:
        ci = 0 if len(hl) and hl[0] not in ('rank', '#') else 1
    blank = 0
    for r in it:
        nm = r[ci] if ci < len(r) else None
        dm = r[di] if di is not None and di < len(r) else None
        if not nm and not dm:
            blank += 1
            if blank > max_blank: break
            continue
        blank = 0
        if isinstance(nm, (int, float)): nm = None
        rows.append((str(nm).strip() if nm else '', str(dm).strip() if dm else '', src))

books = [(f'{S}/old/master.xlsx', 'MASTER REFERENCE OCT'), (f'{S}/old/upload_11oct.xlsx', 'Upload 11 Oct'),
         (f'{S}/old/to_upload_oct11.xlsx', 'To Upload Oct 11'), (f'{S}/old/wave14_v4.xlsx', 'Wave 14 V4')]
SKIPF = ('UNCHECKED', 'CHECKED-2026-10', 'FinServ')     # W15 raw sweep / superseded copies are not delivered prospects
books += [(f, 'Earlier wave: ' + os.path.basename(f)[:-5]) for f in sorted(glob.glob(f'{R}/reports/*.xlsx'))
          if not any(k in f for k in SKIPF)]
for f, src in books:
    wb = openpyxl.load_workbook(f, read_only=True)
    n0 = len(rows)
    for ws in wb.worksheets:
        if re.search(r'read ?me|summary|^00|^99|dropped|reject|^EW', ws.title, re.I): continue
        add_sheet(ws, f'{src} | {ws.title}')
    print(f'{src}: {len(rows) - n0}')
old = pd.DataFrame(rows, columns=['name', 'domain', 'source'])
old['domain'] = old['domain'].str.lower().str.extract(DOM, expand=False).fillna('')
old = old[(old['name'] != '') | (old['domain'] != '')]
old.to_pickle(f'{S}/old_all.pkl')
print('old rows', len(old), 'unique names', old['name'].str.lower().nunique(), 'unique domains', old['domain'].replace('', pd.NA).nunique())
