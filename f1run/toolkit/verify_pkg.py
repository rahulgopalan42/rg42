# Verify a built package: python3.13 -I verify_pkg.py <pkg root dir> <expected live brands>
import sys, os, glob, re, openpyxl, docx, collections
root = sys.argv[1]; exp = int(sys.argv[2])
OPEN = 'Reaching out from SPORTFIVE - the authorized agency managing brands sponsorships for Formula 1 teams working closely with Mercedes, McLaren, Williams & Audi to name a few.'
HOOKA = 'A few of our Formula 1 clients are exploring an '; HOOKB = 'was identified as a potential fit for the following reasons:'
CLOSE = 'Would you be open to a quick call? If interested, we would love to host you at a race to show you how partners are generating ROI.'
BAN = re.compile(r'\b(actually|genuinely|honestly)\b', re.I)
errs = []; emails = collections.Counter(); perbrand = collections.Counter(); tot = 0; nb = 0
for d in sorted(glob.glob(root + '/Batch *')):
    lists = sorted(glob.glob(d + '/* - Merge list (*).xlsx')); tpls = sorted(glob.glob(d + '/* - Word template.docx'))
    if len(lists) != len(tpls): errs.append(f'{d}: {len(lists)} lists vs {len(tpls)} templates')
    bn = 0
    for l in lists:
        pre = l.split(' - Merge list')[0]
        if not os.path.exists(pre + ' - Word template.docx'): errs.append('no template for ' + l)
        ws = openpyxl.load_workbook(l).active; hdr = [c.value for c in ws[1]]
        n = ws.max_row - 1; bn += n
        m = re.search(r'\((\d+) contacts\)', os.path.basename(l))
        if int(m.group(1)) != n: errs.append(f'count mismatch {l}')
        if n > 40: errs.append(f'>40 in {l}')
        ie = hdr.index('Email'); ic = hdr.index('Company')
        for row in ws.iter_rows(min_row=2, values_only=True):
            emails[row[ie].lower()] += 1; perbrand[row[ic]] += 1
            for h, v in zip(hdr, row):
                if isinstance(v, str) and re.search(r'[–—]', v) and h not in ('Title',): errs.append(f'dash in {h}: {row[ic]}')
                if isinstance(v, str) and BAN.search(v): errs.append(f'banned word in {h}: {row[ic]}')
        t = docx.Document(pre + ' - Word template.docx')
        st = t.styles['Normal'].font
        if st.name != 'Arial' or st.size.pt != 12: errs.append(f'template font {st.name} {st.size}')
    if bn > 40: errs.append(f'batch >40: {d} {bn}')
    tot += bn
    e = docx.Document(d + '/' + os.path.basename(d).split(' - ')[0] + ' - Emails.docx')
    txt = '\n'.join(p.text for p in e.paragraphs)
    o = txt.count(OPEN); h = txt.count(HOOKB); c = txt.count(CLOSE); nb += o
    if not (o == h == c): errs.append(f'{d}: opener {o} hook {h} close {c}')
    if txt.count(HOOKA) != o: errs.append(f'{d}: hook start {txt.count(HOOKA)} vs {o}')
    if re.search(r'[–—]', txt): errs.append(f'dash in emails doc {d}: ' + str([txt[max(0,m.start()-40):m.end()+20] for m in re.finditer(r'[–—]', txt)][:3]))
    if BAN.search(txt): errs.append(f'banned word in emails doc {d}')
    fn = e.styles['Normal'].font
    if fn.name != 'Arial' or fn.size.pt != 12: errs.append(f'emails font {fn.name} {fn.size}')
    for p in e.paragraphs:
        for r in p.runs:
            if (r.font.name and r.font.name != 'Arial') or (r.font.size and r.font.size.pt != 12): errs.append(f'run font {r.font.name} {r.font.size} in {d}: {r.text[:40]}'); break
dup = [e for e, n in emails.items() if n > 1]
if dup: errs.append('duplicate emails: ' + str(dup))
over = {b: n for b, n in perbrand.items() if n > 5}
if over: errs.append('more than 5: ' + str(over))
tr = glob.glob(root + '/00 Tracker*.xlsx')[0]; wb = openpyxl.load_workbook(tr); ws = wb['Priority order']
trows = ws.max_row - 1; tc = sum((r[9] or 0) for r in ws.iter_rows(min_row=2, values_only=True))
print('batches', len(glob.glob(root + '/Batch *')), 'brands in emails docs', nb, 'contacts', tot, 'unique emails', len(emails), 'tracker rows', trows, 'tracker contacts', tc, 'brands with contacts', len(perbrand))
if nb != exp: errs.append(f'expected {exp} emails, found {nb}')
if tc != tot: errs.append('tracker contacts != merge contacts')
print('follow-up templates', len(glob.glob(root + '/Follow-up*/*.docx')))
print('ERRORS', len(errs)); [print('  ', x) for x in errs[:40]]
