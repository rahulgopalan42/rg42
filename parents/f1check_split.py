"""Write parents/f1check_in/chunk_NNN.json (800 rows each) for every row that can appear on the master, overlaps and
Drive CSV tabs: ranked parents (overlap_cat A/B) from parents.pkl, plus the Drive CSV brands. Rows: [key, name, domain,
hq_country, sector, note]. Drive brands use the key 'drive:<name>'."""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import inputs
from sectors_v3 import NAMES
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.environ.get('F1_SCRATCH', '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/parents')
par = pd.read_pickle(f'{P}/parents.pkl')
s = lambda x: '' if x is None or (isinstance(x, float) and x != x) else str(x)
sec = lambda n: NAMES[int(n) - 1] if s(n) not in ('', 'nan') and 1 <= int(float(n)) <= len(NAMES) else ''
rows = [[r['key'], s(r['name']), s(r['domain']), s(r['hq_country']), sec(r['sector']), s(r['f1'])]
        for _, r in par[par['overlap_cat'].isin(['A', 'B'])].iterrows()]
w16 = inputs.wave16_ranking()
crit = w16['criterion'].fillna('')
w16 = w16[(w16['funding_100m_apollo'] == True) | crit.str.contains('Valuation|Funding', regex=True)]      # same filter as the Drive CSV tab
rows += [['drive:' + s(r['name']), s(r['name']), s(r['domain']), s(r['country']), s(r['sector']), s(r['f1_deal'])] for _, r in w16.iterrows()]
os.makedirs(f'{R}/parents/f1check_in', exist_ok=True); os.makedirs(f'{R}/parents/f1check_out', exist_ok=True)
for i in range(0, len(rows), 800):
    json.dump(rows[i:i + 500], open(f'{R}/parents/f1check_in/chunk_{i // 800 + 1:03d}.json', 'w'), ensure_ascii=False)
print(len(rows), 'rows ->', (len(rows) + 799) // 800, 'chunks')
