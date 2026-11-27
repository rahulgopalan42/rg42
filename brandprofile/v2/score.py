"""Revised methodology (27 Nov 2026): qualification route, financial confidence, investment tier and the 100-point outreach score.
Everything here is computed from the fields the research wrote down, so the same evidence always gives the same result.
The rubric is described in plain words in the workbook's Methodology tab (build.py writes it from RUBRIC below)."""
import re
TODAY = (2026, 11)
STD = {'equity_funding': 100, 'revenue': 150, 'arr': 50, 'ebitda': 20, 'valuation': 1000, 'transaction_value': 1000, 'aum': 5000}          # Route A, USD millions
EXC = {'equity_funding': (75, 100), 'revenue': (75, 150), 'valuation': (500, 1000), 'transaction_value': (0, 1000)}                        # Route B
LABEL = {'equity_funding': 'total equity funding', 'revenue': 'annual revenue', 'arr': 'annual recurring revenue', 'ebitda': 'annual EBITDA', 'valuation': 'valuation',
         'transaction_value': 'acquisition or transaction value', 'aum': 'assets under management', 'net_income': 'net income', 'debt_funding': 'debt financing',
         'marketing_spend': 'marketing expenditure', 'operating_budget': 'operating budget'}
# company type -> the measure that best shows what it could spend, and the lower bounds of Tiers 1-4 in USD millions
CONSUMER = {'Food & Beverage', 'Alcoholic Drinks', 'Fashion, Apparel & Footwear', 'Luxury, Jewellery & Watches', 'Beauty & Personal Care', 'Consumer Products', 'Retail & E-commerce',
            'Travel, Hotels & Leisure', 'Home & Furniture', 'Media, Entertainment & Publishing', 'Sports, Fitness & Events', 'Video Games & Esports', 'Gambling & Gaming Venues',
            'Airlines & Air Travel', 'Automotive & Mobility', 'Tobacco & Nicotine'}
FIN = {'Banking & Lending', 'Insurance', 'Financial Services & Payments'}
SERVICES = {'Professional & Business Services', 'Staffing & HR', 'Security Services', 'IT Services & Consulting', 'Marketing, Advertising & PR', 'Education & Training', 'Healthcare Services'}
HEALTH = {'Pharma & Biotech', 'Medical Devices & Diagnostics'}
BANDS = {'consumer brand': (5000, 1500, 400, 75), 'software and technology': (2000, 600, 200, 50), 'financial services': (8000, 2000, 500, 100), 'asset or wealth manager': (500000, 150000, 40000, 10000),
         'industrial, resources or infrastructure': (15000, 4000, 1000, 200), 'healthcare products': (10000, 3000, 800, 150), 'services': (10000, 3000, 800, 150)}
EBITDA_BANDS = (2000, 500, 120, 30); EQUITY_BANDS = (None, 1500, 500, 100); VALUE_BANDS = (None, 20000, 5000, 1000)
TIER_TXT = {1: 'Tier 1: USD 20M+', 2: 'Tier 2: USD 8M to below 20M', 3: 'Tier 3: USD 3M to below 8M', 4: 'Tier 4: USD 1M to below 3M', 5: 'Tier 5: below USD 1M', 0: 'Unverified'}
ASSET_RX = re.compile(r'(?i)asset manage|wealth|private bank|private equity|hedge|alternative invest|investment manage|pension|superannuation|family office|private credit|venture capital|trading firm|market mak')
STRONG = re.compile(r'(?i)\bipo\b|listing|acqui|merg|raised|funding round|series [a-k]\b|investment|invest(ed|s) |stake|buyout|chief marketing|\bcmo\b|head of (brand|marketing|partnerships)|rebrand|'
                    r'sponsor|partner(ship)? with .*(team|league|club|tour|championship)|naming rights|campaign|ambassador|headquarter|new (market|office|plant|factory|country|region)|'
                    r'enter(s|ed|ing) |expan|launch(es|ed)? in|opened|opens|entered formula|formula 1|\bf1\b')
