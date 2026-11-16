# F1 Private Sheet Batch 1: <=40-contact batches in ONE organized zip, plus a "Done yesterday" folder. Usage: python3.13 -I batch10.py [--dry]
import json, glob, re, subprocess, sys, os, math, shutil, zipfile, openpyxl
from openpyxl.styles import Font, PatternFill
CAP = 40; TITLE = 'F1 Private Sheet - Batch 1'
items = json.load(open('priv1/items.json'))
DEC = json.load(open('priv1/decisions.json'))
rows = []
for f in sorted(glob.glob('nb10_[0-9][0-9]_rows.json')): rows += json.load(open(f))
key = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
byuser = {}; bykey = {}
for r in rows:
    if r.get('user_name'): byuser[r['user_name'].strip()] = r
    bykey.setdefault(key(r['brand']), r)
cs = {r['user_name']: r for r in json.load(open('priv1/cs10_all.json'))}
DROP = {}
for f in ('pubw1/drop_contacts.json', 'priv1/drop_contacts.json'): DROP.update(json.load(open(f)))
C = {}
for u, r in cs.items(): C[u] = {'people': [dict(name=p['name'], title=p['title'], email=p['email']) for p in r['keep']], 'note': 'Saved contacts from earlier Apollo runs.' if r['keep'] else ''}
for f in sorted(glob.glob('en10_*_out.json')):
    for r in json.load(open(f))['rows']:
        u = r.get('user_name') or r['brand']; c = C.setdefault(u, {'people': [], 'note': ''})
        have = {p['email'].lower() for p in c['people']}
        c['people'] += [p for p in r['people'] if p['email'].lower() not in have]
        if r.get('note'): c['note'] = (c['note'] + ' ' + r['note']).strip()
def clean(ppl):
    out = []
    for p in ppl:
        if p['email'].lower() in DROP: continue
        p = dict(p)
        for kk in ('title', 'name'):
            if p.get(kk): p[kk] = re.sub(r'\s*[–—]\s*', ', ', p[kk])
        out.append(p)
    return out[:4]
for u in C: C[u]['people'] = clean(C[u]['people'])
order = []; missing = []
for it in items:
    r = byuser.get(it['user_name']) or bykey.get(key(it['brand']))
    if r is None: missing.append(it['user_name']); continue
    r = dict(r); r['_tab'] = it['tab']; r['_user'] = it['user_name']
    if it['user_name'] in DEC['decline']: r['skip'] = DEC['decline'][it['user_name']]
    if it['user_name'] in DEC.get('email_name', {}): r['email_name'] = DEC['email_name'][it['user_name']]
    order.append(r)
if missing: print('MISSING ROWS', len(missing), missing[:15])
dec = lambda r: bool(r.get('skip') or any(str(x).startswith('DECLINED') for x in r.get('flags', [])))
declined = [r for r in order if dec(r)]; live = [r for r in order if not dec(r)]
CB = {r['brand']: C.get(r['_user'], {'people': [], 'note': ''}) for r in order}
for r in live:
    r['flags'] = [x for x in r.get('flags', []) if not str(x).startswith('Contacts:')]
    if not CB[r['brand']]['people']: r['flags'].append('Contacts: none found in Apollo.')
# yesterday's 33, copied as delivered
Y = json.load(open('priv1/yesterday_rows.json')); YC = {c['brand']: {'people': clean(c['people']), 'note': 'Delivered 15 Nov (Public Companies Wave 1).'} for c in json.load(open('priv1/yesterday_contacts.json'))['rows']}
for r in Y: r['_user'] = r['_sheet_name']
def pack(rs, CBx, lim):
    out = []; tot = []
    for r in rs:
        kx = len(CBx[r['brand']]['people'])
        for j in range(max(0, len(out) - 3), len(out)):
            if tot[j] + kx <= lim: out[j].append(r); tot[j] += kx; break
        else: out.append([r]); tot.append(kx)
    return out
def balanced(rs, CBx):
    tot = sum(len(CBx[r['brand']]['people']) for r in rs); nb = max(1, math.ceil(tot / CAP)); best = pack(rs, CBx, CAP)
    for lim in range(math.ceil(tot / nb), CAP + 1):
        p = pack(rs, CBx, lim)
        if len(p) <= nb: return p
    return best
