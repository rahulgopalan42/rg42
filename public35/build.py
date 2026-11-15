"""Step 2 of the build: turn the screened, profiled companies into the deliverables.
  build.py check          counts, score distribution and things to review (writes nothing)
  build.py sectors        one workbook per sector in reports/public-companies-by-sector/
  build.py master         the master workbook (Master Companies, 35 sector tabs, Top 500 Prospects, Verification Required, Research Summary)
Inputs: data/universe.json.gz (market data + SEC filings), classify/out_*.txt (sector), enrich/out_*.jsonl (profile fields),
fix/out_*.jsonl (rewritten thin fields), gap/out_*.jsonl (figures for companies with none), review.py (manual decisions).

Priority score = 60% strategic relevance + 40% financial capacity.
  strategic = 25% sector fit (0-10 scale x 10) + 50% company relevance (research pass, 1-5) + 25% geographic reach
  financial = capacity score from qualify.cap_score (size of the estimated annual capacity, growth, evidence, stress)
  High = relevance 4-5 with a score of 60+, or relevance 3 with a score of 74+, and a category assigned;
  Lower = score under 55, relevance 1, or a pending takeover; Medium otherwise."""
import datetime, glob, gzip, html, json, os, re, sys
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); sys.path.insert(0, H)
from sectors35 import SECTORS, ORDER
from qualify import financials, capacity, cap_score, fm
from f1links import f1_link
import review
DATE = '2026-11-15'; OUT = os.path.join(R, 'reports', 'public-companies-by-sector'); CAP = 400
MASTER = os.path.join(R, 'reports', f'F1-PUBLIC-COMPANIES-MASTER-{DATE}.xlsx')
COLS = ['Company Name', 'Headquarters – City and country', 'F1 Investment Category', 'Outreach Priority', 'Company Description', 'Sector / Industry',
        'Stock Ticker / Exchange', 'Annual Revenue (USD)', 'Market Capitalization (USD)', 'Revenue Growth (YoY)', 'EBITDA / Operating Profit',
        'Free Cash Flow / Liquidity', 'Marketing Expenditure (if disclosed)', 'Geographic Reach', 'Main Customer Markets & International Expansion',
        'F1 Sponsorship Rationale', 'Latest Financial Reporting Period', 'Financial & Corporate Sources', 'F1 Sponsorship Verification Source',
        'Financial Capacity Confidence', 'Verification Notes', 'Priority Score (0-100)']
WIDTH = [30, 24, 13, 11, 50, 30, 22, 14, 14, 11, 42, 42, 42, 13, 50, 55, 36, 60, 60, 16, 50, 10]
TAB = {'01': 'AI infrastructure', '02': 'AI software', '03': 'Semiconductors', '04': 'Enterprise software & cyber', '05': 'IT services & consulting',
       '06': 'Fintech & payments', '07': 'Crypto & prediction markets', '08': 'Banks & wealth', '09': 'Insurance & insurtech', '10': 'Betting & iGaming',
       '11': 'Telecoms', '12': 'Satellite & space', '13': 'Defence technology', '14': 'Quantum computing', '15': 'Robotics & industrial tech',
       '16': 'Robotaxis & autonomy', '17': 'Air taxis & air mobility', '18': 'Automotive', '19': 'Ride-hailing & delivery', '20': 'Online travel & cruise',
       '21': 'Airlines, hotels & leisure', '22': 'Logistics & shipping', '23': 'Energy, fuels & lubricants', '24': 'Nuclear & new energy',
       '25': 'Consumer electronics', '26': 'Games & entertainment', '27': 'Beverages & alcohol', '28': 'Restaurants & coffee', '29': 'Food, household & retail',
       '30': 'Beauty & personal care', '31': 'Fashion & footwear', '32': 'Luxury, jewellery & watches', '33': 'Consumer health',
       '34': 'Weight-loss & digital health', '35': 'Asian consumer brands', '36': 'Pharma & biotech', '37': 'Medtech & healthcare', '38': 'Chemicals & materials',
       '39': 'Aerospace & aviation', '40': 'Professional & staffing', '41': 'Real estate & developers', '42': 'Mining, metals & steel', '43': 'Conglomerates & trading',
       '44': 'Construction & building', '45': 'Utilities, power & water', '46': 'Education & edtech'}