TOP_SPONSOR = re.compile(r'(?i)title|principal|main sponsor|main partner|shirt|jersey|naming rights|stadium|arena|premier league|champions league|la liga|bundesliga|serie a|ligue 1|\bnba\b|\bnfl\b|\bmlb\b|\bnhl\b|'
                         r'motogp|formula e|indycar|nascar|\bwec\b|le mans|olympic|fifa|\bipl\b|\bufc\b|\batp\b|\bwta\b|wimbledon|grand slam|ryder cup|pga tour|world cup|tour de france|america\'s cup|sailgp')
NO_ISSUE = re.compile(r'(?i)^\s*(none|no |n/a|nil|nothing|not found|no$)')
SERIOUS = re.compile(r'(?i)sanction|fraud|brib|corrupt|money.launder|criminal|convict|indict|debarr|blacklist')
def year(s):
    m = re.search(r'(19|20)\d\d', str(s or '')); return int(m.group(0)) if m else None
def months_ago(d):
    m = re.match(r'^\s*((?:19|20)\d\d)(?:-(\d{1,2}))?', str(d or ''))
    if not m: return None
    return (TODAY[0] - int(m.group(1))) * 12 + (TODAY[1] - int(m.group(2) or 6))
def num(v):
    try: return float(v)
    except Exception: return None
def metrics(d):
    """the latest usable figure for each metric: {metric: (usd_m, period, kind, source, value_orig, published)}"""
    out = {}
    for f in d.get('fin') or []:
        if not isinstance(f, dict): continue
        m = str(f.get('metric') or '').strip().lower(); v = num(f.get('usd_m'))
        if not m or v is None: continue
        y = year(f.get('period')) or year(f.get('published')) or 0
        cur = out.get(m)
        if cur is None or y > (year(cur[1]) or year(cur[5]) or 0) or (y == (year(cur[1]) or 0) and v > cur[0] and m in ('equity_funding',)):
            out[m] = (v, str(f.get('period') or ''), str(f.get('kind') or 'reported').lower(), str(f.get('source') or ''), str(f.get('value_orig') or ''), str(f.get('published') or ''))
    return out
def ctype(d):
    s = d.get('sector') or ''; sub = ' '.join(str(d.get(k) or '') for k in ('subsector', 'desc'))
    if s == 'Investment & Capital Markets' or (ASSET_RX.search(str(d.get('subsector') or '')) and s in FIN | {'Investment & Capital Markets', 'Real Estate'}): return 'asset or wealth manager'
    if s in ('Software, Internet & AI',): return 'software and technology'
    if s in FIN: return 'financial services'
    if s in HEALTH: return 'healthcare products'
    if s in SERVICES: return 'services'
    if s in CONSUMER and str(d.get('model') or '').upper() != 'B2B': return 'consumer brand'
    return 'industrial, resources or infrastructure'
def top_sponsor(d): return any(TOP_SPONSOR.search(' '.join(str(v) for v in s.values())) for s in (d.get('sponsorships') or []) if isinstance(s, dict))
def has_sponsor(d): return any(isinstance(s, dict) and str(s.get('rights_holder') or '').strip() for s in (d.get('sponsorships') or []))
def backing(d): return bool(str(d.get('parent_backing') or '').strip())
def state_owned(d): return str(d.get('ownership_type') or '').lower() in ('state-owned', 'sovereign fund-backed')
def std_hits(d, M):
    """the standard thresholds met, in the order that suits the company type. For an investment firm its own AUM comes first and the value of
    deals it has done does not count: that is the size of its investments, not of the firm."""
    asset = ctype(d) == 'asset or wealth manager'
    order = ['aum', 'revenue', 'ebitda', 'equity_funding', 'valuation'] if asset else list(STD)
    return [k for k in order if k in M and M[k][0] >= STD[k]]
