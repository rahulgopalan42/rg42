"""Extra discovery source: listed companies from the public market-cap listing (scratchpad/mcap, fetched 19 Oct 2026),
market cap >= USD 1B, that are in NEITHER the consolidated parents NOR any existing dataset. Writes score_in chunks.
Usage: mcap_candidates.py <first_chunk_number> [chunk_size]"""
import glob, html, json, math, re, sys
import pandas as pd
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad'
sys.path.insert(0, f'{R}/wave16')
from dedupe_v2 import strict
first = int(sys.argv[1]); size = int(sys.argv[2]) if len(sys.argv) > 2 else 160
rows = []
for f in glob.glob(f'{S}/mcap/p*.html'):
    h = open(f, errors='ignore').read()
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S):
        nm = re.search(r'company-name">([^<]*)', tr)
        if not nm: continue
        tds = [re.sub('<[^>]+>', '', t).strip() for t in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        name = html.unescape(nm.group(1).strip())
        code = tds[2][len(nm.group(1).strip()):].strip() if len(tds) > 2 else ''
        mc = next((t for t in tds if re.match(r'^\$[\d.]+ ?[TBM]$', t)), '')
        if not mc: continue
        v = float(mc[1:-1]) * {'T': 1000, 'B': 1, 'M': 0.001}[mc[-1]]
        rows.append({'name': name, 'code': code, 'val_bn': round(v, 1), 'country': tds[-1].split()[-1] if tds else ''})
mc = pd.DataFrame(rows).drop_duplicates('name'); mc = mc[mc['val_bn'] >= 1]
base = lambda n: strict(re.sub(r'\s*\(.*?\)\s*', ' ', n))
mc['sn'] = mc['name'].map(strict); mc['bn'] = mc['name'].map(base)
# names already covered: consolidated parents (with aliases, subs, children) and every existing dataset
par = pd.read_pickle(f'{S}/parents/parents.pkl')
known = set()
for col in ('names', 'subs', 'children'):
    for lst in par[col]: known |= {strict(x) for x in (lst or [])}
known |= set(par['sn'])
old = pd.read_pickle(f'{S}/w16/old_v2.pkl'); clay = pd.read_pickle(f'{S}/w16/new_all.pkl')
known |= set(old['name'].map(strict)) | set(clay['name'].map(strict))
known.discard('')
def covered(r): return (len(r.sn) >= 2 and r.sn in known) or (len(r.bn) >= 2 and r.bn in known)
mc['covered'] = [covered(r) for r in mc.itertuples()]
cand = mc[~mc['covered']].sort_values('val_bn', ascending=False)
print('listed companies >= USD 1B', len(mc), '| already covered', int(mc['covered'].sum()), '| new candidates', len(cand))
print(cand[['name', 'code', 'val_bn', 'country']].head(15).to_string())
out = [[r.name, '', r.country, r.code, '', f'listed company; market cap USD {r.val_bn:,.1f}B (verified 2026-10-19)', '', [], True] for r in cand.itertuples()]
n = math.ceil(len(out) / size)
for i in range(n):
    json.dump(out[i * size:(i + 1) * size], open(f'{R}/parents/score_in/chunk_{first + i:02d}.json', 'w'), ensure_ascii=False)
cand[['name', 'code', 'val_bn', 'country']].to_pickle(f'{S}/parents/mcap_cand.pkl')
print('chunks', first, '-', first + n - 1)