batches = balanced(live, CB); ybatches = balanced(Y, YC)
print('brands', len(order), 'live', len(live), 'declined', len(declined), 'contacts', sum(len(CB[r['brand']]['people']) for r in live), 'batches', len(batches), '| yesterday', len(Y), 'contacts', sum(len(v['people']) for v in YC.values()), 'batches', len(ybatches))
for i, b in enumerate(batches, 1): print(f"  batch {i:02d} brands {len(b):2d} contacts {sum(len(CB[r['brand']]['people']) for r in b):2d} tabs {sorted(set(r['_tab'] for r in b))}")
if '--dry' in sys.argv: sys.exit()
root = 'priv1/pkg/' + TITLE; shutil.rmtree('priv1/pkg', ignore_errors=True); os.makedirs(root)
tr = openpyxl.Workbook(); ws = tr.active; ws.title = 'Tracker'
ws.append(['Batch', 'Folder', 'Sheet tab', 'Brand (your sheet)', 'Email name', 'Status', 'Contacts', 'Mail merge to use', 'Sent? (tick)', 'Key flags'])
summ = []
ORDER = ['B2B', 'B2B no reference', 'B2C', 'B2C no reference']
GRP = lambda r: ('B2C' if (r.get('variant') or 'B2B').upper().startswith('B2C') else 'B2B') + ('' if r.get('market_reference') else ' no reference')
def build(b, CBx, i, folder_root, tag, status_word, tabkey):
    n = sum(len(CBx[r['brand']]['people']) for r in b)
    label = f'{tag} - Batch {i:02d}'; folder = f'{tag.split(" - ")[-1] if " - " in tag else "Batch"} {i:02d} ({n} contacts)' if False else (f'Batch {i:02d} ({n} contacts)' if tag == 'P1' else f'Yesterday Batch {i:02d} ({n} contacts)')
    d = f'{folder_root}/{folder}'; os.makedirs(d)
    pre0 = 'Batch' if tag == 'P1' else 'Yesterday Batch'
    json.dump(b, open(f'priv1/{tag}{i:02d}_rows.json', 'w'), indent=1)
    json.dump({'rows': [{'brand': r['brand'], 'people': CBx[r['brand']]['people']} for r in b]}, open(f'priv1/{tag}{i:02d}_contacts.json', 'w'), indent=1)
    json.dump(CBx, open('priv1/_c.json', 'w'))
    out = subprocess.run(['python3.13', '-I', 'v7_assemble.py', label, f'priv1/{tag}{i:02d}_rows.json', f'priv1/{tag}{i:02d}_contacts.json'], capture_output=True, text=True)
    if 'DONE' not in out.stdout: print('ASSEMBLE FAIL', tag, i, out.stdout[-300:], out.stderr[-300:])
    open(f'priv1/{tag}{i:02d}_names.txt', 'w').write('\n'.join(r['brand'] for r in b))
    subprocess.run(['python3.13', '-I', 'contacts_sheet.py', f'priv1/{tag}{i:02d}_names.txt', f'priv1/{tag}{i:02d}_rows.json', 'priv1/_c.json', f'{label} - Contacts.xlsx'], capture_output=True)
    shutil.move(f'{label} - Emails Ready.docx', f'{d}/{pre0} {i:02d} - Emails.docx')
    shutil.move(f'{label} - Contacts.xlsx', f'{d}/{pre0} {i:02d} - Contacts.xlsx')
    lists = sorted(glob.glob(f'{label} - Merge List - *.xlsx'), key=lambda g: ORDER.index(g.split(' - Merge List - ')[1][:-5]))
    mm = []
    for kk, g in enumerate(lists, 1):
        grp = g.split(' - Merge List - ')[1][:-5]; cnt = openpyxl.load_workbook(g).active.max_row - 1
        pre = f'{pre0} {i:02d} - Mail merge {kk} of {len(lists)} - {grp}'
        shutil.move(g, f'{d}/{pre} - Merge list ({cnt} contacts).xlsx')
        shutil.copy(f'F1 Merge Master v7 - {grp}.docx', f'{d}/{pre} - Word template.docx')
        mm.append((grp, cnt))
    for g in glob.glob(f'{label} - Flagged Brands.xlsx') + glob.glob(f'{label.upper()} - Complete.zip'): os.remove(g)
    names = [g for g, _ in mm]
    for r in b:
        kx = len(CBx[r['brand']]['people'])
        fl = [str(x) for x in r.get('flags', []) if not str(x).startswith('Contacts:')]
        imp = [x for x in fl if re.search(r'HOLD|resign|PENDING|ACQUIRED|ALREADY|1260H|Entity List|USER INSTRUCTION|Same house|Reputation|Capacity: (hard|firm)|HQ override|Existing F1|former F1|SPORTFIVE|sanction|COMPLIANCE|CHECK BEFORE|DUPLICATE|RENAMED|not formed|Identity', x, re.I)]
        key_flags = ' | '.join(dict.fromkeys([x[:170] for x in (fl[:1] + imp) if not x.startswith('Rebuilt')]))[:600]
        mmu = (f'Mail merge {names.index(GRP(r)) + 1} - {GRP(r)}' if kx and GRP(r) in names else '-')
        ws.append([f'{pre0} {i:02d}', folder, r.get(tabkey, ''), r['_user'], r.get('email_name') or r['brand'], status_word if kx else status_word + ' (no contacts found)', kx, mmu, '', key_flags])
    summ.append((f'{pre0} {i:02d}', folder, len(b), n, '; '.join(f'{k}. {g} ({c})' for k, (g, c) in enumerate(mm, 1)), ', '.join(dict.fromkeys(r.get(tabkey, '') for r in b))))
