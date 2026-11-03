"""Exclusion index for the 30 Oct 2026 new-brands task: every company, brand, subsidiary and website that appears on
(1) MASTER REFERENCE OCT (Rahul's Drive file, all tabs) and (2) the parent-company prospects workbook (all tabs).
Writes brands200/exclusion.json: {"names": [...normalised...], "domains": [...registrable...]}.
Usage: python exclusion.py <MASTER_REFERENCE_OCT.xlsx>"""
import json, os, re, sys, warnings
import openpyxl
warnings.filterwarnings('ignore')
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUFFIX = re.compile(r'\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|plc|ag|sa|se|nv|bv|gmbh|spa|srl|ab|asa|oyj|kk|pte|pty|holdings?|group|the|s\.a|s\.p\.a)\b\.?', re.I)
def strict(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())
def loose(s): return strict(SUFFIX.sub(' ', re.sub(r'\(.*?\)', ' ', str(s))))
def regdom(d):
    d = re.sub(r'^(https?://)?(www\.)?', '', str(d).strip().lower()).split('/')[0]
    parts = d.split('.')
    if len(parts) >= 3 and parts[-2] in ('co', 'com', 'net', 'org', 'ac', 'gov', 'ne', 'or') and len(parts[-1]) == 2: return '.'.join(parts[-3:])
    return '.'.join(parts[-2:]) if len(parts) >= 2 else ''
DOM = re.compile(r'^(https?://)?(www\.)?[a-z0-9][a-z0-9.\-]*\.[a-z]{2,}(/\S*)?$', re.I)
names, doms, firsts = set(), set(), set()
def add_name(v):
    v = str(v).strip()
    if not v or v.lower() in ('none', 'nan', 'x', 'tbr') or len(v) > 120: return
    for part in re.split(r';|\|', v):                               # "A; B; C" lists of subsidiaries / brands
        part = part.strip()
        if len(strict(part)) >= 3: names.add(strict(part)); names.add(loose(part))
        w = [strict(x) for x in re.sub(r'\(.*?\)', ' ', part).split() if strict(x)]
        if w: firsts.add(w[0])
        for inner in re.findall(r'\(([^)]+)\)', part):             # "Brand (Parent)" -> both
            if len(strict(inner)) >= 4: names.add(strict(inner))
def add_dom(v):
    v = str(v).strip()
    if DOM.match(v): doms.add(regdom(v))
NAMECOLS = re.compile(r'company|brand|parent|subsidiar|^x$|name', re.I)
DOMCOLS = re.compile(r'domain|website', re.I)
def scan(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        rows = ws.iter_rows(values_only=True)
        try: hdr = [str(h or '') for h in next(rows)]
        except StopIteration: continue
        for r in rows:
            for i, v in enumerate(r):
                if v in (None, ''): continue
                h = hdr[i] if i < len(hdr) else ''
                if DOMCOLS.search(h) or DOM.match(str(v).strip()): add_dom(v)
                if NAMECOLS.search(h) and not DOMCOLS.search(h): add_name(v)
            # MASTER REFERENCE tabs with shifted headers: company is column C (worked) or D (original)
            for i in (2, 3):
                if i < len(r) and r[i] not in (None, '') and not DOM.match(str(r[i]).strip()) and len(str(r[i])) < 80: add_name(r[i])
scan(sys.argv[1])
scan(os.path.join(R, 'reports', '2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS.xlsx'))
names.discard(''); doms.discard('')
json.dump({'names': sorted(names), 'domains': sorted(doms), 'first_words': sorted(firsts)}, open(os.path.join(R, 'brands200', 'exclusion.json'), 'w'))
print('exclusion names', len(names), 'domains', len(doms))
