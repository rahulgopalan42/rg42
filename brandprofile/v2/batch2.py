"""Batch 2 onwards: the central discovery register, the research coverage summary by source, the Clay leads tab and the summary text.
Called from deliver.py:  extras(D, Q, W, I, X, batch) returns the pieces write.write() adds to the workbook.
Streams: Clay (company search), Crunchbase, Independent web research. A company found by more than one is 'Multiple sources'."""
import json, os, re, sys
from collections import Counter, OrderedDict, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build as B
import check as C
import score as S
from register import norm, loose, dom
STREAMS = ['Clay', 'Crunchbase', 'Independent web research']
REV = {'75M-200M': 75, '200M-500M': 200, '500M-1B': 500, '1B-10B': 1000, '10B-100B': 10000, '100B-1T': 100000}
REVTXT = {'75M-200M': 'USD 75M to 200M', '200M-500M': 'USD 200M to 500M', '500M-1B': 'USD 500M to 1B', '1B-10B': 'USD 1B to 10B', '10B-100B': 'USD 10B to 100B', '100B-1T': 'USD 100B+'}
SECMAP = [(r'gambl|casino', 'Gambling & Gaming Venues'), (r'computer games|mobile gaming|video game', 'Video Games & Esports'), (r'tobacco', 'Tobacco & Nicotine'),
          (r'educat|e-learning|training|school', 'Education & Training'), (r'advertis|marketing|public relations|market research', 'Marketing, Advertising & PR'),
          (r'environmental|waste|water supply', 'Environmental & Waste Services'), (r'holding', 'Diversified & Other'), (r'brewer|distiller|winer|wine and spirits', 'Alcoholic Drinks'),
          (r'cosmetic|personal care', 'Beauty & Personal Care'), (r'luxury|jewel', 'Luxury, Jewellery & Watches'), (r'apparel|fashion|footwear|textile', 'Fashion, Apparel & Footwear'),
          (r'furniture|home furnish', 'Home & Furniture'), (r'retail', 'Retail & E-commerce'), (r'food|beverage|dairy|restaurant', 'Food & Beverage'), (r'sporting goods|consumer goods|consumer electronics', 'Consumer Products'),
          (r'airline|aviation', 'Airlines & Air Travel'), (r'hospitality|hotel|travel|leisure', 'Travel, Hotels & Leisure'), (r'automotive|motor vehicle', 'Automotive & Mobility'),
          (r'spectator sports|sports', 'Sports, Fitness & Events'), (r'entertainment|broadcast|media|publishing', 'Media, Entertainment & Publishing'), (r'banking', 'Banking & Lending'),
          (r'insurance', 'Insurance'), (r'investment|capital markets|venture|private equity', 'Investment & Capital Markets'), (r'financial', 'Financial Services & Payments'),
          (r'software|internet', 'Software, Internet & AI'), (r'it services|information technology', 'IT Services & Consulting'), (r'telecom|wireless', 'Telecommunications'),
          (r'semiconductor|electronics', 'Semiconductors & Electronics'), (r'pharma|biotech', 'Pharma & Biotech'), (r'medical equipment|medical device', 'Medical Devices & Diagnostics'),
          (r'hospital|health', 'Healthcare Services'), (r'maritime|shipbuild', 'Shipping, Maritime & Shipbuilding'), (r'logistic|truck|freight|transportation', 'Logistics & Transportation'),
          (r'machinery|automation|manufactur', 'Industrial Machinery & Equipment'), (r'chemical|plastics', 'Chemicals & Materials'), (r'oil and gas|oil & gas', 'Oil, Gas & Fuels'),
          (r'utilit|electric power|renewable', 'Utilities & Renewable Energy'), (r'mining|metal', 'Mining & Metals'), (r'packaging', 'Packaging & Printing'), (r'security', 'Security Services'),
          (r'staffing|recruit|human resources', 'Staffing & HR'), (r'construction|engineering', 'Construction & Engineering'), (r'real estate', 'Real Estate'), (r'farming|agricultur', 'Agriculture & Agribusiness')]
