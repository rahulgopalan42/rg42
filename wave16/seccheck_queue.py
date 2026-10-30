"""Sector check: ranked brands whose sector so far rests only on the LinkedIn industry label (researched brands and
earlier-triage brands that never went through the Wave 16 pre-sort). Writes wave16/seccheck/in_NNNN.json (300 rows)
and seccheck/index.json (file -> keys)."""
import json, sys
import pandas as pd
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
sys.path.insert(0, f'{R}/wave16')
from sectors_v3 import NAMES
N = 300
q = pd.read_pickle(f'{S}/final_ranked.pkl')
q = q[(q['sector_basis'] == 'LinkedIn industry') & ~q['presorted'].astype(bool)].sort_values('overall_rank')
desc = q['description'].fillna('').str.replace(r'\s+', ' ', regex=True).str.slice(0, 160)
rows = list(zip(q['k'], q['name'], q['domain'].fillna(''), q['country'].fillna(''), q['industry'].fillna(''),
                q['sector'].map(lambda s: NAMES.index(s) + 1), desc))
idx = {}
for n in range(0, len(rows), N):
    f = f'{n // N + 1:04d}'; chunk = rows[n:n + N]
    json.dump([[j, *r[1:]] for j, r in enumerate(chunk)], open(f'{R}/wave16/seccheck/in_{f}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    idx[f] = [r[0] for r in chunk]
json.dump(idx, open(f'{R}/wave16/seccheck/index.json', 'w'), ensure_ascii=False)
print('queued', len(rows), 'files', len(idx))