for i, b in enumerate(batches, 1): build(b, CB, i, root, 'P1', 'Template + contacts', '_tab')
yroot = f'{root}/Done yesterday (15 Nov) - {len(Y)} brands, copied as delivered'; os.makedirs(yroot)
for r in Y: r['_tab'] = 'Delivered 15 Nov'
for i, b in enumerate(ybatches, 1): build(b, YC, i, yroot, 'Y', 'Done yesterday (copied as delivered)', '_tab')
for r in declined:
    reason = re.sub(r'^DECLINED:\s*', '', str(r.get('skip') or next(x for x in r['flags'] if str(x).startswith('DECLINED'))))
    ws.append(['-', '-', r['_tab'], r['_user'], r['brand'], 'Not built: ' + reason[:300], 0, '-', '', ''])
wbm = openpyxl.load_workbook('priv1/in.xlsx', read_only=True)
for rr in list(wbm['Current F1 Partners'].iter_rows(values_only=True))[1:]:
    if rr and rr[0]: ws.append(['-', '-', str(rr[1] or ''), str(rr[0]), str(rr[0]), 'Not built: already in F1 through its owner (' + str(rr[2] or '') + ')', 0, '-', '', ''])
s2 = tr.create_sheet('Batches', 0); s2.append(['Batch', 'Folder', 'Brands', 'Contacts', 'Mail merges in this batch (Word template + merge list, contacts)', 'Sheet tabs covered', 'Sent? (tick)'])
for x in summ: s2.append(list(x) + [''])
s2.append([]); s2.append(['Total', '', sum(x[2] for x in summ), sum(x[3] for x in summ), '', f'{len(declined)} not built + 5 current F1 partners (see Tracker)'])
for wsx, widths in ((ws, [16, 30, 22, 34, 30, 36, 9, 30, 11, 110]), (s2, [16, 30, 8, 9, 70, 50, 11])):
    for c in wsx[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
    for j, wd in enumerate(widths): wsx.column_dimensions[openpyxl.utils.get_column_letter(j + 1)].width = wd
    wsx.freeze_panes = 'A2'
ws.auto_filter.ref = ws.dimensions
tr.save(f'{root}/00 Tracker - {TITLE}.xlsx')
zn = f'{TITLE.upper()} - Complete.zip'
if os.path.exists(zn): os.remove(zn)
with zipfile.ZipFile(zn, 'w', zipfile.ZIP_DEFLATED) as z:
    allf = sorted(os.path.join(dp, f) for dp, _, fs in os.walk('priv1/pkg') for f in fs)
    for p in allf: z.write(p, os.path.relpath(p, 'priv1/pkg'))
print('done', zn)
