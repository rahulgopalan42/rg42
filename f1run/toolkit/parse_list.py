# Builds the build register from the user's brand list workbook: one row per brand with tab, tab colour,
# brand, domain, country, sector note, and any leftover marking. Detects the header row per tab.
# Usage: python3.13 -I parse_list.py <list.xlsx> <out_register.json>
import json, re, sys, zipfile, collections
import openpyxl

P, OUT = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(P)
wbx = z.read('xl/workbook.xml').decode()
rels = z.read('xl/_rels/workbook.xml.rels').decode()
rid = {a['Id']: a['Target'].lstrip('/') for a in (dict(re.findall(r'(\w+)="([^"]*)"', m.group(0))) for m in re.finditer(r'<Relationship\b[^>]*>', rels))}
tabcol = {}
for m in re.finditer(r'<sheet\b[^>]*>', wbx):
    a = dict(re.findall(r'([\w:]+)="([^"]*)"', m.group(0)))
    name = a['name'].replace('&amp;', '&'); path = rid[a['r:id']]; path = path if path.startswith('xl/') else 'xl/' + path
    with z.open(path) as f:
        head = f.read(6000).decode(errors='ignore')
    t = re.search(r'<tabColor\b[^>]*/>', head)
    rgb = re.search(r'rgb="([0-9A-Fa-f]+)"', t.group(0)) if t else None
    tabcol[name] = rgb.group(1).upper()[-6:] if rgb else ''
is_red = lambda c: bool(c) and int(c[0:2], 16) >= 0xC0 and int(c[2:4], 16) < 0x80 and int(c[4:6], 16) < 0x80

BRAND_H = ('company name', 'parent company name', 'company', 'brand', 'key_brand', 'most relevant brand')
DOM_H = ('domain', 'website', 'url')
CTRY_H = ('hq_country', 'hq country', 'country')
NOTE_H = ('niche', 'industry / sector', 'sector', 'why this brand / approach', 'why_f1', 'why this brand')
SKIP_VALUES = {'yes', 'no', 'key', 'tbr', 'x'}

wb = openpyxl.load_workbook(P, read_only=True, data_only=True)
reg, summary = [], []
for ws in wb.worksheets:
    rows = ws.iter_rows(values_only=True)
    hdr, hdr_idx, buf = None, None, []
    for i, r in enumerate(rows, start=1):
        cells = [str(v).strip().lower() if v is not None else '' for v in r]
        if any(any(c == h or c.startswith(h) for h in BRAND_H) for c in cells):
            hdr, hdr_idx = cells, i
            break
        if i > 12:
            break
    if hdr is None:
        summary.append((ws.title, tabcol[ws.title], 0, 'NO HEADER FOUND', {}))
        continue
    def col(cands):
        for h in cands:
            for j, c in enumerate(hdr):
                if c == h:
                    return j
        for h in cands:
            for j, c in enumerate(hdr):
                if c.startswith(h):
                    return j
        return None
    bi = col(BRAND_H); di = col(DOM_H); ci = col(CTRY_H); ni = col(NOTE_H)
    # a "most relevant brand / subsidiary" column beats the parent when present
    sub = col(('most relevant brand',))
    marks = collections.Counter(); n = 0; seen = set()
    for r in rows:
        if not r or all(v in (None, '') for v in r):
            continue
        vals = [str(v).strip() if v is not None else '' for v in r]
        brand = vals[bi] if bi < len(vals) else ''
        if not brand or brand.lower() in SKIP_VALUES or re.fullmatch(r'[\d.]+', brand):
            continue
        if brand.lower().startswith(('ranked prospects', 'overall outreach', 'additional unscored')):
            continue
        parent = ''
        if sub is not None and sub < len(vals) and vals[sub] and vals[sub].lower() not in ('', 'n/a', '-', 'same'):
            parent, brand = brand, vals[sub]
        for j, v in enumerate(vals[:bi]):
            if v and j != bi and not re.fullmatch(r'[\d.]+', v) and len(v) <= 6 and v.lower() in ('x', 'xx', 'tbr', 'later', 'check', 'yes', 'no'):
                marks[v] += 1
        key = re.sub(r'[^a-z0-9]', '', brand.lower())
        dup = key in seen; seen.add(key)
        reg.append({'tab': ws.title, 'red': is_red(tabcol[ws.title]), 'brand': brand, 'parent': parent,
                    'domain': (vals[di] if di is not None and di < len(vals) else ''),
                    'country': (vals[ci] if ci is not None and ci < len(vals) else ''),
                    'note': (vals[ni][:160] if ni is not None and ni < len(vals) else ''),
                    'mark': next((v for j, v in enumerate(vals[:bi]) if v.lower() in ('x', 'xx', 'tbr', 'later', 'check')), ''),
                    'dup_in_tab': dup})
        n += 1
    summary.append((ws.title, tabcol[ws.title], n, f'hdr row {hdr_idx}: brand={hdr[bi][:22]} dom={hdr[di][:10] if di is not None else "-"} ctry={hdr[ci][:10] if ci is not None else "-"}', dict(marks)))
json.dump(reg, open(OUT, 'w'), indent=0)
red = sum(1 for r in reg if r['red']); print(f'REGISTER {len(reg)} brands | red {red} | non-red {len(reg) - red}')
for t, c, n, info, mk in summary:
    print(f'{t[:30]:30s} {"RED" if is_red(c) else c or "-":7s} {n:4d}  {info}  marks={mk}')
