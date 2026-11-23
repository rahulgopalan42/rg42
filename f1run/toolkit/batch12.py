# New Brands 23 Nov (30 names, v9 template: Arial 12, new opener/hook, up to 5 contacts): brands ranked by F1 priority, packed IN ORDER into <=40-contact batches
# (Batch 01 = the highest-priority brands), one organized zip. Usage: python3.13 -I batch11.py [--dry]
import json, glob, re, subprocess, sys, os, shutil, zipfile, openpyxl
from openpyxl.styles import Font, PatternFill
CAP = 40; TITLE = 'New Brands 23 Nov (priority order)'
items = json.load(open('nb12/items.json'))
DEC = json.load(open('nb12/decisions.json')) if os.path.exists('nb12/decisions.json') else {'decline': {}, 'email_name': {}, 'priority_adj': {}}
rows = []
for f in sorted(glob.glob('nb12_[0-9][0-9]_rows.json')): rows += json.load(open(f))
key = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
byuser = {}; bykey = {}
for r in rows:
    if r.get('user_name'): byuser[r['user_name'].strip()] = r
    bykey.setdefault(key(r['brand']), r)
cs = {r['user_name']: r for r in json.load(open('nb12/cs12_all.json'))}
bad = {}
for f in glob.glob('nb12/cs12_[0-9][0-9]_out.json'):
    for r in json.load(open(f))['rows']: bad[r['user_name']] = {e.lower() for e in (r.get('keep_bad') or [])}
DROP = {}
for f in ('pubw1/drop_contacts.json', 'priv1/drop_contacts.json', 'nb12/drop_contacts.json'):
    if os.path.exists(f): DROP.update(json.load(open(f)))
C = {}
for u, r in cs.items():
    kp = [dict(name=p['name'], title=p['title'], email=p['email']) for p in r['keep'] if p['email'].lower() not in bad.get(u, set())]
    C[u] = {'people': kp, 'note': 'Saved contacts from earlier Apollo runs.' if kp else ''}
for f in sorted(glob.glob('nb12/en12_*_out.json')):
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
    return out[:5]
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
# ---- priority ranking ----
HOLD = re.compile(r'^(HARD HOLD|HOLD|ON HOLD|COMPLIANCE|CHECK BEFORE|ALREADY)', re.I)
def rank_key(r):
    p = r.get('priority') or {}; sc = float(p.get('score') or 0) + float(DEC.get('priority_adj', {}).get(r['_user'], 0))
    fl = [str(x) for x in r.get('flags', [])]
    cap = next((x for x in fl if x.startswith('Capacity:')), '')
    if re.search(r'hard caution', cap, re.I): sc -= 20
    elif re.search(r'firm caution', cap, re.I): sc -= 8
    tier = 2 if any(HOLD.match(x) for x in fl) else 0
    if not CB[r['brand']]['people']: tier = 3          # no contact: template only, at the very end
    r['_score'] = round(sc, 1); r['_tier'] = tier
    return (tier, -sc, r['_user'].lower())
live.sort(key=rank_key)
for n, r in enumerate(live, 1):
    r['_rank'] = n
    r['flags'] = [x for x in r.get('flags', []) if not str(x).startswith('Contacts:') and not str(x).startswith('PRIORITY #')]
    why = (r.get('priority') or {}).get('reason', '')
    tierword = {0: '', 2: ' (held back: hold or check flag)', 3: ' (no contact found)'}[r['_tier']]
    r['flags'].insert(0, f"PRIORITY #{n} of {len(live)}, score {r['_score']}{tierword}: {why}")
    if not CB[r['brand']]['people']: r['flags'].append('Contacts: none found in Apollo.')
def pack(rs, CBx, lim):           # strict order: never move a lower-ranked brand ahead
    out = []; cur = []; n = 0
    for r in rs:
        kx = len(CBx[r['brand']]['people'])
        if cur and n + kx > lim: out.append(cur); cur = []; n = 0
        cur.append(r); n += kx
    if cur: out.append(cur)
    return out
