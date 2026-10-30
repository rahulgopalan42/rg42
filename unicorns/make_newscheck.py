"""Build newscheck_in chunks: every candidate (main, unverified, F1 set-aside, near miss) with its claims + headlines."""
import json, os, re, glob, math, sys
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H); from news import safe
u = pd.read_pickle(f'{H}/all.pkl'); c = u[u['bucket'].isin(['main', 'unverified', 'f1', 'near'])]
os.makedirs(f'{H}/newscheck_in', exist_ok=True); os.makedirs(f'{H}/newscheck_out', exist_ok=True)
done = set()
for f in glob.glob(f'{H}/newscheck_in/*.json'):
    done |= {x['key'] for x in json.load(open(f))}
items, missing = [], 0
for r in c.itertuples():
    if r.brand in done: continue
    f = f'{H}/news/{safe(r.brand)}.json'
    if not os.path.exists(f): missing += 1; continue
    n = json.load(open(f))
    claims = f"private: {r.ev_private} | valuation: {r.ev_val} | funding: {r.ev_fund} | research status: {r.agent_status or r.status}; latest round: {r.latest_round}"
    trim = lambda L: [[t[0][:140], t[1], t[2][:30]] for t in L[:10]]
    items.append({'key': r.brand, 'brand': r.brand, 'domain': r.domain, 'country': r.hq_country, 'claims': claims[:600],
                  'funding_news': trim(n['funding_news']), 'status_news': trim(n['status_news'])})
start = len(glob.glob(f'{H}/newscheck_in/*.json')) + 1; N = 45
for i in range(0, len(items), N): json.dump(items[i:i + N], open(f'{H}/newscheck_in/n{start + i // N:03d}.json', 'w'))
print('items', len(items), 'chunks', math.ceil(len(items) / N), 'from', start, '| still without headlines', missing)
