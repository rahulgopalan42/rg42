# Audit step 2: match doc brands to master rows, record markings, test what each mark meant.
# Usage: python3.13 -I audit_match.py <master.xlsx>   (reads audit_docs.json from this folder)
# Writes audit_rows.json (one row per master brand) and audit_docmatch.json (one row per doc brand).
import collections, glob, json, os, re, sys
import openpyxl

OUT = os.path.dirname(os.path.abspath(__file__))
MASTER = sys.argv[1]
docs = json.load(open(f'{OUT}/audit_docs.json'))
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
SUFFIX = re.compile(r'\b(inc|incorporated|ltd|limited|llc|plc|ag|sa|se|nv|bv|spa|corp|corporation|co|company|'
                    r'group|holdings?|gmbh|kk|oyj|asa|ab|technologies|technology)\b\.?', re.I)
core = lambda s: norm(SUFFIX.sub(' ', re.sub(r'\(.*?\)', ' ', s or '')))
dnorm = lambda d: re.sub(r'^(https?://)?(www\.)?', '', (d or '').strip().lower()).split('/')[0]

DOC_TAB = {'W05': ['Comp - Devtols & Integration'], 'W06': ['Comp - Defense'], 'W07': ['145 - Consumer & Lifestyle'],
           'W08': ['Comp - Automation'], 'W09': ['Comp - DC Power & Cooling'], 'W10': ['139- Photonics & Optical'],
           'W11': ['126- Robotics AI'], 'W12': ['Comp - Storage Hardware'], 'W13': ['75-  Law Firms & Legal AI'],
           'W14': ['200 - Energy & Industrial'], 'W15': ['Comp - EDA'], 'W16': ['41 OT & Physical Security'],
           'W17': ['61-  Home & Living'], 'W18': ['Comp - Services'], 'W19': ['Comp- Tools & Industrial Supply'],
           'W20': ['Complete - Telecom & Space'], 'W21': ['66 - Mobility & Automotive'],
           'W22': ['202 - GRC & Risk SW'], 'W23': ['Comp - Machine Tools', 'Comp -Supercomputing'],
           'W01': [], 'W02': [], 'W03': [], 'W04': []}   # Priority / Up and Coming / Sheet23: no master tab

# domains for doc brands from the Oct 11 run queue files in the repo (waves 2-22)
qdom = {}
for fn in glob.glob('/home/user/rg42/f1run/w*k_*.json'):
    for b in json.load(open(fn)):
        if b.get('domain'):
            qdom.setdefault(norm(b['brand']), dnorm(re.split(r'[\s(]', b['domain'])[0]))

# ---- master rows ----
wb = openpyxl.load_workbook(MASTER, read_only=True, data_only=True)
mrows = []
for ws in wb.worksheets:
    if ws.title == 'OVERVIEW':
        continue
    it = ws.iter_rows(values_only=True)
    hdr = [str(h).strip().lower() if h is not None else '' for h in next(it)]
    if 'company' in hdr:
        ni = hdr.index('company')
    elif 'domain' in hdr:
        ni = hdr.index('domain') - 1
    else:
        ni = 1
    di = hdr.index('domain') if 'domain' in hdr else None
    for rix, r in enumerate(it, start=2):
        vals = list(r)
        name = str(vals[ni]).strip() if ni < len(vals) and vals[ni] is not None else ''
        if not name:
            continue
        mark = ''
        for v in vals[:ni]:
            s = str(v).strip() if v is not None else ''
            if s and not re.fullmatch(r'[\d.]+', s) and s != 'KEY':
                mark = s
        mrows.append({'tab': ws.title, 'row': rix, 'col': ni + 1, 'name': name,
                      'domain': dnorm(str(vals[di])) if di is not None and di < len(vals) and vals[di] else '',
                      'mark': mark, 'templ': None, 'match': None})

by_norm, by_core, by_dom = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
for i, m in enumerate(mrows):
    by_norm[norm(m['name'])].append(i)
    if len(core(m['name'])) >= 3:
        by_core[core(m['name'])].append(i)
    if m['domain']:
        by_dom[m['domain']].append(i)

# ---- match each doc brand ----
dm = []
for d in docs:
    b = d['header']
    tabs = DOC_TAB[d['doc']]
    dom = qdom.get(norm(b), '')
    exact = by_norm.get(norm(b), [])
    cmatch = [i for i in by_core.get(core(b), []) if i not in exact] if len(core(b)) >= 3 else []
    dmatch = [i for i in by_dom.get(dom, []) if i not in exact and i not in cmatch] if dom else []
    verified, uncertain = [], []
    for i in exact:
        verified.append((i, 'exact name'))
    for i in cmatch:
        m = mrows[i]
        if (dom and m['domain'] == dom) or m['tab'] in tabs:
            verified.append((i, 'name variant + ' + ('domain' if dom and m['domain'] == dom else 'same category')))
        else:
            uncertain.append((i, 'name variant only'))
    for i in dmatch:
        m = mrows[i]
        (verified if m['tab'] in tabs else uncertain).append((i, 'same domain' + (' + same category' if m['tab'] in tabs else '')))
    for i, why in verified:
        mrows[i]['templ'] = 'verified'
        mrows[i]['match'] = f'{d["doc"]} #{d["n"]} {b} ({why})'
    for i, why in uncertain:
        if mrows[i]['templ'] != 'verified':
            mrows[i]['templ'] = 'uncertain'
            mrows[i]['match'] = f'{d["doc"]} #{d["n"]} {b} ({why})'
    in_tab = any(mrows[i]['tab'] in tabs for i, _ in verified)
    dm.append({'doc': d['doc'], 'n': d['n'], 'brand': b, 'verified_rows': len(verified), 'uncertain_rows': len(uncertain),
               'tabs': sorted({mrows[i]['tab'] for i, _ in verified}), 'in_mapped_tab': in_tab})

json.dump(mrows, open(f'{OUT}/audit_rows.json', 'w'), indent=0)
json.dump(dm, open(f'{OUT}/audit_docmatch.json', 'w'), indent=0)

# ---- report ----
nf = [x for x in dm if not x['verified_rows'] and not x['uncertain_rows']]
print(f'doc brands {len(dm)} | matched to >=1 master row {sum(1 for x in dm if x["verified_rows"])} | '
      f'uncertain only {sum(1 for x in dm if not x["verified_rows"] and x["uncertain_rows"])} | not in master {len(nf)}')
print('not in master by doc:', dict(collections.Counter(x['doc'] for x in nf)))
off = [x for x in dm if x['verified_rows'] and DOC_TAB[x['doc']] and not x['in_mapped_tab']]
print('matched but outside mapped tab:', len(off), [(x['doc'], x['brand'], x['tabs'][:2]) for x in off[:8]])
print('master rows: verified', sum(1 for m in mrows if m['templ'] == 'verified'),
      '| uncertain', sum(1 for m in mrows if m['templ'] == 'uncertain'), '| total', len(mrows))

def mk(m):
    s = m['mark'].lower()
    return 'x' if s == 'x' else 'tbr' if s == 'tbr' else '' if not s else 'other:' + m['mark']
xt = collections.Counter((mk(m), m['templ'] or 'none') for m in mrows)
print('MARK x TEMPLATE (all tabs):')
for k in sorted({k[0] for k in xt}):
    print(f'   {k or "(blank)":12s} verified={xt[(k, "verified")]:5d} uncertain={xt[(k, "uncertain")]:4d} none={xt[(k, "none")]:5d}')
