# One-brand pack in the v9 template. Usage: python3.13 -I single_brand.py <rows.json> <contacts.json> "<Brand label>" [workdir]
# contacts.json = {"rows":[{"brand":..., "people":[{name,title,email},...]}]}
import json, sys, os, glob, re, shutil, subprocess, zipfile, openpyxl
rowsf, contf, label = sys.argv[1], sys.argv[2], sys.argv[3]; wd = sys.argv[4] if len(sys.argv) > 4 else 'single'
rows = json.load(open(rowsf)); cont = json.load(open(contf))
GRP = lambda r: ('B2C' if (r.get('variant') or 'B2B').upper().startswith('B2C') else 'B2B') + ('' if r.get('market_reference') else ' no reference')
CB = {r['brand']: {'people': r['people'][:5], 'note': ''} for r in cont['rows']}
for r in rows:
    r['_tab'] = r.get('_tab', ''); r['_user'] = r.get('user_name') or r['brand']
    why = (r.get('priority') or {}).get('reason', '')
    r['flags'] = [x for x in r.get('flags', []) if not str(x).startswith(('Contacts:', 'PRIORITY #'))]
    if why: r['flags'].insert(0, f"PRIORITY score {(r.get('priority') or {}).get('score')}: {why}")
os.makedirs(wd, exist_ok=True); title = f'{label.upper()} - Email and Contacts'
root = f'{wd}/pkg/{title}'; shutil.rmtree(f'{wd}/pkg', ignore_errors=True); os.makedirs(root)
json.dump(rows, open(f'{wd}/rows.json', 'w'), indent=1); json.dump({'rows': [{'brand': r['brand'], 'people': CB[r['brand']]['people']} for r in rows]}, open(f'{wd}/contacts.json', 'w'), indent=1)
json.dump(CB, open(f'{wd}/_c.json', 'w')); os.environ['V7_KEEP_ORDER'] = '1'; tag = 'SB - ' + label
out = subprocess.run(['python3.13', '-I', 'v9_assemble.py', tag, f'{wd}/rows.json', f'{wd}/contacts.json'], capture_output=True, text=True, env=os.environ)
if 'DONE' not in out.stdout: print('ASSEMBLE FAIL', out.stdout[-400:], out.stderr[-400:]); sys.exit(1)
open(f'{wd}/names.txt', 'w').write('\n'.join(r['brand'] for r in rows))
subprocess.run(['python3.13', '-I', 'contacts_sheet.py', f'{wd}/names.txt', f'{wd}/rows.json', f'{wd}/_c.json', f'{tag} - Contacts.xlsx'], capture_output=True)
shutil.move(f'{tag} - Emails Ready.docx', f'{root}/{label} - Email.docx'); shutil.move(f'{tag} - Contacts.xlsx', f'{root}/{label} - Contacts.xlsx')
ORDER = ['B2B', 'B2B no reference', 'B2C', 'B2C no reference']
lists = sorted(glob.glob(f'{tag} - Merge List - *.xlsx'), key=lambda g: ORDER.index(g.split(' - Merge List - ')[1][:-5]))
for kk, g in enumerate(lists, 1):
    grp = g.split(' - Merge List - ')[1][:-5]; cnt = openpyxl.load_workbook(g).active.max_row - 1
    pre = f'{label} - Mail merge - {grp}' if len(lists) == 1 else f'{label} - Mail merge {kk} of {len(lists)} - {grp}'
    shutil.move(g, f'{root}/{pre} - Merge list ({cnt} contacts).xlsx'); shutil.copy(f'F1 Merge Master v9 - {grp}.docx', f'{root}/{pre} - Word template.docx')
    shutil.copy(f'Follow-up v9 - {grp} - Word template.docx', f'{root}/{label} - Follow-up (4 working days later, same subject) - {grp} - Word template.docx')
for g in glob.glob(f'{tag} - Flagged Brands.xlsx') + glob.glob(f'{tag.upper()} - Complete.zip'): os.remove(g)
zn = f'{title}.zip'
if os.path.exists(zn): os.remove(zn)
with zipfile.ZipFile(zn, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(os.path.join(dp, f) for dp, _, fs in os.walk(f'{wd}/pkg') for f in fs): z.write(p, os.path.relpath(p, f'{wd}/pkg'))
print('done', zn, [os.path.basename(p) for p in sorted(glob.glob(root + '/*'))])
