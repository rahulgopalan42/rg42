"""New-parameters run (19 Nov 2026): shared data and rules.
Entry (any one): revenue USD 100M+, market value USD 500M+, cash USD 150M+, disclosed marketing spend USD 20M+.
Capacity estimate = the strongest of: the sector's revenue / marketing / profit test, and 1.2-1.5% of cash adjusted for losses and runway.
Categories: Large 12M+, Mid-Level 6-12M, Challenger 4-6M, Emerging 3.5-4M, Strategic Exception below that (only with a stated reason).
F1 links are flagged, not excluded. No cap per sector."""
import glob, gzip, html, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build                      # keep first (see np_select.py)
import sectors35
# sectors added for this run: every sector is now in scope
NEW_S = [('47', 'Tobacco & nicotine', 3, 0.03, 'ind', 'cigarettes, cigars, vaping, nicotine pouches, tobacco leaf'),
         ('48', 'Packaging, paper & forest products', 4, 0.005, 'ind', 'packaging makers, pulp and paper, labels, containers, timber'),
         ('49', 'Agriculture, agribusiness & food commodities', 4, 0.005, 'ind', 'farming, plantations, grain and sugar processors, animal feed, fertiliser, fishing'),
         ('50', 'Other operating companies', 4, 0.01, 'ind', 'operating businesses that fit no other sector')]
for c, n, fit, m, g, d in NEW_S:
    sectors35.SECTORS.setdefault(c, {'code': c, 'name': n, 'fit': fit, 'mkt': m, 'grp': g, 'scope': d})
    if c not in sectors35.ORDER: sectors35.ORDER.append(c)
from sectors35 import SECTORS, ORDER
from qualify import financials, capacity, fm
from f1links import f1_link
import review
def jl(pattern, base=H):
    out = []
    for f in sorted(glob.glob(os.path.join(base, pattern))):
        for l in open(f, encoding='utf-8'):
            l = l.strip()
            if not l: continue
            try: d = json.loads(l)
            except Exception: continue
            if isinstance(d, dict): out.append(d)
    return out
def load(n):
    p = os.path.join(H, 'data', n)
    return json.load(gzip.open(p, 'rt')) if os.path.exists(p) else []
def universe():
    U = {}
    for n in ('universe.json.gz', 'universe2.json.gz', 'universe3.json.gz'):
        for c in load(n):
            if c['sym'] not in U: U[c['sym']] = c
    return U
def classes():
    """sector code per symbol: the earlier classification, overridden by this run's (which has no '00')"""
    cls = {}
    for f in sorted(glob.glob(os.path.join(H, 'classify', 'out_*.txt'))) + sorted(glob.glob(os.path.join(H, 'np', 'classify', 'out_*.txt'))):
        for line in open(f, encoding='utf-8', errors='ignore'):
            p = line.strip().split('|')
            if len(p) == 2 and p[1].strip(): cls[p[0].strip()] = p[1].strip()
    return cls
def profiles():
    """company profiles: earlier pass, then this run's (which carry the extra fields sports, signals, b2b, act)"""
    E = {d['sym']: d for d in jl('enrich/out_*.jsonl') if d.get('sym')}
    for d in jl('fix/out_*.jsonl'):
        e = E.get(d.get('sym'))
        if not e: continue
        for k, lo, hi in (('desc', 10, 20), ('markets', 5, 28), ('rationale', 8, 28)):
            if d.get(k) and lo <= len(str(d[k]).split()) <= hi: e[k] = re.sub(r'\s+', ' ', d[k]).strip()
    N = {d['sym']: d for d in jl('np/enrich/out_*.jsonl') if d.get('sym')}
    S = {d['sym']: d for d in jl('np/extra/out_*.jsonl') if d.get('sym')}           # the four new fields for companies profiled earlier
    for sym, d in N.items(): E[sym] = dict(E.get(sym, {}), **d)
    for sym, d in S.items():
        if sym in E:
            for k in ('sports', 'signals', 'b2b', 'act'):
                if k in d and k not in N.get(sym, {}): E[sym][k] = d[k]
    return E
def runway_factor(f):
    """cash-based capacity is cut when the company is burning its cash"""
    pt = f.get('pretax'); cash = f.get('cash') or 0
    if pt is None or pt >= 0 or not cash: return 1.0
    yrs = cash / abs(pt)
    return 0.25 if yrs < 1 else 0.5 if yrs < 2 else 0.75 if yrs < 4 else 1.0
