# Audit step 3: categorise every master brand, write the updated master copy and the report.
# Usage: python3.13 -I audit_build.py <master.xlsx>   (reads audit_rows.json, audit_docmatch.json, audit_docs.json)
# Master copy is edited at XML level: only the fill of verified brand-name cells changes, plus one appended
# summary sheet. Every other zip entry is copied byte for byte.
import collections, json, os, re, sys, zipfile
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

OUT = os.path.dirname(os.path.abspath(__file__))
MASTER = sys.argv[1]
GREEN = 'FFB7E1A1'                        # distinct from the sheet's existing sage fills (D9EAD3, DCEBDC)
REVIEWED_MIN = 0.10                       # a tab counts as marked up when marks cover >= 10% of its brands
rows = json.load(open(f'{OUT}/audit_rows.json'))
dm = json.load(open(f'{OUT}/audit_docmatch.json'))
docs = json.load(open(f'{OUT}/audit_docs.json'))
TITLES = {'W01': 'Wave 1 Priority - Emails Ready.docx', 'W02': 'Wave 2 Priority - Emails Ready.docx',
          'W03': 'Wave 3 Up and Coming - Emails Ready.docx', 'W04': 'Wave 4 Sheet23 - Emails Ready.docx',
          'W05': 'Wave 5 Devtools - Emails Ready.docx', 'W06': 'Wave 6 Defense - Emails Ready.docx',
          'W07': 'Wave 7 Consumer Lifestyle - Emails Ready.docx', 'W08': 'Wave 8 Robotics - Emails Ready.docx',
          'W09': 'Wave 9 DC Power - Emails Ready.docx', 'W10': 'Wave 10 Photonics - Emails Ready.docx (+ identical copy "... Ready 2.docx")',
          'W11': 'Wave 11 Robotics AI - Emails Ready.docx', 'W12': 'Wave 12 Storage Hardware - Emails Ready.docx',
          'W13': 'Wave 13 Law Firms - Emails Ready.docx', 'W14': 'Wave 14 Energy - Emails Ready.docx',
          'W15': 'Wave 15 EDA - Emails Ready.docx', 'W16': 'Wave 16 OT Physical - Emails Ready.docx',
          'W17': 'Wave 17 Home Living - Emails Ready.docx', 'W18': 'Wave 18 Services - Emails Ready.docx',
          'W19': 'Wave 19 Tools Industrial Supply - Emails Ready.docx', 'W20': 'Wave 20 Telecom Space - Emails Ready.docx',
          'W21': 'Wave 21 Mobility - Emails Ready.docx', 'W22': 'Wave 22 GRC Risk - Emails Ready.docx',
          'W23': 'Wave 23 Machine Tool Supercomputing - Emails Ready.docx'}
TAB_DOC = {'Comp - Devtols & Integration': 'W05', 'Comp - Defense': 'W06', '145 - Consumer & Lifestyle': 'W07',
           'Comp - Automation': 'W08', 'Comp - DC Power & Cooling': 'W09', '139- Photonics & Optical': 'W10',
           '126- Robotics AI': 'W11', 'Comp - Storage Hardware': 'W12', '75-  Law Firms & Legal AI': 'W13',
           '200 - Energy & Industrial': 'W14', 'Comp - EDA': 'W15', '41 OT & Physical Security': 'W16',
           '61-  Home & Living': 'W17', 'Comp - Services': 'W18', 'Comp- Tools & Industrial Supply': 'W19',
           'Complete - Telecom & Space': 'W20', '66 - Mobility & Automotive': 'W21', '202 - GRC & Risk SW': 'W22',
           'Comp - Machine Tools': 'W23', 'Comp -Supercomputing': 'W23'}

