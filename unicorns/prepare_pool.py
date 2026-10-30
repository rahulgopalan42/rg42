"""Clean the Apollo / Clay USD 200M+ pools into screen chunks: drop names already in the research set (all.pkl),
obvious non-companies (funds, banks' investment arms, universities, government), and duplicates."""
import json, glob, os, re, sys, math
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(H), 'brands200')); from match import loose, regdom
u = pd.read_pickle(f'{H}/all.pkl')
have_n = set(u['brand'].map(loose)) | set(u['legal_name'].map(loose)); have_d = {d for L in u['domains'] for d in (L if isinstance(L, list) else [])}
NOISE = re.compile(r'\b(capital|ventures?|partners|fund|funds|investments?|investors|holdings? ltd|equity|private equity|asset management|acquisition corp|spac|university|college|school of|institute|ministry|government|council|agency|foundation|association|bank of|federal|national bank|news|magazine|times|journal|press|media group|consulting group)\b', re.I)
rows, seen = [], set()
for f in sorted(glob.glob(f'{H}/pool2/*.json')) + [f'{H}/pool/apollo.json']:
    for r in json.load(open(f)):
        name, dom = (r[1], r[2]) if len(r) >= 3 else (r[0], '')
        k = loose(name); d = regdom(dom)
        if not k or k in seen or (d and d in seen): continue
        seen.add(k); seen.add(d) if d else None
        if k in have_n or (d and d in have_d): continue
        if NOISE.search(name or ''): continue
        rows.append([name, d, os.path.basename(f)])
for r in json.load(open(f'{H}/pool/clay.json')):
    k = loose(r[0]); d = regdom(r[1])
    if not k or k in seen or k in have_n or (d and d in have_d) or NOISE.search(r[0] or ''): continue
    seen.add(k); rows.append([r[0], d, 'clay:' + (r[2] or '') + '|' + (r[3] or '')])
os.makedirs(f'{H}/pool2/screen_in', exist_ok=True)
for f in glob.glob(f'{H}/pool2/screen_in/*.json'): os.remove(f)
N = 350
for i in range(0, len(rows), N): json.dump(rows[i:i + N], open(f'{H}/pool2/screen_in/s{i // N + 1:02d}.json', 'w'))
print('pool names to screen', len(rows), 'chunks', math.ceil(len(rows) / N))
