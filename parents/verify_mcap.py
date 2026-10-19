"""Step 2b: verify market caps of listed parents against companiesmarketcap.com listing pages fetched on 19 Oct 2026
(scratchpad/mcap/p*.html). Writes verified.pkl: key, val_bn, val_date, val_basis, src."""
import glob, os, re, sys
import pandas as pd
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad'
sys.path.insert(0, f'{R}/wave16')
from dedupe_v2 import strict
rows = []
for f in glob.glob(f'{S}/mcap/p*.html'):
    h = open(f, errors='ignore').read()
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S):
        nm = re.search(r'company-name">([^<]*)', tr); 
        if not nm: continue
        tds = [re.sub('<[^>]+>', '', t).strip() for t in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        code = re.search(r'company-code">([^<]*)', tr)
        code = code.group(1).strip() if code else ''
        if not code and len(tds) > 2: code = tds[2][len(nm.group(1)):].strip()
        mc = next((t for t in tds if re.match(r'^\$[\d.]+ ?[TBM]$', t)), '')
        if not mc: continue
        v = float(mc[1:-1]); unit = mc[-1]; v = v * {'T': 1000, 'B': 1, 'M': 0.001}[unit]
        country = tds[-1].split()[-1] if tds else ''
        rows.append({'name': nm.group(1).strip(), 'code': code, 'val_bn': round(v, 1), 'country': country})
mc = pd.DataFrame(rows).drop_duplicates('name')
print('market-cap rows', len(mc), 'min', mc['val_bn'].min() if len(mc) else None)
base = lambda n: strict(re.sub(r'\s*\(.*?\)\s*', ' ', n))
by_name = {}
for r in mc.itertuples():
    for k in {strict(r.name), base(r.name)}:
        if len(k) >= 4: by_name.setdefault(k, r)
by_code = {r.code.upper(): r for r in mc.itertuples() if r.code}
par = pd.read_pickle(f'{S}/parents/parents.pkl')
out = []
for p in par.itertuples():
    typ = str(p.type or '').lower(); tk = str(p.ticker or '')
    if typ != 'listed' and not tk: continue
    hit = None
    sym = tk.split(':')[-1].strip().upper() if tk else ''
    if sym and sym in by_code: hit = by_code[sym]
    if hit is None:
        for k in {strict(p.name), base(p.name)} | {strict(a) for a in (p.names or [])}:
            if k in by_name: hit = by_name[k]; break
    if hit is None: continue
    # sanity: a knowledge figure that disagrees by more than 5x suggests a wrong match -> skip
    kv = p.val_bn if isinstance(p.val_bn, float) and p.val_bn == p.val_bn else None
    if kv and (hit.val_bn > kv * 5 or hit.val_bn < kv / 5): continue
    out.append({'key': p.key, 'val_bn': hit.val_bn, 'val_date': '2026-10', 'val_basis': 'market cap', 'src': f'companiesmarketcap.com ({hit.name} {hit.code})'})
ver = pd.DataFrame(out)
ver.to_pickle(f'{S}/parents/verified.pkl')
print('verified parents', len(ver), 'of listed', int(((par['type'].astype(str).str.lower() == 'listed') | par['ticker'].astype(str).str.len().gt(0)).sum()))
