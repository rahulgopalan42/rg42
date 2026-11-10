"""Organisations from Crunchbase funding rounds valued at USD 1B+ (new600/cb/rounds/*.json) that are not already in the
project (new600/excluded.json, name match incl. cut-short/variant names). Prints counts; writes new600/rounds_new.json."""
import json, os, sys, glob, bisect
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, strict
ex = json.load(open(os.path.join(H, 'excluded.json'))); NS = set(ex['names']); NL = sorted(n for n in NS if len(n) >= 5)
orgs = {}
for f in sorted(glob.glob(os.path.join(H, 'cb', 'rounds', '*.json'))):
    for e in json.load(open(f))['entities']:
        p = e['properties']; o = p['funded_organization_identifier']; v = (p.get('post_money_valuation') or {}).get('value_usd') or 0
        c = orgs.setdefault(o['uuid'], {'uuid': o['uuid'], 'name': o['value'], 'permalink': o['permalink'], 'val': 0, 'val_date': '', 'rounds': 0})
        c['rounds'] += 1
        if v > c['val']: c['val'], c['val_date'] = v, p.get('announced_on', '')
def known(n):
    for k in {strict(n), loose(n)}:
        if len(k) < 2: continue
        if k in NS: return True
        if len(k) >= 6:
            i = bisect.bisect_left(NL, k)
            if i < len(NL) and NL[i].startswith(k) and len(NL[i]) - len(k) <= 4: return True
            for j in range(len(k) - 1, 5, -1):
                if k[:j] in NS and len(k) - j <= 3: return True
    return False
new = [c for c in orgs.values() if not known(c['name'])]
json.dump(sorted(new, key=lambda c: -c['val']), open(os.path.join(H, 'rounds_new.json'), 'w'), indent=0)
print('orgs', len(orgs), 'new', len(new))
