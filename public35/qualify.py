"""Financial screen for the listed-company database. No hard revenue or market-cap cut-off: every classified company
is evaluated for whether it could credibly fund USD 4M+ a year, with a test that depends on its sector group.

capacity from operations (cap_ops), USD a year:
  consumer : the larger of 8% of the marketing budget (disclosed advertising / marketing expense, else revenue x the
             sector's typical rate) and 0.3% of revenue
  tech     : the larger of 8% of the marketing budget and 0.4% of revenue
  fin      : the larger of 0.25% of revenue and 1.5% of pre-tax profit
  ind      : the larger of 0.3% of revenue and 1.5% of pre-tax profit
  emerging : as tech
capacity from liquidity (cap_liq): 1.2% of cash on hand (1.5% for emerging), not used for banks and insurers
evidence:
  Strong Evidence    cap_ops >= 4M, profitable (pre-tax > 0), revenue and earnings both known
  Plausible Capacity cap_ops >= 4M but loss-making or earnings unknown; or cap_ops 3-4M; or cap_liq >= 4M (cash-rich, early revenue);
                     or a USD 5B+ growth company with USD 250M+ cash; or USD 1B+ market value with no financial figures in the sources
  Insufficient       everything else (not listed)
category: Challenger 4-6M, Mid-level 6-12M, Large 12M+ from cap_ops (loss-making: cap_ops x 0.6);
          To Verify when the only support is cash or a near-miss.
Usage: imported by screen.py and build.py"""
import math
from sectors35 import SECTORS
def fm(v):
    if v is None: return ''
    a = abs(v); s = '-' if v < 0 else ''
    return f'{s}${a/1e9:,.2f}B' if a >= 1e9 else f'{s}${a/1e6:,.0f}M' if a >= 1e6 else f'{s}${a:,.0f}'
def financials(c, grp=None, gap=None):
    """the best available figures for one company. SEC filing figures (latest fiscal year filed: FY2026 where it is already
    out, else FY2025) come first, then the market-data site (trailing twelve months), then the gap-fill lookup.
    grp = the sector group; for banks and insurers the market-data revenue is used because the filing tag is often partial."""
    sec = c.get('sec') or {}; f = {}
    y = '26' if sec.get('rev26') else '25' if sec.get('rev25') else ''; p = {'26': '25', '25': '24'}.get(y, '')
    rev_ttm = c.get('revenue') or None; rev_sec = sec.get('rev' + y) if y else None
    f['mismatch'] = bool(rev_sec and rev_ttm and not (0.4 < rev_sec / rev_ttm < 2.5))      # usually a wrong ticker match or a unit error in the filing data
    partial = bool(grp == 'fin' and rev_sec and rev_ttm and not (0.7 < rev_sec / rev_ttm < 1.4))
    use_sec = bool(rev_sec) and not f['mismatch'] and not partial
    f['fy'] = y if use_sec else ''; f['fy_end'] = sec.get('end' + y) if use_sec else None; f['accn'] = sec.get('accn' + y) if use_sec else None
    f['rev'] = rev_sec if use_sec else rev_ttm; f['rev_src'] = 'sec' if use_sec else ('lst' if c.get('src') == 'sa' else 'cmc') if rev_ttm else ''      # lst = exchange list (second universe)
    f['rev_ttm'] = rev_ttm; f['mcap'] = c.get('mcap'); f['assets'] = c.get('assets') or None
    f['pretax'] = c.get('earnings') if c.get('earnings') not in (None, 0) else (sec.get('pretax' + y) if use_sec else None)
    f['pretax_kind'] = 'Pre-tax profit'; f['pretax_ttm'] = c.get('earnings') not in (None, 0)
    f['cash'] = c.get('cash') or None; f['debt'] = c.get('debt') or None
    f['opm'] = c['opmargin'] / 100 if c.get('opmargin') not in (None, 0) else None
    for k in ('growth', 'opinc', 'ebitda', 'fcf', 'cfo', 'capex', 'mkt', 'sellmkt', 'netinc', 'pretax_fy'): f[k] = None
    f['mkt_kind'] = ''; f['mkt_fy'] = ''; f['sellmkt_fy'] = ''
    if use_sec:
        prev = sec.get('rev' + p) if p else None
        g = rev_sec / prev - 1 if prev and prev > 0 else None
        f['growth'] = g if g is not None and -0.9 < g < 5 else None
        f['opinc'] = sec.get('opinc' + y); da = sec.get('da' + y) or sec.get('da2' + y)
        if f['opinc'] is not None and abs(f['opinc']) > 1.5 * rev_sec: f['opinc'] = None
        f['ebitda'] = f['opinc'] + da if f['opinc'] is not None and da and 0 < da < rev_sec else None
        f['cfo'] = sec.get('cfo' + y); f['capex'] = sec.get('capex' + y)
        f['fcf'] = f['cfo'] - (f['capex'] or 0) if f['cfo'] is not None else None
        f['netinc'] = sec.get('netinc' + y); f['pretax_fy'] = sec.get('pretax' + y)
        for yy in (y, p):                                                   # advertising lines are not tagged every year: take the latest of the two
            if not yy: continue
            for tag, kind in (('adv', 'Advertising expense'), ('mktadv', 'Marketing and advertising expense'), ('mkt', 'Marketing expense')):
                v = sec.get(tag + yy)
                if v and 0 < v < 0.6 * rev_sec and not f['mkt']: f['mkt'] = v; f['mkt_kind'] = kind; f['mkt_fy'] = yy
            v = sec.get('sellmkt' + yy)
            if v and 0 < v < 0.9 * rev_sec and not f['sellmkt']: f['sellmkt'] = v; f['sellmkt_fy'] = yy
    f['gap'] = None
    if gap and not f['rev'] and f['pretax'] is None:                        # no figures in either source: use the gap-fill lookup
        f['rev'] = gap.get('revenue_usd') or None; f['rev_src'] = 'gap' if f['rev'] else ''
        if gap.get('pretax_usd') is not None: f['pretax'] = gap['pretax_usd']
        elif gap.get('net_income_usd') is not None: f['pretax'] = gap['net_income_usd']; f['pretax_kind'] = 'Net income'
        if gap.get('cash_usd') and not f['cash']: f['cash'] = gap['cash_usd']
        f['gap'] = gap
    return f
