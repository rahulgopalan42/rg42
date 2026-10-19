"""Queue every confirmed-new brand that has neither research nor an earlier pre-sort, best preliminary score first.
Writes wave16/presort/in_NNNN.json (150 rows each, compact arrays) and presort/index.json (file -> keys)."""
import json, os, sys
import pandas as pd
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
sys.path.insert(0, f'{R}/wave16')
import scoring_v3 as sc
N = 150
b = pd.read_pickle(f'{S}/base.pkl')
b = b[(b['dup_status'] == 'new') & ~b['researched'] & (b['tri_t'] == '')].copy()
a, s, l, i = sc.prog_fit_df(b)
fin = [sum(sc.prog_fin(r.clay_band, r.funding_100m_apollo, r.type == 'Public Company' or bool(r.apollo_exchange), r.size)) for r in b.itertuples()]
b['pre'] = a * 20 + s * 20 + l * 10 + i * 10 + pd.Series(fin, index=b.index)
b = b.sort_values('pre', ascending=False)
os.makedirs(f'{R}/wave16/presort', exist_ok=True)
idx = {}
desc = b['description'].fillna('').str.replace(r'\s+', ' ', regex=True).str.slice(0, 220)
rows = list(zip(b['k'], b['name'], b['domain'].fillna(''), b['country'].fillna(''), b['industry'].fillna(''),
                b['size'].fillna(''), b['type'].fillna(''), desc))
for n in range(0, len(rows), N):
    fno = n // N + 1; chunk = rows[n:n + N]
    path = f'{R}/wave16/presort/in_{fno:04d}.json'
    json.dump([[j, *r[1:]] for j, r in enumerate(chunk)], open(path, 'w'), ensure_ascii=False, separators=(',', ':'))
    idx[f'{fno:04d}'] = [r[0] for r in chunk]
json.dump(idx, open(f'{R}/wave16/presort/index.json', 'w'), ensure_ascii=False)
print('queued', len(rows), 'files', len(idx))