EXCH = {'T': 'Tokyo Stock Exchange', 'NS': 'NSE India', 'BO': 'BSE India', 'L': 'London Stock Exchange', 'IL': 'London Stock Exchange (IOB)', 'SS': 'Shanghai Stock Exchange',
        'SZ': 'Shenzhen Stock Exchange', 'HK': 'Hong Kong Stock Exchange', 'KS': 'Korea Exchange', 'KQ': 'KOSDAQ', 'PA': 'Euronext Paris', 'AS': 'Euronext Amsterdam',
        'BR': 'Euronext Brussels', 'LS': 'Euronext Lisbon', 'IR': 'Euronext Dublin', 'MI': 'Euronext Milan', 'AX': 'ASX', 'NZ': 'NZX', 'TO': 'Toronto Stock Exchange',
        'V': 'TSX Venture Exchange', 'F': 'Frankfurt Stock Exchange', 'DE': 'Xetra (Frankfurt)', 'HM': 'Hamburg Stock Exchange', 'SW': 'SIX Swiss Exchange',
        'TW': 'Taiwan Stock Exchange', 'TWO': 'Taipei Exchange', 'ST': 'Nasdaq Stockholm', 'HE': 'Nasdaq Helsinki', 'CO': 'Nasdaq Copenhagen', 'IC': 'Nasdaq Iceland',
        'TL': 'Nasdaq Tallinn', 'OL': 'Oslo Børs', 'SR': 'Saudi Exchange (Tadawul)', 'AE': 'UAE (ADX / DFM)', 'QA': 'Qatar Stock Exchange', 'KW': 'Boursa Kuwait',
        'BH': 'Bahrain Bourse', 'OM': 'Muscat Stock Exchange', 'BK': 'Stock Exchange of Thailand', 'TA': 'Tel Aviv Stock Exchange', 'MC': 'Bolsa de Madrid',
        'SA': 'B3 (São Paulo)', 'MX': 'Bolsa Mexicana de Valores', 'SN': 'Santiago Stock Exchange', 'WA': 'Warsaw Stock Exchange', 'PR': 'Prague Stock Exchange',
        'BD': 'Budapest Stock Exchange', 'RO': 'Bucharest Stock Exchange', 'VI': 'Vienna Stock Exchange', 'AT': 'Athens Stock Exchange', 'IS': 'Borsa Istanbul',
        'JO': 'Johannesburg Stock Exchange', 'VN': 'Vietnam (HOSE / HNX)', 'JK': 'Indonesia Stock Exchange', 'SI': 'Singapore Exchange', 'KL': 'Bursa Malaysia',
        'PK': 'Pakistan Stock Exchange', 'KH': 'Cambodia Securities Exchange'}
US_STATES = set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR'.split())
ASIA35 = {'China', 'Hong Kong', 'Taiwan', 'South Korea', 'Singapore', 'Malaysia', 'Thailand', 'Indonesia', 'Vietnam', 'Philippines', 'Macau', 'Cambodia'}
REL = {1: 10, 2: 35, 3: 60, 4: 80, 5: 100}; REACH = {'Global': 100, 'International': 80, 'Regional': 50, 'Domestic': 25}
ROSTER_NOTE = ('Not on the 2025-26 F1 partner roster (424 championship, team and Grand Prix partners; team partner pages re-read 15 Nov 2026). '
               'No parent, subsidiary or brand match')
def jl(pattern):
    for f in sorted(glob.glob(os.path.join(H, pattern))):
        for line in open(f, encoding='utf-8'):
            if line.strip():
                try: yield json.loads(line)
                except ValueError: pass
def dt(s):
    try: return datetime.datetime.strptime(s, '%Y-%m-%d').strftime('%d %b %Y').lstrip('0')
    except (TypeError, ValueError): return ''
def lfm(v, cur, unit='millions'):
    """a figure in the reporting currency (stockanalysis.com shows millions)"""
    if v is None: return ''
    x = v * {'millions': 1e6, 'billions': 1e9, 'thousands': 1e3}.get(str(unit).lower(), 1e6); a = abs(x); sg = '-' if x < 0 else ''
    pre = '$' if cur == 'USD' else cur + ' '
    return f'{sg}{pre}{a / 1e12:,.2f}T' if a >= 1e12 else f'{sg}{pre}{a / 1e9:,.2f}B' if a >= 1e9 else f'{sg}{pre}{a / 1e6:,.0f}M'
def sa_num(sa, k):
    v = sa.get(k)
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
def sa_growth(sa):
    g = sa_num(sa, 'revenue_growth_pct')
    return g / 100 if g is not None and -90 < g < 500 else None
def sa_period(sa): return dt(sa.get('period_end')) or str(sa.get('fy') or 'latest fiscal year')
def sa_usd(v, rev, usd_rev, cur):
    """the same share of the USD revenue shown in the revenue column - an approximation, labelled 'about'"""
    return f' (about {fm(v / rev * usd_rev)})' if cur != 'USD' and rev and usd_rev else ''
def sa_profit(sa, usd_rev=None):
    cur = str(sa.get('currency') or '').upper(); u = sa.get('unit') or 'millions'; rev = sa_num(sa, 'revenue'); parts = []
    for k, lab in (('ebitda', 'EBITDA'), ('operating_income', 'Operating profit')):
        v = sa_num(sa, k)
        if v is not None and rev and abs(v) < 1.5 * rev: parts.append(f'{lab} {lfm(v, cur, u)}{sa_usd(v, rev, usd_rev, cur)}, {v / rev * 100:.1f}% of revenue')
    return '; '.join(parts) + f' (year to {sa_period(sa)}; stockanalysis.com)' if parts else ''
def sa_fcf(sa, usd_rev=None):
    cur = str(sa.get('currency') or '').upper(); v = sa_num(sa, 'free_cash_flow'); rev = sa_num(sa, 'revenue')
    return f"Free cash flow {lfm(v, cur, sa.get('unit') or 'millions')}{sa_usd(v, rev, usd_rev, cur)} (year to {sa_period(sa)}; stockanalysis.com)" if v is not None and rev and abs(v) < rev else ''
def sa_mkt(sa, usd_rev=None):
    cur = str(sa.get('currency') or '').upper(); u = sa.get('unit') or 'millions'; rev = sa_num(sa, 'revenue'); v = sa_num(sa, 'advertising')
    if v and rev and 0 < v < 0.6 * rev: return f'Advertising expense {lfm(v, cur, u)}{sa_usd(v, rev, usd_rev, cur)}, {v / rev * 100:.1f}% of revenue (year to {sa_period(sa)}; stockanalysis.com)'
    v = sa_num(sa, 'selling_marketing')
    if v and rev and 0 < v < 0.9 * rev: return f'Selling and marketing expense {lfm(v, cur, u)}{sa_usd(v, rev, usd_rev, cur)} (year to {sa_period(sa)}; stockanalysis.com): includes sales staff costs; advertising not disclosed separately'
    return ''
