"""Step 1 of the build: sector for every listed company (classification files), its financial figures, the F1 link check
and the capacity verdict. Writes data/screen.json.gz and prints the count per sector.  Usage: screen.py"""
import glob, gzip, html, json, os, re, sys
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from sectors35 import SECTORS, ORDER
from qualify import financials, capacity
from f1links import f1_link
U = {c['sym']: c for c in json.load(gzip.open(os.path.join(H, 'data', 'universe.json.gz'), 'rt'))}
cls = {}
for f in sorted(glob.glob(os.path.join(H, 'classify', 'out_*.txt'))):
    for line in open(f):
        p = line.strip().split('|')
        if len(p) == 2 and p[0] in U: cls[p[0]] = p[1].strip()
out = []; cnt = defaultdict(Counter)
for sym, c in U.items():
    code = cls.get(sym, '')
    if code not in SECTORS: cnt['--'][code or 'unclassified'] += 1; continue
    if c['country'] in ('Russia',): cnt['--']['sanctioned market (Russia)'] += 1; continue
    f = financials(c); k = capacity(f, code)
    web = (c.get('sec') or {}).get('web') or (c.get('clay') or {}).get('domain') or ''
    link, src = f1_link(html.unescape(c['name']), web)
    st = 'f1' if link else 'insufficient' if k['ev'] == 'Insufficient' else 'strong' if k['ev'].startswith('Strong') else 'plausible'
    cnt[code][st] += 1
    out.append({'sym': sym, 'name': html.unescape(c['name']), 'country': c['country'], 'sector': code, 'status': st, 'f1': link, 'f1src': src, 'f': f, 'k': k})
json.dump(out, gzip.open(os.path.join(H, 'data', 'screen.json.gz'), 'wt'), ensure_ascii=False)
print('not in a sector:', dict(cnt['--']))
tot = Counter()
for code in ORDER:
    c = cnt[code]; tot.update(c)
    print(f"{code} {SECTORS[code]['name'][:46]:46s} classified {sum(c.values()):5d} | F1 link {c['f1']:3d} | insufficient {c['insufficient']:4d} | strong {c['strong']:4d} | plausible {c['plausible']:4d}")
print('TOTAL', dict(tot))