def route(d, M):
    """(route, what met it). The research proposes a route; this recomputes it from the figures so the two can be compared."""
    for k in std_hits(d, M): return 'A', f'{LABEL[k]} of USD {STD[k]:,}M or more'.replace('1,000M', '1B').replace('5,000M', '5B')
    if backing(d) and (state_owned(d) or 'subsidiary' in str(d.get('ownership_type') or '').lower() or 'joint venture' in str(d.get('ownership_type') or '').lower()):
        return 'A', 'documented parent-company or state financial backing with a commercial mandate'
    if top_sponsor(d): return 'A', 'existing substantial sponsorship expenditure'
    for k, (lo, hi) in EXC.items():
        if k in M and lo <= M[k][0] < hi and (k != 'transaction_value' or str(d.get('exception_note') or '').strip()):
            return 'B', f'{LABEL[k]} below the standard threshold, with supporting strength'
    alt = [a for a in (d.get('alt_indicators') or []) if isinstance(a, dict) and str(a.get('indicator') or '').strip()]
    if len(alt) >= 2: return 'C', 'two or more independent indicators of scale'
    if has_sponsor(d) and len(alt) >= 1: return 'C', 'a paid sponsorship plus one further indicator of scale'
    return 'none', 'no route met on the evidence found'
def confidence(d, M, rt, why):
    distress = bool(str(d.get('distress') or '').strip()); loss = str(d.get('profitability') or '').lower().startswith('loss')
    if rt == 'none': return 'Unverified capacity', 'No financial route is met on the pages found.'
    if rt == 'A':
        hit = std_hits(d, M)
        rec = [k for k in hit if M[k][2] == 'reported' and (year(M[k][1]) or year(M[k][5]) or 0) >= 2023 and M[k][3].startswith('http')]
        if rec and not (distress and loss): return 'Confirmed capacity', f'Reported {LABEL[rec[0]]} for {M[rec[0]][1] or "a recent period"} meets the standard threshold.'
        if hit: return 'Indicative capacity', ('The qualifying figure is an estimate.' if any(M[k][2] != 'reported' for k in hit) else 'The qualifying figure is older than three financial years.' if not rec else 'Signs of financial strain were found.')
        return 'Indicative capacity', 'Qualifies on ' + why + ', not on a published financial figure.'
    if rt == 'B': return 'Indicative capacity', 'Below a standard threshold; included as a documented exception.'
    return 'Indicative capacity', 'No financials published; qualifies on independent indicators of scale.'
