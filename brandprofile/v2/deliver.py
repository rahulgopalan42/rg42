"""Usage: deliver.py <batch> <workbook.xlsx>
Rebuilds the register, writes the workbook, then records what was delivered:
v2/delivered/<batch>.json (ranked and watchlist names; these count as duplicates from now on) and
v2/batches/<batch>/to_assess.json (names read off a ranking only; not delivered as prospects, so a later batch can assess them)."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import register
register.build()
import build as B, write as Wr
batch, path = sys.argv[1], sys.argv[2]
D = B.load(batch); Q, W, I, tab = B.classify(D['recs']); X = B.classify.discovered
extra = None
if batch != 'b01':
    import batch2
    extra = batch2.extras(D, Q, W, I, X, batch)
Wr.write(D, Q, W, I, tab, path, X, extra)
mine = lambda L: [d for d in L if d['_batch'] == batch]
os.makedirs(os.path.join(H, 'delivered'), exist_ok=True)
json.dump([[B.clean(d['name']), B.clean(d.get('website'))] for d in mine(Q + W)], open(os.path.join(H, 'delivered', batch + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump([[B.clean(d['name']), B.clean(d.get('website')), d['sector']] for d in mine(X)], open(os.path.join(H, 'batches', batch, 'to_assess.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
register.build()
print('ranked', len(Q), '| watchlist', len(W), '| to assess', len(X), '| insufficient', len(I), '| removed at the build', len(D['excluded']), [e[:2] for e in D['excluded']][:12])
