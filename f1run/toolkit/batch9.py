# Public Companies Wave 1: <=40-contact batches packed into ONE organized zip. Usage: python3.13 -I batch9.py [--dry]
import json, glob, re, subprocess, sys, os, math, shutil, zipfile, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
CAP = 40; TITLE = 'Public Companies Wave 1'
items = json.load(open('pubw1/items.json'))
rows = []
for f in sorted(glob.glob('nb9_[0-9][0-9]_rows.json')): rows += json.load(open(f))
byuser = {}
for r in rows:
    if r.get('user_name'): byuser[r['user_name'].strip()] = r
key = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
bykey = {key(r['brand']): r for r in rows}
# contacts: saved ones that fit (keep) + this job's enrichment
cs = {r['user_name']: r for r in json.load(open('pubw1/cs9_all.json'))}
C = {}
for u, r in cs.items(): C[u] = {'people': [dict(name=p['name'], title=p['title'], email=p['email']) for p in r['keep']], 'note': 'Saved contacts from earlier Apollo runs.' if r['keep'] else ''}
for f in sorted(glob.glob('en9_*_out.json')):
    for r in json.load(open(f))['rows']:
        u = r.get('user_name') or r['brand']; c = C.setdefault(u, {'people': [], 'note': ''})
        have = {p['email'].lower() for p in c['people']}
        c['people'] += [p for p in r['people'] if p['email'].lower() not in have]
        if r.get('note'): c['note'] = (c['note'] + ' ' + r['note']).strip()
DROP = json.load(open('pubw1/drop_contacts.json'))
for u in C:
    C[u]['people'] = [p for p in C[u]['people'] if p['email'].lower() not in DROP and 'daniel brow' not in p.get('name', '').lower()][:4]
    for p in C[u]['people']:
        for kk in ('title', 'name'):
            if p.get(kk): p[kk] = re.sub(r'\s*[\u2013\u2014]\s*', ', ', p[kk])
order = []; missing = []
for it in items:
    r = byuser.get(it['user_name']) or bykey.get(key(it['brand']))
    if r is None: missing.append(it['user_name']); continue
    r = dict(r); r['_tab'] = it['tab']; r['_user'] = it['user_name']; r['_order'] = it['order']; order.append(r)
if missing: print('MISSING ROWS', len(missing), missing[:20])
dec = lambda r: bool(r.get('skip') or any(str(x).startswith('DECLINED') for x in r.get('flags', [])))
declined = [r for r in order if dec(r)]; live = [r for r in order if not dec(r)]
CB = {r['brand']: C.get(r['_user'], {'people': [], 'note': ''}) for r in order}
for r in live:
    r['flags'] = [x for x in r.get('flags', []) if not str(x).startswith('Contacts:')]
    if not CB[r['brand']]['people']: r['flags'].append('Contacts: none found in Apollo.')
k = lambda r: len(CB[r['brand']]['people'])
def pack(rs, lim):
    out = []; cur = []; n = 0
    for r in rs:
        if cur and n + k(r) > lim: out.append(cur); cur = []; n = 0
        cur.append(r); n += k(r)
    if cur: out.append(cur)
    return out
tot = sum(k(r) for r in live); nb = max(1, math.ceil(tot / CAP)); batches = pack(live, CAP)
for lim in range(math.ceil(tot / nb), CAP + 1):
    p = pack(live, lim)
    if len(p) <= nb: batches = p; break
