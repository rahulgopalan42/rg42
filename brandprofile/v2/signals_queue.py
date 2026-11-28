"""Usage: signals_queue.py <rows per file> <research rows> <older-sheet rows> [start number]
Input files for the buying-signals pass (brief_signals.md): the strongest companies on capacity, fit and access whose news nobody has
read yet (signals_checked is not yes), from every batch and from the user's older sheet. Names already in an in_s*.jsonl are skipped."""
import glob, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build as B, older as O, score as S
from register import norm
per, n_res, n_old = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); start = int(sys.argv[4]) if len(sys.argv) > 4 else None
bd = os.path.join(H, 'batches', 'b03'); done = set()
for p in glob.glob(os.path.join(bd, 'in_s*.jsonl')) + glob.glob(os.path.join(bd, 'sig_*.jsonl')):
    for d in B.read_jsonl(p): done.add(norm(B.clean(d.get('name'))))
D = B.load(None); Q, W, I, tab = B.classify(D['recs'])
key = lambda d: -(d['A']['fin'] + d['A']['fit'] + d['A']['access'])
res = sorted([d for d in Q if B.clean(d.get('signals_checked')).lower() != 'yes' and norm(B.clean(d['name'])) not in done], key=key)[:n_res]
have = {norm(B.clean(d['name'])) for d in Q + W}
old = [O.record(v) for v in O.gap()]
for d in old: d['A'] = S.assess(d)
old = sorted([d for d in old if norm(d['name']) not in have and norm(d['name']) not in done], key=key)[:n_old]
rows = [{'name': B.clean(d['name']), 'website': B.clean(d.get('website')), 'hq_country': B.clean(d.get('hq_country')), 'sector': d['sector'], 'desc': B.clean(d.get('desc'))[:220]} for d in res + old]
# interleave so every file has both kinds and a spread of sectors
rows = [r for i in range(per) for r in rows[i::per]] if False else rows
print('candidates:', len(res), 'researched +', len(old), 'older sheet; weakest researched candidate scores', -key(res[-1]) if res else None)
if start is None: sys.exit(0)
for i in range(0, len(rows), per):
    p = os.path.join(bd, f'in_s{start + i // per:02d}.jsonl')
    with open(p, 'w', encoding='utf-8') as f:
        for r in rows[i:i + per]: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(os.path.basename(p), len(rows[i:i + per]), rows[i]['name'], '...')