def estimate(f, code):
    """capacity estimate under the new parameters -> dict(cap, basis, ev, loss, stressed, nodata, ops, liq)"""
    s = SECTORS.get(code) or SECTORS['50']; g = s['grp']; rev = f['rev'] or 0; pt = f['pretax']; cash = f['cash'] or 0
    mb = max(f['mkt'], 0.5 * rev * s['mkt']) if f['mkt'] else rev * s['mkt']
    if g == 'consumer': ops = max(0.08 * mb, 0.003 * rev)
    elif g in ('tech', 'emerging'): ops = max(0.08 * mb, 0.004 * rev)
    elif g == 'fin': ops = max(0.0025 * rev, 0.015 * (pt or 0))
    else: ops = max(0.003 * rev, 0.015 * (pt or 0))
    loss = pt is not None and pt < 0
    stressed = loss and cash < abs(pt) and abs(pt) > 0.25 * max(rev, 1)
    eff = ops * (0.6 if loss else 1.0) * (0.5 if stressed else 1.0)
    liq = 0 if g == 'fin' else (0.015 if g == 'emerging' else 0.012) * cash * runway_factor(f)
    nodata = not f['rev'] and pt is None
    cap = max(eff, liq)
    if cap == liq and liq > eff: basis = 'cash reserves (' + ('1.5%' if g == 'emerging' else '1.2%') + ' of cash' + (', cut for cash burn' if runway_factor(f) < 1 else '') + ')'
    elif f['mkt'] and g in ('consumer', 'tech', 'emerging') and 0.08 * mb >= (0.003 if g == 'consumer' else 0.004) * rev: basis = '8% of disclosed marketing spend'
    elif g == 'consumer' and 0.08 * mb > 0.003 * rev: basis = '8% of marketing spend estimated at the sector rate'
    elif g in ('tech', 'emerging') and 0.08 * mb > 0.004 * rev: basis = '8% of marketing spend estimated at the sector rate'
    elif g in ('fin', 'ind') and 0.015 * (pt or 0) > (0.0025 if g == 'fin' else 0.003) * rev: basis = '1.5% of pre-tax profit'
    else: basis = {'consumer': '0.3%', 'tech': '0.4%', 'emerging': '0.4%', 'fin': '0.25%', 'ind': '0.3%'}[g] + ' of revenue'
    if loss and cap == eff and eff > 0: basis += ', cut 40% for losses'
    if nodata: basis = 'no revenue or profit figures in the sources used'
    return {'cap': cap, 'basis': basis, 'loss': loss, 'stressed': stressed, 'nodata': nodata, 'ops': ops, 'liq': liq, 'eff': eff}
def category(cap):
    return 'Large' if cap >= 12e6 else 'Mid-Level' if cap >= 6e6 else 'Challenger' if cap >= 4e6 else 'Emerging' if cap >= 3.5e6 else ''
def entry(f):
    return (f['rev'] or 0) >= 1e8 or (f['mcap'] or 0) >= 5e8 or (f['cash'] or 0) >= 1.5e8 or (f['mkt'] or 0) >= 2e7
def exception_reasons(f, k, code):
    """data reasons why a company below USD 3.5M (or with thin data) may still have commercial potential.
    Size alone (market value, cash) only counts in sectors with an F1 fit of 6 or more."""
    s = SECTORS.get(code) or SECTORS['50']; r = []; fit = s['fit']
    rev = f['rev'] or 0; mc = f['mcap'] or 0; cash = f['cash'] or 0; cap = k['cap']
    if 3e6 <= cap < 3.5e6: r.append(f"near miss: estimate {fm(cap)} a year, inside the USD 3M+ objective")
    elif 2e6 <= cap < 3e6 and fit >= 8: r.append(f"estimate {fm(cap)} a year in a high-fit sector")
    if f.get('growth') is not None and f['growth'] >= 0.2: r.append(f"revenue up {f['growth'] * 100:.0f}% year on year")
    if mc >= 2e9 and fit >= 6: r.append(f'market value {fm(mc)}')
    if cash >= 1.5e8 and s['grp'] in ('tech', 'emerging', 'consumer'): r.append(f'cash {fm(cash)}')
    if (f['mkt'] or 0) >= 2e7: r.append(f"disclosed marketing spend {fm(f['mkt'])}")
    if fit >= 8 and rev >= 1e8 and mc >= 5e8 and not r: r.append('high-fit sector with revenue USD 100M+ and market value USD 500M+')
    if s['grp'] == 'emerging': r.append('emerging sector')
    if k['nodata'] and mc >= 1e9 and fit >= 6: r.append('financial figures missing; market value USD 1B+')
    return r