batches = pack(live, CB, CAP)
print('brands', len(order), 'live', len(live), 'declined', len(declined), 'contacts', sum(len(CB[r['brand']]['people']) for r in live), 'batches', len(batches))
for i, b in enumerate(batches, 1): print(f"  batch {i:02d} ranks {b[0]['_rank']}-{b[-1]['_rank']} brands {len(b):2d} contacts {sum(len(CB[r['brand']]['people']) for r in b):2d} top: {', '.join(r['_user'] for r in b[:4])}")
if '--dry' in sys.argv: sys.exit()
os.environ['V7_KEEP_ORDER'] = '1'
root = 'nb12/pkg/' + TITLE; shutil.rmtree('nb12/pkg', ignore_errors=True); os.makedirs(root)
tr = openpyxl.Workbook(); ws = tr.active; ws.title = 'Priority order'
ws.append(['Priority', 'Batch', 'Folder', 'Sheet tab', 'Brand (your sheet)', 'Email name', 'Priority score', 'Why this rank', 'Status', 'Contacts', 'Mail merge to use', 'Sent? (tick)', 'Key flags'])
summ = []
ORDER = ['B2B', 'B2B no reference', 'B2C', 'B2C no reference']
GRP = lambda r: ('B2C' if (r.get('variant') or 'B2B').upper().startswith('B2C') else 'B2B') + ('' if r.get('market_reference') else ' no reference')
for i, b in enumerate(batches, 1):
    n = sum(len(CB[r['brand']]['people']) for r in b); tag = 'NP'
    label = f'{tag} - Batch {i:02d}'; folder = f'Batch {i:02d} - priority {b[0]["_rank"]} to {b[-1]["_rank"]} ({n} contacts)'
    d = f'{root}/{folder}'; os.makedirs(d)
    json.dump(b, open(f'nb12/{tag}{i:02d}_rows.json', 'w'), indent=1)
    json.dump({'rows': [{'brand': r['brand'], 'people': CB[r['brand']]['people']} for r in b]}, open(f'nb12/{tag}{i:02d}_contacts.json', 'w'), indent=1)
    json.dump(CB, open('nb12/_c.json', 'w'))
    out = subprocess.run(['python3.13', '-I', 'v9_assemble.py', label, f'nb12/{tag}{i:02d}_rows.json', f'nb12/{tag}{i:02d}_contacts.json'], capture_output=True, text=True, env=os.environ)
    if 'DONE' not in out.stdout: print('ASSEMBLE FAIL', i, out.stdout[-300:], out.stderr[-300:])
    open(f'nb12/{tag}{i:02d}_names.txt', 'w').write('\n'.join(r['brand'] for r in b))
    subprocess.run(['python3.13', '-I', 'contacts_sheet.py', f'nb12/{tag}{i:02d}_names.txt', f'nb12/{tag}{i:02d}_rows.json', 'nb12/_c.json', f'{label} - Contacts.xlsx'], capture_output=True)
    shutil.move(f'{label} - Emails Ready.docx', f'{d}/Batch {i:02d} - Emails.docx')
    shutil.move(f'{label} - Contacts.xlsx', f'{d}/Batch {i:02d} - Contacts.xlsx')
    lists = sorted(glob.glob(f'{label} - Merge List - *.xlsx'), key=lambda g: ORDER.index(g.split(' - Merge List - ')[1][:-5]))
    mm = []
    for kk, g in enumerate(lists, 1):
        grp = g.split(' - Merge List - ')[1][:-5]; cnt = openpyxl.load_workbook(g).active.max_row - 1
        pre = f'Batch {i:02d} - Mail merge {kk} of {len(lists)} - {grp}'
        shutil.move(g, f'{d}/{pre} - Merge list ({cnt} contacts).xlsx')
        shutil.copy(f'F1 Merge Master v9 - {grp}.docx', f'{d}/{pre} - Word template.docx')
        mm.append((grp, cnt))
    for g in glob.glob(f'{label} - Flagged Brands.xlsx') + glob.glob(f'{label.upper()} - Complete.zip'): os.remove(g)
    names = [g for g, _ in mm]
    for r in b:
        kx = len(CB[r['brand']]['people'])
        fl = [str(x) for x in r.get('flags', []) if not str(x).startswith(('Contacts:', 'PRIORITY #', 'Rebuilt'))]
        imp = [x for x in fl if re.search(r'HOLD|resign|PENDING|ACQUIRED|ALREADY|1260H|Entity List|USER INSTRUCTION|Same house|Reputation|Capacity: (hard|firm)|HQ override|Existing F1|former F1|SPORTFIVE|sanction|COMPLIANCE|CHECK BEFORE|DUPLICATE|RENAMED|not formed|Identity', x, re.I)]
        key_flags = ' | '.join(dict.fromkeys([x[:170] for x in (fl[:1] + imp)]))[:600]
        mmu = (f'Mail merge {names.index(GRP(r)) + 1} - {GRP(r)}' if kx and GRP(r) in names else '-')
        ws.append([r['_rank'], f'Batch {i:02d}', folder, r['_tab'], r['_user'], r.get('email_name') or r['brand'], r['_score'], (r.get('priority') or {}).get('reason', ''),
                   'Template + contacts' if kx else 'Template only (no contacts found)', kx, mmu, '', key_flags])
    summ.append((f'Batch {i:02d}', folder, f"{b[0]['_rank']}-{b[-1]['_rank']}", len(b), n, '; '.join(f'{k}. {g} ({c})' for k, (g, c) in enumerate(mm, 1)), ', '.join(r['_user'] for r in b[:6]) + (' ...' if len(b) > 6 else '')))
