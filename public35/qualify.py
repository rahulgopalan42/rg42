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
Usage: imported by build.py"""
import math
from sectors35 import SECTORS
def fm(v):
    if v is None: return ''
    a = abs(v); s = '-' if v < 0 else ''
    return f'{s}${a/1e9:,.2f}B' if a >= 1e9 else f'{s}${a/1e6:,.0f}M' if a >= 1e6 else f'{s}${a:,.0f}'
def financials(c):
    """the best available figures for one company and the text for the spreadsheet columns"""
    sec = c.get('sec') or {}; f = {}
    rev_ttm = c.get('revenue') or None; rev_sec = sec.get('rev25')
    f['rev'] = rev_sec or rev_ttm; f['rev_src'] = 'sec' if rev_sec else 'cmc' if rev_ttm else ''
    f['rev_ttm'] = rev_ttm; f['mcap'] = c.get('mcap')
    f['pretax'] = c.get('earnings') if c.get('earnings') not in (None, 0) else sec.get('pretax25')
    f['cash'] = c.get('cash') or None; f['debt'] = c.get('debt') or None
    f['opm'] = c['opmargin'] / 100 if c.get('opmargin') not in (None, 0) else None
    f['growth'] = (sec['rev25'] / sec['rev24'] - 1) if sec.get('rev25') and sec.get('rev24') and sec['rev24'] > 0 else None
    f['opinc'] = sec.get('opinc25'); da = sec.get('da25') or sec.get('da225')
    f['ebitda'] = f['opinc'] + da if f['opinc'] is not None and da else None
    f['fcf'] = sec['cfo25'] - (sec.get('capex25') or 0) if sec.get('cfo25') is not None else None
    adv = sec.get('adv25') or sec.get('mktadv25') or sec.get('mkt25')
    f['mkt'] = adv; f['mkt_kind'] = 'Advertising expense' if sec.get('adv25') else 'Marketing and advertising expense' if sec.get('mktadv25') else 'Marketing expense' if sec.get('mkt25') else ''
    f['sellmkt'] = sec.get('sellmkt25')
    # a revenue mismatch between the filing and the market-data site usually means a wrong ticker match
    f['mismatch'] = bool(rev_sec and rev_ttm and not (0.4 < rev_sec / rev_ttm < 2.5))
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