def tier(d, M, typ):
    """estimated annual partnership investment tier (1-5, 0 = unverified) and the reason. Bands differ by company type; they are not a share of revenue."""
    def band(v, b):
        for i, lo in enumerate(b, 1):
            if lo is not None and v >= lo: return i
        return 5
    t = 0; basis = ''
    if typ == 'asset or wealth manager' and 'aum' in M: t = band(M['aum'][0], BANDS[typ]); basis = f"assets under management of USD {M['aum'][0]:,.0f}M"
    elif typ == 'software and technology' and ('arr' in M or 'revenue' in M):
        k = 'arr' if 'arr' in M and M['arr'][0] >= M.get('revenue', (0,))[0] else 'revenue'; t = band(M[k][0], BANDS[typ]); basis = f"{LABEL[k]} of USD {M[k][0]:,.0f}M"
    elif 'revenue' in M: t = band(M['revenue'][0], BANDS.get(typ, BANDS['services'])); basis = f"annual revenue of USD {M['revenue'][0]:,.0f}M"
    elif 'ebitda' in M: t = band(M['ebitda'][0], EBITDA_BANDS); basis = f"EBITDA of USD {M['ebitda'][0]:,.0f}M"
    elif 'aum' in M: t = band(M['aum'][0], BANDS['asset or wealth manager']); basis = f"assets under management of USD {M['aum'][0]:,.0f}M"
    elif 'equity_funding' in M: t = max(3, band(M['equity_funding'][0], EQUITY_BANDS)); basis = f"equity funding of USD {M['equity_funding'][0]:,.0f}M (capped at Tier 3: funding is not a marketing budget)"
    elif 'valuation' in M or 'transaction_value' in M:
        k = 'valuation' if 'valuation' in M else 'transaction_value'; t = max(3, band(M[k][0], VALUE_BANDS)); basis = f"{LABEL[k]} of USD {M[k][0]:,.0f}M (capped at Tier 3)"
    adj = []
    if t:
        if str(d.get('profitability') or '').lower().startswith('loss') or str(d.get('distress') or '').strip(): t = min(5, t + 1); adj.append('one tier lower: loss-making or under strain')
        if backing(d) and t > 2: t -= 1; adj.append('one tier higher: documented parent or state backing')
    if top_sponsor(d) and (t == 0 or t > 3): t = 3; adj.append('at least Tier 3: already pays for a top-tier sponsorship')
    elif has_sponsor(d) and (t == 0 or t > 4): t = 4; adj.append('at least Tier 4: already pays for a sports sponsorship')
    if t == 0 and backing(d) and state_owned(d): t = 3; basis = 'documented state backing with a commercial mandate'
    return t, (basis + ('; ' + '; '.join(adj) if adj else '')) if (basis or adj) else 'No figure found from which to estimate.'
FITW = {'B2B': {'b2b': 2, 'ecosystem': 2, 'technical': 1, 'hospitality': 1.5, 'geography': 1.5, 'brand': 1, 'consumer': 0, 'category': 1},
        'B2C': {'b2b': 0.5, 'ecosystem': 1, 'technical': 0.5, 'hospitality': 1, 'geography': 2, 'brand': 2, 'consumer': 2, 'category': 1},
        'HYBRID': {'b2b': 1.5, 'ecosystem': 1.5, 'technical': 1, 'hospitality': 1, 'geography': 1.5, 'brand': 1.5, 'consumer': 1, 'category': 1}}
def fit_score(d):
    w = FITW.get(str(d.get('model') or '').strip().upper(), FITW['HYBRID']); f = d.get('fit') or {}
    s = sum(w[k] * max(0, min(3, num(f.get(k)) or 0)) for k in w)
    conflict = str(d.get('category_conflict') or '').lower()
    if conflict.startswith('established'): s = min(s, 15)
    return round(s, 1)
def intent_score(d):
    sig = [s for s in (d.get('signals') or []) if isinstance(s, dict) and str(s.get('what') or '').strip()]
    conf = []; inferred = 0
    for s in sig:
        ma = months_ago(s.get('date')); st = str(s.get('status') or '').lower(); cat = str(s.get('category') or '').lower()
        if st != 'confirmed' or not str(s.get('source') or '').startswith('http') or ma is None or ma > 24 or ma < -1: inferred += 1 if (ma is None or ma <= 24) else 0; continue
        pts = (8 if ma <= 12 else 5) * (1.0 if STRONG.search(str(s.get('what'))) else 0.6)
        if cat == 'marketing' and re.search(r'(?i)sponsor|partner', str(s.get('what'))) and top_sponsor(d): pts *= 0.5        # the same sponsorship already counts under financial capacity
        conf.append((pts, cat, ma))
    conf.sort(reverse=True); total = 0.0; seen = {}
    for pts, cat, ma in conf:
        n = seen.get(cat, 0)
        if not seen: total += pts                                # the strongest signal counts in full
        elif n == 0 and len(seen) < 3: total += pts * 0.625      # a further category: 5 of 8, 3 of 5
        elif n == 1: total += 2                                  # a second event of a category already counted
        seen[cat] = n + 1
    total += min(4, 2 * inferred)
    return round(min(25, total), 1), len(conf), sorted(seen), inferred