def f1_flag(sym, c, e):
    """(kind, text): kind = 'partner' (holds a current F1 deal itself), 'group' (parent, subsidiary or sister of a partner), 'note', or ''"""
    name = re.sub(r'\s+', ' ', html.unescape(c['name'])).strip(); sec = c.get('sec') or {}
    web = sec.get('web') or (c.get('clay') or {}).get('domain') or ''
    link, _ = f1_link(name, web); txt = ''
    if link: txt = link
    elif sym in review.ROSTER_EXTRA: txt = review.ROSTER_EXTRA[sym]
    elif sym in review.F1 and review.F1[sym][0] in ('exclude', 'note'): txt = review.F1[sym][1]; 
    elif e and str(e.get('f1') or '').strip(): txt = str(e['f1']).strip()
    if not txt or (sym in review.F1 and review.F1[sym][0] == 'clear'): return '', ''
    if sym in review.F1 and review.F1[sym][0] == 'note': return 'note', txt
    group = bool(re.search(r'(?i)parent / owner|parent of|part of|owned by|owner of|subsidiar|sister|brand of|\bowns\b|majority|taken private by|stake', txt))
    return ('group' if group else 'partner'), txt

# ---------------------------------------------------------------- extra public figures and the commercial screen
def fin_pages():
    """the 'Financials Overview' page figures per symbol (np_fin.py)"""
    return {d['sym']: d for d in jl('np/fin/out.jsonl') if d.get('found')}
def screen_scores():
    """commercial-motivation score (1-5 or ?) for companies below the capacity threshold (np_screen_brief.md)"""
    S = {}
    for f in sorted(glob.glob(os.path.join(H, 'np', 'screen', 'out_*.txt'))):
        for line in open(f, encoding='utf-8', errors='ignore'):
            p = line.strip().split('|')
            if len(p) == 2: S[p[0].strip()] = p[1].strip()
    return S
_STOP = set('the inc incorporated corp corporation co company ltd limited llc plc sa ag se nv bv gmbh spa ab as oy holdings holding group'.split())
def _toks(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', html.unescape(str(s))).encode('ascii', 'ignore').decode().lower()
    return [t for t in re.split(r'[^a-z0-9]+', s) if t and t not in _STOP]
def same_company(name, title):
    a = _toks(re.sub(r'\(.*?\)', ' ', name)); b = _toks(re.sub(r'\([A-Z]+:[^)]*\)|\([A-Z.\-]+\)|Financials Overview', ' ', title))
    if not a or not b: return False
    return a[0] in b or b[0] in a or ''.join(a)[:6] == ''.join(b)[:6]
def apply_fin(f, c, d):
    """fills profit, cash, debt, cash flow and revenue growth from the page where the first sources had none. Figures are in the
    reporting currency; they are converted with the exchange-list rate, or (no rate held) as the same share of the USD revenue."""
    cur = str(d.get('currency') or '').upper(); u = {'millions': 1e6, 'thousands': 1e3, 'billions': 1e9}.get(str(d.get('unit') or 'millions').lower(), 1e6)
    rp = d.get('revenue_ttm') or d.get('revenue_fy'); sa = c.get('sa') or {}; approx = False
    if not sa and not same_company(c['name'], d.get('title', '')): return False
    if cur == 'USD': mult = u
    elif sa and sa.get('cur') == cur and sa.get('fx'): mult = u * sa['fx']
    elif f['rev'] and rp and rp > 0: mult = f['rev'] / rp; approx = True
    else: return False
    if f['rev'] and rp and not approx and not 0.4 < rp * mult / f['rev'] < 2.5: f['page_mismatch'] = True; return False
    used = []
    if f['pretax'] is None:
        pm = d.get('pretax_margin_ttm_pct'); rt = d.get('revenue_ttm')
        if pm is not None and rt: f['pretax'] = pm / 100 * rt * mult; f['pretax_kind'] = 'Pre-tax profit'; f['pretax_ttm'] = True; used.append('profit')
        elif d.get('netinc_ttm') is not None: f['pretax'] = d['netinc_ttm'] * mult; f['pretax_kind'] = 'Net income'; f['pretax_ttm'] = True; used.append('profit')
        elif d.get('opinc_ttm') is not None: f['pretax'] = d['opinc_ttm'] * mult; f['pretax_kind'] = 'Operating profit'; f['pretax_ttm'] = True; used.append('profit')
    if not f['cash'] and d.get('cash'): f['cash'] = d['cash'] * mult; used.append('cash')
    if not f['debt'] and d.get('debt'): f['debt'] = d['debt'] * mult
    if f['fcf'] is None and d.get('fcf_ttm') is not None: f['fcf'] = d['fcf_ttm'] * mult; f['capex'] = f['capex'] or 1
    if f['growth'] is None:
        g = d.get('growth_ttm_pct'); note = 'trailing 12 months to ' + str(d.get('ttm_to') or 'the latest quarter')
        if g is None: g = d.get('growth_fy_pct'); note = str(d.get('fy') or 'latest fiscal year')
        if g is not None and -90 < g < 500: f['growth'] = g / 100; f['growth_note'] = note; used.append('growth')
    if not f['rev'] and rp: f['rev'] = rp * mult; f['rev_src'] = 'page'; used.append('revenue')
    f['page'] = d; f['page_used'] = used; f['page_approx'] = approx
    return True