def money(pos, neg, v): return f'{pos} {fm(v)}' if v >= 0 else f'{neg} {fm(-v)}'
def words(s): return len(str(s or '').split())
def ticker(c, gap=None):
    if c.get('sa'): return f"{c['sym'].split('@')[0].split('.')[0] if c['sa']['code'] not in ('NYSE', 'NASDAQ', 'AMEX') else c['sym'].split('@')[0]} / {c['sa']['exchange']}"
    sym = c['sym']; m = re.search(r'\.([A-Z]+)$', sym)
    if m and m.group(1) == 'AE' and gap and '/quote/' in str(gap.get('source_url') or ''):
        return f"{sym[:m.start()]} / " + ('Abu Dhabi Securities Exchange (ADX)' if '/adx/' in gap['source_url'] else 'Dubai Financial Market (DFM)' if '/dfm/' in gap['source_url'] else EXCH['AE'])
    if m: return f"{sym[:m.start()]} / {EXCH.get(m.group(1), m.group(1))}"
    ex = (c.get('sec') or {}).get('exch') or ''
    ex = {'TXSE': 'Texas Stock Exchange', 'CBOE': 'Cboe'}.get(ex, ex)
    return f'{sym} / {ex}' if ex else f'{sym} / US-listed'
def headquarters(c, e):
    h = re.sub(r'\s+', ' ', (e.get('hq') or '')).strip()
    if h and ',' in h: return h, True
    sec = c.get('sec') or {}
    if sec.get('city'):
        return f"{sec['city'].title()}, {'United States' if (sec.get('state') or '') in US_STATES else c['country']}", True
    cl = ((c.get('clay') or {}).get('city') or '').split(',')[0].strip()
    if cl: return f"{cl}, {c['country']}", True
    return f"{c['country']} (city not confirmed)", False
def col_profit(f, grp):
    yr = f" (year to {dt(f['fy_end'])})" if f['fy_end'] else ''; ttm = ' (trailing 12 months)'; parts = []
    if f['gap'] and not yr: yr = ttm if 'TTM' in str(f['gap'].get('period') or '') else f" ({f['gap'].get('period') or 'latest reported year'})"
    neg = 'Pre-tax loss' if f['pretax_kind'] == 'Pre-tax profit' else 'Net loss'
    if grp == 'fin':
        if f['pretax'] is not None: parts.append(money(f['pretax_kind'], neg, f['pretax']) + (ttm if f['pretax_ttm'] else yr))
        if f['netinc'] is not None: parts.append(money('Net income', 'Net loss', f['netinc']) + yr)
    else:
        if f['ebitda'] is not None: parts.append(money('EBITDA', 'EBITDA loss', f['ebitda']))
        if f['opinc'] is not None: parts.append(money('Operating profit', 'Operating loss', f['opinc']))
        if parts: parts[-1] += yr
        elif f['pretax'] is not None:
            parts.append(money(f['pretax_kind'], neg, f['pretax']) + (ttm if f['pretax_ttm'] else yr))
            if f['opm'] is not None and f['pretax_ttm'] and (f['opm'] >= 0) == (f['pretax'] >= 0): parts.append(f"pre-tax margin {f['opm']:.1f}%")
    return '; '.join(parts) or 'Not available'
def col_liq(f, grp):
    yr = f" (year to {dt(f['fy_end'])})" if f['fy_end'] else ''; parts = []
    if grp == 'fin':
        if f['assets']: parts.append(f"Total assets {fm(f['assets'])}")
        if f['cash']: parts.append(f"Cash {fm(f['cash'])}")
    else:
        if f['fcf'] is not None: parts.append(('Free cash flow ' if f['capex'] else 'Operating cash flow ') + fm(f['fcf']) + yr)
        if f['cash']: parts.append(f"Cash {fm(f['cash'])}")
        if f['debt']: parts.append(f"Total debt {fm(f['debt'])}")
    return '; '.join(parts) or 'Not available'
def col_mkt(f, sec):
    if f['mkt']:
        e = dt(sec.get('end' + f['mkt_fy'])); pct = f['mkt'] / f['rev'] * 100 if f['rev'] else None
        return f"{f['mkt_kind']} {fm(f['mkt'])}" + (f" ({pct:.1f}% of revenue" if pct else ' (') + (f"; year to {e}" if e else '') + '; annual filing)'
    if f['sellmkt']:
        e = dt(sec.get('end' + f['sellmkt_fy']))
        return f"Selling and marketing expense {fm(f['sellmkt'])}" + (f" (year to {e})" if e else '') + ': includes sales staff costs; advertising not disclosed separately'
    return 'Not Disclosed'
def col_period(f):
    if f['rev_src'] == 'sec': return f"Fiscal year to {dt(f['fy_end'])} (annual filing); market value, cash and debt at Nov 2026"
    if f['rev_src'] == 'lst': return 'Trailing 12 months to the latest reported quarter (stockanalysis.com exchange list, Nov 2026)'
    if f['rev_src'] == 'cmc' or f['pretax_ttm']: return 'Trailing 12 months to the latest reported quarter (retrieved Nov 2026)'
    if f['gap']: return re.sub(r'^TTM', 'Trailing 12 months', str(f['gap'].get('period') or 'Latest reported year')) + '; market value at Nov 2026'
    return 'No revenue or profit figures in the sources used; market value at Nov 2026'