LISTED_TXT = re.compile(r'(?i)\b(NYSE|NASDAQ|Nasdaq|LSE|TSX|ASX|SEHK|HKEX|Euronext|OTCQX|OTC Markets|publicly[- ]traded|publicly[- ]listed|is listed on|listed on the|stock exchange|ticker)\b')
def clay_sector(ind):
    t = B.clean(ind).lower()
    return next((s for rx, s in SECMAP if re.search(rx, t)), 'Diversified & Other')
def stage_from(st, src, logged=''):
    if st == 'dup': return 'Left out: delivered in an earlier batch' if src.startswith('delivered') else 'Left out: already on your master'
    if st == 'f1': return 'Left out: holds a current F1 deal'
    if st == 'listed': return 'Left out: listed company' if logged else 'Not researched: the name matches a listed company'
    return ''
def register(D, Q, W, I, X, batch):
    """One row per company found by any stream, with what became of it."""
    R = OrderedDict(); alias = {}; raw = Counter()
    def get(name, site=''):
        name = B.clean(name); keys = {k for k in (norm(name), loose(name)) if len(k) >= 2} | ({'@' + dom(site)} if dom(site) else set())
        k0 = next((alias[k] for k in keys if k in alias), None)
        if k0 is None:
            k0 = norm(name) or name.lower()
            R[k0] = {'name': name, 'site': B.clean(site), 'country': '', 'sector': '', 'streams': set(), 'sources': [], 'figure': '', 'stage': '', 'where': '', 'cluster': '', 'check': '', 'origins': set(), 'nclay': 0}
        for k in keys: alias[k] = k0
        r = R[k0]
        if not r['site'] and B.clean(site): r['site'] = B.clean(site)
        return r
    def src(r, u):
        u = B.clean(u)
        if u and u not in r['sources'] and len(r['sources']) < 3: r['sources'].append(u)
    for lab, L in (('Ranked', Q), ('Verification watchlist', W), ('Researched: insufficient capacity on the figures found', I), ('Read off a ranking only: still to assess', X)):
        for d in L:
            r = get(d['name'], d.get('website')); v = d.get('_via') or 'Independent web research'
            if not re.match(r'v\d\d_', d['_cluster']): r['origins'].add(d['_cluster'])
            r['streams'] |= {'Clay', 'Independent web research'} if v == 'Multiple sources' else {v}
            r['country'] = B.clean(d.get('hq_country')); r['sector'] = d['sector']; r['stage'] = lab; r['cluster'] = d['_cluster']; r['check'] = 'New'
            r['where'] = (f"{d.get('tab')}, rank {d.get('rank_sector')} (overall {d.get('rank_all')})" if lab == 'Ranked' else 'Verification Watchlist tab' if lab.startswith('Verification') else 'Supporting Research tab' if lab.startswith('Researched') else 'Discovered - To Assess tab')
            src(r, d.get('discovery_source')); M = d['A']['M']; k = next((k for k in ('revenue', 'aum', 'equity_funding', 'valuation', 'ebitda', 'arr', 'transaction_value') if k in M), None)
            if k: r['figure'] = S.LABEL[k].capitalize() + ': ' + B.figline(M, k)
            for u in sorted(B.sources(d))[:1]: src(r, u)
    def loose_row(d, stream, name, site, country, sector, figure, source, cluster, logged_stage='', why=''):
        r = get(name, site); r['streams'].add(stream); src(r, source)
        if stream == 'Clay': r['nclay'] += 1
        elif cluster: r['origins'].add(cluster)
        if not r['country']: r['country'] = B.clean(country)
        if not r['sector']: r['sector'] = sector
        if not r['figure'] and B.clean(figure): r['figure'] = B.clean(figure)
        if not r['cluster']: r['cluster'] = cluster
        if not r['stage']:
            st, disp, s2, hits = C.lookup(r['name'] + (' | ' + r['site'] if r['site'] else ''), batch=batch)
            stg = stage_from(st, s2, logged_stage)
            if stg: r['stage'] = stg; r['check'] = (s2 or disp)[:120]
            elif logged_stage: r['stage'] = logged_stage; r['check'] = B.clean(why)[:160]
            else: r['stage'] = 'New: not yet researched'; r['check'] = ('Close to: ' + disp[:100]) if st == 'possible' else 'New'
        return r
    for d in D['disc']:
        stg = B.clean(d.get('stage')).lower(); chk = B.clean(d.get('check')).upper()
        logged = 'Left out: listed company' if 'LISTED' in chk and 'left' in stg else ('Left out by the research: ' + (B.clean(d.get('why')) or 'see notes')) if stg.startswith('left') and 'MASTER' not in chk and 'DELIVERED' not in chk and 'F1' not in chk else ''
        sec = B.SECKEY.get(norm(B.clean(d.get('sector')))) or B.clean(d.get('sector'))
        loose_row(d, 'Independent web research', d['name'], d.get('website'), d.get('hq_country'), sec, d.get('figure'), d.get('source'), d['_cluster'], logged, d.get('why'))
    for d in D['clay']:
        fig = ('Revenue bracket (Clay estimate): ' + REVTXT.get(B.clean(d.get('annual_revenue')), B.clean(d.get('annual_revenue')))) if B.clean(d.get('annual_revenue')) else ''
        r = loose_row(d, 'Clay', d['name'], d.get('domain') or d.get('website'), d.get('country'), clay_sector(d.get('industry')), fig, d.get('linkedin'), d.get('_file', 'clay'))
        r.setdefault('clay', d)
        if r['stage'] == 'New: not yet researched' and LISTED_TXT.search(B.clean(d.get('desc'))):
            r['stage'] = 'Not researched: its Clay description mentions a stock listing (its own or its parent\'s)'; r['check'] = 'Clay marks it privately held; to confirm'
    for nm, why, key, b in D['dups']:
        if not nm: continue
        w = why.upper(); lg = 'Left out: listed company' if 'LISTED' in w else ('Left out by the research: ' + why[:140]) if not any(t in w for t in ('MASTER', 'DELIVERED', 'F1 PARTNER')) else ''
        loose_row({}, 'Independent web research', nm, '', '', '', '', '', key, lg, why)
    for nm, why, key in D['excluded']:
        r = get(nm); r['streams'].add('Independent web research')
        if r['stage'] in ('', 'New: not yet researched'): r['stage'] = 'Left out: ' + why.split(':')[0].lower(); r['check'] = why[:140]
    for r in R.values(): r['via'] = 'Multiple sources' if len(r['streams']) > 1 else next(iter(r['streams']), 'Independent web research')
    raw = {'Clay': sum(max(0, r['nclay'] - 1) for r in R.values()), 'Independent web research': sum(max(0, len(r['origins']) - 1) for r in R.values()), 'Crunchbase': 0}
    return R, raw
