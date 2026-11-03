# Build <=50-contact batches for the 3 Nov upload sheet. Usage: python3 batch_build.py [--dry]
import json, glob, re, subprocess, sys, os, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
CAP = 50
items = json.load(open('up3nov/items.json'))
rows = []
for f in sorted(glob.glob('nb5_0[0-7]_rows.json')): rows += json.load(open(f))
reuse = json.load(open('nb5_08_rows.json'))
SUF = r'\b(inc|corp|corporation|ltd|limited|plc|llc|ag|sa|se|nv|co|company|group|holdings?|technologies|technology|the|labs?|ai)\b'
key = lambda s: re.sub(r'[^a-z0-9]', '', re.sub(SUF, '', (s or '').lower()))
bynew = {key(r['brand']): r for r in rows}
byuser = {r.get('user_name'): r for r in reuse}
C = json.load(open('nb5_contacts_existing.json'))
for f in sorted(glob.glob('en5_*_out.json')):
    for r in json.load(open(f))['rows']: C[r['brand']] = {'people': r['people'], 'note': r.get('note', '')}
order = []; missing = []
for it in items:
    r = byuser.get(it['clean']) if it['reuse'] else bynew.get(key(it['clean']))
    if r is None: missing.append(it['clean']); continue
    r = dict(r); r['_sheet'] = it['sheet']; r['_user'] = it['clean']; r['_rank'] = it['rank']; r['_tier'] = it['tier']
    order.append(r)
if missing: print('MISSING ROWS', missing)
declined = [r for r in order if r.get('skip') or any(str(x).startswith('DECLINED') for x in r.get('flags', []))]
live = [r for r in order if r not in declined]
for r in live:
    r['flags'] = [x for x in r.get('flags', []) if not str(x).startswith('Contacts:')]
    if not C.get(r['brand'], {}).get('people'): r['flags'].append('Contacts: none found in Apollo.')
batches = []; cur = []; n = 0; sheet = None
for r in live:
    k = len(C.get(r['brand'], {}).get('people', []))
    if cur and (n + k > CAP or r['_sheet'] != sheet):
        batches.append(cur); cur = []; n = 0
    cur.append(r); n += k; sheet = r['_sheet']
if cur: batches.append(cur)
print('brands', len(order), 'live', len(live), 'declined', len(declined), 'batches', len(batches))
for i, b in enumerate(batches, 1):
    print(f"  batch {i:02d} {b[0]['_sheet']:13} brands {len(b):2d} contacts {sum(len(C.get(r['brand'],{}).get('people',[])) for r in b)}")
if '--dry' in sys.argv: sys.exit()
os.makedirs('up3nov/out', exist_ok=True); json.dump(C, open('up3nov/_c.json', 'w'))
idx = openpyxl.Workbook(); ws = idx.active; ws.title = 'Index'
ws.append(['Batch', 'Sheet', 'Rank', 'Tier', 'Brand (your sheet)', 'Email name', 'Template', 'Contacts', 'Key flag'])
for i, b in enumerate(batches, 1):
    label = f"Upload 3 Nov - Batch {i:02d}"
    json.dump(b, open(f'up3nov/b{i:02d}_rows.json', 'w'), indent=1)
    json.dump({'rows': [{'brand': r['brand'], 'people': C.get(r['brand'], {}).get('people', [])} for r in b]}, open(f'up3nov/b{i:02d}_contacts.json', 'w'), indent=1)
    out = subprocess.run(['python3.13', '-I', 'v7_assemble.py', label, f'up3nov/b{i:02d}_rows.json', f'up3nov/b{i:02d}_contacts.json'], capture_output=True, text=True)
    if 'DONE' not in out.stdout: print('ASSEMBLE FAIL', i, out.stdout[-400:], out.stderr[-400:])
    names = f'up3nov/b{i:02d}_names.txt'; open(names, 'w').write('\n'.join(r['brand'] for r in b))
    subprocess.run(['python3.13', '-I', 'contacts_sheet.py', names, f'up3nov/b{i:02d}_rows.json', 'up3nov/_c.json', f'{label} - Contacts.xlsx'], capture_output=True)
    z = f"{label.upper()} - Complete.zip"
    subprocess.run(['zip', '-q', '-j', z, f'{label} - Contacts.xlsx'])
    for r in b:
        reused = next((re.sub(r'^Reused: template first built in the (.+?) pack.*', r'reused (\1)', str(x)) for x in r['flags'] if str(x).startswith('Reused:')), 'built today')
        key_flag = next((str(x)[:140] for x in r['flags'] if re.match(r'(ACQUIRED|PENDING|ALREADY|RENAMED|Capacity: (hard|firm)|Reputation|Same house|State)', str(x), re.I)), '')
        ws.append([i, r['_sheet'], r['_rank'], r['_tier'], r['_user'], r.get('email_name') or r['brand'], reused, len(C.get(r['brand'], {}).get('people', [])), key_flag])
for r in declined:
    ws.append(['Declined', r['_sheet'], r['_rank'], r['_tier'], r['_user'], r['brand'], re.sub(r'^DECLINED:\s*', '', str(r.get('skip') or next(x for x in r['flags'] if str(x).startswith('DECLINED'))))[:200], 0, ''])
for k, wd in enumerate([8, 13, 7, 8, 32, 30, 34, 9, 90]): ws.column_dimensions[openpyxl.utils.get_column_letter(k + 1)].width = wd
for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions
idx.save('Upload 3 Nov - Batch Index (no contacts).xlsx')
print('done')
