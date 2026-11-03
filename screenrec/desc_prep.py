"""Split the companies of the screen-recording workbook into batches for the description writers, in outreach order
(ranks 1-2,000 and the current-F1 tab first). Each row: [id, brand, hq_country, hq_location, crunchbase_industries,
crunchbase_short_description, total_funding_as_shown, last_funding_date, listed].
Usage: desc_prep.py <ocr dir with build.json> [batch size]  -> screenrec/desc/in_NNN.json (skips ids already described)"""
import json, os, sys, glob
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200'))
from match import loose

def cid(c): return f"{loose(c['brand']) or c['brand'].lower()}|{c['country']}"

if __name__ == '__main__':
    d = json.load(open(os.path.join(sys.argv[1], 'build.json'))); N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    D = os.path.join(H, 'desc'); os.makedirs(D, exist_ok=True)
    done = set()
    for f in glob.glob(os.path.join(D, 'out_*.json')):
        try: done |= {r[0] for r in json.load(open(f))}
        except Exception: pass
    order = d['main'][:2000] + d['f1'] + d['main'][2000:]
    rows, seen = [], set()
    for c in order:
        k = cid(c)
        if k in done or k in seen: continue
        seen.add(k)
        rows.append([k, c['brand'], c['country'], c['hq'], c['subsector'], c['desc'], c['total'], c['date'], bool(c['listed'])])
    start = len(glob.glob(os.path.join(D, 'in_*.json')))
    for i in range(0, len(rows), N):
        json.dump(rows[i:i + N], open(os.path.join(D, f'in_{start + i // N + 1:03d}.json'), 'w'), ensure_ascii=False)
    print(len(rows), 'companies ->', -(-len(rows) // N), 'batches from', f'in_{start + 1:03d}')
