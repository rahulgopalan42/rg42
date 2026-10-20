"""Slice unscreened Wave 15 candidates into screening batches, best pre-score first.
Usage: python3 -I wave15/screen_prep.py [batch_size]"""
import json, glob, os, sys
W = '/home/user/rg42/wave15'
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
cands = json.load(open(f'{W}/w15_candidates.json'))
done = set()
for f in glob.glob(f'{W}/screen/in_*.json'):
    for r in json.load(open(f)): done.add(r['id'])
todo = [r for r in cands if (r['domain'] or r['key']) not in done]
todo.sort(key=lambda r: -r['score'])
start = len(glob.glob(f'{W}/screen/in_*.json'))
for i in range(0, len(todo), N):
    chunk = [dict(id=r['domain'] or r['key'], company=r['name'], website=r['domain'], country=r['country'],
                  database_industry=r['industry'], db_revenue_band=r['rev_band'], db_staff=r['emp'],
                  raised_100m_plus=r['funded'], owner_hint=r['owner'], sector_guess=r['sector'])
             for r in todo[i:i + N]]
    json.dump(chunk, open(f'{W}/screen/in_{start + i // N + 1:04d}.json', 'w'), indent=0, ensure_ascii=False)
print('new batches', (len(todo) + N - 1) // N, 'brands', len(todo))
