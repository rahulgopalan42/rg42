"""Usage: queue.py <batch> <rows per file> <max files> [start number]
Builds the research queue from the discovery register: names found by any stream that are new and that nobody has researched,
largest first, and writes them as input files v2/batches/<batch>/in_qNN.jsonl. Names already queued (in any in_q*.jsonl) are skipped."""
import glob, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build as B, batch2 as X2
from register import norm
batch = sys.argv[1]; per = int(sys.argv[2]); maxf = int(sys.argv[3]); start = int(sys.argv[4]) if len(sys.argv) > 4 else None
D = B.load(batch); Q, W, I, tab = B.classify(D['recs']); X = B.classify.discovered
R, raw = X2.register(D, Q, W, I, X, batch)
bd = os.path.join(H, 'batches', batch); queued = set()
for p in glob.glob(os.path.join(bd, 'in_q*.jsonl')):
    for d in B.read_jsonl(p): queued.add(norm(d['name']))
disc = {}
for d in D['disc']: disc.setdefault(norm(B.clean(d['name'])), d)
THR = {'revenue': 150, 'equity_funding': 100, 'valuation': 1000, 'aum': 5000, 'ebitda': 20, 'arr': 50, 'transaction_value': 1000}
rows = []
for k, r in R.items():
    if r['stage'] != 'New: not yet researched' or norm(r['name']) in queued: continue
    d = disc.get(k) or disc.get(norm(r['name'])) or {}; c = r.get('clay') or {}
    try: usd = float(d.get('usd_m')) if d.get('usd_m') not in (None, '') else None
    except Exception: usd = None
    metric = B.clean(d.get('metric')).lower() or ('revenue' if c else '')
    lo = X2.REV.get(B.clean(c.get('annual_revenue')))
    size = (usd / THR.get(metric, 150) if usd else 0) or ((lo or 0) / 150 * 0.8)        # how far above the threshold; a Clay bracket counts a little less than a stated figure
    has_src = bool(B.clean(d.get('source'))) or bool(c)
    if usd is not None and metric in THR and usd < THR[metric] * 0.5 and not lo: continue # clearly below every band
    rows.append((0 if size >= 1 else 1 if has_src else 2, -size, r['name'].lower(), re.sub(r'\d+', '', r['cluster'].split('_')[0]) + r['cluster'] if not r['cluster'].startswith('clay') else 'clay',
                 {'name': r['name'], 'website': r['site'], 'hq_country': r['country'], 'sector': r['sector'], 'subsector': B.clean(d.get('subsector')) or B.clean(c.get('industry')),
                  'figure': B.clean(d.get('figure')) or r['figure'], 'metric': metric, 'usd_m': usd if usd else lo, 'source': B.clean(d.get('source')) or B.clean(c.get('linkedin')) or 'Clay company search',
                  'via': r['via'], 'employee_count': c.get('employee_count'), 'clay_revenue': B.clean(c.get('annual_revenue')), 'desc': B.clean(c.get('desc'))[:300]}))
rows.sort(key=lambda t: t[:3])
print('queue size', len(rows), '| with a figure at or above a threshold', sum(1 for t in rows if t[0] == 0), '| already queued', len(queued))
# round-robin across the discovery streams, so every sector and source moves forward together and the big country rankings do not crowd out the rest
from collections import defaultdict, deque
G = defaultdict(deque)
for t in rows: G[t[3]].append(t)
print('by stream:', {k: len(v) for k, v in sorted(G.items())})
W8 = {'clay': 3, 'cc01_europe': 2, 'cc02_world': 2}          # larger streams get more turns per round
rows = []
while any(G.values()):
    for k in sorted(G):
        for _ in range(W8.get(k, 1)):
            if G[k]: rows.append(G[k].popleft())
if start is None: sys.exit(0)
n = 0
for i in range(maxf):
    part = [t[4] for t in rows[i * per:(i + 1) * per]]
    if not part: break
    p = os.path.join(bd, f'in_q{start + i:02d}.jsonl')
    with open(p, 'w', encoding='utf-8') as f:
        for d in part: f.write(json.dumps(d, ensure_ascii=False) + '\n')
    n += len(part); print(os.path.basename(p), len(part), part[0]['name'], '...', part[-1]['name'])
print('written', n, '| left in the queue', len(rows) - n)