def access_score(d):
    a = d.get('access') or {}; own = str(a.get('owner_led') or '').lower(); st = str(a.get('structure') or '').lower(); aut = str(d.get('marketing_autonomy') or '').lower()
    s = {'yes': 4, 'unknown': 2, '': 2}.get(own, 1) + {'lean': 3, 'mid': 2}.get(st, 0) + (1 if str(a.get('marketing_head_identified') or '').lower() == 'yes' else 0) + {'yes': 2, 'unknown': 1, '': 1}.get(aut, 0)
    if st == 'complex' or state_owned(d): s = min(s, 6)
    return min(10, s)
def assess(d):
    M = metrics(d); typ = ctype(d); rt, why = route(d, M); conf, conf_why = confidence(d, M, rt, why); t, t_why = tier(d, M, typ)
    distress = bool(str(d.get('distress') or '').strip()); prof = str(d.get('profitability') or '').lower()
    if conf != 'Unverified capacity' and t == 5 and (distress and prof.startswith('loss')): conf, conf_why = 'Insufficient capacity', 'Small on the figures found, loss-making and under strain.'
    afford = {1: 14, 2: 14, 3: 13, 4: 9, 5: 3, 0: 5}[t]
    rel = {'Confirmed capacity': 9, 'Indicative capacity': 5 if rt == 'C' else 6, 'Unverified capacity': 2, 'Insufficient capacity': 0}[conf]
    recent_raise = any(isinstance(s, dict) and str(s.get('category') or '').lower() == 'capital' and str(s.get('status') or '').lower() == 'confirmed' and (months_ago(s.get('date')) or 99) <= 24
                       and re.search(r'(?i)raised|round|series|investment|invest|growth capital|stake', str(s.get('what') or '')) for s in (d.get('signals') or []))
    owner_backed = backing(d) or bool(str(d.get('pe_swf_owner') or '').strip())
    strength = max(0, min(8, (4 if prof.startswith('profit') else 0 if prof.startswith('loss') else 1) + (2 if owner_backed else 0) + (2 if recent_raise else 0) - (4 if distress else 0)))
    mk = 4 if top_sponsor(d) else 3 if 'marketing_spend' in M else 2 if has_sponsor(d) else 0
    fin = afford + rel + strength + mk
    fit = fit_score(d); intent, nsig, cats, ninf = intent_score(d); acc = access_score(d)
    total = round(fin + fit + intent + acc, 1)
    pr = 'High' if total >= 75 else 'Medium' if total >= 55 else 'Watchlist' if total >= 35 else 'Low'
    flags = []
    conflict = str(d.get('category_conflict') or '')
    if conflict.lower().startswith('established'): flags.append('Established category conflict: ' + conflict.split(':', 1)[-1].strip()); pr = min(pr, 'Watchlist', key=['High', 'Medium', 'Watchlist', 'Low'].index) if pr in ('High', 'Medium') else pr
    elif conflict.lower().startswith('potential'): flags.append('Possible category conflict to verify: ' + conflict.split(':', 1)[-1].strip())
    comp = str(d.get('compliance') or '').strip()
    if comp and not NO_ISSUE.match(comp):
        flags.append('Compliance point to weigh: ' + comp)
        if SERIOUS.search(comp) and pr in ('High', 'Medium'): pr = 'Watchlist'          # a serious point caps the priority; a lesser one is flagged only
    if conf == 'Insufficient capacity': pr = 'Low'
    if pr in ('High', 'Medium') and conflict.lower().startswith('established'): pr = 'Watchlist'
    agent_rt = str(d.get('route') or '').strip().upper()
    if agent_rt in ('A', 'B', 'C') and rt != 'none' and agent_rt != rt: flags.append(f'The research filed it under Route {agent_rt}; the figures support Route {rt}')
    return {'M': M, 'type': typ, 'route': rt, 'route_why': why, 'conf': conf, 'conf_why': conf_why, 'tier': t, 'tier_txt': TIER_TXT[t], 'tier_why': t_why,
            'fin': fin, 'fin_parts': {'affordability': afford, 'reliability': rel, 'strength': strength, 'marketing': mk}, 'fit': fit, 'intent': intent, 'access': acc,
            'total': total, 'priority': pr, 'signals_confirmed': nsig, 'signal_cats': cats, 'signals_inferred': ninf, 'flags': flags}
