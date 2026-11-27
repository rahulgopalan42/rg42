"""Usage: check.py "Company name" ["Company name | website.com" ...]
Duplicate and eligibility check for the revised non-public methodology. Only the user's master spreadsheet counts as a duplicate.
IN MASTER  = already on the master spreadsheet: leave it out.  ALREADY DELIVERED = sent in an earlier batch under this methodology: leave it out.
F1 PARTNER = the brand holds a current Formula 1 deal: leave it out.
LISTED?    = the name matches a listed company: leave it out if it is that company; keep it if it is a different, unlisted company.
POSSIBLE   = close to a master name: read it; same company, alias or old name = leave it out.
NEW        = not in the master: eligible (a note may say it is on the user's older 48-tab sheet; that is allowed)."""
import bisect, gzip, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from register import norm, loose, dom, aliases
J = json.load(gzip.open(os.path.join(H, 'register.json.gz'), 'rt', encoding='utf-8')); N = J['names']; D = J['domains']; V = J.get('delivered') or {}; VD = J.get('delivered_domains') or {}
KEYS = sorted(k for k, v in N.items() if v[2] in ('dup', 'f1'))
VKEYS = sorted(set(V) - set(KEYS))
def near(q, delivered=True):
    if len(q) < 4: return []
    i = bisect.bisect_left(KEYS, q); out = []
    while i < len(KEYS) and KEYS[i].startswith(q) and len(out) < 4:
        if KEYS[i] != q and len(KEYS[i]) <= len(q) + 16: out.append(N[KEYS[i]])
        i += 1
    i = bisect.bisect_left(VKEYS, q)
    while delivered and i < len(VKEYS) and VKEYS[i].startswith(q) and len(out) < 4:
        if VKEYS[i] != q and len(VKEYS[i]) <= len(q) + 16 and V[VKEYS[i]] not in out: out.append(V[VKEYS[i]])
        i += 1
    for n in range(len(q) - 1, 4, -1):
        if q[:n] in N and N[q[:n]][2] in ('dup', 'f1') and len(out) < 5: out.append(N[q[:n]]); break
    return out
def lookup(arg, batch=None):
    # batch: when a batch is being rebuilt, its own delivered names do not count against it
    """(status, display name, source). status: dup | f1 | listed | possible | new"""
    name, _, site = arg.partition('|'); name = name.strip(); d = dom(site); hits = []
    for a in aliases(name):
        for k in (norm(a), loose(a)):
            if k in N: hits.append(N[k])
    if d and d in D: hits.append(D[d])
    h = next((x for x in hits if x[2] == 'dup'), None)
    if h: return 'dup', h[0], h[1], hits
    own = 'delivered under the revised methodology: ' + str(batch); dv = []
    for a in aliases(name):
        for k in (norm(a), loose(a)):
            if k in V and V[k][1] != own: dv.append(V[k])
    if d and d in VD and VD[d][1] != own: dv.append(VD[d])
    if dv: return 'dup', dv[0][0], dv[0][1], hits + dv
    for kind in ('f1', 'listed'):
        h = next((x for x in hits if x[2] == kind), None)
        if h: return kind, h[0], h[1], hits
    c = []
    for a in aliases(name):
        for v in near(loose(a), delivered=batch is None):
            if v not in c: c.append(v)
    return ('possible' if c else 'new'), '; '.join(f'{v[0]} [{v[1]}]' for v in c[:4]), '', hits
def check(arg):
    name = arg.partition('|')[0].strip(); st, disp, src, hits = lookup(arg)
    note = next((x for x in hits if x[2] in ('info', 'f1owner')), None)
    tail = (f' (note: {note[1]}' + ('; allowed' if note[2] == 'info' else '; allowed as a separate brand, record the possible conflict') + ')') if note else ''
    if st == 'dup': return f'{name}: ' + ('ALREADY DELIVERED' if src.startswith('delivered') else 'IN MASTER') + f' - {src} (as {disp})'
    if st == 'f1': return f'{name}: F1 PARTNER - {src} (as {disp})'
    if st == 'listed': return f'{name}: LISTED? - matches the listed company {disp}; leave it out if it is that company' + tail
    if st == 'possible': return f'{name}: POSSIBLE - {disp}' + tail
    return f'{name}: NEW' + tail
if __name__ == '__main__':
    for a in sys.argv[1:]: print(check(a))
