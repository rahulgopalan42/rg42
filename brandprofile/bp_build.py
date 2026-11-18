"""Brand workbook in the listed-company format, from the user's Crunchbase brand sheet.
  bp_build.py check     counts only
  bp_build.py xlsx      writes reports/F1-BRAND-PROFILES-<date>.xlsx
Inputs: data/brands.json.gz (prep.py), out/out_*.jsonl (first profile pass), check/out_*.jsonl (second, independent pass on
the key rows), review.py (manual decisions), and the listed-company data of public35/ for brands that are listed."""
import unicodedata, datetime, glob, gzip, html, json, math, os, re, sys
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
for p in ('brands200', 'parents', 'screenrec', 'public35'): sys.path.insert(0, os.path.join(R, p))       # public35 first: its build.py and review.py are the ones wanted
import importlib.util
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
pb = _load('pub_build', os.path.join(R, 'public35', 'build.py')); import review as prev
from qualify import financials, capacity, cap_score, fm
from sectors35 import SECTORS
from f1links import f1_link
from match import loose, strict
import sectors_cb
sys.path.insert(0, H)
try: import bp_review as rv
except ImportError: rv = None
DATE = '2026-11-15'; TODAY = datetime.date(2026, 11, 15)
OUTFILE = os.path.join(R, 'reports', f'F1-BRAND-PROFILES-{DATE}.xlsx')
COLS = pb.COLS + ['Profile Confidence', 'Marked "x" in Your Sheet', 'Brand Name in Your Sheet', 'Tab in Your Sheet']
WIDTH = pb.WIDTH + [12, 10, 28, 26]
FIT = sectors_cb.FIT; NAMES48 = list(sectors_cb.NAMES)
REL = pb.REL; REACH = pb.REACH
# listed-company sector code used only to pick the capacity test for a listed brand
PUB = {'Automotive & Mobility': '18', 'Aerospace, Defence & Space': '13', 'Airlines & Air Travel': '21', 'Travel, Hotels & Leisure': '21', 'Gambling & Gaming Venues': '10',
       'Sports, Fitness & Events': '21', 'Video Games & Esports': '26', 'Software, Internet & AI': '04', 'Media, Entertainment & Publishing': '26', 'Telecommunications': '11',
       'Semiconductors & Electronics': '03', 'IT Services & Consulting': '05', 'Banking & Lending': '08', 'Insurance': '09', 'Investment & Capital Markets': '08',
       'Financial Services & Payments': '06', 'Oil, Gas & Fuels': '23', 'Utilities & Renewable Energy': '45', 'Mining & Metals': '42', 'Chemicals & Materials': '38',
       'Industrial Machinery & Equipment': '15', 'Shipping, Maritime & Shipbuilding': '22', 'Logistics & Transportation': '22', 'Building Products & Materials': '44',
       'Construction & Engineering': '44', 'Real Estate': '41', 'Home & Furniture': '29', 'Luxury, Jewellery & Watches': '32', 'Beauty & Personal Care': '30',
       'Fashion, Apparel & Footwear': '31', 'Alcoholic Drinks': '27', 'Food & Beverage': '29', 'Tobacco & Nicotine': '29', 'Consumer Products': '29', 'Retail & E-commerce': '29',
       'Pharma & Biotech': '36', 'Medical Devices & Diagnostics': '37', 'Healthcare Services': '37', 'Agriculture & Agribusiness': '29', 'Packaging & Printing': '38',
       'Environmental & Waste Services': '45', 'Security Services': '40', 'Staffing & HR': '40', 'Marketing, Advertising & PR': '40', 'Government, Non-profit & Associations': '40',
       'Professional & Business Services': '40', 'Education & Training': '46', 'Diversified & Other': '43'}
MON = {m: i for i, m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split(), 1)}
def clean(x): return re.sub(r'\s+', ' ', str(x or '')).strip()
def words(s): return len(clean(s).split())
def jl(pattern):
    out = []
    for f in sorted(glob.glob(os.path.join(H, pattern))):
        for line in open(f, encoding='utf-8'):
            line = line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except Exception: pass
    return out
def money_range(s):
    """'USD 677M - USD 876M | ...' -> (low, high) in USD of the first range; high None for 'and above'"""
    first = s.split('|')[0]
    v = [float(a) * {'M': 1e6, 'B': 1e9}[b] for a, b in re.findall(r'USD\s*([\d.]+)\s*([MB])', first)]
    if not v: return None, None
    if len(v) == 1 or v[1] <= v[0]: return v[0], None
    return v[0], v[1]