# ---- categorise ----
tabs = list(dict.fromkeys(r['tab'] for r in rows))
marked_share = {t: sum(1 for r in rows if r['tab'] == t and r['mark']) / max(1, sum(1 for r in rows if r['tab'] == t)) for t in tabs}
for r in rows:
    m = r['mark'].strip().lower()
    if r['templ'] == 'verified':
        r['cat'] = 'Verified'
        r['note'] = 'Template exists although marked x' if m == 'x' else ''
    elif r['templ'] == 'uncertain':
        r['cat'], r['note'] = 'D', 'Possible template match, name not certain: ' + r['match']
    elif m == 'x':
        r['cat'], r['note'] = 'C', 'Marked x (your rule: x = no template wanted)'
    elif m == 'tbr':
        r['cat'], r['note'] = 'D', 'Marked TBR (meaning not defined on record)'
    elif m:
        r['cat'], r['note'] = 'D', f'Marked "{r["mark"]}" (meaning not defined on record)'
    elif marked_share[r['tab']] >= REVIEWED_MIN:
        r['cat'], r['note'] = 'A', 'Unmarked in a tab you marked up (opt-out rule: not excluded)'
    else:
        r['cat'], r['note'] = 'B', 'Unmarked in a tab with no or very few marks'
conflicts = [r for r in rows if r['cat'] == 'Verified' and r['note']]

# duplicates across tabs
from_norm = collections.defaultdict(list)
for r in rows:
    from_norm[re.sub(r'[^a-z0-9]', '', r['name'].lower())].append(r)
dups = {k: v for k, v in from_norm.items() if len({x['tab'] for x in v}) > 1}

# ---- summary table ----
summary = []
for t in tabs:
    tr = [r for r in rows if r['tab'] == t]
    c = collections.Counter(r['cat'] for r in tr)
    mk = collections.Counter(('x' if r['mark'].lower() == 'x' else 'TBR' if r['mark'].lower() == 'tbr' else 'other' if r['mark'] else 'blank') for r in tr)
    d = TAB_DOC.get(t)
    status = 'Missing (no document in shared folder)' if not d else ('Exists, complete' if c['Verified'] >= len(tr) - c['C'] else 'Exists, incomplete')
    summary.append({'tab': t, 'total': len(tr), 'verified': c['Verified'], 'unverified': len(tr) - c['Verified'],
                    'doc': TITLES[d] if d else '', 'status': status, 'A': c['A'], 'B': c['B'], 'C': c['C'], 'D': c['D'],
                    'x': mk['x'], 'TBR': mk['TBR'], 'other': mk['other'], 'blank': mk['blank'],
                    'marked_up': f'{marked_share[t]:.0%}'})

# ---- report workbook ----
rep = openpyxl.Workbook()
def sheet(title, header, data, widths):
    ws = rep.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
    for d in data:
        ws.append(d)
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    ws.freeze_panes = 'A2'
rep.remove(rep.active)
sheet('Category Summary', ['Spreadsheet tab', 'Total brands', 'Verified templates', 'Missing/unverified', 'Word document status',
                           'Word document', 'A requested-missing', 'B no indication', 'C not required (x)', 'D review',
                           'x marks', 'TBR marks', 'other marks', 'unmarked', 'share of tab marked'],
      [[s['tab'], s['total'], s['verified'], s['unverified'], s['status'], s['doc'], s['A'], s['B'], s['C'], s['D'],
        s['x'], s['TBR'], s['other'], s['blank'], s['marked_up']] for s in summary],
      [32, 10, 10, 12, 30, 48, 10, 10, 10, 9, 8, 8, 8, 9, 10])
key = lambda r: (tabs.index(r['tab']), r['row'])
cols = ['Spreadsheet tab', 'Row', 'Brand', 'Existing marking', 'Reason']
for cat, title in (('A', 'A Requested but missing'), ('B', 'B No indication'), ('C', 'C Not required (x)'), ('D', 'D Requires review')):
    sheet(title, cols, [[r['tab'], r['row'], r['name'], r['mark'], r['note']] for r in sorted(rows, key=key) if r['cat'] == cat],
          [32, 6, 40, 16, 80])
sheet('Verified templates', ['Spreadsheet tab', 'Row', 'Brand', 'Existing marking', 'Template found in (doc, email #, name)', 'Note'],
      [[r['tab'], r['row'], r['name'], r['mark'], r['match'], r['note']] for r in sorted(rows, key=key) if r['cat'] == 'Verified'],
      [32, 6, 40, 14, 70, 34])
nf = [x for x in dm if not x['verified_rows'] and not x['uncertain_rows']]
sheet('Docs brands not in master', ['Document', 'Email #', 'Brand (has a template)', 'Why'],
      [[TITLES[x['doc']], x['n'], x['brand'], 'Brand does not appear in any master tab'] for x in nf], [44, 8, 40, 40])
