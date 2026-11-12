"""Which of the 17 priority sectors are already covered by the brand lists delivered so far.
A brand belongs to a sector if its category fields or description match the sector's patterns (sectors.py), or it is
one of the sector's known leading names. Each brand carries the best level it reached on any list:
  good     = on a researched prospect list (verdict Yes / Stretch, verified ranking, curated sector / unicorn / parent lists)
  rec      = only on the screen-recordings list (Crunchbase, USD 150M+ funding)
  low      = only on database-derived lists nobody researched (Wave 16 preliminary ranking, Wave 15 'Low-value', raw sweeps)
  rejected = only ever on a dropped / rejected tab
Usage: classify.py [sector id ...]   prints counts and samples for checking the patterns."""
import bisect, gzip, json, os, random, re, sys, unicodedata
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, H); sys.path.insert(0, os.path.join(R, 'brands200'))
from sectors import S, ASIA
from match import loose, strict
sys.path.insert(0, os.path.join(R, 'new600'))
from excl import why as excl_why
ORDER = {'good': 3, 'rec': 2, 'low': 1, 'rejected': 0, 'f1': -1, 'index': -2, 'none': -3}
GENERIC_SEED = set('nomad ada magic adept friend eve air lift front smart digit agility hello future centr sweat keep lean zig hop rain plus play arc due iron tia cove done muse hatch free sky hello kind sunday plus play rain bolt via found manual future mirror tempo stable codex sphere iron canvas weave clone foundation humanoid wing merlin smart tank peak line chang spot apex kepler leon paul quick presto check beat hala ninja nana rabbit alto three bell spark globe true salt digi personal lion cooper seed needed stake coral shuffle blaze zeal meta nothing shark polar ring nest marshall honor sigma away july antler root hippo alan ethos coalition discovery progressive nationwide travelers writer magic factory friend chai speak gamma clay sierra harvey glean runway dust switch aligned modal bridge mesh noble agora conduit sling lemon infinite meow dakota squads altitude usual maple levels lumen calm clue mira forth forward timeline blueprint muse hatch ladder done cove hers rory alloy keep cura tensor beep coco embark turing gama electra blade regent plana boom manna volant matic cobot formic mimic skild agility sanctuary hexagon totum hiber xona mangata enterprise budget dollar national firefly thrifty avis lime tier bird dott hop revel curb little zig sea orion lotte peak smart tank genesis fila discovery line kakao naver coupang nexon orange claro movistar vivo tigo entel personal plus play free salt sunrise three telia elisa ais globe smart true vi figure circle rain stable arc sky frax tron sui ice mural due sphere iron infinite lion kao seb ems paul leon quick coco h pi'.split())
RECF = re.compile(r'SCREEN-RECORDINGS', re.I); RAWF = re.compile(r'Wave15-Database-Sweep-UNCHECKED|FinServ-Gap-List', re.I)
F1_TAB = re.compile(r'f1 sponsor|already f1|current f1|f1 partner|on grid|f1 ties|f1 deal', re.I)
DROP_TAB = re.compile(r'drop|exclud|reject|removed|not qualif|fail|left out|out of scope|duplicate|parked|deferred|defunct|below|not found|no longer', re.I)
LOW_TAB = re.compile(r'manual review|leftover|pending|unchecked|to check|unverified|preliminary|backlog|needs? (?:check|review)|database|sweep|all records|raw', re.I)
NEG_V = re.compile(r'^(no\b|none|drop|reject|fail|exclud)', re.I)
LOW_V = re.compile(r'low-value|preliminary|very low|pre-sort|database only|not verified|needs web check|unverified', re.I)
FILES = []
# combined sector labels that would pull a whole neighbouring sector in (every bank matching 'insurance', ...)
COMBINED = re.compile(r'banking, insurance & finserv|banking & insurance|ai cloud & data|travel & hospitality|health & wellness|iot & connectivity|trading & crypto|automation & robotics|telecom & space|consumer & lifestyle|tech media & gaming|mobility & automotive', re.I)
def load():
    d = json.load(gzip.open(os.path.join(H, 'brands.json.gz'), 'rt')); FILES[:] = d['files']
    for c in d['brands']:
        best = None; f1 = False; lv = []
        for fi, tab, v, q in c['on']:
            f = FILES[fi]
            if F1_TAB.search(tab): f1 = True; continue
            l = 'rejected' if (DROP_TAB.search(tab) or q.startswith('LOG ') or NEG_V.search(v)) else 'rec' if RECF.search(f) else \
                'low' if (RAWF.search(f) or LOW_TAB.search(tab) or LOW_V.search(v + ' ' + q)) else 'good'
            lv.append((ORDER[l], l, f'{f} > {tab}'))
        lv.sort(key=lambda x: -x[0])
        c['level'] = lv[0][1] if lv else 'f1'; c['f1'] = f1
        c['where'] = [w for _, l, w in lv if l == c['level']][:4] if lv else ['current F1 sponsor tab']
        el = [COMBINED.sub(' ', x) for x in c['cat'] if not x.startswith('TAB ')]
        c['strong'] = ' ; '.join(x for x in el if ',' not in x)          # single labels: a sector, an industry, a niche
        c['ct'] = ' ; '.join(el); c['dt'] = ' '.join(c['desc'])          # ct also holds comma lists of database tags (weak evidence)
        c['tabs'] = [x[4:] for x in c['cat'] if x.startswith('TAB ')]
    return d['brands']
