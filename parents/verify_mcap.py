"""Step 2b: verify market caps of listed parents against companiesmarketcap.com listing pages fetched on 19 Oct 2026
(scratchpad/mcap/p*.html). Writes verified.pkl: key, val_bn, val_date, val_basis, src."""
import glob, html, os, re, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs
R = inputs.REPO; S = inputs.S
from dedupe_v2 import strict
rows = inputs.market_cap_rows()
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
    def tok(n): return {t for t in re.findall(r'[a-z0-9]{3,}', str(n).lower()) if t not in ('the', 'group', 'inc', 'corp', 'corporation', 'company', 'holdings', 'international', 'limited', 'ltd', 'plc', 'and')}
    if sym and sym in by_code and (tok(by_code[sym].name) & (tok(p.name) | {t for a in (p.names or []) for t in tok(a)})): hit = by_code[sym]
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
