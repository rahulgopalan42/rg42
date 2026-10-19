# Queue the next research v2 batches from triage 'real' rows not yet queued.
# Order: triage fit desc, scale (large, mid, unknown), fin_proxy desc. Small and fit 0 are skipped.
# Usage: python -I wave16/queue2.py [max_rows]
import json, glob, sys, os
import pandas as pd

SP = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9

p = pd.read_pickle(f'{SP}/phase1.pkl').drop_duplicates('rd').set_index('rd')
tri = [r for f in sorted(glob.glob('wave16/triage/out_*.json')) for r in json.load(open(f))]
queued = {r['id'] for f in glob.glob('wave16/verify2/in_*.json') for r in json.load(open(f))}
last = max(int(os.path.basename(f)[3:7]) for f in glob.glob('wave16/verify2/in_*.json'))

SC = {'large': 0, 'mid': 1, 'unknown': 2}
rows = [r for r in tri if r['t'] == 'real' and r.get('scale') in SC and (r.get('fit') or 0) >= 1
        and r['id'] not in queued and r['id'] in p.index]
rows.sort(key=lambda r: (-r['fit'], SC[r['scale']], -p.at[r['id'], 'fin_proxy']))
rows = rows[:MAX]

out = []
for r in rows:
    x = p.loc[r['id']]
    out.append({'id': r['id'], 'company': x['name'], 'sector': x['sector'], 'country': x['country'],
                'type': x['type'], 'staff': x['size'], 'clay_revenue_band': (x['rev_estimate'] or 'none').replace('Clay band', 'Clay estimate'),
                'apollo_funding_100m': bool(x['funding_100m_apollo']),
                'parent_hint': r.get('parent') or x['parent_hint'] or '',
                'triage_note': f"real; fit {r['fit']}; scale {r['scale']}; {r.get('note', '')}"})
for i in range(0, len(out), 10):
    last += 1
    json.dump(out[i:i + 10], open(f'wave16/verify2/in_{last:04d}.json', 'w'), indent=0, ensure_ascii=False)
print(len(out), 'rows queued; last batch', last)