def level(c): return c['level']
def member(s, c):
    ct, dt, tabs = c['ct'], c['dt'], c['tabs']
    if s.get('asia') and not ASIA.search(c['country']): return ''
    hit = 'category' if s['cat'].search(c['strong']) else 'description' if (s['desc'].search(dt) or s['desc'].search(ct)) else \
          'sector tab' if s['tab'] and any(s['tab'].search(t) for t in tabs) else ''
    if not hit or s['neg'].search(c['strong'] + ' ' + dt[:200]): return ''
    return hit
def fold(x): return ''.join(ch for ch in unicodedata.normalize('NFKD', str(x)) if not unicodedata.combining(ch))
def compute(B=None, want=None):
    B = B or load(); KEY = {}
    for c in B:
        for k in {loose(c['name']) or c['name'].lower(), loose(fold(c['name']))}:
            if k and (k not in KEY or ORDER[c['level']] > ORDER[KEY[k]['level']]): KEY[k] = c
    SK = sorted(KEY)
    BIG = {}; FULL = {}
    for lv in ('good', 'rec', 'low', 'rejected'):
        FULL[lv] = {strict(fold(c['name'])): c['name'] for c in B if c['level'] == lv}
        BIG[lv] = '|' + '|'.join(FULL[lv]) + '|'
    def find(k):
        """brands whose cleaned name is this name, or starts with it (legal / descriptive tail of up to 25 characters)"""
        hit = [KEY[k]] if k in KEY else []
        if len(k) >= 6:
            i = bisect.bisect_left(SK, k)
            while i < len(SK) and SK[i].startswith(k) and len(hit) < 12:
                if len(SK[i]) - len(k) <= 25: hit.append(KEY[SK[i]])
                i += 1
        return hit
    out = []
    for s in S:
        if want and s['id'] not in want: continue
        rows = {}
        for c in B:
            h = member(s, c)
            if h: rows[id(c)] = (c, h)
        groups = []                                        # leading names; aliases (one name a prefix of the other) are one company
        for nm in s['seeds']:
            k = loose(fold(nm))
            if len(k) <= 2: continue
            g = next((g for g in groups if any((k.startswith(x) or x.startswith(k)) and min(len(k), len(x)) >= 3 for x in g['keys'])), None)
            if g: g['keys'].append(k)
            else: groups.append({'name': nm, 'keys': [k]})
        for g in groups:
            found = [c for k in g['keys'] for c in find(k)]
            g['level'] = max((c['level'] for c in found), key=lambda x: ORDER[x]) if found else 'none'
            g['as'] = max(found, key=lambda c: ORDER[c['level']])['name'] if found else ''
            if g['level'] == 'none':                           # inside a longer name, e.g. 'Woowa Brothers (Baemin)'
                for lv in ('good', 'rec', 'low', 'rejected'):
                    k = next((k for k in g['keys'] if len(k) >= 6 and k in BIG[lv]), None)
                    if k:
                        i = BIG[lv].index(k); a = BIG[lv].rfind('|', 0, i) + 1; b = BIG[lv].find('|', i)
                        g['level'] = lv; g['as'] = FULL[lv].get(BIG[lv][a:b], ''); break
            if g['level'] == 'none' and any(excl_why(x) for x in [g['name']]):
                g['level'] = 'index'                           # named on a list only as a brand / subsidiary of a listed parent, or in a research pool
            for k in g['keys']:                                # the exact-name brand joins the sector list even if no pattern matched
                c = KEY.get(k)
                if c and id(c) not in rows and k not in GENERIC_SEED and len(k) >= 5: rows[id(c)] = (c, 'known name')
        out.append({'s': s, 'rows': list(rows.values()), 'seeds': groups})
    return out
def save():
    res = []
    for r in compute():
        s = r['s']
        rows = [[c['name'], c['country'], c['web'], c['level'], bool(c.get('f1')), ' | '.join(c['where']), (c['dt'] or c['strong'] or c['ct'])[:400], h] for c, h in r['rows']]
        res.append({'id': s['id'], 'name': s['name'], 'group': s['group'], 'rows': rows, 'seeds': [[g['name'], g['level'], g['as']] for g in r['seeds']]})
        print(s['id'], s['name'], len(rows), flush=True)
    json.dump(res, gzip.open(os.path.join(H, 'result.json.gz'), 'wt'), ensure_ascii=False)
if __name__ == '__main__':
    if sys.argv[1:] == ['--save']: save(); sys.exit()
    random.seed(3); want = set(sys.argv[1:])
    for r in compute(want=want):
        s = r['s']
        lv = {k: [c for c, h in r['rows'] if level(c) == k] for k in ORDER}
        sd = {k: [g['name'] for g in r['seeds'] if g['level'] == k] for k in ORDER}
        hits = __import__('collections').Counter(h for c, h in r['rows'])
        print(f"\n== {s['id']} {s['name']} | researched {len(lv['good'])} | recordings only {len(lv['rec'])} | database only {len(lv['low'])} | rejected {len(lv['rejected'])}")
        print('   matched by', dict(hits))
        print(f"   leading names {len(r['seeds'])}: researched {len(sd['good'])}, recordings {len(sd['rec'])}, database {len(sd['low'])}, rejected {len(sd['rejected'])}, nowhere {len(sd['none'])}")
        if want:
            for k in ('good', 'rec', 'low'):
                for c in random.sample(lv[k], min(14, len(lv[k]))): print(f"   [{k}] {c['name'][:34]:34s} | {' ; '.join(x for x in c['cat'])[:70]} | {' '.join(c['desc'])[:90]}")
            print('   NOWHERE:', ', '.join(sd['none'])[:1500]); print('   DB ONLY:', ', '.join(sd['low'])[:900]); print('   REC ONLY:', ', '.join(sd['rec'])[:900])
