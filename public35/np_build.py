"""New-parameters workbook (19 Nov 2026): listed companies NOT on the 15 Nov master, scored under the updated parameters.

Entry (any one): revenue USD 100M+, market value USD 500M+, cash USD 150M+, disclosed marketing spend USD 20M+.
Capacity estimate (strongest indicator): Technology 0.4% of revenue or 8% of marketing spend; Consumer 0.3% / 8%;
  Financial 0.25% of revenue or 1.5% of pre-tax profit; Industrial / other 0.3% / 1.5%; cash-rich 1.2-1.5% of cash, cut for losses and runway.
Categories: Large 12M+, Mid-Level 6-12M, Challenger 4-6M, Emerging 3.5-4M, Strategic Exception (below that, with a stated reason).
Priority score: 30% strategic fit, 25% financial capacity, 25% buying signals, 20% team fit / B2B / activation.
F1 links are flagged, not excluded. No cap per sector.
Usage: np_build.py check | np_build.py write"""
import html, json, math, os, re, sys, unicodedata
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); sys.path.insert(0, H)
import build                       # keep first (see np_select.py)
import np_common as nc
import np_select as ns
import review
from np_common import SECTORS, ORDER, fm
DATE = '2026-11-19'
OUT = os.path.join(R, 'reports', f'F1-PUBLIC-COMPANIES-NEW-PARAMETERS-NEW-BRANDS-{DATE}.xlsx')
TAB = dict(build.TAB, **{'47': 'Tobacco & nicotine', '48': 'Packaging & paper', '49': 'Agriculture & food commodities', '50': 'Other operating companies'})
COLS = ['Company Name', 'Headquarters', 'F1 Investment Category', 'Outreach Priority', 'Short Company Description', 'Annual Revenue (USD)', 'Market Capitalization (USD)',
        'Cash / Profitability', 'Estimated Sponsorship Capacity', 'Financial Capacity Confidence', 'Geographic Reach', 'Existing Sports / F1 Partnerships',
        'Strategic Rationale for F1', 'Buying Signals', 'Sources / Verification Status',
        'Sector', 'Stock Ticker / Exchange', 'Main Customer Markets', 'Priority Score (0-100)', 'Capacity Estimate (USD a year)', 'On Your Brand Sheet?']
WIDTH = [30, 24, 15, 11, 46, 14, 14, 40, 40, 13, 13, 52, 50, 52, 70, 28, 22, 44, 10, 14, 30]
REL = {1: 10, 2: 35, 3: 60, 4: 80, 5: 100}; REACH = {'Global': 100, 'International': 80, 'Regional': 50, 'Domestic': 25}
HIGH, MED = 52.0, 42.0             # priority cut-offs on the 0-100 score
RANK = {'High': 0, 'Medium': 1, 'Lower': 2}; CATS = ['Large', 'Mid-Level', 'Challenger', 'Emerging', 'Strategic Exception']
clean = lambda x: re.sub(r'\s+', ' ', str(x or '')).strip()
def usd(v):
    if v is None: return ''
    a = abs(v)
    return f'${a / 1e9:,.2f}B' if a >= 1e9 else f'${a / 1e6:,.1f}M' if a >= 1e5 else 'under $0.1M'
