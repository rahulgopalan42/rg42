"""Write score_in chunks for connector-sourced parents that still need knowledge scoring.
Only records that can reach the master ranking or manual review are scored: category A, category C, and category B
records where the parent itself is not yet in any dataset (group-level new). Apollo/Lusha records whose parent is
already listed in the existing datasets are left unscored and reported in the summary instead.
Usage: split_score.py <first_chunk_number> [chunk_size]"""
import json, math, os, sys
import pandas as pd
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad'; R = '/home/user/rg42'
first = int(sys.argv[1]); size = int(sys.argv[2]) if len(sys.argv) > 2 else 160
par = pd.read_pickle(f'{S}/parents/parents.pkl')
import glob
assigned = set()
for f_ in glob.glob(f'{R}/parents/score_in/chunk_*.json'):
    if int(f_[-7:-5]) < first:
        assigned |= {str(r[0]).strip().lower() for r in json.load(open(f_))}
ns = par[par['needs_score'] & ((par['overlap_cat'] != 'B') | (par['parent_listed'] == 'no')) & ~par['name'].astype(str).str.strip().str.lower().isin(assigned)]
cl = lambda v: '' if v is None or (isinstance(v, float) and math.isnan(v)) else v
rows = [[cl(r['name']), cl(r['domain']), cl(r['hq_country']), cl(r.get('exchange')), cl(r.get('revenue_printed')), cl(r.get('lusha_industry')),
         cl(r.get('naics0')), list(r['children'])[:8] if isinstance(r['children'], (list, tuple)) else [],
         bool(r.get('apollo_funding')) or ('lusha' in str(r['sources']).lower())] for _, r in ns.iterrows()]
n = math.ceil(len(rows) / size)
for i in range(n):
    json.dump(rows[i * size:(i + 1) * size], open(f'{R}/parents/score_in/chunk_{first + i:02d}.json', 'w'), ensure_ascii=False)
print('rows to score', len(rows), 'chunks', first, '-', first + n - 1, '| unscored but parent already listed (left as is):', int((par['needs_score'] & ~par.index.isin(ns.index)).sum()))