def funding(r):
    """(usd value used, text shown, exact?) from the Crunchbase total and the USD range of the search it came from"""
    raw = clean(r['funding']); lo, hi = money_range(r['range'])
    digits = re.sub(r'[^\d]', '', raw); amt = float(digits) if digits else None
    usd = raw.startswith('$') and not re.match(r'^[A-Z]{1,3}\$', raw)
    if amt and usd and (lo is None or (0.8 * lo <= amt <= 1.25 * (hi or 1e13))): return amt, fm(amt), True
    if lo is not None:
        rng = f"USD {fm(lo)[1:]}-{fm(hi)[1:]}" if hi else f"USD {fm(lo)[1:]} or more"
        shown = (raw + ', ' if amt and not usd and re.match(r'^[^\d]', raw) else '') + rng + ' (Crunchbase range)'
        return lo, shown, False
    if amt and usd: return amt, fm(amt), True
    return None, '', False
def last_round(r):
    m = re.search(r'([A-Za-z]{3})[a-z]*\.?\s*(\d{1,2})\s*,\s*(\d{4})', r['last'])
    if not m or m.group(1).lower() not in MON: return None
    y = int(m.group(3))
    if not 1990 <= y <= 2026: return None
    try: return datetime.date(y, MON[m.group(1).lower()], min(int(m.group(2)), 28))
    except ValueError: return None
def norm_country(c): return {'usa': 'unitedstates', 'us': 'unitedstates', 'uk': 'unitedkingdom', 'uae': 'unitedarabemirates', 'korea': 'southkorea', 'republicofkorea': 'southkorea'}.get(strict(c), strict(c))
def same_country(a, b):
    a, b = norm_country(a), norm_country(b); cn = {'china', 'hongkong'}
    return a == b or (a in cn and b in cn)
STATUS = {'private', 'listed', 'subsidiary', 'state-owned', 'non-commercial', 'defunct', 'unknown'}
STAGE = {'commercial', 'pre-revenue', 'project', 'fund', 'non-commercial'}
PE = re.compile(r'\b(EQT|Nexus Capital|Thoma Bravo|Vista Equity|KKR|Blackstone|Hg|HgCapital|Permira|Advent International|Bain Capital|TPG|Warburg Pincus|Apollo|Silver Lake|Francisco Partners|'
                r'Insight Partners|General Atlantic|Clearlake|Prospect Capital|CVC|Cinven|Apax|BC Partners|Leonard Green|Stone Point|Hellman & Friedman|Carlyle|Sycamore Partners|Veritas Capital|'
                r'Platinum Equity|Symphony Technology|STG|Genstar|GTCR|New Mountain|Madison Dearborn|TA Associates|Summit Partners|Providence Equity|Ardian|PAI Partners|Bridgepoint|Triton|'
                r'Nordic Capital|L Catterton|Golden Gate Capital|Elliott|Energy Capital Partners|Stonepeak|I Squared|DigitalBridge|Stone Canyon|Investindustrial|Lunate)\b', re.I)
# a reported change is a point to verify only when it is unsettled (pending, unconfirmed) or threatens the company itself (insolvency, closure)
CHANGE = re.compile(r'not confirmed|unconfirmed|could not confirm|not completed|completion|pending|agreed (to|sale|in)|\bagreed\b|proposed|planned|plans to|announced|in talks|\bbid\b|offer for|'
                    r'expected|reported|bankrupt|chapter 11|chapter 7|liquidat|insolv|administration|receivership|restructur|delist|wound|wind[- ]down|ceased|shut|dissol|unwound|unwind', re.I)
GENERIC_TOK = set('group holding holdings company corporation international global technologies technology systems solutions industries services financial bank energy motors motor pharma pharmaceuticals '
                  'therapeutics capital partners resources digital software network networks media entertainment china india japan american national first united general'.split())