for r in declined:
    reason = re.sub(r'^DECLINED:\s*', '', str(r.get('skip') or next(x for x in r['flags'] if str(x).startswith('DECLINED'))))
    ws.append(['-', '-', '-', r['_tab'], r['_user'], r['brand'], '', '', 'Not built: ' + reason[:300], 0, '-', '', ''])
s2 = tr.create_sheet('Batches', 0); s2.append(['Batch', 'Folder', 'Priority ranks', 'Brands', 'Contacts', 'Mail merges in this batch (Word template + merge list, contacts)', 'Top brands in this batch', 'Sent? (tick)'])
for x in summ: s2.append(list(x) + [''])
s2.append([]); s2.append(['Total', '', '', sum(x[3] for x in summ), sum(x[4] for x in summ), '', f'{len(declined)} not built (see Priority order tab)'])
s3 = tr.create_sheet('How ranked', 2)
for line in ['Brands are ranked by an F1 priority score out of 100, from today\'s research on each brand:',
             'Spending power (up to 35): revenue, valuation, recent funding, profits.',
             'Global reach (up to 20): how well known the brand is across F1 markets.',
             'F1 fit (up to 30): how much F1 does for what they sell, buyers or fans already in F1, a competitor already on the grid, open categories.',
             'Buying signals (up to 15): a raise in the last 12 months, IPO preparation, new regions, a marketing push, existing sports deals.',
             'Adjustments: capacity "firm caution" minus 8, "hard caution" minus 20.',
             'Held back to the end: brands with a HOLD, COMPLIANCE, CHECK BEFORE SENDING or ALREADY ON THE GRID flag, then brands with no contact found (template only).',
             'Batches are filled strictly in rank order up to 40 contacts, so Batch 01 holds the highest-priority brands.']:
    s3.append([line])
s3.column_dimensions['A'].width = 140
for wsx, widths in ((ws, [9, 10, 34, 22, 30, 26, 9, 70, 30, 9, 26, 11, 100]), (s2, [10, 40, 12, 8, 9, 60, 70, 11])):
    for c in wsx[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
    for j, wd in enumerate(widths): wsx.column_dimensions[openpyxl.utils.get_column_letter(j + 1)].width = wd
    wsx.freeze_panes = 'A2'
ws.auto_filter.ref = ws.dimensions
tr.save(f'{root}/00 Tracker - {TITLE}.xlsx')
fud = f'{root}/Follow-up templates (send 4 working days later, same subject)'; os.makedirs(fud)
for g in ORDER:
    if os.path.exists(f'Follow-up v9 - {g} - Word template.docx'): shutil.copy(f'Follow-up v9 - {g} - Word template.docx', f'{fud}/Follow-up - {g} - Word template.docx')
zn = 'NEW BRANDS 23 NOV - Complete.zip'
if os.path.exists(zn): os.remove(zn)
with zipfile.ZipFile(zn, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(os.path.join(dp, f) for dp, _, fs in os.walk('nb12/pkg') for f in fs): z.write(p, os.path.relpath(p, 'nb12/pkg'))
print('done', zn)
