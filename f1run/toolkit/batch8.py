# Build <=50-contact batches for TEMPLATES.xlsx Round 2 and Round 3. Usage: python3.13 -I batch8.py [--dry]
import json, glob, re, subprocess, sys, os, openpyxl
from openpyxl.styles import Font, PatternFill
CAP = 50
items = json.load(open('up5nov_r23/items.json'))
rank = {}
for it in items:
    rank[it['sheet']] = rank.get(it['sheet'], 0) + 1; it['rank'] = rank[it['sheet']]
SUF = r'\b(inc|corp|corporation|ltd|limited|plc|llc|ag|sa|se|nv|co|company|group|holdings?|the|spa|s\.p\.a\.)\b'
key = lambda s: re.sub(r'[^a-z0-9]', '', re.sub(SUF, '', (s or '').lower()))
new = []
for f in sorted(glob.glob('nb8_0[0-3]_rows.json')): new += json.load(open(f))
inp = {}
for f in sorted(glob.glob('nb8_0[0-3].json')):
    for x in json.load(open(f)): inp[key(x['brand'])] = x['brand']
bynew = {}
for r in new:
    u = r.get('user_name') or inp.get(key(r['brand'])) or r['brand']
    bynew[key(u)] = r; bynew.setdefault(key(r['brand']), r)
byuser = {r['user_name']: r for r in json.load(open('nb8_04_rows.json'))}
# contacts: saved earlier (keyed by sheet name) plus this job's enrichment (keyed by input brand = sheet name)
ex = json.load(open('up5nov_r23/existing_raw.json'))
C = {}
for u, v in ex.items(): C[u] = {'people': list(v['people']), 'note': f"Saved contacts from an earlier Apollo run ({v['file']})."}
for f in sorted(glob.glob('en8_*_out.json')):
    for r in json.load(open(f))['rows']:
        c = C.setdefault(r['brand'], {'people': [], 'note': ''})
        have = {p['email'].lower() for p in c['people']}
        c['people'] += [p for p in r['people'] if p['email'].lower() not in have]
        if r.get('note'): c['note'] = (c['note'] + ' ' + r['note']).strip()
for u in C: C[u]['people'] = C[u]['people'][:4]
order = []; missing = []; seen = {}
for it in items:
    u = it['name']
    if u in seen:  # same brand listed on both sheets: one template, listed once
        seen[u]['_also'] = f"{it['sheet']} #{it['rank']}"; continue
    r = byuser.get(u) or bynew.get(key(u))
    if r is None: missing.append(u); continue
    r = dict(r); r['_sheet'] = it['sheet']; r['_user'] = u; r['_rank'] = it['rank']; r['_tier'] = it.get('prio') or it.get('cat') or ''
    r['_ckey'] = u; seen[u] = r; order.append(r)
if missing: print('MISSING ROWS', missing)
CB = {r['brand']: C.get(r['_ckey'], {'people': [], 'note': ''}) for r in order}
declined = [r for r in order if r.get('skip') or any(str(x).startswith('DECLINED') for x in r.get('flags', []))]
live = [r for r in order if r not in declined]
for r in live:
    r['flags'] = [x for x in r.get('flags', []) if not str(x).startswith('Contacts:')]
    if r.get('_also'): r['flags'].append(f"Also listed on your sheet at {r['_also']}: one template covers both.")
    if not CB[r['brand']]['people']: r['flags'].append('Contacts: none found in Apollo.')
import math
def pack(rows, limit):
    out = []; cur = []; n = 0
    for r in rows:
        k = len(CB[r['brand']]['people'])
        if cur and n + k > limit: out.append(cur); cur = []; n = 0
        cur.append(r); n += k
    if cur: out.append(cur)
    return out
