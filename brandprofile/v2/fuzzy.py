"""Usage: fuzzy.py <batch>
Second duplicate pass for names the exact check cannot see: the same company under a longer or shorter name
(for example "Storck" against "August Storck", "Robert Bosch GmbH" against "Bosch"). Prints candidate pairs for review."""
import gzip, json, os, re, sys, unicodedata
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build as B
GENERIC = set('group groupe grupo gruppo gruppe holding holdings company companies co corp corporation inc ltd limited llc plc gmbh ag se sa sas spa srl bv nv ab as oy kg international global worldwide the and of de la le el du des und y e industries industry enterprises partners capital services service solutions systems technologies technology bank banco banque foods food energy energia motors motor auto automotive insurance media entertainment sports sport retail stores store markets market hotels hotel resorts airlines airways air pharma pharmaceuticals health healthcare care medical construction engineering consulting management investment investments financial finance association national american united general first new china india australia europe european asia pacific america north south east west usa uk'.split())
def toks(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower()
    return [t for t in re.findall(r'[a-z0-9]+', n) if t not in GENERIC and len(t) > 1]
def run(batch):
    M = json.load(gzip.open(os.path.join(H, 'master_names.json.gz'), 'rt', encoding='utf-8')); pool = [(x[0], x[1]) for x in M]
    for p in sorted(os.listdir(os.path.join(H, 'delivered'))):
        if p[:-5] != batch: pool += [(x[0], 'delivered in ' + p[:-5]) for x in json.load(open(os.path.join(H, 'delivered', p), encoding='utf-8'))]
    idx = defaultdict(list); freq = Counter()
    for nm, src in pool:
        T = set(toks(nm))
        for t in T: idx[t].append((nm, src, T)); freq[t] += 1
    D = B.load(batch); Q, W, I, tab = B.classify(D['recs']); out = []
    for d in Q + W:
        nm = B.clean(d['name']); T = set(toks(nm))
        if not T: continue
        seen = set()
        for t in T:
            if freq[t] > 6 or (len(t) < 4 and not (len(T) == 1 and len(t) == 3)): continue
            for mn, src, MT in idx.get(t, []):
                if mn in seen: continue
                if (T <= MT or MT <= T) and re.sub(r'[^a-z0-9]', '', mn.lower()) != re.sub(r'[^a-z0-9]', '', nm.lower()):
                    seen.add(mn); out.append((nm, mn, src, B.clean(d.get('hq_country')), d['sector'], d['_cluster']))
    return out
if __name__ == '__main__':
    out = run(sys.argv[1]); print(len(out), 'candidate pairs')
    for r in sorted(out): print(' | '.join(r))