# ------------------------------------------------------------------ the user's brand sheet (for the last column)
SUF = re.compile(r'\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|plc|sa|ag|se|nv|bv|gmbh|spa|srl|ab|as|oy|pte|pty|holdings?|group|the)\b')
def loose(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower().replace('&', ' and ')
    s = re.sub(r'[^a-z0-9 ]', ' ', s); s = SUF.sub(' ', s)
    return re.sub(r'\s+', '', s)
def load_known():
    """the 18,851 brands on the user's 48-tab sheet: loose name -> tab"""
    import gzip
    p = os.path.join(R, 'brandprofile', 'data', 'brands.json.gz'); K = {}
    if os.path.exists(p):
        for d in json.load(gzip.open(p, 'rt')):
            for n in (d.get('brand'), d.get('orig_brand')):
                k = loose(n or '')
                if len(k) >= 3: K.setdefault(k, d.get('tab') or 'on the sheet')
    return K
def on_sheet(K, name):
    for n in [name, re.sub(r'\(.*?\)', ' ', name)] + re.findall(r'\(([^)]+)\)', name):
        k = loose(n)
        if len(k) >= 3 and k in K: return 'Yes: ' + K[k] + ' tab'
    return 'No'
# ------------------------------------------------------------------ F1 links
import f1links as fl
COUNTRY = set('japan india malaysia pakistan china indonesia thailand nigeria bangladesh lanka kenya ghana egypt philippines vietnam korea brasil brazil mexico chile polska poland '
              'argentina peru colombia turkey turkiye uganda zambia tanzania morocco'.split())
GROUP = re.compile(r"(?i)\bparent\b|parent's|sister|subsidiary of|owned by|majority-owned|controlled by|shareholder|same group|group\)|through its parent|"
                   r"parent of|owner of|part of|taken private by|joint venture|holding company of|split off|spun off")
UNSURE = re.compile(r'(?i)verify|possible|not sure|unsure|assum|unconfirmed|may be|weaker match|not certain|unclear')
NAMED = [(re.compile(p), t) for p, t in [            # partners confirmed after the roster was compiled (partner pages re-read in Nov 2026)
    (r'(?i)^adobe\b', 'Adobe is a current F1 partner'), (r'(?i)^sharkninja', 'SharkNinja is a current F1 partner'), (r'(?i)^logitech', 'Logitech is a current F1 partner'),
    (r'(?i)^wynn resorts', 'Wynn Resorts is a Las Vegas Grand Prix founding partner'), (r'(?i)^caesars entertainment', 'Caesars Entertainment is a Las Vegas Grand Prix partner'),
    (r'(?i)bradesco', 'Bradesco is on the Haas partner page (Nov 2026)'), (r'(?i)^stratasys', 'Stratasys is a current F1 team supplier and partner'), (r'(?i)^abbvie', 'AbbVie is a current F1 partner'),
    (r'(?i)^intel\b', 'Intel is a current F1 partner'), (r'(?i)^rakuten$|^rakuten group', 'Rakuten becomes a Ferrari partner from 2027'), (r'(?i)mercado ?libre', 'Mercado Libre is a current F1 partner'),
    (r'(?i)^daimler truck', 'Daimler Truck (Mercedes-Benz Trucks) is a current F1 partner'), (r'(?i)^(ntt|nippon telegraph)\b(?! data)', 'NTT becomes a McLaren partner from 2027 (announced 4 Nov 2026)')]]
NAMED_GROUP = [(re.compile(r'(?i)^ntt data'), 'NTT, the parent, becomes a McLaren partner from 2027 (announced 4 Nov 2026)')]
KIND_FIX = {'002668.SZ': 'group', '532466.BO': 'group', '2380.SR': 'group', 'TABAK.PR': 'group', '544028.BO': 'group', 'ENR.F': 'group', 'DTE.DE': 'group', 'BRK-B': 'group',
            'SFL.MI': 'note', 'PHG': 'note', 'MCD': 'note', 'VVV': 'note'}       # manual reading of the link text: local or sister companies, licensees, brand owned by someone else
_W = None
def web_check(sym):
    """the live web check of the top prospects of the first pass (f1web/), with the manual overrides"""
    global _W
    if _W is None:
        _W = {d['sym']: dict(d, when='15 Nov 2026') for d in nc.jl('f1web/out_*.jsonl') if d.get('sym') and d.get('status') not in (None, 'not_checked')}
        _W.update({d['sym']: dict(d, when='19 Nov 2026') for d in nc.jl('np/f1web/out_*.jsonl') if d.get('sym') and d.get('status') not in (None, 'not_checked')})
    w = _W.get(sym)
    if not w: return '', ''
    st = review.WEB.get(sym, w['status']); det = clean(w.get('detail')).rstrip('.') + (f" ({w['source_url']})" if w.get('source_url') else '')
    return st, f"web search, {w['when']}: " + det
SIGNAL_CORRECTED = {'544466.BO', '3388.HK'}        # the event did happen; the web search corrected its date
def signal_check(sym):
    """the web check of one desk-research buying signal (np/f1web/): (status, note with source) or ('', '')"""
    web_check(sym); w = _W.get(sym) or {}
    st = clean(w.get('signal_status')).lower()
    if st not in ('confirmed', 'not found', 'contradicted'): return '', ''
    if st == 'contradicted' and sym in SIGNAL_CORRECTED: st = 'corrected'
    return st, clean(w.get('signal_note')).rstrip('.') + (f" ({w['signal_url']})" if w.get('signal_url') else '')
F1_OWNER = re.compile(r'(?i)^(formula one group|liberty media|liberty live|liberty formula)')
def f1_status(sym, c, e):
    """(kind, text): 'partner' = holds a current F1 deal itself, or through its own brand, team or engine programme;
    'group' = a local subsidiary, the parent, a sister company or a shareholder of one; 'note' = looser or unconfirmed link; '' = none found"""
    name = clean(html.unescape(c['name'])); sec = c.get('sec') or {}
    web = sec.get('web') or (c.get('clay') or {}).get('domain') or ''
    dec = review.F1.get(sym)
    if dec and dec[0] == 'clear': return '', ''
    link, _ = nc.f1_link(name, web); own = clean((e or {}).get('f1'))
    if link:
        txt = own if len(own) >= 12 else link.replace(' - parent / owner', ' (brand or team of this company)')
        words = [w.lower().strip('.') for w in re.split(r"[^A-Za-z0-9&'+]+", re.sub(r'\(.*?\)', ' ', name)) if w]
        direct = fl.loose(name) in fl.NAMES or fl.loose(name) in fl.TWO
        if not direct and any(w in COUNTRY for w in words): return 'group', txt                      # local subsidiary of a partner
        if link.endswith(' - parent / owner') and re.search(r'(?i)\bgroup\b|parent\)|shareholder', link): return 'group', txt
        return 'partner', txt
    wst, wdet = web_check(sym)
    if wst == 'current': return 'partner', 'Found by ' + wdet
    for pat, t in NAMED:
        if pat.search(name): return 'partner', t
    for pat, t in NAMED_GROUP:
        if pat.search(name): return 'group', t
    if sym in review.ROSTER_EXTRA: txt = review.ROSTER_EXTRA[sym]
    elif dec: txt = dec[1]
    elif own: txt = own
    elif wst in ('related', 'unclear'): return 'note', 'From ' + wdet
    elif wst == 'past': return 'past', 'from ' + wdet
    else: return '', ''
    if dec and dec[0] == 'note': return 'note', txt
    if not (sym in review.ROSTER_EXTRA or dec) and (UNSURE.search(txt) or (build.LOOSE_LINK.search(txt) and not build.TIGHT_LINK.search(txt))): return 'note', txt
    return ('group' if GROUP.search(txt) else 'partner'), txt
# ------------------------------------------------------------------ scores
def strat_score(code, rel): return 0.4 * SECTORS[code]['fit'] * 10 + 0.6 * REL[rel]
def fin_score(k):
    cap = k['cap']
    s = 25 if k['nodata'] else 45 + 55 * min(1, math.log(cap / 3.5e6) / math.log(50e6 / 3.5e6)) if cap >= 3.5e6 else max(10, 45 * cap / 3.5e6)
    return max(0, min(100, s - (15 if k['stressed'] else 0)))
EXPAND = re.compile(r'(?i)expan|entering|\benter(s|ed)?\b|launch|roll-?out|new markets?|opening (stores|offices|in)')
def signal_score(f, e, chk=('', '')):
    """(0-100, text for the Buying Signals column). Signals from figures count as found; signals from the company review are marked 'to verify'."""
    pts = 0; data = []; g = f.get('growth')
    if g is not None:
        src = f.get('growth_note') or ('latest fiscal year, annual filing' if f['rev_src'] == 'sec' else 'latest reported year')
        if f.get('page') and 'growth' in (f.get('page_used') or []): src += ', stockanalysis.com'
        if g >= 0.2: pts += 35; data.append(f'Revenue up {g * 100:.0f}% year on year ({src})')
        elif g >= 0.08: pts += 20; data.append(f'Revenue up {g * 100:.0f}% year on year ({src})')
        elif g <= -0.1: pts -= 10; data.append(f'Caution: revenue down {-g * 100:.0f}% year on year ({src})')
    if (f['mkt'] or 0) >= 2e7: pts += 15; data.append(f"Disclosed {f['mkt_kind'].lower() or 'marketing expense'} {fm(f['mkt'])} (annual filing)")
    sports = clean(e.get('sports')); sig = clean(e.get('signals')); markets = clean(e.get('markets')); desk = []; web = ''
    if sports: pts += 25; desk.append('existing sports sponsorship (see Existing Sports / F1 Partnerships)')
    if sig and chk[0] == 'contradicted': web = 'A reported signal was not supported by a web search on 19 Nov 2026 and is not counted: ' + chk[1]; sig = ''
    if sig:
        n = len([p for p in re.split(r';|\.\s+(?=[A-Z])', sig) if p.strip()]); pts += 20 if n <= 1 else 30
        if chk[0] in ('confirmed', 'corrected'):
            web = ('Confirmed' if chk[0] == 'confirmed' else 'Confirmed, with the date corrected,') + ' by web search, 19 Nov 2026: ' + chk[1]
            if n > 1: desk.append('other reported items: ' + sig.rstrip('.'))
        else: desk.append(sig.rstrip('.') + (' (a web search on 19 Nov 2026 did not find this)' if chk[0] == 'not found' else ''))
    if EXPAND.search(markets) and not re.search(r'(?i)no verified expansion', markets): pts += 10; desk.append('international expansion noted in the company profile')
    parts = ['; '.join(data)] if data else []
    if web: parts.append(web)
    if desk: parts.append('Desk research, to verify: ' + '; '.join(desk))
    return max(0, min(100, pts)), '. '.join(p.rstrip('.') for p in parts) or 'None identified in the sources used'
def team_score(e, reach, kind):
    b = e.get('b2b') if e.get('b2b') in (1, 2, 3, 4, 5) else 3; a = e.get('act') if e.get('act') in (1, 2, 3, 4, 5) else 3
    hi, lo = max(a, b), min(a, b); conflict = {'partner': 30, 'group': 60, 'note': 60}.get(kind, 100)
    return 0.45 * (hi - 1) * 25 + 0.15 * (lo - 1) * 25 + 0.25 * REACH[reach] + 0.15 * conflict
def confidence(x):
    k, f = x['k'], x['f']
    if k['nodata']: return 'Low', 'no revenue or profit figures in the sources used'
    if x['gross']: return 'Low', 'reported revenue is gross trading or investment value, so it was not used'
    if not x['cat']: return 'Low', 'estimate is below the USD 3.5M threshold'
    if k['stressed']: return 'Low', 'losses are large relative to cash on hand'
    if k['basis'].startswith('cash reserves'): return 'Medium', 'estimate rests on cash reserves, not on operations'
    if k['loss']: return 'Medium', 'loss-making, so the estimate was cut'
    if f['pretax'] is None: return 'Medium', 'profit not found in the sources used, so the estimate rests on revenue'
    return 'High', ''
def cash_profit(f, grp):
    parts = []; per = ' (trailing 12 months)' if f.get('pretax_ttm') else (f" (year to {build.dt(f['fy_end'])})" if f['fy_end'] else '')
    if f['pretax'] is not None:
        kind = f['pretax_kind']; neg = {'Pre-tax profit': 'Pre-tax loss', 'Net income': 'Net loss', 'Operating profit': 'Operating loss'}.get(kind, 'Loss')
        parts.append(build.money(kind, neg, f['pretax']) + per)
    if f['ebitda'] is not None: parts.append(build.money('EBITDA', 'EBITDA loss', f['ebitda']))
    elif f['opinc'] is not None and f['pretax_kind'] != 'Operating profit': parts.append(build.money('operating profit', 'operating loss', f['opinc']))
    if f['cash']: parts.append('cash ' + fm(f['cash']))
    if f['debt']: parts.append('total debt ' + fm(f['debt']))
    if grp == 'fin' and f['assets']: parts.append('total assets ' + fm(f['assets']))
    if grp != 'fin' and f['fcf'] is not None: parts.append(('free cash flow ' if f['capex'] else 'operating cash flow ') + fm(f['fcf']))
    s = '; '.join(parts)
    return s[0].upper() + s[1:] if s else 'Not available in the sources used'
DUP_SYMS = {'5183.KL': 'PETRONAS Chemicals Group (PCHEM.KL kept)', '6033.KL': 'PETRONAS Gas (PETGAS.KL kept)'}        # the same company under a second ticker form
DUP_FLAG = re.compile(r'(?i)duplicate|secondary (frankfurt )?(quote|listing|line)|b-share line|second share class|paired share')
ACQ = re.compile(r'(?i)being acquired|taken private|take-private|agreed to (be )?acquire|acquired by|merged (into|with)|insolvency|bankrupt|delist')
# ------------------------------------------------------------------ assemble
def assemble():
    C, st = ns.candidates(); K = load_known()
    onmaster = {loose(re.sub(r'\(.*?\)', ' ', r['name'])) for r in build.assemble()['rows']}
    rows = []; below = []; out = Counter()
    for x in C:
        sym, c, e, f, k = x['sym'], x['c'], x['e'] or {}, x['f'], x['k']; name = clean(html.unescape(c['name'])); code = x['code']
        base = {'sym': sym, 'name': name, 'c': c, 'f': f, 'k': k, 'code': code if code in SECTORS else '', 'scr': x.get('scr', '')}
        if not x['listed']:
            why = ('estimate below USD 3.5M a year and no growth, cash, marketing or strategic reason found'
                   + (f"; company review score {x['scr']} of 5" if x.get('scr') in ('1', '2', '3') else '; company not recognised in the review' if x.get('scr') == '?' else ''))
            below.append(dict(base, why=why)); out['below the threshold with no stated reason'] += 1; continue
        if code not in SECTORS: below.append(dict(base, why='business not identified: no sector could be assigned')); out['business not identified'] += 1; continue
        if sym in review.DROP: out['removed: ' + review.DROP[sym]] += 1; continue
        if x['listed'] and loose(re.sub(r'\(.*?\)', ' ', name)) in onmaster: out['already on the 15 Nov master under another ticker'] += 1; continue
        if sym in DUP_SYMS: out['second listing of a company already on the list'] += 1; continue
        if F1_OWNER.search(name): out['owner of the Formula 1 commercial rights (not a sponsor prospect)'] += 1; continue
        if not e: below.append(dict(base, why='qualifies on figures; company profile not written yet')); out['no profile yet'] += 1; continue
        flags = '' if sym in review.CLEAR_FLAG else clean(e.get('flags'))
        if flags.lower() in ('high', 'medium', 'low', 'none', 'n/a', '-'): flags = ''
        if build.DROP_FLAG.search(flags): out['delisted, bankrupt, sanctioned or not a commercial company'] += 1; continue
        if DUP_FLAG.search(flags): out['second share line of a company already counted'] += 1; continue
        rel = e.get('rel') if e.get('rel') in REL else 2; reach = e.get('reach') if e.get('reach') in REACH else 'Regional'
        cat = x['cat']
        if not cat:
            need = 4 if x['why'] and x['why'][0].startswith('company review') else 3
            if rel < need:
                below.append(dict(base, why=f"below the threshold; reason found in the figures ({'; '.join(x['why'])}) but the company profile gives strategic relevance {rel} of 5"))
                out['below the threshold: profile relevance too low for a Strategic Exception'] += 1; continue
            cat = 'Strategic Exception'
        e = dict(e); e.update(review.FIX.get(sym, {})); e['conf'] = clean(e.get('conf')).lower()
        kind, f1txt = f1_status(sym, c, e); kind = KIND_FIX.get(sym, kind) if kind else kind
        hq, hq_ok = build.headquarters(c, e)
        if not hq_ok and '(listing)' in hq: hq = 'Not confirmed (US-listed)'
        strat = strat_score(code, rel); fin = fin_score(k); sig, sigtxt = signal_score(f, e, signal_check(sym)); team = team_score(e, reach, kind)
        score = round(0.30 * strat + 0.25 * fin + 0.25 * sig + 0.20 * team, 1)
        acq = bool(ACQ.search(flags))
        pr = 'High' if score >= HIGH else 'Medium' if score >= MED else 'Lower'
        if rel <= 1 or acq: pr = 'Lower'
        if pr == 'High' and (e['conf'] == 'low' or rel < 3): pr = 'Medium'
        cf, cfwhy = confidence(dict(x, cat=x['cat']))
        notes = []
        if cat == 'Strategic Exception': notes.append('Strategic Exception because: ' + '; '.join(x['why']))
        if cfwhy: notes.append(f'capacity confidence {cf}: {cfwhy}')
        if f.get('mismatch'): notes.append('revenue in the SEC filing data and the market-data site differ widely: check the latest report')
        if f.get('page_mismatch'): notes.append('the figures page did not match the revenue held, so profit and cash were not taken from it')
        if e['conf'] == 'low': notes.append('company profile written with low confidence: check description, HQ and markets')
        if not hq_ok: notes.append('HQ city not confirmed')
        if flags: notes.append(('reported corporate status, confirm: ' if build.VERIFY_FLAG.search(flags) else '') + flags)
        if kind in ('group', 'note'): notes.append('check for a category conflict with the F1 link')
        if sym in review.NOTE: notes.append(review.NOTE[sym])
        rows.append(dict(base, e=e, cat=cat, why=x['why'], rel=rel, reach=reach, hq=hq, kind=kind, f1txt=f1txt, strat=strat, fin=fin, sig=sig, sigtxt=sigtxt, team=team,
                         score=score, priority=pr, cf=cf, notes=notes, gross=x['gross'], known=on_sheet(K, name), webnone=web_check(sym)[0] == 'none', webdone=bool(web_check(sym)[0])))
    # one line per company: keep the larger listing
    best = {}; drop = set()
    for r in sorted(rows, key=lambda r: -(r['f']['mcap'] or 0)):
        c = r['c']; dom = fl.regdom((c.get('sec') or {}).get('web') or (c.get('clay') or {}).get('domain') or '')
        keys = [('n', loose(re.sub(r'\(.*?\)', ' ', r['name'])) or loose(r['name']))]
        if any(k2 in best for k2 in keys): drop.add(id(r)); r['dup_of'] = next(best[k2]['name'] for k2 in keys if k2 in best); continue
        for k2 in keys: best[k2] = r
    out['second listing of a company already on the list'] += len(drop); dups = [(r['name'], r['dup_of']) for r in rows if id(r) in drop]
    rows = [r for r in rows if id(r) not in drop]
    rows.sort(key=lambda r: (RANK[r['priority']], -r['score'], -(r['f']['mcap'] or 0)))
    partners = [r for r in rows if r['kind'] == 'partner']; main = [r for r in rows if r['kind'] != 'partner']
    bysec = defaultdict(list)
    for r in main: bysec[r['code']].append(r)
    return {'rows': main, 'partners': partners, 'below': below, 'bysec': bysec, 'out': out, 'st': st, 'n': len(C), 'dups': dups}
def cells(r):
    c, e, f, k = r['c'], r['e'], r['f'], r['k']; grp = SECTORS[r['code']]['grp']
    if k['nodata']: cap = 'Not estimated: no revenue or profit figures in the sources used'
    else: cap = f"{usd(k['cap'])} a year: {k['basis']}"
    f1 = {'partner': 'CURRENT F1 PARTNER: ', 'group': 'F1 LINK IN THE GROUP, check for conflict: ', 'note': 'Possible F1 link, check: ', 'past': 'Earlier F1 link, not current: '}.get(r['kind'], '') + r['f1txt'] if r['kind'] else \
         'No current F1 partnership found (2025-26 roster of 424 partners' + ('; web search, Nov 2026' if r.get('webnone') else '') + ')'
    sports = clean(e.get('sports'))
    sp = f1.rstrip('.') + '. ' + ('Other sports (desk research, to verify): ' + sports.rstrip('.') if sports else 'No other sports sponsorship identified') + '.'
    src = build.col_sources(c, f)
    if not (c.get('sec') or {}).get('web'): src = re.sub(r'; company site: [^;]+', '', src)          # only websites taken from the company's own filings
    if f.get('page'):
        src += ('; stockanalysis.com Financials Overview for ' + ', '.join(f.get('page_used') or ['figures'])
                + (' (reporting currency, converted as the same share of the USD revenue)' if f.get('page_approx') else '') + ': ' + str(f['page'].get('source_url')))
    status = ('Status: figures from public sources (Nov 2026); F1 status checked by web search' + ('' if 'web search, 15 Nov' in r['f1txt'] or not r.get('webdone') else ' on 19 Nov 2026')
              + '; profile and other desk research not web-verified.') if r.get('webdone') else \
             'Status: figures from public sources (Nov 2026); profile, sponsorships and desk-research signals not web-verified.'
    if r['notes']: status += ' To verify: ' + '; '.join(n.rstrip('.') for n in r['notes']) + '.'
    return [r['name'], r['hq'], r['cat'], r['priority'], clean(e.get('desc')), f['rev'] if f['rev'] else 'Not available', f['mcap'] if f['mcap'] else 'Not available',
            cash_profit(f, grp), cap, r['cf'], r['reach'], sp, clean(e.get('rationale')), r['sigtxt'], 'Sources: ' + src + '. ' + status,
            SECTORS[r['code']]['name'], build.ticker(c, f['gap']), clean(e.get('markets')), r['score'], round(k['cap']) if not k['nodata'] else 'Not estimated', r['known']]
# ------------------------------------------------------------------ Excel
def style_sheet(ws, n):
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    head = PatternFill('solid', fgColor='1F3864'); extra = PatternFill('solid', fgColor='595959'); wrap = Alignment(wrap_text=True, vertical='top'); top = Alignment(vertical='top')
    fills = {'High': PatternFill('solid', fgColor='C6EFCE'), 'Medium': PatternFill('solid', fgColor='FFEB9C'), 'Lower': PatternFill('solid', fgColor='EDEDED'), 'Low': PatternFill('solid', fgColor='FCE4D6'),
             'Large': PatternFill('solid', fgColor='BDD7EE'), 'Mid-Level': PatternFill('solid', fgColor='DDEBF7'), 'Challenger': PatternFill('solid', fgColor='E2EFDA'),
             'Emerging': PatternFill('solid', fgColor='FFF2CC'), 'Strategic Exception': PatternFill('solid', fgColor='FCE4D6')}
    money = '[>=1000000000]$#,##0.00,,,"B";[>=1000000]$#,##0,,"M";$#,##0'
    for j, w in enumerate(WIDTH, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
        h = ws.cell(1, j); h.font = Font(bold=True, color='FFFFFF'); h.fill = head if j <= 15 else extra; h.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[1].height = 44; ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(COLS))}{max(n + 1, 2)}'
    longcols = {5, 8, 9, 12, 13, 14, 15, 18, 21}
    for i in range(2, n + 2):
        ws.row_dimensions[i].height = 62
        for j in range(1, len(COLS) + 1): ws.cell(i, j).alignment = wrap if j in longcols else top
        for j in (6, 7):
            if isinstance(ws.cell(i, j).value, (int, float)): ws.cell(i, j).number_format = money
        if isinstance(ws.cell(i, 20).value, (int, float)): ws.cell(i, 20).number_format = '[>=1000000000]$#,##0.00,,,"B";$#,##0.0,,"M"'
        ws.cell(i, 19).number_format = '0.0'
        for j in (3, 4, 10):
            fl = fills.get(ws.cell(i, j).value)
            if fl: ws.cell(i, j).fill = fl