RUBRIC = [
 ('Financial capacity (35 points)', ''),
 ('Affordability, 14', 'From the investment tier: Tier 1 or 2 = 14, Tier 3 = 13, Tier 4 = 9, Tier 5 = 3, unverified = 5. Tiers 1 to 3 score almost the same on purpose: once a company can afford the opportunity, being bigger does not make it a better prospect.'),
 ('Reliability of the evidence, 9', 'Confirmed capacity = 9; Indicative = 6 (5 where it rests on Route C indicators); Unverified = 2; Insufficient = 0.'),
 ('Financial strength, 8', 'Stated profitability 4 (unknown 1, loss-making 0); documented parent, state, private equity or sovereign owner behind it +2; an equity raise in the past 24 months +2; signs of distress -4.'),
 ('Marketing spend already shown, 4', 'A top-tier paid sponsorship = 4; disclosed marketing expenditure = 3; another paid sports sponsorship = 2; none found = 0.'),
 ('Strategic Formula 1 fit (30 points)', ''),
 ('Eight ratings of 0 to 3', 'B2B opportunity, customer ecosystem, technical integration, hospitality, geographic alignment, brand positioning, consumer activation, category availability. Each is rated 0 (none), 1 (weak), 2 (credible) or 3 (strong and specific) from what the pages show.'),
 ('Weights by business model', 'The weights add to 10 for every model, so a B2B company is not penalised for having no consumer activation and a consumer brand is not penalised for having no technical integration. '
  'B2B: B2B 2, ecosystem 2, technical 1, hospitality 1.5, geography 1.5, brand 1, consumer 0, category 1. B2C: B2B 0.5, ecosystem 1, technical 0.5, hospitality 1, geography 2, brand 2, consumer 2, category 1. '
  'Hybrid: B2B 1.5, ecosystem 1.5, technical 1, hospitality 1, geography 1.5, brand 1.5, consumer 1, category 1. An established category conflict caps fit at 15.'),
 ('Buying intent and timing (25 points)', ''),
 ('Confirmed signals', 'Only dated, sourced events of the past 24 months count as confirmed. The strongest counts in full: 8 points if in the past 12 months, 5 if 12 to 24 months old; a minor event (not a raise, deal, senior marketing hire, rebrand, sponsorship, campaign or market entry) counts 60%. '
  'A signal in a second or third category adds 5 or 3. A second event in a category already counted adds 2. One corporate event is one signal, however many articles report it.'),
 ('Inferred signals and double counting', 'Inferred signals add 2 each, 4 at most. A sponsorship already counted under financial capacity counts half here. A company with no signal scores 0 here and stays eligible.'),
 ('Decision-maker accessibility (10 points)', ''),
 ('How it is built', 'Owner, founder or a visible chief executive runs it 4 (unknown 2, no 1); structure lean 3, mid 2, complex 0; a marketing or partnerships head is identifiable +1; the brand controls its own marketing 2 (unknown 1). Complex groups and state-owned companies are capped at 6.'),
 ('Priority', '75 to 100 High; 55 to 74 Medium; 35 to 54 Watchlist; below 35 Low. An established category conflict, or a serious compliance point (sanctions, fraud, bribery, criminal proceedings), caps the priority at Watchlist; lesser points are flagged in Verification Notes. Insufficient capacity is always Low. Unverified capacity goes to the Financial Verification Watchlist, not the qualified ranking.'),
 ('Ties', 'In order: financial capacity, Formula 1 fit, buying intent, accessibility, then name.')]