def capacity(f, sector):
    s = SECTORS[sector]; g = s['grp']; rev = f['rev'] or 0; pt = f['pretax']; cash = f['cash'] or 0
    mb = max(f['mkt'], 0.5 * rev * s['mkt']) if f['mkt'] else rev * s['mkt']        # narrow 'advertising cost' lines understate marketing: floor at half the sector rate
    if g == 'consumer': ops = max(0.08 * mb, 0.003 * rev)
    elif g in ('tech', 'emerging'): ops = max(0.08 * mb, 0.004 * rev)
    elif g == 'fin': ops = max(0.0025 * rev, 0.015 * (pt or 0))
    else: ops = max(0.003 * rev, 0.015 * (pt or 0))
    liq = 0 if g == 'fin' else (0.015 if g == 'emerging' else 0.012) * cash
    stressed = pt is not None and pt < 0 and cash < 1.0 * abs(pt) and abs(pt) > 0.25 * max(rev, 1)
    if stressed: ops *= 0.5; liq *= 0.5
    loss = pt is not None and pt < 0
    mcap = f['mcap'] or 0
    nodata = not f['rev'] and pt is None                 # no fundamentals in the sources used (mostly Gulf-listed companies)
    access = g in ('tech', 'emerging') and mcap >= 5e9 and cash >= 2.5e8      # large, well-funded growth company: can raise capital
    if ops >= 4e6 and not loss and pt is not None and rev: ev = 'Strong Evidence'
    elif ops >= 4e6 or liq >= 4e6 or ops >= 3e6: ev = 'Plausible Capacity'
    elif access or (nodata and mcap >= 1e9): ev = 'Plausible Capacity'
    else: ev = 'Insufficient'
    eff = ops * (0.6 if loss else 1.0)
    if ev == 'Insufficient': cat = ''
    elif ops >= 4e6 and eff >= 4e6: cat = 'Large' if eff >= 12e6 else 'Mid-level' if eff >= 6e6 else 'Challenger'
    elif ops >= 4e6: cat = 'Challenger'
    else: cat = 'To Verify'
    basis = ('marketing budget (disclosed)' if f['mkt'] and g in ('consumer', 'tech', 'emerging') and 0.08 * mb >= 0.004 * rev else
             'revenue and sector marketing rate' if g == 'consumer' else 'revenue / profit') if ops >= 3e6 else 'cash reserves'
    if nodata: basis = 'market value only: financial figures not available in the sources used'
    elif ops < 3e6 and liq < 4e6 and access: basis = 'access to capital (large, well-funded growth company)'
    return {'ops': ops, 'liq': liq, 'ev': ev, 'cat': cat, 'basis': basis, 'stressed': stressed, 'loss': loss, 'nodata': nodata, 'cap': max(eff, 0) if ops >= 3e6 else liq}
def cap_score(k, f):
    """financial capacity 0-100 for the priority score"""
    v = k['cap']
    base = 35 if k['cat'] == 'To Verify' else min(100, 40 + 60 * math.log(max(v, 4e6) / 4e6) / math.log(50e6 / 4e6))
    if f['growth'] is not None: base += 8 if f['growth'] >= 0.2 else 4 if f['growth'] >= 0.08 else -8 if f['growth'] <= -0.1 else 0
    if k['ev'] == 'Strong Evidence': base += 5
    if k['stressed']: base -= 15
    return max(0, min(100, base))