def clay_leads(R, batch):
    """Clay rows that are new and that nobody has researched yet, as rows in the master's format (priority: To Verify)."""
    out = []
    for r in R.values():
        d = r.get('clay')
        if not d or r['stage'] != 'New: not yet researched': continue
        br = B.clean(d.get('annual_revenue')); lo = REV.get(br)
        rec = {'name': r['name'], 'website': B.clean(d.get('domain') or d.get('website')), 'hq_city': B.clean(d.get('locality')), 'hq_country': B.clean(d.get('country')), 'sector': clay_sector(d.get('industry')),
               'subsector': B.clean(d.get('industry')), 'desc': B.clean(d.get('desc'))[:260], 'ownership_type': 'requires verification', 'employees': d.get('employee_count') if isinstance(d.get('employee_count'), (int, float)) else None,
               'fin': [{'metric': 'revenue', 'value_orig': REVTXT.get(br, br) + ' (Clay estimate bracket)', 'usd_m': lo, 'period': '', 'kind': 'estimated', 'source': B.clean(d.get('linkedin')) or 'Clay company search'}] if lo else [],
               'fit': {}, 'fit_rationale': 'Not yet assessed: found in Clay only.', 'category_conflict': 'not assessed', 'conf': 'low', 'reach': '',
               'outstanding': 'Confirm it is unlisted and who owns it (Clay marks subsidiaries of listed groups as privately held); confirm revenue from a company or registry source; write the Formula 1 case',
               'sources': [B.clean(d.get('linkedin'))] if B.clean(d.get('linkedin')) else [], 'discovered_via': 'Clay', 'discovery_source': 'Clay company search: ' + B.clean(d.get('query')),
               '_batch': batch, '_cluster': d.get('_file', 'clay'), '_via': 'Clay', '_watchfile': True, '_listing_txt': 'Not verified (Clay marks it privately held)'}
        st, disp, s2, hits = C.lookup(rec['name'] + (' | ' + rec['website'] if rec['website'] else ''), batch=batch); note = next((x for x in hits if x[2] == 'info'), None)
        rec['_sheet'] = note[1] if note else ''; rec['_possible'] = disp if st == 'possible' else ''; rec['_listed_name'] = ''
        a = S.assess(rec); a['conf'] = 'Unverified capacity'; a['conf_why'] = "Clay's modelled revenue bracket only: neither the figure nor the ownership has been checked on a company or registry page"
        a['tier'] = 0; a['tier_txt'] = 'Unverified'; a['tier_why'] = 'no verified figure'; a['priority'] = 'To Verify'; rec['A'] = a; rec['tab'] = 'Clay Leads (Unconfirmed)'; rec['rank_all'] = ''; rec['rank_sector'] = ''
        rec['_ord'] = (-(lo or 0), -(rec['employees'] or 0), rec['name'].lower()); out.append(rec)
    out.sort(key=lambda d: d['_ord'])
    return out