def col_sources(c, f):
    sec = c.get('sec') or {}; src = []
    if f['rev_src'] == 'sec' and f['accn']: src.append(f"SEC EDGAR annual filing {f['accn']}: https://www.sec.gov/Archives/edgar/data/{sec['cik']}/{f['accn'].replace('-', '')}/")
    has_fund = c.get('revenue') or c.get('earnings')
    if c.get('sa'): src.append(f"stockanalysis.com {c['sa']['exchange']} list and company page (market value and revenue in {c['sa']['cur']}, converted to USD at the Nov 2026 rate): {c['sa']['url']}")
    else: src.append('companiesmarketcap.com (' + ('market value, revenue, earnings, cash, debt' if has_fund else 'market value') + '; Nov 2026)')
    if f['gap'] and f['gap'].get('source_url'): src.append(f['gap']['source_url'])
    web = re.sub(r'^(https?://)?(www\.)?', '', (sec.get('web') or (c.get('clay') or {}).get('domain') or '').strip().lower()).split('/')[0]
    if web: src.append('company site: ' + web)
    return '; '.join(src)
VERIFY_FLAG = re.compile(r'unclear|acquir|merg|private|distress|restructur|taken over|chapter 11|spun|delist|bankrupt', re.I)
DROP_FLAG = re.compile(r'delisted or bankrupt|sanctioned|central bank', re.I)
def assemble():
    U = {c['sym']: c for c in json.load(gzip.open(os.path.join(H, 'data', 'universe.json.gz'), 'rt'))}
    u2 = os.path.join(H, 'data', 'universe2.json.gz')                  # companies added from the full exchange lists
    if os.path.exists(u2): U.update({c['sym']: c for c in json.load(gzip.open(u2, 'rt')) if c['sym'] not in U})
    cls = {}
    for f in sorted(glob.glob(os.path.join(H, 'classify', 'out_*.txt'))):
        for line in open(f):
            p = line.strip().split('|')
            if len(p) == 2 and p[0] in U: cls[p[0]] = p[1].strip()
    E = {d['sym']: d for d in jl('enrich/out_*.jsonl') if d.get('sym')}
    nfix = 0
    for d in jl('fix/out_*.jsonl'):
        e = E.get(d.get('sym'))
        if not e: continue
        for k, lo, hi in (('desc', 10, 20), ('markets', 5, 28), ('rationale', 8, 28)):
            if d.get(k) and lo <= words(d[k]) <= hi: e[k] = re.sub(r'\s+', ' ', d[k]).strip(); nfix += 1
    G = {d['sym']: d for d in jl('gap/out_*.jsonl') if d.get('found')}
    FIN = {d['sym']: d for d in jl('fin/out_*.jsonl') if d.get('found') and d.get('revenue')}                   # latest fiscal year from stockanalysis.com (top prospects outside the SEC data)
    W = {d['sym']: d for d in jl('f1web/out_*.jsonl') if d.get('sym') and d.get('status') not in (None, 'not_checked')}      # live web check of the top prospects
    rows = []; out = Counter(); missing = []; f1x = []
    for sym, c in U.items():
        code0 = cls.get(sym, '')
        if code0 not in SECTORS: out['not in any sector (funds, shells, tobacco, packaging, agriculture) or not classified'] += 1; continue
        if c['country'] == 'Russia' or sym.endswith('.ME'): out['Russian market'] += 1; continue
        name = re.sub(r'\s+', ' ', html.unescape(c['name'])).strip(); sec = c.get('sec') or {}
        web = sec.get('web') or (c.get('clay') or {}).get('domain') or ''
        link, src = f1_link(name, web)
        if link: out['current F1 partner, or parent / subsidiary of one (roster match)'] += 1; f1x.append((sym, name, link)); continue
        if sym in review.ROSTER_EXTRA: out['current F1 partner, or parent / subsidiary of one (partner pages re-read, Nov 2026)'] += 1; f1x.append((sym, name, review.ROSTER_EXTRA[sym])); continue
        e = E.get(sym); code = code0
        if e:
            s2 = str(e.get('sector') or '')
            if s2 == '00': out['not in any sector (company review)'] += 1; continue
            if s2 in SECTORS and not (s2 == '35' and c['country'] not in ASIA35): code = s2
        if sym in review.DROP: out['removed: ' + review.DROP[sym]] += 1; continue
        sa = FIN.get(sym)
        grp = SECTORS[code]['grp']; f = financials(c, grp, G.get(sym))
        if sa and f['pretax'] is None and f['rev'] and sa_num(sa, 'operating_income') is not None and sa_num(sa, 'revenue'):
            f['pretax'] = sa_num(sa, 'operating_income') / sa_num(sa, 'revenue') * f['rev']; f['pretax_kind'] = 'Operating profit'      # same margin applied to the USD revenue
        gross = bool(f['rev'] and f['mcap'] and f['rev'] > 3 * f['mcap'] and (code == '07' or grp == 'fin'))     # gross trading / investment value booked as revenue
        if gross and sa and str(sa.get('currency') or '').upper() == 'USD' and sa_num(sa, 'revenue') and sa_num(sa, 'revenue') * 1e6 < 0.1 * f['rev']:
            f['rev'] = sa_num(sa, 'revenue') * 1e6; f['rev_src'] = 'sa'; f['mkt'] = None; gross = False; netrev = True      # net revenue instead of gross trading value
        else: netrev = False
        k = capacity(dict(f, rev=None, mkt=None) if gross else f, code)
        if k['ev'] == 'Insufficient': out['insufficient financial capacity'] += 1; continue
        if not e: missing.append(sym); continue
        f1txt = (e.get('f1') or '').strip(); f1note = ''
        if f1txt:
            dec = review.F1.get(sym, ('exclude', f1txt))
            if dec[0] == 'exclude': out['current F1 partner, or parent / subsidiary of one (company review)'] += 1; f1x.append((sym, name, dec[1])); continue
            if dec[0] == 'note': f1note = dec[1]
        w = W.get(sym); webnote = ''
        if w:
            st = review.WEB.get(sym, w['status'])
            if st == 'current': out['current F1 partner, or parent / subsidiary of one (web check, Nov 2026)'] += 1; f1x.append((sym, name, w.get('detail', ''))); continue
            webnote = {'none': 'no current F1 sponsorship found', 'past': 'former F1 sponsor, not current: ' + str(w.get('detail', '')),
                       'related': 'not a sponsor, but linked: ' + str(w.get('detail', '')), 'unclear': 'unclear, check: ' + str(w.get('detail', ''))}.get(st, '')
            if st in ('related', 'unclear'): f1note = (f1note + ' ' if f1note else '') + 'Web check: ' + str(w.get('detail', ''))
            if webnote and w.get('source_url') and st != 'none': webnote += ' (' + w['source_url'] + ')'
        flags = '' if sym in review.CLEAR_FLAG else re.sub(r'\s+', ' ', (e.get('flags') or '')).strip()
        if DROP_FLAG.search(flags): out['delisted, bankrupt, sanctioned or not a commercial company'] += 1; continue
        rel = e.get('rel') if e.get('rel') in REL else 2; reach = e.get('reach') if e.get('reach') in REACH else 'Regional'
        fit = SECTORS[code]['fit']; strat = 0.25 * fit * 10 + 0.50 * REL[rel] + 0.25 * REACH[reach]; fin = cap_score(k, f)
        score = round(0.6 * strat + 0.4 * fin, 1)
        e.update(review.FIX.get(sym, {}))
        hq, hq_ok = headquarters(c, e)
        notes = []                                     # (type, text); every type except 'info' puts the row on the Verification Required tab
        if k['cat'] == 'To Verify':
            why = ('no revenue or profit figures in the sources used; rests on market value' if k['nodata'] else
                   'rests on access to capital (large, well-funded growth company with little revenue)' if k['basis'].startswith('access') else
                   'rests on cash reserves, not on operating revenue' if k['ops'] < 3e6 else 'estimated capacity is just under the USD 4M Challenger level')
            notes.append(('cat', 'Investment category not assigned: ' + why))
        if k['stressed']: notes.append(('data', 'Losses are large relative to cash on hand: check the funding position'))
        elif k['loss'] and k['cat'] != 'To Verify': notes.append(('info', 'Loss-making: capacity estimate discounted'))
        if netrev: notes.append(('info', 'Revenue shown is net revenue from stockanalysis.com; the market-data site reports gross trading value'))
        if c.get('src') == 'sa' and f['pretax'] is None: notes.append(('info', 'Profit not confirmed in the sources used: capacity rests on revenue'))
        if gross: notes.append(('data', 'Reported revenue is gross trading or investment value, not net revenue: it was not used for the capacity estimate'))
        if f['mismatch']: notes.append(('data', 'Revenue in the SEC filing data and the market-data site differ widely, so the filing figures were not used: check the latest report'))
        if f['gap']: notes.append(('info', 'Revenue and profit from stockanalysis.com, converted from local currency (' + str(f['gap'].get('currency_note') or '') + ')'))
        if e.get('conf') == 'low': notes.append(('profile', 'Company profile written with low confidence: check description, HQ and markets'))
        if not hq_ok: notes.append(('info', 'HQ city not confirmed'))
        if flags:
            if VERIFY_FLAG.search(flags): notes.append(('corp', 'Reported corporate status - confirm current position: ' + flags))
            else: notes.append(('info', flags[0].upper() + flags[1:]))
        if sym in review.NOTE: f1note = (f1note + ' ' if f1note else '') + review.NOTE[sym]
        if f1note: notes.append(('f1', f1note))
        rows.append({'sym': sym, 'c': c, 'e': e, 'f': f, 'k': k, 'sector': code, 'name': name, 'hq': hq, 'rel': rel, 'reach': reach, 'strat': strat, 'fin': fin, 'score': score,
                     'notes': notes, 'verify': any(t != 'info' for t, _ in notes), 'f1note': f1note, 'webnote': webnote, 'sa': sa if sa and f['rev_src'] != 'sec' else None})
    for r in rows:
        k = r['k']; s = r['score']
        acq = any(t == 'corp' and re.search(r'acquir|private|taken over', x, re.I) for t, x in r['notes'])
        if r['rel'] <= 1 or s < 55 or acq: p = 'Lower'
        elif k['cat'] != 'To Verify' and ((r['rel'] >= 4 and s >= 60) or (r['rel'] == 3 and s >= 74)): p = 'High'
        else: p = 'Medium'
        if p == 'High' and r['e'].get('conf') == 'low': p = 'Medium'
        r['priority'] = p
    rank = {'High': 0, 'Medium': 1, 'Lower': 2}
    bysec = defaultdict(list)
    for r in rows: bysec[r['sector']].append(r)
    final = []; cut = Counter()
    for code in ORDER:
        L = sorted(bysec[code], key=lambda r: (-r['score'], -(r['f']['mcap'] or 0)))
        if len(L) > CAP: cut[code] = len(L) - CAP; L = L[:CAP]
        L.sort(key=lambda r: (rank[r['priority']], -r['score'], -(r['f']['mcap'] or 0)))
        bysec[code] = L; final += L
    return {'rows': final, 'bysec': bysec, 'out': out, 'missing': missing, 'f1x': f1x, 'cut': cut, 'universe': len(U), 'nfix': nfix, 'U': U}