def toks(name): return {w for w in re.findall(r'[a-z0-9]+', html.unescape(str(name)).lower()) if len(w) >= 4 and w not in GENERIC_TOK}
def tkey(t):
    """'VOLCAR B (Stockholm)', 'VOLCAR-B.ST', '0175 (Hong Kong)', '175.HK' -> one comparable key"""
    t = re.sub(r'\(.*?\)', '', str(t)).strip(); t = re.split(r'[.@]', t)[0] if re.search(r'[.@]', t) and not re.match(r'^[A-Z]{1,4}\.[A-Z]$', t) else t
    k = re.sub(r'[^A-Z0-9]', '', t.upper())
    return (k.lstrip('0') or k) if k.isdigit() else k
RSTEP = ['Domestic', 'Regional', 'International', 'Global']
JOINT = re.compile(r'co-?owned|co-?owner|jointly owned|part-owned|joint[- ]venture|\bJV\b|minority|\bstake\b|shareholder|consortium|sister|group link|group company|same group', re.I)
OWNED = re.compile(r'subsidiar|majority|owned by|controlled by|parent|owner of|\bowns\b|brand of|division of|part of|acquired by', re.I)
SOFT = re.compile(r'licen[cs]|franchis|distribut|bottl|dealer|supplier|supplies|possible|unconfirmed|reported|announced|planned|pending|former|until 20|ended|not confirmed|no direct|not a sponsor|not a partner|tie-in|rights holder|broadcast', re.I)
# rule change of 18 Nov 2026: a subsidiary whose parent or sister brand is an F1 partner stays in (with a note) when a builder sets SUBS_IN
SUBS_IN = False
F1_SELF = {'Alpine', 'McLaren Racing', 'Gulf Oil Lubricants India'}      # subsidiaries that carry the F1 name themselves: always out
F1_SUB = 'Its parent or a sister brand is a current F1 partner: '
def f1_decide(text):
    """the profile's F1 note -> exclude (the brand, its owner or its subsidiary is a current partner) or a note for a looser link"""
    if JOINT.search(text) or (SOFT.search(text) and not OWNED.search(text)) or re.search(r'possible|unconfirmed|former|ended', text, re.I):
        return ('note', 'Reported link to an F1 partner (not a parent or subsidiary): ' + text.rstrip('.') + '. Check for category conflict.')
    return ('exclude', text)
