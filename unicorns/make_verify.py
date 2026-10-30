"""Write verify_in chunks (40 rows) for every merged candidate that could pass Rahul's tests and is not yet web-checked.
Run after build.py (reads all.pkl). Also takes connector-pool names that research did not find (pool/screen_out.json)."""
import json, os, sys, glob
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(H), 'brands200')); from match import loose
u = pd.read_pickle(f'{H}/all.pkl')
nv = lambda x: None if x != x else float(x)
cand = u[~u['verified'] & ~u['banned'] & (u['status'].isin(['private', '']) | u['status_conflict'])
         & ((u['valuation_bn'] >= 0.8) | u['valuation_bn'].isna()) & ((u['funding_m'] >= 150) | u['funding_m'].isna())]
done = set()
for f in glob.glob(f'{H}/verify_in/*.json'):
    for r in json.load(open(f)): done.add(loose(r[1]))
rows = [[r['brand'], r['brand'], r['domain'], r['hq_country'], nv(r['valuation_bn']), r['vdate'], nv(r['funding_m']), r['status'], r['latest_round'],
         r['source_url'], r['what'], r['status_all'] if r['status_conflict'] else ''] for _, r in cand.iterrows() if loose(r['brand']) not in done]
pf = f'{H}/pool/screen_out.json'
if os.path.exists(pf):
    have = set(u['brand'].map(loose)) | done
    for r in json.load(open(pf)):          # [name, domain, country, verdict]
        if r[3] in ('Y', '?') and loose(r[0]) not in have: rows.append([r[0], r[0], r[1], r[2], None, '', None, '', '', '', '', 'pool']); have.add(loose(r[0]))
start = len(glob.glob(f'{H}/verify_in/*.json')) + 1
for i in range(0, len(rows), 40):
    n = start + i // 40; json.dump(rows[i:i + 40], open(f'{H}/verify_in/v{n:03d}.json', 'w'))
print('rows to verify', len(rows), 'chunks', (len(rows) + 39) // 40, 'starting at', start)
