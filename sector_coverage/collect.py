"""Every brand in every workbook delivered so far (reports/*.xlsx, all tabs) -> sector_coverage/brands.json.gz.
One record per brand (matched on the cleaned name): its category fields, its descriptions, and every workbook tab it
appears on with that tab's verdict / research-status values, so classify.py can tell researched prospects from
database-only rows and rejects.  Usage: collect.py"""
import glob, gzip, json, os, re, sys, warnings
from openpyxl import load_workbook
warnings.filterwarnings('ignore')
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, regdom
SKIP_FILE = re.compile(r'Send-Ready|Audit|SECTOR-COVERAGE', re.I)                      # email merge file, audit of the master sheet
REC = re.compile(r'SCREEN-RECORDINGS', re.I)
SKIP_TAB = re.compile(r'read ?me|overview|summary|^qc$|ranges check|page check|index|legend|method|reconciliation', re.I)
NAME = [re.compile(p, re.I) for p in (r'^brand$', r'^company$', r'^parent company name$', r'^name$', r'^key_brand$')]
CAT = re.compile(r'niche|sector|industry|categor|cluster|sub-?sector|archetype', re.I)          # short category-like fields
DESC = re.compile(r'sells|what they do|about the company|^description|what_it', re.I)           # what the company does
NOTTEXT = re.compile(r'confidence|rank|score|pts|source|date|why', re.I)
DOM = re.compile(r'^(domain|website)$', re.I); CTRY = re.compile(r'^(hq|hq[_ ]country|country)$', re.I)
VERD = re.compile(r'^(verdict.*|tag \(verdict\))$', re.I)
QUAL = re.compile(r'^(ranking type|research status|research confidence|status|reason)$', re.I)
out = {}; files = []
for f in sorted(glob.glob(os.path.join(R, 'reports', '*.xlsx'))):
    b = os.path.basename(f)
    if SKIP_FILE.search(b): continue
    files.append(b[:-5]); fi = len(files) - 1; wb = load_workbook(f, read_only=True); n = 0
    for ws in wb.worksheets:
        t = ws.title
        if SKIP_TAB.search(t): continue
        if REC.search(b) and t not in ('ALL PROSPECTS (RANKED)', 'ALREADY F1 SPONSORS'): continue     # sector tabs repeat the main tab
        hdr = None; seen_tab = set()
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if hdr is None:
                if i > 8: break
                if row and sum(1 for c in row if isinstance(c, str)) >= 3:
                    hdr = [str(c or '').strip() for c in row]
                    ni = next((hdr.index(h) for p in NAME for h in hdr if p.search(h)), None)
                    if ni is None: break
                    ti = [j for j, h in enumerate(hdr) if CAT.search(h) and not NOTTEXT.search(h) and j != ni]
                    xi = [j for j, h in enumerate(hdr) if DESC.search(h) and not NOTTEXT.search(h) and j != ni and j not in ti]
                    di = next((j for j, h in enumerate(hdr) if DOM.search(h)), None)
                    ci = next((j for j, h in enumerate(hdr) if CTRY.search(h)), None)
                    vi = next((j for j, h in enumerate(hdr) if VERD.search(h)), None)
                    qi = [j for j, h in enumerate(hdr) if QUAL.search(h)]
                    log = len(hdr) <= 6 and any(re.search(r'^reason', h, re.I) for h in hdr)      # drop logs: company | reason
                continue
            if ni >= len(row) or not isinstance(row[ni], str) or not row[ni].strip() or len(row[ni]) > 90: continue
            nm = row[ni].strip(); k = loose(nm) or nm.lower()
            if len(k) < 2: continue
            c = out.setdefault(k, {'name': nm, 'web': '', 'country': '', 'cat': [], 'desc': [], 'on': []})
            for j in ti:
                if j < len(row) and row[j] not in (None, ''):
                    v2 = str(row[j]).strip()[:200]
                    if v2 not in c['cat'] and len(c['cat']) < 14: c['cat'].append(v2)
            for j in xi:
                if j < len(row) and row[j] not in (None, ''):
                    v2 = str(row[j]).strip()[:500]
                    if v2 not in c['desc'] and sum(len(x) for x in c['desc']) < 1400: c['desc'].append(v2)
            if k not in seen_tab:
                seen_tab.add(k)
                v = str(row[vi]).strip()[:30] if vi is not None and vi < len(row) and row[vi] else ''
                q = ' ; '.join(str(row[j]).strip()[:45] for j in qi if j < len(row) and row[j])[:110]
                c['on'].append([fi, t, v, ('LOG ' if log else '') + q])
            if di is not None and di < len(row) and row[di] and not c['web']: c['web'] = regdom(row[di])
            if ci is not None and ci < len(row) and row[ci] and not c['country']: c['country'] = str(row[ci]).strip()[:40]
            n += 1
    wb.close(); print(f'{n:7d} rows  {b}', flush=True)
json.dump({'files': files, 'brands': list(out.values())}, gzip.open(os.path.join(H, 'brands.json.gz'), 'wt'), ensure_ascii=False)
print('unique brands', len(out))
