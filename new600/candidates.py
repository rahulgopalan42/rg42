"""Crunchbase pulls (new600/cb/p1..p5.json) minus every brand already in the project (new600/excluded.json).
Writes new600/candidates.json with the reason each pulled company was kept or dropped."""
import json, os, sys, re, bisect
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, strict, regdom
ex = json.load(open(os.path.join(H, 'excluded.json')))
NS = set(ex['names']); DS = set(ex['domains']); NL = sorted(n for n in NS if len(n) >= 5)
rows = {}
for i in range(1, 6):
    for r in json.load(open(os.path.join(H, 'cb', f'p{i}.json'))):
        rows.setdefault(r[0], {'uuid': r[0], 'name': r[1], 'permalink': r[2], 'web': r[3] or '', 'funding': r[4],
                               'ipo': r[5], 'val': r[6] if len(r) > 6 else None, 'pull': i})
def why(c):
    d = regdom(c['web'])
    if d and d in DS and d not in ('linkedin.com', 'facebook.com', 'google.com', 'github.io', 'wixsite.com'): return 'website'
    for k in {strict(c['name']), loose(c['name'])}:
        if len(k) < 2: continue
        if k in NS: return 'name'
        if len(k) >= 6:                       # cut-short OCR reads / name variants: an excluded name of 6+ chars that this one starts with, or vice versa
            i = bisect.bisect_left(NL, k)
            if i < len(NL) and NL[i].startswith(k) and len(NL[i]) - len(k) <= 4: return 'name variant'
            for j in range(len(k) - 1, 5, -1):
                if k[:j] in NS and len(k) - j <= 3: return 'name variant'
    return ''
out = []
for c in rows.values():
    c['excluded'] = why(c); out.append(c)
json.dump(out, open(os.path.join(H, 'candidates.json'), 'w'))
from collections import Counter
print('pulled', len(out), Counter(c['excluded'] or 'NEW' for c in out))
print('new by pull', Counter(c['pull'] for c in out if not c['excluded']))
print('new by ipo', Counter(c['ipo'] for c in out if not c['excluded']))
