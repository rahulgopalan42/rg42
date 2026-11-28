"""Builds the exclusion register for non-public prospecting (governing methodology, section 2).
Usage: register.py [master.xlsx]      (the master is read once and its names are kept in v2/master_names.json.gz)
Writes v2/register.json.gz: {"names": {key: [display name, source, kind]}, "domains": {...}}. kind: dup = on the master spreadsheet
(any tab) or already delivered under the revised methodology; f1 = holds a current F1 deal; listed = name of a listed company;
f1owner and info = recorded for information, not exclusions."""
import glob, gzip, json, os, re, sys, unicodedata
H = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(H); R = os.path.dirname(B)
SUF = re.compile(r'\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|llp|lp|plc|sa|sas|ag|se|nv|bv|gmbh|kg|kgaa|spa|srl|ab|as|asa|oy|oyj|pte|pty|sdn|bhd|holdings?|group|the)\b')
# letters that have no ASCII decomposition were silently dropped, so 'Altınbaş' and 'ALTINBAŞ', 'Ørsted' and 'Orsted', 'Voßloh' and 'Vossloh' did not match (28 Nov 2026)
_TR = str.maketrans({'ı': 'i', 'İ': 'I', 'ø': 'o', 'Ø': 'O', 'ß': 'ss', 'æ': 'ae', 'Æ': 'AE', 'œ': 'oe', 'Œ': 'OE', 'đ': 'd', 'Đ': 'D', 'ł': 'l', 'Ł': 'L', 'ð': 'd', 'Ð': 'D', 'þ': 'th', 'Þ': 'Th'})
def norm(s): return re.sub(r'[^a-z0-9]+', '', unicodedata.normalize('NFKD', str(s).translate(_TR)).encode('ascii', 'ignore').decode().lower())
def loose(s):
    s = unicodedata.normalize('NFKD', str(s).translate(_TR)).encode('ascii', 'ignore').decode().lower().replace('&', ' and ')
    s = re.sub(r'[^a-z0-9 ]', ' ', s); s = SUF.sub(' ', s)
    return re.sub(r'\s+', '', s)
def dom(u):
    u = str(u or '').strip().lower(); u = re.sub(r'^[a-z]+://', '', u); u = u.split('/')[0].split('?')[0]; u = re.sub(r'^www\d?\.', '', u)
    return u if re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', u) else ''
def aliases(name):
    """the name itself plus the parts of 'A (B)', 'A (formerly B)', 'A / B' and 'A, trading as B'"""
    n = str(name).strip(); out = [n]
    m = re.match(r'^(.*?)\s*\((.*?)\)\s*$', n)
    if m:
        out.append(m.group(1)); inner = re.sub(r'(?i)^(formerly|previously|now|fka|aka|ex-?|trading as|part of|owned by)\s+', '', m.group(2)).strip()
        if inner and not re.search(r'(?i)^(listed|private|unlisted|brand|group|holding|the |a |an )', inner) and len(inner) > 2 and not re.search(r'(?i)\b(of|in|by|for|platform|services?|company|maker|operator|consultancy|spinout)\b', m.group(2)): out.append(inner)
    for sep in (' / ', ' dba ', ' d/b/a ', ', trading as ', ' t/a '):
        if sep in n.lower(): out += [p.strip() for p in re.split(re.escape(sep), n, flags=re.I)]
    return [a for a in out if a and len(norm(a)) >= 2]
def read_master(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True); out = []
    for ws in wb.worksheets:
        if ws.title in ('Summary', 'Key'): continue
        it = ws.iter_rows(values_only=True); h = [str(c or '') for c in next(it)]
        ci = 0; wi = next((i for i, c in enumerate(h) if c.strip().lower() == 'website'), None); oi = next((i for i, c in enumerate(h) if c.strip() == 'On Your Sheet?'), None)
        if ws.title == 'Templates Created': continue
        for r in it:
            if not r or r[ci] is None or not isinstance(r[ci], str): continue
            src = 'master: ' + ws.title
            if oi is not None and oi < len(r) and str(r[oi] or '').startswith('Yes'): src += ' (on your 48-tab sheet)'
            out.append([r[ci].strip(), src, dom(r[wi]) if wi is not None and wi < len(r) else ''])
    return out