def assemble():
    B = json.load(gzip.open(os.path.join(H, 'data', 'brands.json.gz'), 'rt', encoding='utf-8'))
    P = {d['id']: d for d in jl('out/out_*.jsonl') if isinstance(d, dict) and d.get('id')}
    C2 = {d['id']: d for d in jl('check/out_*.jsonl') if isinstance(d, dict) and d.get('id')}
    SPOT = {d['id']: d for d in jl('data/spot_web.jsonl') if d.get('found') and d.get('sure') in ('high', 'medium') and not (rv and d['id'] in rv.SPOT_SKIP)}
    W3 = {d['id']: d for d in jl('web/out_*.jsonl') if isinstance(d, dict) and d.get('id')}          # web verification of the uncertain rows
    A = pb.assemble(); U = A['U']; master = {r['sym']: r for r in A['rows']}
    cls = {}
    for f in sorted(glob.glob(os.path.join(R, 'public35', 'classify', 'out_*.txt'))):
        for line in open(f):
            p = line.strip().split('|')
            if len(p) == 2: cls[p[0]] = p[1].strip()
    G = {d['sym']: d for d in pb.jl('gap/out_*.jsonl') if d.get('found')}
    byname = defaultdict(list); byroot = defaultdict(list)
    for s, c in U.items():
        byname[loose(html.unescape(c['name']))].append(s); byroot[tkey(s)].append(s)
    rows = []; f1x = []; missing = []; stat = Counter()
    for r in B:
        e = P.get(r['id'])
        if not e: missing.append(r['id']); continue
        e = dict(e); c2 = C2.get(r['id']); differ = []; minor = []
        if c2:                                             # second, independent pass: it decides the key facts; a difference is recorded
            stat['2x'] += 1; stat['2x wiki ' + (clean(c2.get('wiki')).lower() or 'none')] += 1
            for k in ('reach', 'status', 'ticker', 'parent', 'stage', 'changed', 'name', 'hq', 'f1'):
                a, b = clean(e.get(k)), clean(c2.get(k))
                if k in ('reach', 'status', 'stage') and a != b and b:
                    step = abs(RSTEP.index(a.title()) - RSTEP.index(b.title())) if k == 'reach' and a.title() in RSTEP and b.title() in RSTEP else 9
                    (minor if step == 1 else differ).append(f'{k}: {a or "-"} / {b}')
                    stat[f'2x {k} ' + ('one step' if step == 1 else 'differs')] += 1
                if k == 'hq' and b and a.split(',')[-1].strip().lower() != b.split(',')[-1].strip().lower(): stat['2x hq country differs'] += 1
                if b or k in ('ticker', 'parent', 'changed', 'f1'): e[k] = c2.get(k, e.get(k))
            if c2.get('sector') and c2.get('sector') != e.get('sector'): stat['2x sector differs'] += 1
            for k in ('desc', 'markets', 'rationale', 'industry', 'sector', 'rel', 'basis'):
                if c2.get(k) not in (None, ''): e[k] = c2[k]
            e['conf'] = min(clean(e.get('conf')).lower() or 'low', clean(c2.get('conf')).lower() or 'low', key=lambda x: {'high': 2, 'medium': 1}.get(x, 0))
        sp = SPOT.get(r['id']); spot = False
        if sp:                                             # blind web spot-check: the facts it established replace the desk assessment
            spot = True; fold = lambda t: unicodedata.normalize('NFKD', clean(t)).encode('ascii', 'ignore').decode().lower()
            whq = re.sub(r'\s*\([^)]*\)', '', clean(sp.get('hq')))
            if whq and fold(whq) != fold(e.get('hq')) and r['id'] not in rv.SPOT_KEEP_HQ: e['hq'] = whq
            ws = clean(sp.get('status')).lower(); was = clean(e.get('status')).lower()
            if ws in STATUS and ws != 'unknown':
                e['status'] = ws; e['parent'] = re.sub(r'\s*\([^)]*\)?.*$', '', clean(sp.get('parent'))) if ws in ('subsidiary', 'state-owned') else ''
                if ws != 'listed': e['ticker'] = ''
                elif not clean(e.get('ticker')) and re.match(r'^[A-Z0-9.\- ]{1,12} \(', clean(sp.get('ticker'))): e['ticker'] = clean(sp.get('ticker'))
            wc = re.sub(r'\s+for\s+~?(about\s+)?(US)?[$€£][\d.,]+\s?(bn|billion|m|million)?', '', clean(sp.get('changed')))
            if wc and (ws != was or re.search(r'renam|rebrand|formerly', wc, re.I)): e['changed'] = wc.rstrip('.')
            if clean(sp.get('reach')).title() in RSTEP and r['id'] not in rv.SPOT_KEEP_REACH: e['reach'] = sp['reach']; e['basis'] = 'known'
            if clean(e.get('conf')).lower() == 'low': e['conf'] = 'medium'
            differ = []; minor = []
        w3 = W3.get(r['id']); web = bool(w3) and clean(w3.get('web')).lower() == 'found'
        if w3 and not web: stat['web not found'] += 1
        if web:                                            # found on the web: these facts replace the desk assessment, and settle earlier differences
            stat['web'] += 1
            for k in ('reach', 'status'):
                a, b = clean(e.get(k)).lower(), clean(w3.get(k)).lower()
                if a != b: stat[f'web changed {k}'] += 1
                if k == 'reach' and a.title() in RSTEP and b.title() in RSTEP and abs(RSTEP.index(a.title()) - RSTEP.index(b.title())) >= 2: stat['web changed reach 2+ steps'] += 1
                if k == 'status' and a == 'unknown' and b != 'unknown': stat['web settled unknown status'] += 1
            for k in ('name', 'hq', 'desc', 'sector', 'industry', 'reach', 'basis', 'markets', 'rationale', 'rel', 'status', 'stage', 'conf'):
                if w3.get(k) not in (None, ''): e[k] = w3[k]
            for k in ('ticker', 'parent', 'changed', 'f1'): e[k] = w3.get(k, '')
            differ = []; minor = []
        if rv and r['id'] in rv.FIX: e.update(rv.FIX[r['id']])
        name = clean(e.get('name')) or r['brand']
        conf = clean(e.get('conf')).lower(); conf = conf if conf in ('high', 'medium', 'low') else 'low'
        status = clean(e.get('status')).lower(); status = status if status in STATUS else 'unknown'
        stage = clean(e.get('stage')).lower(); stage = stage if stage in STAGE else 'commercial'
        sector = clean(e.get('sector')); sector = sector if sector in FIT else r['sector']
        reach = clean(e.get('reach')).title(); reach_ok = reach in REACH; reach = reach if reach_ok else 'Domestic'
        basis = clean(e.get('basis')).lower(); basis = basis if basis in ('stated', 'known', 'inferred') else 'inferred'
        rel = e.get('rel') if e.get('rel') in REL else 2
        hq = clean(e.get('hq')); parts = [x.strip() for x in hq.split(',') if x.strip()]
        if len(parts) >= 3: hq = parts[0] + ', ' + parts[-1]                       # "City, State, Country" -> "City, Country"
        country = parts[-1] if parts else r['country']
        if len(parts) == 2 and parts[0] == parts[1] and parts[0] in ('Hong Kong', 'Singapore', 'Monaco', 'Macau', 'Luxembourg', 'Gibraltar'): hq = parts[0]
        hq = hq.strip().strip(',').strip()
        if not re.search(r'[A-Za-z\u00C0-\u024F]{3}', hq) or re.search(r'\d|:|crunchbase', hq, re.I): hq = ''      # unreadable location in the recording
        if not hq or hq.lower() in ('unknown', 'n/a', 'not known', 'none'): hq = clean(r['country']) or 'Not recorded'
        ticker_txt = clean(e.get('ticker')); parent = clean(e.get('parent')); changed = clean(e.get('changed'))
        # ---- F1 exclusion
        link = ''; route = ''
        for nm in [name, r['brand']] + ([parent] if parent and status == 'subsidiary' else []):      # the brand's own names first, then its owner
            l, _ = f1_link(nm)
            if l: link = l + (f' (owner: {parent})' if nm == parent and nm not in (name, r['brand']) else ''); route = 'parent' if nm == parent and nm not in (name, r['brand']) else 'own'; break
        f1txt = clean(e.get('f1')); f1note = ''
        if rv and r['id'] in rv.F1: dec = rv.F1[r['id']]; route = 'hand'
        elif link: dec = ('exclude', link)
        elif f1txt and f1txt.lower() not in ('none', 'no', 'n/a', '-'): dec = f1_decide(f1txt); route = 'profile'
        else: dec = ('clear', '')
        f1route = (route, status, parent)
        if SUBS_IN and dec[0] == 'exclude' and status == 'subsidiary' and route in ('parent', 'profile', 'hand') and name not in F1_SELF: dec = ('note', F1_SUB + dec[1])
        pe = status == 'subsidiary' and bool(PE.search(parent))     # owned by an investment firm: a private company, not a subsidiary of an operating group
        if pe: status = 'private'
        # ---- listed brand: find it in the listed-company data
        sym = None
        if status == 'listed' or (rv and r['id'] in rv.SYM):
            roots = {tkey(t) for t in re.split(r'[,;/]', ticker_txt) if tkey(t)}
            nk = {k for k in (loose(name), loose(r['brand']), loose(re.sub(r'^the\s+', '', name, flags=re.I))) if len(k) >= 3}
            cand = {s for k in nk for s in byname.get(k, [])}
            good = [s for s in cand if same_country(U[s]['country'], country) or tkey(s) in roots]
            if not good:                                   # same ticker, and the two names share a distinctive word or one contains the other
                tk = toks(name) | toks(r['brand'])
                for s in {s for t in roots for s in byroot.get(t, [])}:
                    un = toks(U[s]['name']); lk = loose(U[s]['name'])
                    if (tk & un) or any(len(k) >= 4 and (k in lk or lk in k) for k in nk if len(lk) >= 4): good.append(s)
                same = [s for s in good if same_country(U[s]['country'], country)]
                good = same or (good if len(good) == 1 else [])
                if not good:                               # same ticker and same country, one candidate only: accept without a name match (short names such as BT, Wix, Gen)
                    rc = [s for t in roots for s in byroot.get(t, []) if same_country(U[s]['country'], country)]
                    if len(set(rc)) == 1: good = rc
            if good: sym = max(good, key=lambda s: (s in master, U[s].get('mcap') or 0))
            if rv and r['id'] in rv.SYM: sym = rv.SYM[r['id']]
        if sym and dec[0] != 'exclude':
            if sym in prev.ROSTER_EXTRA: dec = ('exclude', prev.ROSTER_EXTRA[sym])
            elif prev.F1.get(sym, ('',))[0] == 'exclude': dec = ('exclude', prev.F1[sym][1])
        if dec[0] == 'exclude': f1x.append({'r': r, 'name': name, 'why': dec[1], 'sector': sector, 'route': f1route[0] if 'sym' not in dir() or dec[1] in (link, f1txt) or route == 'hand' else 'listed', 'status': f1route[1], 'parent': f1route[2]}); stat['current F1 partner, or parent / subsidiary of one'] += 1; continue
        if dec[0] == 'note': f1note = dec[1]
        # ---- financial capacity
        amt, fund_txt, exact = funding(r); d = last_round(r); age = ((TODAY.year - d.year) * 12 + TODAY.month - d.month) if d else None
        notes = []; pub = None; fin_cells = None
        if sym:
            c = U[sym]; mr = master.get(sym)
            if mr: f, k, grp = mr['f'], mr['k'], SECTORS[mr['sector']]['grp']; pc = pb.cells(mr)
            else:
                code = cls.get(sym) if cls.get(sym) in SECTORS else PUB[sector]; grp = SECTORS[code]['grp']; f = financials(c, grp, G.get(sym))
                gross = bool(f['rev'] and f['mcap'] and f['rev'] > 3 * f['mcap'] and (code == '07' or grp == 'fin'))
                k = capacity(dict(f, rev=None, mkt=None) if gross else f, code); pc = None
            if pc: fin_cells = {'ticker': pc[6], 'rev': pc[7], 'mcap': pc[8], 'growth': pc[9], 'profit': pc[10], 'liq': pc[11], 'mkt': pc[12], 'period': pc[16], 'src': pc[17]}
            else: fin_cells = {'ticker': pb.ticker(c, f['gap']), 'rev': f['rev'] or 'Not available', 'mcap': f['mcap'] or 'Not available', 'growth': round(f['growth'], 4) if f['growth'] is not None else 'Not available',
                               'profit': pb.col_profit(f, grp), 'liq': pb.col_liq(f, grp), 'mkt': pb.col_mkt(f, c.get('sec') or {}), 'period': pb.col_period(f), 'src': pb.col_sources(c, f)}
            if k['ev'] == 'Insufficient': cat, ev, capv, fin = 'To Verify', 'Not Established', 0, 15; notes.append(('cat', 'Investment category not assigned: the published figures do not support USD 4M a year'))
            else:
                cat, ev, capv, fin = k['cat'], k['ev'], k['cap'], cap_score(k, f)
                if cat == 'To Verify': notes.append(('cat', 'Investment category not assigned: the published figures leave capacity just short or unclear'))
            pub = {'sym': sym, 'f': f, 'k': k}
        else:
            w = 0.02 if age is not None and age <= 24 else 0.01 if age is not None and age <= 48 else 0.0
            capv = w * amt if amt else 0
            blocked = ('reported closed or absorbed' if status == 'defunct' else 'public body or non-profit, not a commercial sponsor' if status == 'non-commercial' or stage == 'non-commercial' else
                       'pre-revenue: funding pays for development, not marketing' if stage == 'pre-revenue' else 'single project or asset vehicle: funding is project finance' if stage == 'project' else
                       'investment fund or holding vehicle, not an operating brand' if stage == 'fund' else '')
            if blocked: cat, ev, fin, capv = 'To Verify', 'Not Established', 15, 0; notes.append(('info', 'Investment category not assigned: ' + blocked))
            elif capv >= 4e6:
                cat = 'Large' if capv >= 12e6 else 'Mid-level' if capv >= 6e6 else 'Challenger'; ev = 'Plausible Capacity'
                fin = min(100, 40 + 60 * math.log(capv / 4e6) / math.log(50e6 / 4e6))
            elif capv >= 3e6: cat, ev, fin = 'To Verify', 'Plausible Capacity', 35; notes.append(('cat', 'Investment category not assigned: funding-based estimate is just under the USD 4M Challenger level'))
            else:
                cat, ev, fin = 'To Verify', 'Not Established', 20
                why = ('no funding figure' if not amt else 'date of the last funding round could not be read' if age is None else
                       f'last funding round was in {d.year}, too old to show current capacity' if age > 48 else 'funding raised is below the level that supports USD 4M a year')
                notes.append(('info', 'Investment category not assigned: ' + why))
            if status == 'listed': notes.append(('data', 'Listed, but not matched to the financial data used: revenue and market value not filled; capacity rests on funding raised'))
        fit = FIT[sector]; strat = 0.25 * fit * 10 + 0.50 * REL[rel] + 0.25 * REACH[reach]; score = round(0.6 * strat + 0.4 * fin, 1)
        # ---- notes
        if r.get('note'): notes.append(('info', r['note'][0].upper() + r['note'][1:]))
        if conf == 'low': notes.append(('profile', 'Profile written with low confidence: little is known about this company; check description, HQ and markets'))
        if not reach_ok: notes.append(('profile', 'Geographic reach not established'))
        elif basis == 'inferred': notes.append(('reach', 'Geographic reach inferred from the type of business and location, not confirmed'))
        if web or spot: notes.append(('info', 'Ownership, listing and reach looked up on the web on 15 Nov 2026'))
        if differ: notes.append(('profile', 'Two independent assessments differed (first / second, second used): ' + '; '.join(differ)))
        if minor: notes.append(('info', 'Reach was assessed twice and the two results were one step apart (first / second, second used): ' + '; '.join(minor)))
        if changed and CHANGE.search(changed): notes.append(('corp', 'Reported corporate change - confirm current position: ' + changed))
        elif changed: notes.append(('info', changed))
        if status == 'subsidiary' and parent: notes.append(('info', f'Owned by {parent}: a sponsorship decision may sit with the parent'))
        if pe: notes.append(('info', f'Owned by {parent} (investment firm)'))
        if status == 'unknown': notes.append(('profile', 'Ownership and listing status not confirmed'))
        if status == 'defunct': notes.append(('corp', 'Reported closed or absorbed: confirm before any outreach'))
        if sector != r['sector']: notes.append(('info', f"On the '{r['sector']}' tab in your sheet; its business is {sector}"))
        if 'low OCR confidence' in r['flags']: notes.append(('profile', 'Name was hard to read in the recording: check the company name'))
        if strict(name) != strict(r['brand']) and not strict(name).startswith(strict(r['brand'].rstrip('. '))[:max(6, len(strict(r['brand'])) - 3)]):
            notes.append(('info', f"Listed in your sheet as '{r['brand']}'"))
        if r['user_added']: notes.append(('info', 'Brand added by you: no Crunchbase data on the sheet, profile written from general knowledge'))
        if f1note: notes.append(('f1', f1note))
        if re.search(r'tobacco', r['flags'], re.I) or sector == 'Tobacco & Nicotine': notes.append(('info', 'Tobacco, nicotine or cannabis: advertising restrictions apply in most F1 markets'))
        rows.append({'r': r, 'e': e, 'name': name, 'hq': hq, 'sector': sector, 'reach': reach, 'basis': basis, 'rel': rel, 'conf': conf, 'status': status, 'stage': stage, 'parent': parent,
                     'ticker_txt': ticker_txt, 'cat': cat, 'ev': ev, 'cap': capv, 'fin': fin, 'score': score, 'notes': notes, 'pub': pub, 'fin_cells': fin_cells, 'fund_txt': fund_txt,
                     'fund_exact': exact, 'date': d, 'age': age, 'f1note': f1note, 'differ': differ, 'checked': bool(c2), 'web': web or spot, 'src': (w3 or {}).get('src') or []})
    seen = {}                                                # the same company entered twice in the sheet (old and new name, two tabs, a misread name)
    for x in rows:
        seen.setdefault((re.sub(r'[^a-z0-9]', '', x['name'].lower()), x['r']['country']), []).append(x)
    for k, grp in seen.items():
        if len(grp) > 1 and k[0]:
            for x in grp:
                o = [y for y in grp if y is not x][0]
                x['notes'].append(('info', f"Same company as '{o['r']['brand']}' on the '{o['r']['sector']}' tab of your sheet (row {o['r']['row']})"))
    for x in rows:
        acq = x['status'] == 'defunct' or (x['status'] == 'subsidiary' and x['cat'] == 'To Verify')
        if x['rel'] <= 1 or x['score'] < 55 or acq: p = 'Lower'
        elif x['cat'] != 'To Verify' and ((x['rel'] >= 4 and x['score'] >= 60) or (x['rel'] == 3 and x['score'] >= 74)): p = 'High'
        else: p = 'Medium'
        if p == 'High' and x['conf'] == 'low': p = 'Medium'
        x['priority'] = p
        x['verify'] = p != 'Lower' and any(t not in ('info',) for t, _ in x['notes'])
    rank = {'High': 0, 'Medium': 1, 'Lower': 2}
    rows.sort(key=lambda x: (rank[x['priority']], -x['score'], -(x['cap'] or 0), x['name'].lower()))
    return {'rows': rows, 'f1x': f1x, 'missing': missing, 'B': B, 'stat': stat}