def add_sheet(wb, title, rows, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title; ws.append(COLS)
    for r in rows: ws.append(cells(r))
    style_sheet(ws, len(rows)); return ws
KEY = [('What this workbook is', 'Listed companies that meet the updated parameters of 19 Nov 2026 and were NOT on the public-company master of 15 Nov 2026 (7,558 companies). Columns 1-15 follow the order you set; six working columns follow in grey.'),
       ('Entry test (any one)', 'Annual revenue USD 100M+, market value USD 500M+, cash USD 150M+, or disclosed marketing spend USD 20M+. Funds, shells, second share lines, delisted and Russian-market companies are removed.'),
       ('Estimated Sponsorship Capacity', 'The strongest applicable indicator. Technology: 0.4% of revenue or 8% of marketing spend. Consumer: 0.3% of revenue or 8% of marketing spend. Financial services: 0.25% of revenue or 1.5% of pre-tax profit. Industrial and other: 0.3% of revenue or 1.5% of pre-tax profit. Cash-rich: 1.2% of cash (1.5% in emerging sectors), cut to 75%, 50% or 25% when cash covers under 4, 2 or 1 years of losses. Loss-makers: the operating estimate is cut 40%, and halved again when losses exceed cash. Marketing spend is the disclosed figure where there is one, otherwise the sector benchmark. It is an estimate, not a confirmed budget; very large figures only mean "well above USD 12M".'),
       ('F1 Investment Category', 'Large USD 12M+; Mid-Level USD 6-12M; Challenger USD 4-6M; Emerging USD 3.5-4M; Strategic Exception = below USD 3.5M or figures missing, with a stated reason (near miss at USD 3M+, revenue growth of 20%+, large market value or cash in a sector that fits F1, disclosed marketing spend of USD 20M+, an emerging sector, or a clear commercial case found in the company review). The reason is written in column 15.'),
       ('Outreach Priority', 'From the Priority Score (0-100): 30% strategic fit with F1 (sector fit and company relevance), 25% financial capacity, 25% buying signals, 20% team fit, B2B value and activation potential (with a deduction for an existing F1 link). High = 52 or more, Medium = 42-52, Lower = under 42. A company being acquired or with relevance 1 of 5 is Lower; a profile written with low confidence cannot be High.'),
       ('Financial Capacity Confidence', 'High = profitable, with revenue and profit both in the sources. Medium = loss-making, profit not found, or the estimate rests on cash. Low = below the threshold, figures missing, or losses large relative to cash. The reason is in column 15.'),
       ('Existing Sports / F1 Partnerships', 'F1 links are flagged, not excluded. "CURRENT F1 PARTNER" companies are on their own tab. "F1 LINK IN THE GROUP" = the parent, a subsidiary or a sister company is a partner: check for a category conflict. Other sports sponsorships come from desk research and are to verify. The High-priority companies with no known F1 link were also checked with a live web search on 19 Nov 2026; any found to be current sponsors were moved to the partner tab.'),
       ('Buying Signals', 'From figures: revenue growth of 8%+ (20%+ counts more) and disclosed marketing spend of USD 20M+. From desk research (marked "to verify"): funding or listing, leadership change, rebrand, expansion, new sponsorship, product launch. For the High-priority companies one desk-research signal each was checked with a web search on 19 Nov 2026; the result is written in the cell. None of these is a stated sponsorship intention.'),
       ('Financial figures', 'SEC annual filings where the company files in the US; otherwise companiesmarketcap.com (trailing 12 months) or the stockanalysis.com exchange lists and Financials Overview pages, converted to USD at Nov 2026 rates. "Not available" means not in the sources used, not zero.'),
       ('Profile fields', 'Headquarters, description, reach, markets and rationale are desk-research summaries that were not individually web-verified.'),
       ('Below Threshold tab', 'Companies that pass the entry test but have an estimate under USD 3.5M and no stated reason. They are kept for transparency and were each scored 1-5 for commercial motivation; a 4 or 5 moved the company onto the list.'),
       ('Not used', 'Apollo was not used. Crunchbase could not be used: the account allowance is exhausted until 1 Dec 2026.')]
def write(A):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook(); rows = A['rows']; ws = wb.active; ws.title = 'Summary'
    S = [('title', f'Listed companies under the updated F1 parameters: new brands ({DATE})'),
         ('text', f"{len(rows):,} listed companies that meet the updated parameters and were not on the 15 Nov master, in {sum(1 for c in ORDER if A['bysec'][c])} sector tabs. "
                  f"A further {len(A['partners'])} already hold an F1 deal themselves and are flagged on their own tab. Capacity figures are estimates, not confirmed budgets."),
         ('blank', ''), ('head', ['Sector', 'Companies', 'High', 'Medium', 'Lower'] + CATS)]
    for code in ORDER:
        L = A['bysec'][code]
        if not L: continue
        pc = Counter(r['priority'] for r in L); cc = Counter(r['cat'] for r in L)
        S.append(('row', [f"{code} {SECTORS[code]['name']}", len(L), pc['High'], pc['Medium'], pc['Lower']] + [cc[c] for c in CATS]))
    pc = Counter(r['priority'] for r in rows); cc = Counter(r['cat'] for r in rows)
    S.append(('total', ['Total', len(rows), pc['High'], pc['Medium'], pc['Lower']] + [cc[c] for c in CATS]))
    S += [('blank', ''), ('sub', 'How the list was reached')]
    st = A['st']; out = A['out']
    S.append(('kv', ['Listed companies reviewed (three sources, incl. 4,485 added for the new USD 100M revenue / USD 500M market value floor)', sum(st.values()) - st['no sector yet']]))
    S.append(('kv', ['Already on the 15 Nov master (not repeated here)', st['on the 15 Nov master']]))
    S.append(('kv', ['Below the entry test', st['below the entry criteria']]))
    S.append(('kv', ['Funds, shells and second share lines', st['fund, shell or duplicate line']]))
    S.append(('kv', ['Russian market', st['Russian market']]))
    S.append(('kv', ['Pass the entry test but below USD 3.5M with no stated reason (Below Threshold tab)', len(A['below'])]))
    for k2, v in sorted(out.items(), key=lambda t: -t[1]):
        if v and not k2.startswith(('below the threshold', 'removed: ')) and k2 not in ('business not identified', 'no profile yet'): S.append(('kv', ['Taken out: ' + k2, v]))
    rem = sum(v for k2, v in out.items() if k2.startswith('removed: '))
    if rem: S.append(('kv', ['Taken out: taken private, merged, old ticker, second listing or on the US Entity List', rem]))
    S.append(('kv', ['Current F1 partners (flagged on their own tab)', len(A['partners'])]))
    S.append(('kv', ['Listed on the sector tabs', len(rows)]))
    S += [('blank', ''), ('sub', 'How to read the columns')] + [('kv', [a, b]) for a, b in KEY]
    ws.column_dimensions['A'].width = 62
    for j, w in zip('BCDEFGHIJ', [11, 8, 9, 8, 8, 10, 11, 10, 18]): ws.column_dimensions[j].width = w
    for kind, v in S:
        if kind == 'blank': ws.append(['']); continue
        ws.append(v if isinstance(v, list) else [v]); i = ws.max_row
        if kind == 'title': ws.cell(i, 1).font = Font(bold=True, size=14)
        elif kind == 'sub': ws.cell(i, 1).font = Font(bold=True, size=12)
        elif kind in ('head', 'total'):
            for j in range(1, 11):
                ws.cell(i, j).font = Font(bold=True, color='FFFFFF' if kind == 'head' else '000000')
                if kind == 'head': ws.cell(i, j).fill = PatternFill('solid', fgColor='1F3864'); ws.cell(i, j).alignment = Alignment(wrap_text=True, vertical='center')
        elif kind == 'kv':
            ws.cell(i, 1).font = Font(bold=True); ws.cell(i, 1).alignment = Alignment(wrap_text=True, vertical='top')
            if isinstance(v[1], str):
                ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=14); ws.cell(i, 2).alignment = Alignment(wrap_text=True, vertical='top'); ws.row_dimensions[i].height = max(15, 15 * (len(v[1]) // 135 + 1))
        elif kind == 'text': ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=14); ws.cell(i, 1).alignment = Alignment(wrap_text=True, vertical='top'); ws.row_dimensions[i].height = max(15, 15 * (len(v) // 190 + 1))
    add_sheet(wb, 'All New Brands', rows)
    for code in ORDER:
        if A['bysec'][code]: add_sheet(wb, f'{code} {TAB[code]}'[:31], A['bysec'][code])
    add_sheet(wb, 'Current F1 Partners', A['partners'])
    wb2 = wb.create_sheet('Below Threshold')
    hdr = ['Company Name', 'Country', 'Sector', 'Stock Ticker / Exchange', 'Annual Revenue (USD)', 'Market Capitalization (USD)', 'Estimated Sponsorship Capacity (USD a year)', 'Why it is not on the list']
    wb2.append(hdr)
    for b in sorted(A['below'], key=lambda b: (b['code'] or 'zz', -(b['k']['cap'] or 0))):
        f = b['f']
        wb2.append([b['name'], b['c']['country'], SECTORS[b['code']]['name'] if b['code'] else 'Not identified', build.ticker(b['c'], f['gap']), f['rev'] if f['rev'] else 'Not available',
                    f['mcap'] if f['mcap'] else 'Not available', round(b['k']['cap']) if not b['k']['nodata'] else 'Not estimated', b['why']])
    for j, w in enumerate([38, 18, 34, 26, 14, 14, 16, 90], 1):
        wb2.column_dimensions[get_column_letter(j)].width = w
        h = wb2.cell(1, j); h.font = Font(bold=True, color='FFFFFF'); h.fill = PatternFill('solid', fgColor='1F3864'); h.alignment = Alignment(wrap_text=True, vertical='center')
    wb2.row_dimensions[1].height = 44; wb2.freeze_panes = 'B2'; wb2.auto_filter.ref = f'A1:H{len(A["below"]) + 1}'
    for i in range(2, len(A['below']) + 2):
        for j in (5, 6):
            if isinstance(wb2.cell(i, j).value, (int, float)): wb2.cell(i, j).number_format = '[>=1000000000]$#,##0.00,,,"B";[>=1000000]$#,##0,,"M";$#,##0'
        if isinstance(wb2.cell(i, 7).value, (int, float)): wb2.cell(i, 7).number_format = '$#,##0.0,,"M"'
    ks = wb.create_sheet('Key'); ks.column_dimensions['A'].width = 34; ks.column_dimensions['B'].width = 130
    for a, b in KEY:
        ks.append([a, b]); ks.cell(ks.max_row, 1).font = Font(bold=True)
        ks.cell(ks.max_row, 1).alignment = Alignment(vertical='top'); ks.cell(ks.max_row, 2).alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(OUT); return OUT
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'; A = assemble(); rows = A['rows']
    if cmd == 'check':
        print('listed', len(rows), '| current F1 partners', len(A['partners']), '| below threshold tab', len(A['below']))
        for k2, v in sorted(A['out'].items(), key=lambda t: -t[1]): print(f'  out {v:5d}  {k2}')
        print('priority', Counter(r['priority'] for r in rows), '| category', Counter(r['cat'] for r in rows), '| confidence', Counter(r['cf'] for r in rows))
        print('F1 link kinds', Counter(r['kind'] for r in rows + A['partners']), '| on the brand sheet', Counter(r['known'][:3] for r in rows))
        for hi, md in ((62, 50), (55, 45), (52, 42), (50, 40), (48, 38)): print('  cut-offs', hi, md, Counter('High' if r['score'] >= hi else 'Medium' if r['score'] >= md else 'Lower' for r in rows))
        sc = sorted(r['score'] for r in rows); print('score deciles', [sc[int(len(sc) * q / 10)] for q in range(10)], sc[-1])
        for nm in ('strat', 'fin', 'sig', 'team'):
            v = sorted(r[nm] for r in rows); print(f'  {nm:5s} deciles', [round(v[int(len(v) * q / 10)]) for q in range(10)], round(v[-1]))
        for code in ORDER:
            L = A['bysec'][code]; pc = Counter(r['priority'] for r in L)
            if L: print(f"{code} {TAB[code]:30s} {len(L):4d}  H {pc['High']:3d} M {pc['Medium']:3d} L {pc['Lower']:3d}  top: " + ', '.join(r['name'][:22] for r in L[:5]))
    elif cmd == 'write': print(len(rows), write(A))