def build(master=None):
    """Only the user's master spreadsheet (every tab) and anything already delivered under the revised methodology count as duplicates
    (user's instruction of 27 Nov 2026). Listed companies and brands holding a current F1 deal are kept as eligibility checks.
    Everything else (the older 48-tab sheet, earlier waves and research batches) is recorded as information only and does not exclude."""
    mp = os.path.join(H, 'master_names.json.gz')
    if master: json.dump(read_master(master), gzip.open(mp, 'wt', encoding='utf-8'), ensure_ascii=False)
    N = {}; D = {}
    PRI = {'dup': 0, 'f1': 1, 'listed': 2, 'f1owner': 3, 'gp': 3, 'info': 4}
    def put(name, kind, src, d=''):
        for a in aliases(name):
            for k in {norm(a), loose(a)}:
                if len(k) >= 2 and (k not in N or PRI[kind] < PRI[N[k][2]]): N[k] = [str(name), src, kind]
        d = dom(d)
        if d and (d not in D or PRI[kind] < PRI[D[d][2]]): D[d] = [str(name), src, kind]
    for name, src, d in json.load(gzip.open(mp, 'rt', encoding='utf-8')): put(name, 'dup', src, d)               # 1. the master spreadsheet, every tab
    V = {}; VD = {}                                                                                                  # 2. already delivered under the revised methodology: kept apart, so a batch can be rebuilt
    for p in sorted(glob.glob(os.path.join(H, 'delivered', '*.json'))):
        src = 'delivered under the revised methodology: ' + os.path.basename(p)[:-5]
        for nm, site in json.load(open(p, encoding='utf-8')):
            for a in aliases(nm):
                for k in {norm(a), loose(a)}:
                    if len(k) >= 2: V.setdefault(k, [str(nm), src, 'dup'])
            if dom(site): VD.setdefault(dom(site), [str(nm), src, 'dup'])
    f1 = os.path.join(R, 'unicorns', 'ref', 'f1_sponsors_2026.json')                                                 # 3. brands holding a current F1 deal
    if os.path.exists(f1):
        J = json.load(open(f1, encoding='utf-8')); rows = J if isinstance(J, list) else J.get('rows') or J.get('sponsors') or []
        for r in rows:
            if isinstance(r, list) and len(r) >= 3 and isinstance(r[0], str): put(r[0], 'f1', f'current F1 partner ({r[2]})', r[1])
    fp = os.path.join(H, 'f1_extra.json')                                                                            # 3b. confirmed later additions: [name, site, property, source]
    if os.path.exists(fp):
        for r in json.load(open(fp, encoding='utf-8')): put(str(r[0]).strip(), 'f1', f'current F1 partner ({r[2]})', r[1])
    fp = os.path.join(H, 'f1_gp_partners_2026.json')                                                                 # 3c. names read off Grand Prix promoters' partner pages
    if os.path.exists(fp):
        for r in json.load(open(fp, encoding='utf-8')):
            if not (isinstance(r, list) and len(r) >= 3 and len(str(r[0]).strip()) >= 2): continue
            soft = re.search(r'(?i)circuit|names from|COTA', str(r[2]))      # a year-round circuit page, or a name read from a logo file: a note to check, not an exclusion
            put(str(r[0]).strip(), 'gp' if soft else 'f1', ('on a Grand Prix circuit partner page: ' + str(r[2])) if soft else f'current F1 partner ({r[2]})')
    for k, v in json.load(open(os.path.join(B, 'newsec', 'known.json'), encoding='utf-8')).items():                  # 4. listed companies, F1 partners and their owners, as recorded earlier
        t = v[1]
        kind = 'f1' if t.startswith('current F1 partner') and 'owner' not in t else 'f1owner' if 'owner of' in t or 'or owner' in t else 'listed' if t.startswith('listed') else 'info'
        if kind == 'info': t = 'your older 48-tab sheet' if t.startswith('on the sheet') else t
        put(v[0], kind, t)
    for d in json.load(gzip.open(os.path.join(B, 'data', 'brands.json.gz'), 'rt', encoding='utf-8')):                # 5. information only: the older 48-tab sheet
        for nm in (d.get('brand'), d.get('orig_brand')):
            if nm: put(nm, 'info', 'your older 48-tab sheet: ' + str(d.get('tab') or d.get('sector') or '') + (' (you marked it x)' if d.get('mark') else ''))
    json.dump({'names': N, 'domains': D, 'delivered': V, 'delivered_domains': VD}, gzip.open(os.path.join(H, 'register.json.gz'), 'wt', encoding='utf-8'), ensure_ascii=False)
    return N, D
if __name__ == '__main__':
    from collections import Counter
    N, D = build(sys.argv[1] if len(sys.argv) > 1 else None)
    print('name keys', len(N), '| domains', len(D), '|', dict(Counter(v[2] for v in N.values())))
    M = json.load(gzip.open(os.path.join(H, 'master_names.json.gz'), 'rt', encoding='utf-8')); print('master rows read', len(M), '| unique names', len({norm(m[0]) for m in M}))
