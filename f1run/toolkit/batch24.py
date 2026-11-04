# Batch 24: gap fills for the 3 Nov upload sheet. Run: python3.13 -I batch24.py
import json, glob, re, copy, subprocess
rows_by = {}
for f in sorted(glob.glob('up3nov/b[0-9][0-9]_rows.json')):
    n = int(re.search(r'b(\d+)_', f).group(1))
    for r in json.load(open(f)): rows_by[r['brand']] = (n, r)
user_of = {r['brand']: r['_user'] for _, r in rows_by.values()}
E = json.load(open('en6_out.json'))
P = json.load(open('pub_inboxes.json'))
out_rows, C, notes = [], {}, {}
# 1) new templates
getty = copy.deepcopy([x for x in json.load(open('nb3_02_rows.json')) if x['brand'] == 'Getty Images'][0])
getty['flags'] = ['HOLD: Getty Images has been in a prepackaged Chapter 11 since 21 Oct 2026 (the brief normally declines Chapter 11 cases). Built at your request; send only after it emerges, expected by end 2026. It is already Formula 1\'s Official Photographic Agency at series level, so a team deal must not clash with F1\'s rights.'] + [f for f in getty['flags'] if not str(f).startswith('Contacts:')]
getty['_user'] = 'Getty Images'
new = json.load(open('nb6_00_rows.json'))
for r in new:
    r['_user'] = {'SoundHound AI': 'LivePerson (now SoundHound AI)', 'LevelBlue': 'Cybereason (now LevelBlue)'}[r['brand']]
    r['flags'] = [('Replacement: ' + ('LivePerson was acquired by SoundHound AI (closed 4 Sep 2026); this template pitches SoundHound AI.' if r['brand'] == 'SoundHound AI' else 'Cybereason was acquired by LevelBlue; this template pitches LevelBlue.'))] + r.get('flags', [])
for r in [getty] + new:
    out_rows.append(r)
    e = next((x for x in E['rows'] if x['brand'] == r['brand']), {'people': [], 'note': ''})
    C[r['brand']] = {'people': e['people'], 'note': 'New template in this batch.' + (' ' + e.get('note', '') if e.get('note') else '')}
# 2) Apollo top-ups and public inboxes for brands whose template is in an earlier batch
add = {}
for x in E['rows']:
    if x['brand'] in rows_by: add.setdefault(x['brand'], []).extend(x['people'])
for x in P['rows']:
    b = x['brand']
    if b not in rows_by: print('NO ROW FOR', b); continue
    for c in x['contacts']:
        if c.get('email'):
            add.setdefault(b, []).append({'name': 'Team', 'title': c['label'] + ' (public inbox on company site)', 'email': c['email'], 'role': 'field_marketing', 'linkedin': '', 'location': c.get('source', '')})
        elif c.get('form_url'):
            notes.setdefault(b, []).append(f"{c['label']}: {c['form_url']}")
for b, ppl in add.items():
    n, r = rows_by[b]
    r = copy.deepcopy(r)
    r['flags'] = [f'Additional contacts only: the template for this brand is in Batch {n:02d}. Send these contacts the same email.'] + [f for f in r.get('flags', []) if not str(f).startswith('Contacts:')]
    out_rows.append(r)
    note = f'Template in Batch {n:02d}. Added here: ' + ', '.join(sorted({('public inbox' if p['name'] == 'Team' else 'Apollo contact') for p in ppl}))
    if notes.get(b): note += '. Web forms: ' + '; '.join(notes[b])
    C[b] = {'people': ppl, 'note': note}
for b, ns in notes.items():
    if b not in add and b in rows_by:
        n, r = rows_by[b]; r = copy.deepcopy(r); out_rows.append(r)
        C[b] = {'people': [], 'note': f'Template in Batch {n:02d}. No email published; contact routes: ' + '; '.join(ns)}
tot = sum(len(v['people']) for v in C.values())
print('brands', len(out_rows), 'contacts', tot)
assert tot <= 50, tot
label = 'Upload 3 Nov - Batch 24'
json.dump(out_rows, open('up3nov/b24_rows.json', 'w'), indent=1)
json.dump({'rows': [{'brand': r['brand'], 'people': C[r['brand']]['people']} for r in out_rows]}, open('up3nov/b24_contacts.json', 'w'), indent=1)
json.dump(C, open('up3nov/b24_c.json', 'w'), indent=1)
o = subprocess.run(['python3.13', '-I', 'v7_assemble.py', label, 'up3nov/b24_rows.json', 'up3nov/b24_contacts.json'], capture_output=True, text=True); print(o.stdout[-200:], o.stderr[-300:])
open('up3nov/b24_names.txt', 'w').write('\n'.join(r['brand'] for r in out_rows))
subprocess.run(['python3.13', '-I', 'contacts_sheet.py', 'up3nov/b24_names.txt', 'up3nov/b24_rows.json', 'up3nov/b24_c.json', f'{label} - Contacts.xlsx'])
subprocess.run(['zip', '-q', '-j', f'{label.upper()} - Complete.zip', f'{label} - Contacts.xlsx'])
# index update
import openpyxl
wb = openpyxl.load_workbook('Upload 3 Nov - Batch Index (no contacts).xlsx'); ws = wb.active
for row in ws.iter_rows(min_row=2):
    b = row[5].value
    if row[0].value == 'Declined' and row[4].value in ('Getty Images', 'LivePerson', 'Cybereason'):
        row[0].value = 24; nb = {'Getty Images': 'Getty Images', 'LivePerson': 'SoundHound AI', 'Cybereason': 'LevelBlue'}[row[4].value]
        row[5].value = nb; row[6].value = 'built 4 Nov (HOLD until Chapter 11 exit)' if nb == 'Getty Images' else f'built 4 Nov for new owner {nb}'; row[7].value = len(C[nb]['people'])
    for b2, v in C.items():
        if row[5].value == b2 and row[0].value not in (24, 'Declined') and v['people']:
            row[7].value = (row[7].value or 0) + len(v['people']); row[8].value = ((row[8].value or '') + f' | +{len(v["people"])} contacts in Batch 24').strip(' |')
        elif row[5].value == b2 and row[0].value not in (24, 'Declined') and not v['people']:
            row[8].value = ((row[8].value or '') + ' | contact routes (forms) in Batch 24').strip(' |')
wb.save('Upload 3 Nov - Batch Index (no contacts).xlsx')
print('ok')