def cells(r):
    c, e, f, k = r['c'], r['e'], r['f'], r['k']; grp = SECTORS[r['sector']]['grp']; sa = r.get('sa')
    growth = f['growth'] if f['growth'] is not None else (sa_growth(sa) if sa else None)
    profit = col_profit(f, grp); liq = col_liq(f, grp); mkt = col_mkt(f, c.get('sec') or {}); period = col_period(f); sources = col_sources(c, f)
    if sa:
        ur = f['rev']
        if grp != 'fin' and sa_profit(sa, ur): profit = sa_profit(sa, ur)
        if grp != 'fin' and sa_fcf(sa, ur): liq = sa_fcf(sa, ur) + ('; ' + liq if liq != 'Not available' else '')
        if mkt == 'Not Disclosed' and sa_mkt(sa, ur): mkt = sa_mkt(sa, ur)
        period = (f'Fiscal year to {sa_period(sa)} (stockanalysis.com); market value at Nov 2026' if f['rev_src'] != 'cmc' else
                  f'Fiscal year to {sa_period(sa)} for growth, profit and cash flow (stockanalysis.com); revenue is trailing 12 months (companiesmarketcap.com, Nov 2026)')
        if sa.get('source_url') and str(sa['source_url']) not in sources: sources += '; ' + str(sa['source_url'])
    if growth is not None: growth = round(growth, 4)
    clean = lambda x: re.sub(r'\s+', ' ', str(x or '')).strip()
    f1 = ROSTER_NOTE + ('. Web search check, 15 Nov 2026: ' + r['webnote'] if r['webnote'] else '') + ('. Note: ' + r['f1note'] if r['f1note'] and not r['webnote'] else '')
    return [r['name'], r['hq'], k['cat'], r['priority'], clean(e.get('desc')), SECTORS[r['sector']]['name'], ticker(c, f['gap']),
            f['rev'] if f['rev'] else 'Not available', f['mcap'] if f['mcap'] else 'Not available', growth if growth is not None else 'Not available',
            profit, liq, mkt, r['reach'], clean(e.get('markets')), clean(e.get('rationale')), period,
            sources, f1, k['ev'], '; '.join(t for _, t in r['notes']), r['score']]