F1_NOTE = ('Not on the 2025-26 F1 partner roster (424 championship, team and Grand Prix partners; team partner pages re-read and the partner lists of 13 Grands Prix '
           'searched on 15 Nov 2026). No parent, subsidiary or brand match')
SRC = 'Crunchbase search results recorded Oct-Nov 2026 (name, headquarters, industries, total funding, last funding round)'
def cells(x):
    r, e = x['r'], x['e']; fc = x['fin_cells']; st = x['status']
    last = pb.dt(x['date'].isoformat()) if x['date'] else ''
    fund = (f"Total funding raised {x['fund_txt']}" + (f"; last round {last}" if last else '') + ' (Crunchbase)') if x['fund_txt'] else 'Not available'
    if fc:
        tick, rev, mcap, growth, profit, mkt, period = fc['ticker'], fc['rev'], fc['mcap'], fc['growth'], fc['profit'], fc['mkt'], fc['period']
        liq = fc['liq'] if fc['liq'] != 'Not available' else ''
        liq = (liq + '; ' if liq else '') + (fund[0].lower() + fund[1:] if liq and fund != 'Not available' else fund) if fund != 'Not available' else (liq or 'Not available')
        src = fc['src'] + '; ' + SRC
    else:
        nd = 'Not disclosed (private company)' if st in ('private', 'subsidiary', 'state-owned') else 'Not available'
        tick = ((x['ticker_txt'] or 'Listed (ticker not confirmed)') if st == 'listed' else 'Private (not listed)' if st == 'private' else
                (f"Not listed: owned by {x['parent']}" if x['parent'] else 'Not listed: subsidiary') if st == 'subsidiary' else 'Not listed: state-owned' if st == 'state-owned' else
                'Not listed: public body or non-profit' if st == 'non-commercial' else 'Not listed: reported closed or absorbed' if st == 'defunct' else 'Listing status not confirmed')
        rev = nd; mcap = 'Not applicable (not listed)' if st in ('private', 'subsidiary', 'state-owned', 'non-commercial', 'defunct') else 'Not available'
        growth = nd; profit = nd; liq = fund; mkt = 'Not Disclosed'
        period = ('No financial statements in the sources used; ' + (f'last funding round {last} (Crunchbase)' if last else 'last funding date not readable'))
        src = SRC
    f1 = F1_NOTE + ('. Note: ' + x['f1note'] if x['f1note'] else '')
    ind = clean(e.get('industry')); sec = x['sector'] + (': ' + ind if ind else '')
    return [x['name'], x['hq'], x['cat'], x['priority'], clean(e.get('desc')), sec, tick, rev, mcap, growth, profit, liq, mkt, x['reach'], clean(e.get('markets')), clean(e.get('rationale')),
            period, src, f1, x['ev'], '; '.join(t for _, t in x['notes']) or 'None flagged', x['score'], x['conf'].title(), 'x' if r['mark'] else '', r['brand'], r['sector']]
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    A = assemble(); rows = A['rows']
    print(len(A['B']), 'brands |', len(rows), 'profiled |', len(A['missing']), 'without a profile |', len(A['f1x']), 'F1-linked (own tab)')
    print('priority', dict(Counter(x['priority'] for x in rows)), '| category', dict(Counter(x['cat'] for x in rows)), '| confidence', dict(Counter(x['ev'] for x in rows)))
    print('reach', dict(Counter(x['reach'] for x in rows)), '| basis', dict(Counter(x['basis'] for x in rows)), '| profile conf', dict(Counter(x['conf'] for x in rows)))
    print('status', dict(Counter(x['status'] for x in rows)), '| stage', dict(Counter(x['stage'] for x in rows)), '| matched to listed data', sum(1 for x in rows if x['pub']))
    print('verify', sum(x['verify'] for x in rows), '| marked x', sum(x['r']['mark'] for x in rows), {p: sum(1 for x in rows if x['r']['mark'] and x['priority'] == p) for p in ('High', 'Medium', 'Lower')})
    if cmd == 'xlsx':
        import write_xlsx; write_xlsx.write(A, OUTFILE, COLS, WIDTH, cells); print(OUTFILE)