batches = []
for sh in dict.fromkeys(r['_sheet'] for r in live):
    rows = [r for r in live if r['_sheet'] == sh]
    tot = sum(len(CB[r['brand']]['people']) for r in rows); nb = max(1, math.ceil(tot / CAP))
    best = pack(rows, CAP)
    for lim in range(math.ceil(tot / nb), CAP + 1):  # smallest even limit that still needs only nb batches
        p = pack(rows, lim)
        if len(p) <= nb: best = p; break
    batches += best
print('brands', len(order), 'live', len(live), 'declined', len(declined), 'batches', len(batches), 'contacts', sum(len(v['people']) for v in CB.values()))
for i, b in enumerate(batches, 1):
    print(f"  batch {i:02d} {b[0]['_sheet']:8} brands {len(b):2d} contacts {sum(len(CB[r['brand']]['people']) for r in b)}")
if declined: print('  declined:', [r['_user'] for r in declined])
if '--dry' in sys.argv: sys.exit()
os.makedirs('up5nov_r23/out', exist_ok=True); json.dump(CB, open('up5nov_r23/_c.json', 'w'))
idx = openpyxl.Workbook(); ws = idx.active; ws.title = 'Index'
ws.append(['Batch', 'Sheet', 'Rank', 'Priority / category', 'Brand (your sheet)', 'Email name', 'Template', 'Contacts', 'Key flag'])
for i, b in enumerate(batches, 1):
    label = f"{b[0]['_sheet']} - Batch {i:02d}"
    json.dump(b, open(f'up5nov_r23/b{i:02d}_rows.json', 'w'), indent=1)
    json.dump({'rows': [{'brand': r['brand'], 'people': CB[r['brand']]['people']} for r in b]}, open(f'up5nov_r23/b{i:02d}_contacts.json', 'w'), indent=1)
    out = subprocess.run(['python3.13', '-I', 'v7_assemble.py', label, f'up5nov_r23/b{i:02d}_rows.json', f'up5nov_r23/b{i:02d}_contacts.json'], capture_output=True, text=True)
    if 'DONE' not in out.stdout: print('ASSEMBLE FAIL', i, out.stdout[-400:], out.stderr[-400:])
    names = f'up5nov_r23/b{i:02d}_names.txt'; open(names, 'w').write('\n'.join(r['brand'] for r in b))
    subprocess.run(['python3.13', '-I', 'contacts_sheet.py', names, f'up5nov_r23/b{i:02d}_rows.json', 'up5nov_r23/_c.json', f'{label} - Contacts.xlsx'], capture_output=True)
    z = f"{label.upper()} - Complete.zip"
    subprocess.run(['zip', '-q', '-j', z, f'{label} - Contacts.xlsx'])
    for r in b:
        reused = next((re.sub(r'^Reused: template first built in the (.+?) pack.*', r'reused (\1)', str(x)) for x in r['flags'] if str(x).startswith('Reused:')), 'built today')
        key_flag = next((str(x)[:140] for x in r['flags'] if re.match(r'(ACQUIRED|PENDING|ALREADY|RENAMED|Capacity: (hard|firm)|Reputation|Same house|State|HQ override|Defen[cs]e)', str(x), re.I)), '')
        ws.append([i, r['_sheet'], r['_rank'], r['_tier'], r['_user'] + (f" (also {r['_also']})" if r.get('_also') else ''), r.get('email_name') or r['brand'], reused, len(CB[r['brand']]['people']), key_flag])
for r in declined:
    ws.append(['Declined', r['_sheet'], r['_rank'], r['_tier'], r['_user'], r['brand'], re.sub(r'^DECLINED:\s*', '', str(r.get('skip') or next(x for x in r['flags'] if str(x).startswith('DECLINED'))))[:200], 0, ''])
for k, wd in enumerate([8, 9, 6, 22, 32, 30, 34, 9, 90]): ws.column_dimensions[openpyxl.utils.get_column_letter(k + 1)].width = wd
for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions
idx.save('Rounds 2-3 - Batch Index (no contacts).xlsx')
print('done')
