"""Queue stage-2 (full) verification batches: Yes + Stretch survivors not yet queued, best first.
Usage: python3 -I wave15/verify_prep.py [batch_size]   (run screen_merge.py first)"""
import json, glob, sys
W = '/home/user/rg42/wave15'
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
kept = json.load(open(f'{W}/screen_kept.json'))
queued = set()
for f in glob.glob(f'{W}/verify/in_*.json'):
    queued |= {r['id'] for r in json.load(open(f))}
def pr(r):
    try: fit = int(r.get('fit') or 0)
    except (TypeError, ValueError): fit = 0
    return {'Yes': 60 + 8 * fit, 'Stretch': 40 + 6 * fit}.get(r.get('verdict_guess'), 0)
todo = [r for r in kept if r.get('verdict_guess') in ('Yes', 'Stretch') and r['id'] not in queued]
todo.sort(key=lambda r: -pr(r))
keys = ['id', 'name', 'website', 'country', 'scale_route', 'scale_evidence', 'staff_est', 'parent', 'f1_tie',
        'sector', 'fit', 'verdict_guess', 'note']
start = len(glob.glob(f'{W}/verify/in_*.json'))
for i in range(0, len(todo), N):
    chunk = [{k: r.get(k, '') for k in keys} | {'company': r['name']} for r in todo[i:i + N]]
    json.dump(chunk, open(f'{W}/verify/in_{start + i // N + 1:04d}.json', 'w'), ensure_ascii=False, indent=0)
print('queued', len(todo), 'batches', (len(todo) + N - 1) // N, 'from', start + 1)