print('brands', len(order), 'live', len(live), 'declined', len(declined), 'contacts', tot, 'batches', len(batches))
for i, b in enumerate(batches, 1): print(f"  batch {i:02d} brands {len(b):2d} contacts {sum(k(r) for r in b):2d} tabs {sorted(set(r['_tab'] for r in b))}")
if '--dry' in sys.argv: sys.exit()
root = 'pubw1/pkg/' + TITLE; shutil.rmtree('pubw1/pkg', ignore_errors=True); os.makedirs(root + '/Mail merge templates')
json.dump(CB, open('pubw1/_c.json', 'w'))
tr = openpyxl.Workbook(); ws = tr.active; ws.title = 'Tracker'
ws.append(['Batch', 'Folder', 'Sheet tab', 'Brand (your sheet)', 'Email name', 'Status', 'Contacts', 'Sent? (tick)', 'Key flags'])
summ = []
for i, b in enumerate(batches, 1):
    label = f'Wave 1 - Batch {i:02d}'; n = sum(k(r) for r in b)
    folder = f'Batch {i:02d} ({n} contacts)'; d = f'{root}/{folder}'; os.makedirs(d + '/Mail merge')
    json.dump(b, open(f'pubw1/b{i:02d}_rows.json', 'w'), indent=1)
    json.dump({'rows': [{'brand': r['brand'], 'people': CB[r['brand']]['people']} for r in b]}, open(f'pubw1/b{i:02d}_contacts.json', 'w'), indent=1)
    out = subprocess.run(['python3.13', '-I', 'v7_assemble.py', label, f'pubw1/b{i:02d}_rows.json', f'pubw1/b{i:02d}_contacts.json'], capture_output=True, text=True)
    if 'DONE' not in out.stdout: print('ASSEMBLE FAIL', i, out.stdout[-300:], out.stderr[-300:])
    open(f'pubw1/b{i:02d}_names.txt', 'w').write('\n'.join(r['brand'] for r in b))
    subprocess.run(['python3.13', '-I', 'contacts_sheet.py', f'pubw1/b{i:02d}_names.txt', f'pubw1/b{i:02d}_rows.json', 'pubw1/_c.json', f'{label} - Contacts.xlsx'], capture_output=True)
    shutil.move(f'{label} - Emails Ready.docx', f'{d}/Batch {i:02d} - Emails.docx')
    shutil.move(f'{label} - Contacts.xlsx', f'{d}/Batch {i:02d} - Contacts.xlsx')
    for g in glob.glob(f'{label} - Merge List - *.xlsx'): shutil.move(g, f"{d}/Mail merge/Batch {i:02d} - {g.split(' - ', 2)[2]}")
    for g in glob.glob(f'{label} - Flagged Brands.xlsx') + glob.glob(f'{label.upper()} - Complete.zip'): os.remove(g)
    for r in b:
        fl = [str(x) for x in r['flags'] if not str(x).startswith(('Contacts:',))]
        imp = [x for x in fl if re.search(r'HOLD|resign|PENDING|ACQUIRED|ALREADY|1260H|Entity List|USER INSTRUCTION|Same house|Reputation|Capacity: (hard|firm)|HQ override|Existing F1|former F1|Rebuilt', x, re.I)]
        key_flags = ' | '.join(dict.fromkeys([x[:170] for x in (fl[:1] + imp) if not x.startswith('Rebuilt')]))[:600]
        ws.append([i, folder, r['_tab'], r['_user'], r.get('email_name') or r['brand'], 'Template + contacts' if k(r) else 'Template only (no contacts found)', k(r), '', key_flags])
    summ.append((i, folder, len(b), n, ', '.join(dict.fromkeys(r['_tab'] for r in b))))
for r in declined:
    reason = re.sub(r'^DECLINED:\s*', '', str(r.get('skip') or next(x for x in r['flags'] if str(x).startswith('DECLINED'))))
    ws.append(['-', '-', r['_tab'], r['_user'], r['brand'], 'Declined: ' + reason[:300], 0, '', ''])
for m in glob.glob('F1 Merge Master v7 - *.docx'): shutil.copy(m, f'{root}/Mail merge templates/')
s2 = tr.create_sheet('Batches', 0); s2.append(['Batch', 'Folder', 'Brands', 'Contacts', 'Sheet tabs covered', 'Sent? (tick)'])
for x in summ: s2.append(list(x) + [''])
s2.append([]); s2.append(['Total', '', sum(x[2] for x in summ), sum(x[3] for x in summ), f'{len(declined)} declined (see Tracker)'])
for wsx, widths in ((ws, [7, 22, 22, 34, 30, 30, 9, 11, 110]), (s2, [7, 24, 8, 9, 70, 11])):
    for c in wsx[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
    for j, wd in enumerate(widths): wsx.column_dimensions[openpyxl.utils.get_column_letter(j + 1)].width = wd
    wsx.freeze_panes = 'A2'
ws.auto_filter.ref = ws.dimensions
tr.save(f'{root}/00 Tracker - {TITLE}.xlsx')
zn = f'{TITLE.upper()} - Complete.zip'
if os.path.exists(zn): os.remove(zn)
with zipfile.ZipFile(zn, 'w', zipfile.ZIP_DEFLATED) as z:
    allf = sorted(os.path.join(dp, f) for dp, _, fs in os.walk('pubw1/pkg') for f in fs)
    for p in allf: z.write(p, os.path.relpath(p, 'pubw1/pkg'))
print('done', zn)
