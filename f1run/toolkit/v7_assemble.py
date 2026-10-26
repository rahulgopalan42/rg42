# Assembles a delivery pack from v7 template rows + Apollo contacts.
# Usage: python3.13 v7_assemble.py "<Wave Label>" <templates.json> <contacts.json>
#   templates.json: list of v7 rows (brand, variant, designation, fit_reason, target_audience,
#                   market_overlap, shared_values, market_reference, f1_audience, flags, ...)
#   contacts.json:  {"rows": [{"brand", "people": [{"name","title","role","email"}]}]}
# Output in the scratchpad: up to 4 Merge List xlsx (one per master variant), an Emails Ready docx
# in the same format as the sent emails (Calibri 11, 1.5 spacing, blank line between blocks, bold
# designation and bullet labels, bold SPORTFIVE), and "<LABEL UPPER> - Complete.zip" with those plus
# the 4 Merge Master v7 docx files.
import json, os, re, sys, zipfile
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_BREAK

SCRATCH = os.path.dirname(os.path.abspath(__file__))
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
SUBJECT = 'Exploring Formula 1 Team Partnership Opportunity'
COLS = ['First_name', 'Full_name', 'Title', 'Role', 'Email', 'Company', 'Subject', 'Partner_designation',
        'Fit_reason', 'Target_audience', 'Market_overlap', 'Shared_values', 'Market_reference', 'F1_Audience']
FIELDS = ['designation', 'fit_reason', 'target_audience', 'market_overlap', 'shared_values',
          'market_reference', 'f1_audience']
MASTERS = ['F1 Merge Master v7 - B2B.docx', 'F1 Merge Master v7 - B2B no reference.docx',
           'F1 Merge Master v7 - B2C.docx', 'F1 Merge Master v7 - B2C no reference.docx']
OPENER = ('Reaching out from SPORTFIVE - the authorized agency managing brands sponsorships for '
          'Formula 1 teams working closely with McLaren, Haas, Audi & Mercedes to name a few.')
CLOSE = ('Would you be open to a quick call?')
BULLETS = [('Your target audience: ', 'target_audience'), ('Market Overlap: ', 'market_overlap'),
           ('Market Reference: ', 'market_reference'), ('Shared Values: ', 'shared_values'),
           ('Formula 1 Audience: ', 'f1_audience')]
qc_log = []


def scrub(text, brand, field):
    """Apply the QC scrub; log anything that needed changing."""
    if not isinstance(text, str):
        return ''
    t = text.strip()
    before = t
    t = re.sub(r'\s*[—–]\s*', ', ', t)          # em/en dashes
    t = t.replace('!', '.')
    t = re.sub(r'\b(actually|genuinely|honestly)\b,?\s*', '', t, flags=re.I)
    t = re.sub(r'\*\*|__', '', t)                          # markdown bold
    t = re.sub(r'\s{2,}', ' ', t).strip()
    if field != 'target_audience' and '$' in t:
        qc_log.append(f'{brand}: dollar figure outside target_audience ({field})')
    if t != before:
        qc_log.append(f'{brand}: scrubbed {field}')
    return t


def first_name(full):
    full = (full or '').strip()
    return full.split()[0] if full else 'there'


def group_of(row):
    v = 'B2C' if (row.get('variant') or 'B2B').upper().startswith('B2C') else 'B2B'
    return v + ('' if row.get('market_reference') else ' no reference')


def fmt(p):
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p


def write_email(doc, row, who='[First name]'):
    """Writes one email into the docx exactly as it will merge."""
    fmt(doc.add_paragraph(f'Hi {who},'))
    fmt(doc.add_paragraph())
    fmt(doc.add_paragraph(OPENER))
    fmt(doc.add_paragraph())
    p = fmt(doc.add_paragraph('A few of our Formula 1 teams are looking for an '))
    p.add_run(row['designation']).bold = True
    g = group_of(row)
    if g.startswith('B2B'):
        p.add_run(f', and {row["brand"]} was identified for the following reasons:')
    else:
        p.add_run(f', and {row["brand"]} was identified as a potential fit {row["fit_reason"]}')
    for label, field in BULLETS:
        if field == 'market_reference' and not row.get('market_reference'):
            continue
        if field == 'f1_audience' and (g.startswith('B2B') or not row.get('f1_audience')):
            continue
        fmt(doc.add_paragraph())
        p = fmt(doc.add_paragraph(style='List Bullet'))
        p.add_run(label).bold = True
        p.add_run(row[field])
    fmt(doc.add_paragraph())
    fmt(doc.add_paragraph(CLOSE))
    fmt(doc.add_paragraph())
    fmt(doc.add_paragraph('Rahul'))
    fmt(doc.add_paragraph('Major Motorsport Projects - Global Sales'))
    fmt(doc.add_paragraph()).add_run('SPORTFIVE').bold = True


