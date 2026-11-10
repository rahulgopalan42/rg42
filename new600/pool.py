"""All Crunchbase pulls for the new-brands task, merged by organisation uuid, each marked with why it is excluded
(already in a list / sheet: website, name, name variant) or '' if new. Writes new600/pool.json.
Sources: cb/p1..p5.json (funding >= USD 200M with a round since 2025; PrivCo valuation >= 1B), cb/sample/*.json
(funding USD 150-200M since 2025; 100-150M sample), cb/rounds/*.json (rounds valued >= USD 1B that raised < 150M)."""
import json, os, sys, glob, bisect
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, strict, regdom
ex = json.load(open(os.path.join(H, 'excluded.json')))
NS = set(ex['names']); DS = set(ex['domains']); NL = sorted(n for n in NS if len(n) >= 5)
GENERIC_DOM = {'linkedin.com', 'facebook.com', 'google.com', 'github.io', 'wixsite.com', 'medium.com', 'notion.site', 'linktr.ee'}
orgs = {}
def add(uuid, name, permalink, **kw):
    c = orgs.setdefault(uuid, {'uuid': uuid, 'name': name, 'permalink': permalink, 'web': '', 'funding': None, 'ipo': '',
                               'privco_val': None, 'round_val': None, 'round_val_date': '', 'src': []})
    for k, v in kw.items():
        if k == 'src': c['src'].append(v)
        elif k == 'round_val':
            if v and v > (c['round_val'] or 0): c['round_val'], c['round_val_date'] = v, kw.get('round_val_date', '')
        elif k == 'round_val_date': pass
        elif v not in (None, ''): c[k] = v
for i in range(1, 6):
    for r in json.load(open(os.path.join(H, 'cb', f'p{i}.json'))):
        add(r[0], r[1], r[2], web=r[3] or '', funding=r[4], ipo=r[5], privco_val=r[6] if len(r) > 6 else None, src=f'p{i}')
for f in sorted(glob.glob(os.path.join(H, 'cb', 'sample', '*.json'))):
    for e in json.load(open(f))['entities']:
        p = e['properties']; idf = p['identifier']
        add(e['uuid'], idf['value'], idf.get('permalink', ''), web=p.get('website_url') or '',
            funding=(p.get('funding_total') or {}).get('value_usd'), src=os.path.basename(f).rsplit('_p', 1)[0])
for f in sorted(glob.glob(os.path.join(H, 'cb', 'rounds', '*.json'))):
    for e in json.load(open(f))['entities']:
        p = e['properties']; o = p['funded_organization_identifier']
        add(o['uuid'], o['value'], o.get('permalink', ''), round_val=(p.get('post_money_valuation') or {}).get('value_usd'),
            round_val_date=p.get('announced_on', ''), src='rounds')
def why(c):
    d = regdom(c['web'])
    if d and d in DS and d not in GENERIC_DOM: return 'website'
    for k in {strict(c['name']), loose(c['name'])}:
        if len(k) < 2: continue
        if k in NS: return 'name'
        if len(k) >= 6:
            i = bisect.bisect_left(NL, k)
            if i < len(NL) and NL[i].startswith(k) and len(NL[i]) - len(k) <= 4: return 'name variant'
            for j in range(len(k) - 1, 5, -1):
                if k[:j] in NS and len(k) - j <= 3: return 'name variant'
    return ''
for c in orgs.values(): c['src'] = sorted(set(c['src'])); c['excluded'] = why(c)
json.dump(list(orgs.values()), open(os.path.join(H, 'pool.json'), 'w'))
from collections import Counter
print('organisations', len(orgs), Counter('excluded' if c['excluded'] else 'NEW' for c in orgs.values()))
print('new by source', Counter(s for c in orgs.values() if not c['excluded'] for s in c['src']))