# ------------------------------------------------------------------ Excel
def style_sheet(ws, n):
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    head = PatternFill('solid', fgColor='1F3864'); wrap = Alignment(wrap_text=True, vertical='top'); top = Alignment(vertical='top')
    fills = {'High': PatternFill('solid', fgColor='C6EFCE'), 'Medium': PatternFill('solid', fgColor='FFEB9C'), 'Lower': PatternFill('solid', fgColor='EDEDED'),
             'To Verify': PatternFill('solid', fgColor='FCE4D6'), 'Plausible Capacity': PatternFill('solid', fgColor='FFF2CC')}
    money_fmt = '[>=1000000000]$#,##0.00,,,"B";[>=1000000]$#,##0,,"M";$#,##0'
    for j, w in enumerate(WIDTH, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
        h = ws.cell(1, j); h.font = Font(bold=True, color='FFFFFF'); h.fill = head; h.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[1].height = 44; ws.freeze_panes = 'B2'
    ws.auto_filter.ref = f'A1:{get_column_letter(len(COLS))}{max(n + 1, 2)}'
    longcols = {5, 11, 12, 13, 15, 16, 17, 18, 19, 21}
    for i in range(2, n + 2):
        ws.row_dimensions[i].height = 62                      # four lines: keeps rows even; longer cells stay readable in the formula bar
        for j in range(1, len(COLS) + 1):
            x = ws.cell(i, j); x.alignment = wrap if j in longcols else top
        for j in (8, 9):
            if isinstance(ws.cell(i, j).value, (int, float)): ws.cell(i, j).number_format = money_fmt
        if isinstance(ws.cell(i, 10).value, (int, float)): ws.cell(i, 10).number_format = '0.0%'
        ws.cell(i, 22).number_format = '0.0'
        for j in (3, 4, 20):
            fl = fills.get(ws.cell(i, j).value)
            if fl: ws.cell(i, j).fill = fl
def add_sheet(wb, title, rows, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title; ws.append(COLS)
    for r in rows: ws.append(cells(r))
    style_sheet(ws, len(rows)); return ws
KEY = [('F1 Investment Category', 'Estimated annual sponsorship capacity: Challenger USD 4-6M, Mid-level USD 6-12M, Large USD 12M+. "To Verify" = the evidence does not support a category yet.'),
       ('Outreach Priority', 'High / Medium / Lower from the Priority Score: 60% strategic relevance (sector fit, company relevance, geographic reach) and 40% financial capacity.'),
       ('Financial Capacity Confidence', 'Strong Evidence = profitable, with revenue or marketing spend that supports USD 4M+ a year. Plausible Capacity = could fund it, but loss-making, cash-based, a near-miss or missing figures. Companies with insufficient capacity are not listed.'),
       ('Capacity is an estimate', 'It is derived from revenue, profit, cash and disclosed marketing spend with sector-specific tests. It is not a stated sponsorship budget.'),
       ('Financial figures', 'Revenue, growth, EBITDA / operating profit, cash flow and marketing spend come from SEC annual filings where the company files in the US; otherwise revenue, pre-tax profit, cash and debt are trailing-12-month figures from companiesmarketcap.com, or market value and revenue from the stockanalysis.com exchange lists. "Not available" / "Not Disclosed" = not in the sources used, not zero.'),
       ('Profile fields', 'Headquarters, description, markets and rationale are desk-research summaries and were not individually web-verified. Rows written with low confidence are flagged in Verification Notes.'),
       ('F1 exclusion', 'Current Formula 1 championship, team and Grand Prix partners, team owners and engine suppliers, and their parents and subsidiaries, are excluded (2025-26 roster of 424 partners, compiled Aug-Oct 2026).'),
       ('Verification Notes', 'What to check before outreach: unassigned category, data gaps, recent corporate actions, licence or franchise links to an F1 partner.')]
def add_key(wb):
    from openpyxl.styles import Alignment, Font
    ws = wb.create_sheet('Key'); ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 120
    for a, b in KEY:
        ws.append([a, b]); ws.cell(ws.max_row, 1).font = Font(bold=True)
        ws.cell(ws.max_row, 1).alignment = Alignment(vertical='top'); ws.cell(ws.max_row, 2).alignment = Alignment(wrap_text=True, vertical='top')
def sector_path(code):
    slug = re.sub(r'[^A-Za-z0-9]+', '-', SECTORS[code]['name']).strip('-').upper()
    return os.path.join(OUT, f'F1-PUBLIC-COMPANIES-{code}-{slug}-{DATE}.xlsx')
def write_sector(A, code):
    from openpyxl import Workbook
    wb = Workbook(); add_sheet(wb, f'{code} {TAB[code]}'[:31], A['bysec'][code], first=True); add_key(wb)
    os.makedirs(OUT, exist_ok=True); p = sector_path(code); wb.save(p); return p
def summary_rows(A):
    rows = A['rows']; out = A['out']; S = []
    S.append(('title', f'Listed companies that could fund a Formula 1 partnership - research summary ({DATE})'))
    S.append(('text', f"{len(rows):,} listed companies across {len(ORDER)} sectors: the original 35 plus 11 added at your request (36-46), where Formula 1 already has sponsors or a clear commercial logic. Each company appears once, in its best-fit sector. Current F1 partners and their parents and subsidiaries are excluded."))
    S.append(('blank', ''))
    S.append(('head', ['Sector', 'F1 fit (0-10)', 'Companies', 'High', 'Medium', 'Lower', 'Large', 'Mid-level', 'Challenger', 'To Verify', 'Strong Evidence', 'Plausible Capacity', 'Note']))
    for code in ORDER:
        L = A['bysec'][code]; pc = Counter(r['priority'] for r in L); cc = Counter(r['k']['cat'] for r in L); ec = Counter(r['k']['ev'] for r in L)
        note = f"{A['cut'][code]} more qualified; top {CAP} by priority score listed" if A['cut'].get(code) else ('all qualified companies listed' if L else 'no qualified listed company found')
        S.append(('row', [f"{code} {SECTORS[code]['name']}", SECTORS[code]['fit'], len(L), pc['High'], pc['Medium'], pc['Lower'], cc['Large'], cc['Mid-level'], cc['Challenger'], cc['To Verify'],
                          ec['Strong Evidence'], ec['Plausible Capacity'], note]))
    pc = Counter(r['priority'] for r in rows); cc = Counter(r['k']['cat'] for r in rows); ec = Counter(r['k']['ev'] for r in rows)
    S.append(('total', ['Total', '', len(rows), pc['High'], pc['Medium'], pc['Lower'], cc['Large'], cc['Mid-level'], cc['Challenger'], cc['To Verify'], ec['Strong Evidence'], ec['Plausible Capacity'], '']))
    S.append(('blank', ''))
    S.append(('sub', 'How the list was narrowed'))
    S.append(('kv', ['Listed companies reviewed (11,396 from the market-data site, the rest added from full exchange lists)', A['universe']]))
    for k, v in sorted(out.items(), key=lambda x: -x[1]):
        if k.startswith('removed: '): continue
        S.append(('kv', ['Taken out: ' + k, v]))
    rem = sum(v for k, v in out.items() if k.startswith('removed: '))
    if rem: S.append(('kv', ['Taken out: taken private, merged, duplicate listing or on the US Entity List', rem]))
    if A['missing']: S.append(('kv', ['Qualified on figures but not profiled (not listed)', len(A['missing'])]))
    S.append(('kv', [f'Qualified but outside the top {CAP} of a sector', sum(A['cut'].values())]))
    S.append(('kv', ['Listed in this workbook', len(rows)]))
    S.append(('blank', ''))
    S.append(('sub', 'How to read the columns'))
    for a, b in KEY: S.append(('kv', [a, b]))
    S.append(('blank', ''))
    S.append(('sub', 'Sources'))
    for a, b in [('Market data', 'companiesmarketcap.com data downloads, Nov 2026: market value, trailing-12-month revenue and pre-tax earnings, cash, debt, total assets (11,396 listed companies).'),
                 ('Exchange lists', 'stockanalysis.com lists for 56 home-market exchanges, Nov 2026: ticker, market value and trailing-12-month revenue for every listed company. Used to add companies the market-data site does not carry, mostly in China, Japan, Hong Kong, South Korea, Taiwan and India. Local currency converted to USD at Nov 2026 rates.'),
                 ('Company filings', 'SEC EDGAR official data (data.sec.gov): annual revenue, operating income, depreciation, operating cash flow, capital spending and advertising / marketing expense for the latest fiscal year filed (FY2026 where already out, otherwise FY2025) and the year before; business address and exchange.'),
                 ('Gap fill', 'stockanalysis.com for Gulf and other listings with no figures in the two sources above.'),
                 ('F1 partner roster', '424 current partners from official team partner pages and rtrsports.com, pitdebrief.com, sports-khabri.com, compiled Aug-Oct 2026. The official partner pages of McLaren, Red Bull Racing, Mercedes, Aston Martin, Williams, Alpine, Audi, Haas and Racing Bulls were re-read on 15 Nov 2026, and the 200 highest-ranked companies were each checked with a live web search; both steps removed further current sponsors.'),
                 ('Not used', 'Apollo was not used.')]: S.append(('kv', [a, b]))
    S.append(('blank', ''))
    S.append(('sub', 'Limits to keep in mind'))
    for t in ['Revenue growth, EBITDA, free cash flow and marketing spend are only available for companies that file with the SEC (mainly US-listed); elsewhere the columns show pre-tax profit, cash and debt, or "Not available".',
              'Companies added from the exchange lists come with market value and revenue only. Their capacity is rated Plausible, not Strong, unless a fiscal-year lookup confirmed profit, and their profit, cash and marketing columns read "Not available" / "Not Disclosed".',
              'Companies under about USD 190M of revenue were not added from the exchange lists, because with revenue-only data none could pass a capacity test.',
              'Company profiles (HQ, description, markets, rationale) are desk-research summaries that were not individually web-verified; check them before outreach, starting with the rows on the Verification Required tab.',
              'Sponsorship capacity is an estimate from public figures, not a known budget. No sponsorship intentions are implied.',
              'F1 partner check: the live web search covered the 200 highest-ranked companies and found about ten current sponsors the roster had missed, mostly deals signed in 2026. Companies ranked below that were checked against the roster and the re-read team pages only, so re-check any company against current team announcements before contact.',
              'Emerging sectors (quantum computing, robotaxis, air taxis, satellite) have few listed companies with the means to sponsor, so those lists are short by design.']: S.append(('text', '- ' + t))
    return S
def write_master(A):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook(); rows = A['rows']
    add_sheet(wb, 'Master Companies', sorted(rows, key=lambda r: (r['sector'], {'High': 0, 'Medium': 1, 'Lower': 2}[r['priority']], -r['score'])), first=True)
    for code in ORDER: add_sheet(wb, f'{code} {TAB[code]}'[:31], A['bysec'][code])
    add_sheet(wb, 'Top 500 Prospects', sorted(rows, key=lambda r: ({'High': 0, 'Medium': 1, 'Lower': 2}[r['priority']], -r['score'], -(r['f']['mcap'] or 0)))[:500])
    add_sheet(wb, 'Verification Required', sorted([r for r in rows if r['verify']], key=lambda r: (r['sector'], -r['score'])))
    ws = wb.create_sheet('Research Summary'); ws.column_dimensions['A'].width = 62
    for j, w in zip('BCDEFGHIJKLM', [12, 11, 8, 9, 8, 8, 10, 11, 10, 15, 17, 60]): ws.column_dimensions[j].width = w
    for kind, v in summary_rows(A):
        if kind == 'blank': ws.append(['']); continue
        ws.append(v if isinstance(v, list) else [v]); i = ws.max_row
        if kind == 'title': ws.cell(i, 1).font = Font(bold=True, size=14)
        elif kind == 'sub': ws.cell(i, 1).font = Font(bold=True, size=12)
        elif kind in ('head', 'total'):
            for j in range(1, 14):
                ws.cell(i, j).font = Font(bold=True, color='FFFFFF' if kind == 'head' else '000000')
                if kind == 'head': ws.cell(i, j).fill = PatternFill('solid', fgColor='1F3864'); ws.cell(i, j).alignment = Alignment(wrap_text=True, vertical='center')
        elif kind == 'kv':
            ws.cell(i, 1).font = Font(bold=True); ws.cell(i, 1).alignment = Alignment(wrap_text=True, vertical='top')
            if isinstance(v[1], str): ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=13); ws.cell(i, 2).alignment = Alignment(wrap_text=True, vertical='top'); ws.row_dimensions[i].height = max(15, 15 * (len(v[1]) // 150 + 1))
        elif kind == 'text': ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=13); ws.cell(i, 1).alignment = Alignment(wrap_text=True, vertical='top'); ws.row_dimensions[i].height = max(15, 15 * (len(v) // 210 + 1))
    wb.save(MASTER); return MASTER
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'; A = assemble(); rows = A['rows']
    if cmd == 'check':
        print('listed', len(rows), '| profile fields rewritten', A['nfix'], '| qualified but no profile', len(A['missing']), A['missing'][:40])
        for k, v in sorted(A['out'].items(), key=lambda x: -x[1]): print(f'  out {v:5d}  {k}')
        print('priority', Counter(r['priority'] for r in rows), '| category', Counter(r['k']['cat'] for r in rows), '| evidence', Counter(r['k']['ev'] for r in rows))
        print('on verification tab', sum(r['verify'] for r in rows), Counter(t for r in rows for t, _ in r['notes']))
        sc = sorted(r['score'] for r in rows); print('score deciles', [sc[int(len(sc) * q / 10)] for q in range(10)], sc[-1])
        for code in ORDER:
            L = A['bysec'][code]; pc = Counter(r['priority'] for r in L)
            print(f"{code} {TAB[code]:30s} {len(L):4d}  H {pc['High']:3d} M {pc['Medium']:3d} L {pc['Lower']:3d}  cut {A['cut'].get(code, 0):3d}  top: " + ', '.join(r['name'] for r in sorted(L, key=lambda r: -r['score'])[:5]))
    elif cmd == 'sectors':
        for code in (sys.argv[2:] or ORDER): print(len(A['bysec'][code]), write_sector(A, code))
    elif cmd == 'master': print(len(rows), write_master(A))
