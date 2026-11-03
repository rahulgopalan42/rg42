"""Round-2 helpers. step 'pool': screened Apollo/Clay names (Y/?) -> minimal records in discover2_out/pool_screen.json.
step 'apollo': domains of round-2 candidates without an Apollo result -> ref/apollo_extra2_in.json.
step 'enrich': round-2 candidates (research defaults / pool rows) -> ref/enrich2_in_N.json for the scoring pass."""
import json, glob, os, sys, math
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(H), 'brands200')); from match import loose, regdom
F = ['brand', 'legal_name', 'parent', 'hq_country', 'hq_city', 'domain', 'sector', 'what', 'valuation_bn', 'valuation_date', 'valuation_basis',
     'funding_m', 'latest_round', 'status', 'investors', 'revenue_m', 'why', 'a', 's', 'l', 'n', 'f1_status', 'f1_deal', 'sport_deals', 'headcount',
     'fund_recency', 'brand_hires', 'competitor_f1', 'motorsport', 'expansion', 'race_footprint', 'founder', 'evidence', 'ceo', 'conf', 'source_url', 'note']
step = sys.argv[1]
if step == 'pool':
    out = []
    for f in sorted(glob.glob(f'{H}/pool2/screen_out/*.json')):
        for r in json.load(open(f)):
            if len(r) < 6 or str(r[2]).strip() not in ('Y', '?'): continue
            d = {k: None for k in F}
            d.update(brand=r[0], legal_name='', parent='', hq_country=r[3] or '', hq_city='', domain=r[1] or '', sector=r[4] if isinstance(r[4], int) else 48, what='',
                     valuation_basis='', latest_round='', status='private', investors='', why='', f1_status='', f1_deal='', sport_deals='', evidence='', ceo='',
                     conf='L', source_url='', note=f'Apollo/Clay funding pool; screen {r[2]}: {r[5]}', valuation_date='')
            for k in ('a', 's', 'l', 'n', 'headcount', 'fund_recency', 'brand_hires', 'competitor_f1', 'motorsport', 'expansion', 'race_footprint', 'founder'): d[k] = 0
            out.append(d)
    json.dump(out, open(f'{H}/discover2_out/pool_screen.json', 'w')); print('pool records', len(out))
else:
    u = pd.read_pickle(f'{H}/all.pkl')
    r2 = u[u['found_by'].str.contains(r'\bv\d\d\b|pool_screen', regex=True) & ~u['already_sent'] & u['bucket'].isin(['main', 'unverified', 'near', 'f1'])]
    if step == 'apollo':
        ds = sorted({d for L, a in zip(r2['domains'], r2['apollo_funding']) if a == 'not checked' for d in L})
        json.dump(ds, open(f'{H}/ref/apollo_extra2_in.json', 'w')); print('domains for Apollo', len(ds))
    if step == 'enrich':
        done = set()
        for f in glob.glob(f'{H}/ref/enrich2_in_*.json'): done |= {x[0] for x in json.load(open(f))}
        nv = lambda x: None if x != x else float(x)
        rows = [['b:' + r.brand, r.brand, r.domain, r.hq_country, r.hq_city, r.what or r.sector_name, nv(r.valuation_bn), nv(r.funding_m), r.investors[:80], r.latest_round]
                for r in r2.itertuples() if r.verdict == 'verified' and 'b:' + r.brand not in done]
        start = len(glob.glob(f'{H}/ref/enrich2_in_*.json')) + 1; N = 80
        for i in range(0, len(rows), N): json.dump(rows[i:i + N], open(f'{H}/ref/enrich2_in_{start + i // N}.json', 'w'))
        print('rows to score', len(rows), 'chunks', math.ceil(len(rows) / N), 'from', start)