def coverage(R, raw, Q, W, I, X, leads, D):
    cols = STREAMS + ['Multiple sources']; rows = list(R.values())
    def cnt(pred, by='via'):
        c = Counter(r[by] for r in rows if pred(r)); return [c.get(k, 0) for k in cols] + [sum(c.values())]
    disc = [sum(1 for r in rows if s in r['streams']) for s in STREAMS]
    T = [['Companies discovered through the stream (after removing repeats inside the stream)'] + disc + ['', len(rows), 'The last column is the number of different companies in the register. A company found by two streams is counted under each stream here.'],
         ['Companies found by that stream only'] + cnt(lambda r: True) + ['"Multiple sources" = found by Clay and by independent web research.'],
         ['Left out: already on your master'] + cnt(lambda r: r['stage'] == 'Left out: already on your master') + ['Checked against every tab of PRIVATE NEW- 27_11 by name, alias and website.'],
         ['Left out: delivered in an earlier batch'] + cnt(lambda r: r['stage'] == 'Left out: delivered in an earlier batch') + ['Batch 1 (ranked and watchlist companies).'],
         ['Left out: holds a current F1 deal'] + cnt(lambda r: r['stage'] == 'Left out: holds a current F1 deal') + ['Championship, team or Grand Prix partner.'],
         ['Left out: listed company'] + cnt(lambda r: r['stage'] == 'Left out: listed company') + ['Own shares publicly traded.'],
         ['Left out by the research for another reason'] + cnt(lambda r: r['stage'].startswith('Left out by the research') or r['stage'].startswith('Left out: russian') or r['stage'].startswith('Left out: name') or r['stage'].startswith('Left out: same company')) + ['Alias of a master company, closed, absorbed, sanctioned and similar; the reason is in the Discovery Register.'],
         ['Genuinely new and financially qualified (ranked)'] + cnt(lambda r: r['stage'] == 'Ranked') + ['On the Consolidated Ranking and the sector tabs.'],
         ['Researched: needs financial verification'] + cnt(lambda r: r['stage'] == 'Verification watchlist') + ['On the Verification Watchlist tab.'],
         ['Researched: insufficient capacity on the figures found'] + cnt(lambda r: r['stage'].startswith('Researched: insufficient')) + ['Supporting Research tab only.'],
         ['Read off a ranking, still to assess'] + cnt(lambda r: r['stage'].startswith('Read off a ranking')) + ['Discovered - To Assess tab.'],
         ['New, not yet researched'] + cnt(lambda r: r['stage'] == 'New: not yet researched') + [f'In the Discovery Register; the {len(leads):,} that came from Clay are also on the Clay Leads (Unconfirmed) tab.'],
         ['Not researched: probably listed, or part of a listed group'] + cnt(lambda r: r['stage'].startswith('Not researched:')) + ['The name matches a listed company, or the Clay description mentions a stock listing. To be confirmed either way; not counted as a lead.'],
         ['Repeats removed (the same company found more than once)'] + [raw.get(s, 0) for s in STREAMS] + [sum(1 for r in rows if r['via'] == 'Multiple sources'), sum(raw.values()) + sum(1 for r in rows if r['via'] == 'Multiple sources'),
          'Clay: the same company returned by two searches. Web: the same company found by two researchers. More than one stream: found by Clay and by web research, kept once.']]
    return T