def main():
    label, tpl_path, con_path = sys.argv[1], sys.argv[2], sys.argv[3]
    data = json.load(open(tpl_path))
    rows = data['rows'] if isinstance(data, dict) else data
    skipped = [r for r in rows if r.get('skip')]
    rows = [r for r in rows if not r.get('skip')]
    contacts = {}
    for r in json.load(open(con_path)).get('rows', []):
        contacts.setdefault(norm(r['brand']), []).extend(r.get('people') or [])

    for row in rows:
        for f in FIELDS:
            row[f] = scrub(row.get(f, ''), row['brand'], f)
        if row.get('variant_flag'):
            row.setdefault('flags', []).insert(0, 'B2B/B2C: ' + row['variant_flag'])
    flagged = [r for r in rows if r.get('variant_flag')]
    if flagged or skipped:
        wbf = Workbook(); wsf = wbf.active; wsf.title = 'Flagged'
        wsf.append(['Brand', 'Built as', 'Reason it could be the other', 'Designation'])
        for c in wsf[1]:
            c.font = Font(bold=True)
        for r in flagged:
            wsf.append([r['brand'], r.get('variant', ''), r['variant_flag'], r.get('designation', '')])
        for col, w in zip('ABCD', (34, 10, 90, 40)):
            wsf.column_dimensions[col].width = w
        if skipped:
            wss = wbf.create_sheet('Not built')
            wss.append(['Brand', 'Why no template'])
            for c in wss[1]:
                c.font = Font(bold=True)
            for r in skipped:
                wss.append([r['brand'], r['skip']])
            wss.column_dimensions['A'].width = 34; wss.column_dimensions['B'].width = 120
        wbf.save(os.path.join(SCRATCH, f'{label} - Flagged Brands.xlsx'))

    # ---- merge lists ----
    groups, no_contact = {}, []
    for row in rows:
        ppl = [p for p in contacts.get(norm(row['brand']), []) if p.get('email')][:4]
        if not ppl:
            no_contact.append(row['brand'])
            continue
        g = group_of(row)
        for p in ppl:
            groups.setdefault(g, []).append([
                first_name(p.get('name')), p.get('name', ''), p.get('title', ''), p.get('role', ''),
                p['email'], row['brand'], SUBJECT, row['designation'], row['fit_reason'],
                row['target_audience'], row['market_overlap'], row['shared_values'],
                row['market_reference'], row['f1_audience'] if g.startswith('B2C') else ''])
    out_files = []
    for g, lst in groups.items():
        wb = Workbook()
        ws = wb.active
        ws.title = 'Merge List'
        ws.append(COLS)
        for c in ws[1]:
            c.font = Font(bold=True)
        for r in lst:
            ws.append(r)
        for col, w in zip('ABCDEFGHIJKLMN', (14, 24, 30, 16, 34, 28, 40, 34, 60, 70, 60, 60, 60, 60)):
            ws.column_dimensions[col].width = w
        for r in ws.iter_rows(min_row=2):
            for c in r[8:]:
                c.alignment = Alignment(wrap_text=True, vertical='top')
        fn = f'{label} - Merge List - {g}.xlsx'
        wb.save(os.path.join(SCRATCH, fn))
        out_files.append(fn)
        print(f'{fn}: {len(lst)} rows')

    # ---- emails ready docx ----
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(12)
    doc.add_heading(f'{label} - Emails Ready ({len(rows)} brands)', level=1)
    doc.add_paragraph(f'Subject line: {SUBJECT}. One page per brand: notes for you first (never send '
                      f'these), then the contacts, then the email exactly as it merges.')
    for i, row in enumerate(sorted(rows, key=lambda r: r['brand'].lower())):
        if i:
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        doc.add_heading(f'{row["brand"]} ({group_of(row)})', level=2)
        for fl in row.get('flags') or []:
            p = doc.add_paragraph()
            p.add_run('NOTE: ').bold = True
            p.add_run(str(fl))
        ppl = [p for p in contacts.get(norm(row['brand']), []) if p.get('email')][:4]
        if ppl:
            doc.add_paragraph('Contacts: ' + '; '.join(f'{p.get("name","")} ({p.get("title","")}) '
                                                        f'{p["email"]}' for p in ppl))
        else:
            p = doc.add_paragraph()
            p.add_run('NOTE: no verified work email found in Apollo, source a contact manually.').bold = True
        doc.add_paragraph()
        write_email(doc, row)
    er = f'{label} - Emails Ready.docx'
    doc.save(os.path.join(SCRATCH, er))

    # ---- zip ----
    zname = f'{label.upper()} - Complete.zip'
    with zipfile.ZipFile(os.path.join(SCRATCH, zname), 'w', zipfile.ZIP_DEFLATED) as z:
        extra = [f'{label} - Flagged Brands.xlsx'] if (flagged or skipped) else []
        for fn in out_files + [er] + extra + MASTERS:
            z.write(os.path.join(SCRATCH, fn), fn)
    print('QC items:', len(qc_log))
    for q in qc_log:
        print('  ', q)
    print('brands with NO contacts:', no_contact)
    print('DONE:', zname)


if __name__ == '__main__':
    main()