sheet('Duplicate brands', ['Brand', 'Tabs (row)', 'Template verified?'],
      [[v[0]['name'], '; '.join(f'{x["tab"]} ({x["row"]})' for x in v), 'yes' if any(x['cat'] == 'Verified' for x in v) else 'no']
       for v in dups.values()], [40, 90, 16])
rep.save(f'{OUT}/Missing Templates Report - Brand Outreach Audit.xlsx')

# ---- updated master copy (XML-level) ----
targets = collections.defaultdict(set)
for r in rows:
    if r['cat'] == 'Verified':
        col = openpyxl.utils.get_column_letter(r['col'])
        targets[r['tab']].add(f'{col}{r["row"]}')
zin = zipfile.ZipFile(MASTER)
files = {i.filename: zin.read(i.filename) for i in zin.infolist()}
wbx = files['xl/workbook.xml'].decode()
rels = files['xl/_rels/workbook.xml.rels'].decode()
rid_target = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship [^>]*?Id="([^"]+)"[^>]*?Target="([^"]+)"', rels)}
rid_target.update({m.group(2): m.group(1) for m in re.finditer(r'<Relationship [^>]*?Target="([^"]+)"[^>]*?Id="([^"]+)"', rels)})
sheet_file = {}
for m in re.finditer(r'<sheet [^>]*?name="([^"]+)"[^>]*?r:id="([^"]+)"', wbx):
    name = m.group(1).replace('&amp;', '&').replace('&apos;', "'").replace('&quot;', '"')
    tgt = rid_target[m.group(2)].lstrip('/')
    sheet_file[name] = tgt if tgt.startswith('xl/') else 'xl/' + tgt

styles = files['xl/styles.xml'].decode()
fills_m = re.search(r'<fills count="(\d+)"[^>]*>(.*?)</fills>', styles, re.S)
new_fill = int(fills_m.group(1))
styles = styles.replace(fills_m.group(0), fills_m.group(0).replace(f'count="{new_fill}"', f'count="{new_fill + 1}"', 1)
                        .replace('</fills>', f'<fill><patternFill patternType="solid"><fgColor rgb="{GREEN}"/><bgColor indexed="64"/></patternFill></fill></fills>'))
xfs_m = re.search(r'<cellXfs count="(\d+)"[^>]*>(.*?)</cellXfs>', styles, re.S)
xf_list = re.findall(r'<xf\b[^>]*?(?:/>|>.*?</xf>)', xfs_m.group(2), re.S)
clone, added = {}, []
def green_style(s):
    if s not in clone:
        xf = xf_list[s]
        xf = re.sub(r'fillId="\d+"', f'fillId="{new_fill}"', xf) if 'fillId=' in xf else xf.replace('<xf ', f'<xf fillId="{new_fill}" ', 1)
        xf = re.sub(r'applyFill="\d"', 'applyFill="1"', xf) if 'applyFill=' in xf else xf.replace('<xf ', '<xf applyFill="1" ', 1)
        clone[s] = len(xf_list) + len(added); added.append(xf)
    return clone[s]
painted = collections.Counter()
for tab, refs in targets.items():
    path = sheet_file[tab]
    xml = files[path].decode()
    def sub(m):
        attrs = m.group(1)
        ref = re.search(r'\br="([A-Z]+\d+)"', attrs).group(1)
        if ref not in refs:
            return m.group(0)
        s = re.search(r'\bs="(\d+)"', attrs)
        ns = green_style(int(s.group(1)) if s else 0)
        attrs = re.sub(r'\bs="\d+"', f's="{ns}"', attrs) if s else attrs + f' s="{ns}"'
        painted[tab] += 1
        return f'<c{attrs}{m.group(2)}'
    xml = re.sub(r'<c(\s[^>]*?)(/?>)', sub, xml)
    files[path] = xml.encode()
n_xf = int(xfs_m.group(1))
styles = styles.replace(xfs_m.group(0), xfs_m.group(0).replace(f'count="{n_xf}"', f'count="{n_xf + len(added)}"', 1)
                        .replace('</cellXfs>', ''.join(added) + '</cellXfs>'))
files['xl/styles.xml'] = styles.encode()

# summary sheet (inline strings, appended last so tab order and navigation stay unchanged)
def cell(ref, v, bold=False):
    if isinstance(v, (int, float)):
        return f'<c r="{ref}"><v>{v}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>'
lines = [['TEMPLATE AUDIT SUMMARY (25 Oct 2026)'],
         [f'Green brand cell (fill {GREEN[2:]}) = a dedicated outreach email for that brand was verified in the shared Word documents. Nothing else in this workbook was changed.'],
         ['Markings: x = no template wanted (your September rule). TBR, Later, CHECK and other marks are left as you wrote them and listed for review in the separate report.'],
         ['Note: some rows already carried a pale green or sage row colour from the original sheet; the audit green is brighter and applies to the brand cell only.'],
         [],
         ['Spreadsheet tab', 'Total brands', 'Verified templates', 'Missing/unverified', 'Word document status', 'Word document',
          'A requested-missing', 'B no indication', 'C not required (x)', 'D review']]
lines += [[s['tab'], s['total'], s['verified'], s['unverified'], s['status'], s['doc'], s['A'], s['B'], s['C'], s['D']] for s in summary]
tot = [sum(s[k] for s in summary) for k in ('total', 'verified', 'unverified', 'A', 'B', 'C', 'D')]
lines.append(['TOTAL', tot[0], tot[1], tot[2], '', '', tot[3], tot[4], tot[5], tot[6]])
rows_xml = ''.join('<row r="%d">%s</row>' % (i + 1, ''.join(cell(f'{chr(65 + j)}{i + 1}', v) for j, v in enumerate(l)))
                   for i, l in enumerate(lines))
sheet_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             '<cols><col min="1" max="1" width="34" customWidth="1"/><col min="2" max="4" width="12" customWidth="1"/>'
             '<col min="5" max="5" width="34" customWidth="1"/><col min="6" max="6" width="50" customWidth="1"/>'
             '<col min="7" max="10" width="12" customWidth="1"/></cols>'
             f'<sheetData>{rows_xml}</sheetData></worksheet>')
n = 1
while f'xl/worksheets/sheet{n}.xml' in files:
    n += 1
new_path = f'xl/worksheets/sheet{n}.xml'
files[new_path] = sheet_xml.encode()
rid = 'rIdAudit1'
files['xl/_rels/workbook.xml.rels'] = rels.replace('</Relationships>',
    f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
    f'Target="worksheets/sheet{n}.xml"/></Relationships>').encode()
max_id = max(int(x) for x in re.findall(r'<sheet [^>]*?sheetId="(\d+)"', wbx))
files['xl/workbook.xml'] = wbx.replace('</sheets>', f'<sheet name="Template Audit Summary" sheetId="{max_id + 1}" r:id="{rid}"/></sheets>').encode()
ct = files['[Content_Types].xml'].decode()
files['[Content_Types].xml'] = ct.replace('</Types>', f'<Override PartName="/{new_path}" '
    'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>').encode()
dst = f'{OUT}/Brand Outreach Template Audit — Updated.xlsx'
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
    for i in zin.infolist():
        zout.writestr(i, files[i.filename])
    zout.writestr(new_path, files[new_path])

json.dump({'summary': summary, 'painted': painted, 'conflicts': [[r['tab'], r['name']] for r in conflicts],
           'dups': len(dups), 'dups_verified': sum(1 for v in dups.values() if any(x['cat'] == 'Verified' for x in v))},
          open(f'{OUT}/audit_summary.json', 'w'), indent=0)
print('painted cells:', sum(painted.values()), '| verified rows:', sum(1 for r in rows if r['cat'] == 'Verified'))
print('categories:', dict(collections.Counter(r['cat'] for r in rows)), '| conflicts (x but templated):', len(conflicts))
print('duplicate brand names across tabs:', len(dups), '| of which templated:', sum(1 for v in dups.values() if any(x['cat'] == 'Verified' for x in v)))
print('lightly marked tabs (<10% marks) with some marks:', [t for t in tabs if 0 < marked_share[t] < REVIEWED_MIN])