def extras(D, Q, W, I, X, batch):
    import write as Wr
    R, raw = register(D, Q, W, I, X, batch); leads = clay_leads(R, batch); T = coverage(R, raw, Q, W, I, X, leads, D)
    byname = {r['name']: r for r in R.values()}
    for d in Q + W + I + X:                              # one answer per company on how it was found: the register's, which sees all streams
        r = byname.get(B.clean(d['name']))
        if r: d['_via'] = r['via']
    n = len(Q); bn = batch[1:].lstrip('0'); fmt = lambda c: '; '.join(f'{k} {v}' for k, v in c.most_common())
    pr = Counter(d['A']['priority'] for d in Q); cf = Counter(d['A']['conf'] for d in Q); tr = Counter(d['A']['tier_txt'] for d in Q); rt = Counter('Route ' + d['A']['route'] for d in Q)
    own = Counter(B.clean(d.get('ownership_type')) or 'requires verification' for d in Q); reg = Counter(Wr.region(d) for d in Q); sec = Counter(d['sector'] for d in Q); via = Counter(d.get('_via') for d in Q)
    stages = Counter(r['stage'] for r in R.values()); onsheet = sum(1 for d in Q + W if d.get('_sheet'))
    gaps = []
    gp = os.path.join(H, 'batches', batch, 'gaps.txt')
    if os.path.exists(gp): gaps = [l.rstrip() for l in open(gp, encoding='utf-8') if l.strip()]
    empty = [s for s in B.SECTORS if s not in sec]
    SUM = [(f'Formula 1 prospects, non-public companies: revised methodology, research batch {bn} ({B.DATE}): Clay, Crunchbase and independent web research',),
           [f"{n:,} genuinely new qualified companies, ranked; {len(W):,} on the financial verification watchlist; {len(leads):,} unconfirmed Clay leads; {len(X):,} read off rankings and still to assess. "
            f"None is on your master spreadsheet (PRIVATE NEW- 27_11) or in batch 1: every name was checked against every tab of the master and against batch 1 by name, alias and website, before research and again when this file was built."],
           [f"The central discovery register holds {len(R):,} different companies found by the three streams. The Research Coverage tab shows what each stream contributed and what became of every name."], [],
           ('The three streams',),
           [f"Clay: {sum(1 for r in R.values() if 'Clay' in r['streams']):,} companies pulled from Clay's company search (privately held, by industry and revenue bracket). Clay's revenue is a modelled bracket and it marks many subsidiaries of listed groups as privately held, "
            "so a Clay name is ranked only after its ownership and figures were checked on the web; the rest are on the Clay Leads (Unconfirmed) tab, as on your master."],
           ['Crunchbase: not run. The monthly allowance on your account is used up (500,000 of 500,000 data tokens) and resets on 1 Dec 2026. Nothing in this workbook comes from Crunchbase.'],
           [f"Independent web research: {sum(1 for r in R.values() if 'Independent web research' in r['streams']):,} companies, from rankings, registries, association and exhibitor lists, portfolio pages and company sites, read in local languages where that helped. "
            f"{sum(1 for r in R.values() if r['via'] == 'Independent web research'):,} of them were found by web research only."], [],
           ('Deduplication',),
           ['Excluded as duplicates: every company on any tab of your master, and every company delivered in batch 1. Brands on your older 48-tab sheet are not excluded (your instruction of 27 Nov), and are marked in the On Your Sheet? column.'],
           [f"Left out as already on the master: {stages.get('Left out: already on your master', 0):,}. Already delivered in batch 1: {stages.get('Left out: delivered in an earlier batch', 0):,}. Holding a current F1 deal: {stages.get('Left out: holds a current F1 deal', 0):,}. "
            f"Listed: {stages.get('Left out: listed company', 0):,}. {onsheet:,} of the delivered companies are also on your older 48-tab sheet."], [],
           ('What is in this workbook',),
           ['Research Coverage: contribution of each stream, duplicates removed, what is new, what is left. Consolidated Ranking and the sector tabs: the new qualified companies, ranked across and within sectors (Domestic on its own tab).'],
           ['Verification Watchlist: researched, attractive, no financial route shown yet. Clay Leads (Unconfirmed): new names from Clay that nobody has verified yet, largest first. Discovered - To Assess: names read off a ranking only.'],
           ['Discovery Register: every company found by any stream, where it was found and what became of it. Supporting Research, Methodology, Backtest, Research Record, Excluded, Key: as in batch 1.'], [],
           ('The new ranked companies',),
           [f"By priority: {fmt(pr)}."], [f"By financial confidence: {fmt(cf)}."], [f"By qualification route: {fmt(rt)}."], [f"By estimated annual investment tier: {fmt(tr)}."],
           [f"By discovery stream: {fmt(via)}."], [f"By region of headquarters: {fmt(reg)}."], [f"By ownership: {fmt(own)}."], [f"By sector ({len(sec)} sectors): {fmt(sec)}."],
           [f"Sectors with no new company in this batch: {', '.join(empty) or 'none'}."], [],
           ('Limits and what remains',)] + [[g] for g in gaps] + [
           ['No sector is described as exhaustive. Each researcher stopped on time or search limits and wrote down what was not reached; those notes are on the Research Record tab, and the names found but not researched are in the Discovery Register.'],
           ['Not available: PitchBook, Orbis, D&B Hoovers, Sales Navigator. Apollo was not used. Figures are as stated on the page cited; Clay brackets are labelled as estimates. Nothing was estimated or filled in by me.']]
    def after_summary(wb):
        Wr.grid(wb, 'Research Coverage', ['Measure', 'Clay', 'Crunchbase (not run: allowance used up until 1 Dec 2026)', 'Independent web research', 'Found by more than one stream', 'All streams', 'Note'],
                [62, 14, 20, 16, 16, 14, 90], T, height=None)
    def before_support(wb):
        if leads: Wr.main_tab(wb, 'Clay Leads (Unconfirmed)', [B.row(d, watch=True) for d in leads])
        rows = sorted(R.values(), key=lambda r: (r['stage'], r['sector'], r['name'].lower()))
        Wr.grid(wb, 'Discovery Register', ['Company', 'Website', 'Country', 'Sector', 'Discovered Through', 'Where It Was Found', 'Figure as Found', 'What Became of It', 'Check Against the Master and Batch 1', 'Where in This Workbook', 'Research Stream File'],
                [36, 24, 18, 28, 22, 60, 36, 40, 44, 40, 30],
                [[r['name'], r['site'], r['country'], r['sector'], r['via'], '; '.join(r['sources']), r['figure'], r['stage'], r['check'], r['where'], B.CLUSTER.get(r['cluster'], r['cluster'])] for r in rows], height=None)
    return {'summary': SUM, 'after_summary': after_summary, 'before_support': before_support, 'register': R, 'leads': leads, 'coverage': T, 'stages': stages}
