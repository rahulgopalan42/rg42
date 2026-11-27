"""Builds the revised-methodology workbook from the research batches.
Usage: build.py check | build.py xlsx <output.xlsx>
Reads v2/batches/*/ (MAIN d*.jsonl, WATCH watch_*.jsonl, DUPS dups_*.jsonl, NOTES notes_*.txt) and v2/backtest/results.json.
Main tabs keep the master's 45 columns in order, with three columns added after Outreach Priority."""
import glob, json, os, re, sys
from collections import Counter, OrderedDict, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import score as S
import check as C
from register import norm, loose, dom
FMT = json.load(open(os.path.join(H, 'format.json'), encoding='utf-8'))
DATE = '27 Nov 2026'
CLUSTER = {'d01_asset_wealth': 'asset management, wealth management and private banks', 'd02_private_equity': 'private equity and alternative investment firms',
           'd03_industrial_europe': 'industrial and manufacturing, Europe', 'd04_industrial_row': 'industrial and manufacturing, outside Europe',
           'd05_logistics_aviation': 'logistics, shipping, private aviation, aerospace and space', 'd06_mining_chemicals': 'mining, metals, materials and chemicals',
           'd07_energy_telecom': 'energy, telecoms and digital infrastructure', 'd08_consumer_west': 'consumer, food and drink, luxury: Europe and North America',
           'd09_consumer_row': 'consumer, retail, hospitality, real estate: Asia-Pacific, Middle East, Africa, Latin America', 'd10_software_nonvc': 'bootstrapped and private equity-owned software',
           'd11_financial_insurance': 'financial services, insurance and payments', 'd12_healthcare': 'healthcare, medical technology and pharmaceuticals',
           'd13_services_construction': 'professional and commercial services, construction, real estate', 'd14_state_parent': 'state-owned, sovereign-backed and parent-backed brands',
           'a01_assess': 'assessment of companies found on rankings in batch 1 (part 1)', 'a02_assess': 'assessment of companies found on rankings in batch 1 (part 2)',
           'a03_assess': 'assessment of companies found on rankings in batch 1 (part 3)', 'a04_assess': 'assessment of companies found on rankings in batch 1 (part 4)', 'a05_assess': 'assessment of companies found on rankings in batch 1 (second attempt at the ones not reached)',
           's01_gambling': 'gambling and gaming venues, in depth', 's02_videogames': 'video games and esports, in depth', 's03_tobacco_alcohol': 'tobacco, nicotine and alcoholic drinks, in depth',
           's04_environment': 'environmental and waste services, in depth', 's05_marketing': 'marketing, advertising and PR, in depth', 's06_education': 'education and training, in depth',
           's07_diversified': 'conglomerates and family holding groups', 's08_healthcare': 'pharma, medical technology and healthcare services, in depth', 's09_retail': 'retail and e-commerce, in depth',
           's10_automotive': 'automotive and mobility, in depth', 's11_financial': 'payments, financial services and banking, in depth', 's12_consumer': 'consumer products, beauty and home, in depth',
           'c01_europe': 'largest non-listed and family companies by country, Europe (local-language rankings)', 'c02_world': 'largest non-listed, family and state companies by country, outside Europe',
           's13_food_agri': 'food, beverage and agriculture, in depth', 's14_media_sports': 'media, entertainment, sports and fitness, in depth', 's15_travel': 'travel, hotels, leisure and airlines, in depth',
           's16_tech_telecom': 'telecommunications, electronics and IT services, in depth', 's17_industrial': 'industrial, chemicals, building products and packaging, in depth', 's18_luxury_fashion': 'luxury, watches, jewellery, fashion and footwear, in depth', 's19_energy_logistics': 'energy, utilities, logistics, shipping and aerospace, in depth',
           'q01_assess': 'follow-up research on names from the discovery register (part 1)', 'q02_assess': 'follow-up research on names from the discovery register (part 2)', 'q03_assess': 'follow-up research on names from the discovery register (part 3)', 'q04_assess': 'follow-up research on names from the discovery register (part 4)', 'q05_assess': 'follow-up research on names from the discovery register (part 5)', 'q06_assess': 'follow-up research on names from the discovery register (part 6)', 'q07_assess': 'follow-up research on names from the discovery register (part 7)', 'q08_assess': 'follow-up research on names from the discovery register (part 8)', 'q09_assess': 'follow-up research on names from the discovery register (part 9)', 'q10_assess': 'follow-up research on names from the discovery register (part 10)', 'q11_assess': 'follow-up research on names from the discovery register (part 11)', 'q12_assess': 'follow-up research on names from the discovery register (part 12)', 'q13_assess': 'follow-up research on names from the discovery register (part 13)', 'q14_assess': 'follow-up research on names from the discovery register (part 14)', 'q15_assess': 'follow-up research on names from the discovery register (part 15)', 'q16_assess': 'follow-up research on names from the discovery register (part 16)', 'q17_assess': 'follow-up research on names from the discovery register (part 17)', 'q18_assess': 'follow-up research on names from the discovery register (part 18)', 'q19_assess': 'follow-up research on names from the discovery register (part 19)', 'q20_assess': 'follow-up research on names from the discovery register (part 20)', 'q21_assess': 'follow-up research on names from the discovery register (part 21)', 'q22_assess': 'follow-up research on names from the discovery register (part 22)', 'q23_assess': 'follow-up research on names from the discovery register (part 23)', 'q24_assess': 'follow-up research on names from the discovery register (part 24)', 'q25_assess': 'follow-up research on names from the discovery register (part 25)', 'q26_assess': 'follow-up research on names from the discovery register (part 26)', 'q27_assess': 'follow-up research on names from the discovery register (part 27)', 'q28_assess': 'follow-up research on names from the discovery register (part 28)', 'q29_assess': 'follow-up research on names from the discovery register (part 29)', 'q30_assess': 'follow-up research on names from the discovery register (part 30)',
           'v01_clay': 'Clay leads verified on the web (part 1)', 'v02_clay': 'Clay leads verified on the web (part 2)', 'v03_clay': 'Clay leads verified on the web (part 3)'}
FILE_OK = re.compile(r'^(watch_|dups_)?[a-z]\d\d_[a-z0-9_]+$')
def via(d):
    v = clean(d.get('discovered_via')).lower()
    return 'Clay' if 'clay' in v and 'web' not in v and 'multiple' not in v else 'Crunchbase' if 'crunchbase' in v and 'multiple' not in v else 'Multiple sources' if 'multiple' in v or ('clay' in v and 'web' in v) else 'Independent web research'
SECTORS = ['Automotive & Mobility', 'Aerospace, Defence & Space', 'Airlines & Air Travel', 'Travel, Hotels & Leisure', 'Gambling & Gaming Venues', 'Sports, Fitness & Events', 'Video Games & Esports',
           'Software, Internet & AI', 'Media, Entertainment & Publishing', 'Telecommunications', 'Semiconductors & Electronics', 'IT Services & Consulting', 'Banking & Lending', 'Insurance',
           'Investment & Capital Markets', 'Financial Services & Payments', 'Oil, Gas & Fuels', 'Utilities & Renewable Energy', 'Mining & Metals', 'Chemicals & Materials', 'Industrial Machinery & Equipment',
           'Shipping, Maritime & Shipbuilding', 'Logistics & Transportation', 'Building Products & Materials', 'Construction & Engineering', 'Real Estate', 'Home & Furniture', 'Luxury, Jewellery & Watches',
           'Beauty & Personal Care', 'Fashion, Apparel & Footwear', 'Alcoholic Drinks', 'Food & Beverage', 'Tobacco & Nicotine', 'Consumer Products', 'Retail & E-commerce', 'Pharma & Biotech',
           'Medical Devices & Diagnostics', 'Healthcare Services', 'Agriculture & Agribusiness', 'Packaging & Printing', 'Environmental & Waste Services', 'Security Services', 'Staffing & HR',
           'Marketing, Advertising & PR', 'Professional & Business Services', 'Education & Training', 'Diversified & Other']
SECKEY = {norm(s): s for s in SECTORS}
CHECKED = {'d01_asset_wealth': 330, 'd02_private_equity': 400, 'd03_industrial_europe': 230, 'd04_industrial_row': 270, 'd05_logistics_aviation': 455, 'd06_mining_chemicals': 270, 'd07_energy_telecom': 520,
           'd08_consumer_west': 450, 'd09_consumer_row': 600, 'd10_software_nonvc': 560, 'd11_financial_insurance': 330, 'd12_healthcare': 190, 'd13_services_construction': 1350, 'd14_state_parent': 330}
def sources(d):
    s = set()
    for u in list(d.get('sources') or []) + [f.get('source') for f in (d.get('fin') or []) if isinstance(f, dict)] + [x.get('source') for x in (d.get('alt_indicators') or []) if isinstance(x, dict)]:
        u = clean(u)
        if u.startswith('http'): s.add(u)
    return s
RUSSIA = re.compile(r'(?i)^\s*(russia|russian federation)\s*$')
def clean(v): return re.sub(r'\s+', ' ', str(v)).strip() if v not in (None, '') else ''
def money(m):
    if m is None: return ''
    return f'${m / 1000:,.2f}B' if abs(m) >= 1000 else f'${m:,.0f}M'
def read_jsonl(p):
    out = []
    for l in open(p, encoding='utf-8'):
        l = l.strip()
        if not l: continue
        try: d = json.loads(l)
        except Exception: continue
        if isinstance(d, dict): out.append(d)
    return out
def load(only=None):
    """only: read one batch folder (for example 'b02'); None reads every batch"""
    recs = []; dups = []; notes = {}; log = []; disc = []; clay = []
    for bd in sorted(glob.glob(os.path.join(H, 'batches', '*'))):
        batch = os.path.basename(bd)
        if only and batch != only: continue
        for p in sorted(glob.glob(os.path.join(bd, '*.jsonl'))):
            base = os.path.basename(p)[:-6]
            if base.startswith('disc_'):                 # the discovery register kept by each researcher: every name read off a list, whatever became of it
                for d in read_jsonl(p):
                    if clean(d.get('name')): d['_cluster'] = base[5:]; d['_batch'] = batch; disc.append(d)
                continue
            if not FILE_OK.match(base): continue         # work files (inputs, checks) are not research output
            if base.startswith('dups_'):
                for d in read_jsonl(p): dups.append((clean(d.get('name')), clean(d.get('why')), base[5:], batch))
                continue
            watch = base.startswith('watch_'); key = base[6:] if watch else base
            for d in read_jsonl(p):
                if clean(d.get('name')): d['_cluster'] = key; d['_batch'] = batch; d['_watchfile'] = watch; recs.append(d)
        for p in sorted(glob.glob(os.path.join(bd, 'notes_*.txt'))): notes[os.path.basename(p)[6:-4]] = open(p, encoding='utf-8', errors='replace').read()
    raw = len(recs)
    # eligibility and the duplicate check, run again on every line whatever the research did
    keep = []; excluded = []
    for d in recs:
        nm = clean(d['name']); st, disp, src, hits = C.lookup(nm + (' | ' + clean(d.get('website')) if clean(d.get('website')) else ''), batch=d['_batch'])
        if st in ('dup', 'f1'): excluded.append((nm, ('Already delivered: ' if src.startswith('delivered') else 'Already on the master: ' if st == 'dup' else 'Holds a current F1 deal: ') + src, d['_cluster'])); continue
        if RUSSIA.search(clean(d.get('hq_country'))): excluded.append((nm, 'Russian company (geographic exclusion)', d['_cluster'])); continue
        own = clean(d.get('ownership_type')).lower()
        if st == 'listed' and 'subsidiary' not in own and not re.search(r'(?i)\b(private|unlisted|not listed|family|founder|partnership|state|mutual|co-op)', own + ' ' + clean(d.get('outstanding'))):
            excluded.append((nm, 'Name matches a listed company and the line does not show it is unlisted: ' + disp, d['_cluster'])); continue
        note = next((x for x in hits if x[2] == 'info'), None)
        d['_sheet'] = note[1] if note else ''; d['_listed_name'] = disp if st == 'listed' else ''; d['_possible'] = disp if st == 'possible' else ''
        keep.append(d)
    # one line per company across clusters and batches
    best = OrderedDict(); xdup = []
    def rank(d): return (0 if d['_watchfile'] else 1, {'high': 3, 'medium': 2, 'low': 1}.get(clean(d.get('conf')).lower(), 0), len(d.get('fin') or []) + len(d.get('signals') or []))
    alias = {}
    for d in keep:
        keys = {norm(d['name']), loose(d['name'])} | ({'@' + dom(d.get('website'))} if dom(d.get('website')) else set())
        k0 = next((alias[k] for k in keys if k in alias), None)
        if k0 is None:
            k0 = norm(d['name']); best[k0] = d
        else:
            old = best[k0]; win, lose = (d, old) if rank(d) > rank(old) else (old, d)
            if clean(lose.get('sector')) and clean(lose.get('sector')) != clean(win.get('sector')): win['_secondary'] = clean(lose.get('sector'))
            for f in ('fin', 'signals', 'sponsorships', 'alt_indicators'):
                have = {json.dumps(x, sort_keys=True) for x in (win.get(f) or [])}
                win[f] = (win.get(f) or []) + [x for x in (lose.get(f) or []) if json.dumps(x, sort_keys=True) not in have]
            best[k0] = win; xdup.append((clean(lose['name']), lose['_cluster'], win['_cluster']))
        for k in keys: alias[k] = k0
    out = []
    use = Counter(u for d in best.values() for u in sources(d)); listpages = {u for u, n in use.items() if n >= 15}
    for d in best.values():
        sr = sources(d)
        # read off a ranking page only (or no page recorded): discovered, but ownership and the Formula 1 case were not looked at company by company
        d['_discovery_only'] = (not sr) or sr <= listpages
        sec = SECKEY.get(norm(clean(d.get('sector'))))
        if not sec: sec = 'Diversified & Other'; d['_sector_note'] = clean(d.get('sector'))
        d['sector'] = sec; d['A'] = S.assess(d); d['_via'] = via(d); out.append(d)
    if only != 'b01':
        for p in sorted(glob.glob(os.path.join(H, 'discovery', 'clay', '*.jsonl'))):
            for d in read_jsonl(p):
                if clean(d.get('name')): d['_file'] = os.path.basename(p)[:-6]; clay.append(d)
        for p in sorted(glob.glob(os.path.join(H, 'discovery', 'clay', 'notes_*.txt'))): notes[os.path.basename(p)[6:-4]] = open(p, encoding='utf-8', errors='replace').read()
    n = Counter(d['_cluster'] for d in disc)
    for k, v in n.items(): CHECKED[k] = v
    return {'recs': out, 'raw': raw, 'excluded': excluded, 'xdup': xdup, 'dups': dups, 'notes': notes, 'disc': disc, 'clay': clay, 'only': only}
def order_key(d): a = d['A']; return (-a['total'], -a['fin'], -a['fit'], -a['intent'], -a['access'], len(a['flags']), clean(d['name']).lower())
def classify(R):
    """qualified = a route is met and capacity is Confirmed or Indicative; watch = no route met (financial verification needed); low = Insufficient capacity"""
    X = [d for d in R if d.get('_discovery_only')]; R = [d for d in R if not d.get('_discovery_only')]
    classify.discovered = sorted(X, key=lambda d: (d['sector'], -(d['A']['M'].get('revenue', (0,))[0]), clean(d['name']).lower()))
    Q = [d for d in R if d['A']['conf'] in ('Confirmed capacity', 'Indicative capacity')]; W = [d for d in R if d['A']['conf'] == 'Unverified capacity']; I = [d for d in R if d['A']['conf'] == 'Insufficient capacity']
    Q.sort(key=order_key)
    for i, d in enumerate(Q, 1): d['rank_all'] = i
    tab = defaultdict(list)
    for d in Q: d['tab'] = 'Domestic' if clean(d.get('reach')).title() == 'Domestic' else d['sector']; tab[d['tab']].append(d)
    for t, L in tab.items():
        if t == 'Domestic':
            by = defaultdict(int)
            for d in L: by[d['sector']] += 1; d['rank_sector'] = by[d['sector']]
        else:
            for i, d in enumerate(L, 1): d['rank_sector'] = i
    W.sort(key=lambda d: (-(d['A']['fit'] + d['A']['intent'] + d['A']['access']), clean(d['name']).lower()))
    for i, d in enumerate(W, 1): d['rank_all'] = i; d['rank_sector'] = ''; d['tab'] = 'Verification Watchlist'
    for d in I: d['rank_all'] = ''; d['rank_sector'] = ''; d['tab'] = 'Not prioritised'
    return Q, W, I, tab
# ---------------------------------------------------------------- the main row, in the master's column order
def figline(M, k):
    v = M.get(k)
    if not v: return ''
    bits = [b for b in (v[1], v[2], v[4] if v[4] and not v[4].upper().startswith('USD') else '') if b]
    return f"{money(v[0])}" + (' (' + '; '.join(bits) + ')' if bits else '')
def parent_cell(d):
    own = clean(d.get('ownership_type')); pi = clean(d.get('parent_immediate')); pu = clean(d.get('parent_ultimate')); pl = clean(d.get('parent_listed')).lower(); pe = clean(d.get('pe_swf_owner'))
    if pi.lower() in ('none', 'n/a', 'na', '-'): pi = ''
    if pu.lower() in ('none', 'n/a', 'na', '-') or pu == pi: pu = ''
    if pi:
        t = pi + ({'listed': ' (listed)', 'private': ' (privately held)', 'state': ' (state-owned)'}.get(pl, ' (listing status to verify)' if 'verif' in pl else ''))
        if pu: t += '; ultimate parent: ' + pu
        if pe and pe.lower() not in t.lower(): t += '; controlling investor: ' + pe
        t += '. Own marketing function: ' + (clean(d.get('marketing_autonomy')) or 'unknown')
        if clean(d.get('parent_backing')): t += '. Backing: ' + clean(d.get('parent_backing'))
        return t
    if 'verification' in own.lower(): return 'Ownership requires verification'
    if pe: return f'None: owned by an investment firm or fund ({pe})'
    if own.lower() in ('state-owned', 'sovereign fund-backed'): return 'None: state-owned' + (f' ({pu})' if pu else '')
    return 'None (independent company)'
def sig_cells(d):
    out = {'capital': [], 'ipo': [], 'geographic': [], 'marketing': [], 'other': []}; cats = set()
    for s in d.get('signals') or []:
        if not isinstance(s, dict) or not clean(s.get('what')): continue
        st = clean(s.get('status')).lower(); cat = clean(s.get('category')).lower(); ok = st == 'confirmed' and clean(s.get('source')).startswith('http') and (S.months_ago(s.get('date')) or 99) <= 24
        t = ('Confirmed: ' if ok else 'Lead only: ') + clean(s['what']) + ' (' + '; '.join(b for b in (clean(s.get('date')), clean(s.get('source'))) if b) + ')'
        if ok: cats.add(cat)
        if re.search(r'(?i)\bipo\b|initial public offering|stock market listing|to list on', clean(s['what'])): out['ipo'].append(t)
        out[cat if cat in ('capital', 'geographic', 'marketing') else 'other'].append(t)
    return out, cats
def evidence(d):
    a = d['A']; M = a['M']
    if a['route'] in ('A', 'B'):
        ks = S.std_hits(d, M) if a['route'] == 'A' else [k for k, (lo, hi) in S.EXC.items() if k in M and lo <= M[k][0] < hi]
        if ks:
            k = ks[0]; v = M[k]; t = f"{S.LABEL[k].capitalize()}: {v[4] or money(v[0])}" + (f" (USD {v[0]:,.0f}M)" if v[4] and not v[4].upper().startswith('USD') else '') + '; '.join([''] + [b for b in (v[1], v[2]) if b])
            if a['route'] == 'B' and clean(d.get('exception_note')): t += '. Exception: ' + clean(d['exception_note'])
            return t, v[3]
        if S.backing(d): return 'Backing: ' + clean(d['parent_backing']), next((u for u in (d.get('sources') or []) if str(u).startswith('http')), '')
        sp = next((s for s in (d.get('sponsorships') or []) if isinstance(s, dict) and clean(s.get('rights_holder'))), None)
        if sp: return 'Existing sponsorship: ' + '; '.join(clean(sp.get(k)) for k in ('rights_holder', 'designation', 'announced') if clean(sp.get(k))), clean(sp.get('source'))
    alt = [x for x in (d.get('alt_indicators') or []) if isinstance(x, dict) and clean(x.get('indicator'))]
    if alt: return 'Indicators of scale: ' + '; '.join(clean(x['indicator']) + (': ' + clean(x.get('evidence')) if clean(x.get('evidence')) else '') for x in alt[:4]), next((clean(x.get('source')) for x in alt if clean(x.get('source'))), '')
    return 'No qualifying figure found on the pages read', ''
COLS = FMT['columns'][:7] + ['Outreach Rank (Sector)', 'Outreach Rank (All Sectors)', 'Overall Score (0-100)'] + FMT['columns'][7:]
WIDTH = FMT['widths'][:7] + [11, 11, 11] + FMT['widths'][7:]
def row(d, watch=False):
    a = d['A']; M = a['M']; sig, cats = sig_cells(d); ev, evsrc = evidence(d)
    hq = ', '.join(b for b in (clean(d.get('hq_city')), clean(d.get('hq_country'))) if b) or 'Not recorded'
    own = clean(d.get('ownership_type')) or 'requires verification'; pl = clean(d.get('parent_listed')).lower(); pi = clean(d.get('parent_immediate'))
    liq = '; '.join(f"{S.LABEL[k].capitalize()}: {figline(M, k)}" for k in ('equity_funding', 'valuation', 'transaction_value', 'aum', 'debt_funding') if k in M) or 'Not disclosed'
    prof = '; '.join(f"{S.LABEL[k].capitalize() if k != 'ebitda' else 'EBITDA'}: {figline(M, k)}" for k in ('ebitda', 'net_income') if k in M) or ('Profitable, figure not disclosed' if clean(d.get('profitability')).lower().startswith('profit') else 'Not found')
    periods = sorted({v[1] for v in M.values() if v[1]}, key=lambda p: S.year(p) or 0)
    srcs = []
    for u in [v[3] for v in M.values()] + list(d.get('sources') or []):
        u = clean(u)
        if u.startswith('http') and u not in srcs: srcs.append(u)
    sp = '; '.join(clean(s.get('rights_holder')) + ' (' + ', '.join(clean(s.get(k)) for k in ('sport', 'designation', 'announced') if clean(s.get(k))) + ')' for s in (d.get('sponsorships') or []) if isinstance(s, dict) and clean(s.get('rights_holder'))) or 'None found'
    why_now = next((clean(s.get('what')) + ' (' + clean(s.get('date')) + ')' for s in (d.get('signals') or []) if isinstance(s, dict) and clean(s.get('status')).lower() == 'confirmed' and clean(s.get('what'))), '')
    rationale = clean(d.get('fit_rationale')) + (' Why now: ' + why_now + '.' if why_now else '') + (' Customer overlap: ' + clean(d['customer_overlap']) + '.' if clean(d.get('customer_overlap')) else '')
    conflict = clean(d.get('category_conflict')) or 'not assessed'
    notes = [a['conf_why'], 'Investment tier basis: ' + a['tier_why']] + a['flags']
    if clean(d.get('outstanding')): notes.append('Still to verify: ' + clean(d['outstanding']))
    if clean(d.get('distress')): notes.append('Strain noted: ' + clean(d['distress']))
    if d.get('_listed_name'): notes.append(f"Its name matches the listed company {d['_listed_name']}: confirm this is the unlisted business")
    if d.get('_possible'): notes.append('Close to a master name, judged a different company: ' + d['_possible'])
    if d.get('_sector_note'): notes.append('Sector as recorded by the research: ' + d['_sector_note'])
    sheet = d.get('_sheet') or ''
    onsheet = ('Not on the master. On your older 48-tab sheet (' + sheet.split(': ', 1)[-1].replace(' (you marked it x)', '') + ')') if sheet.startswith('your older 48-tab sheet') and ': ' in sheet else 'Not on the master. On your older 48-tab sheet' if sheet else 'No (new brand)'
    c = [clean(d['name']), '', '', 'x' if 'you marked it x' in sheet else '', hq, a['tier_txt'] + (' (estimate)' if a['tier'] else ''), a['priority'] if not watch else 'To Verify',
         d.get('rank_sector', '') if not watch else '', d.get('rank_all', ''), a['total'],
         clean(d.get('desc')), d['sector'] + (': ' + clean(d.get('subsector')) if clean(d.get('subsector')) else ''),
         d.get('_listing_txt') or (('Not listed: subsidiary of ' + pi + (' (listed)' if pl == 'listed' else '')) if pi and 'subsidiary' in own.lower() else 'Private (not listed)'),
         (figline(M, 'revenue') or (('ARR ' + figline(M, 'arr')) if 'arr' in M else 'Not disclosed')), 'Not applicable (not listed)', 'Not found', prof, liq,
         figline(M, 'marketing_spend') or 'Not Disclosed', clean(d.get('reach')).title() or 'Not recorded',
         clean(d.get('markets')) + (' Expansion: ' + clean(d['expansion_markets']) if clean(d.get('expansion_markets')) else ''), rationale,
         periods[-1] if periods else 'Not stated', '; '.join(srcs[:5]) or 'None recorded',
         f'Not on the 2025-26 F1 partner roster (checked {DATE}). Category check: {conflict}', a['conf'], '; '.join(n for n in notes if n) or 'None flagged', round(a['fit'] / 30 * 100, 1), (clean(d.get('conf')) or 'medium').title(),
         onsheet, d.get('tab', d['sector']), d['sector'], clean(d.get('subsector')), own, parent_cell(d),
         'Pre-revenue' if re.search(r'(?i)pre-revenue|no revenue yet', clean(d.get('desc')) + ' ' + clean(d.get('outstanding'))) else 'Selling',
         (f"Route {a['route']}: {a['route_why']}" if a['route'] != 'none' else 'No route met yet'), ev, evsrc, sp,
         '; '.join(sig['capital']) or 'None found', '; '.join(sig['ipo']) or 'None found', '; '.join(sig['geographic']) or 'None found', '; '.join(sig['marketing'] + sig['other']) or 'None found',
         min(4, len(cats)), ('Yes: ' + clean(d['expansion_markets'])) if clean(d.get('expansion_markets')) else ('Yes: see new regions' if sig['geographic'] else 'Not found'),
         f"Revised methodology, batch {d['_batch'][1:].lstrip('0') or '1'} ({DATE}). Found through: {d.get('_via') or 'Independent web research'}. Research: {CLUSTER.get(d['_cluster'], d['_cluster'])}", f'New: added on {DATE}']
    assert len(c) == len(COLS), (len(c), len(COLS))
    return c
SUPCOLS = ['Company', 'Website', 'Other Names', 'Sector', 'Subsector', 'Secondary Sector', 'Description', 'Products and Services', 'Business Model', 'Target Customers', 'Ownership Structure', 'Immediate Parent',
           'Ultimate Parent', 'Parent Listed or Private', 'Private Equity or Sovereign Owner', 'Minority Investors', 'Own Marketing Function', 'Basis for That', 'Parent or State Backing (evidence)',
           'Headquarters', 'Employees', 'Countries', 'Stores or Sites', 'Operating Markets', 'Expansion Markets', 'Geographic Reach', 'Relevant F1 Race Markets',
           'Revenue', 'ARR', 'EBITDA', 'Net Income', 'Equity Funding', 'Debt Funding', 'Valuation', 'Acquisition or Transaction Value', 'AUM', 'Marketing Expenditure', 'All Figures (original currency, period, reported or estimated, source)',
           'Alternative Indicators of Scale', 'Qualification Route', 'What Met the Route', 'Exception Note (Route B)', 'Profitability', 'Signs of Strain', 'Financial Confidence', 'Why That Confidence',
           'Estimated Annual Investment Tier', 'Tier Basis', 'Company Type Used for the Tier', 'Existing Sponsorships', 'Buying Signals (dated, with source)', 'F1 Rationale', 'Customer Overlap With F1',
           'Fit Ratings (0-3)', 'Category Conflict', 'Decision-Maker Roles', 'Owner- or Founder-Led', 'Structure', 'Score: Financial Capacity (35)', '  Affordability (14)', '  Reliability (9)', '  Strength (8)',
           '  Marketing Shown (4)', 'Score: F1 Fit (30)', 'Score: Buying Intent (25)', 'Score: Accessibility (10)', 'Overall Score (100)', 'Priority', 'Rank in Sector', 'Rank Across Sectors',
           'Compliance Points', 'Still to Verify', 'Sources', 'Date Last Verified', 'Master Spreadsheet Check', 'Research Cluster', 'Discovered Through', 'Discovery Source']
SUPW = [30, 22, 20, 24, 22, 20, 44, 30, 10, 28, 22, 24, 24, 14, 22, 24, 10, 28, 36, 22, 10, 9, 14, 34, 28, 13, 24, 18, 14, 14, 14, 16, 14, 14, 16, 14, 14, 60, 50, 9, 34, 34, 14, 24, 18, 36, 22, 40, 22, 40, 60, 46, 30, 40, 34,
        30, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 9, 9, 24, 36, 50, 13, 40, 34, 22, 40]
def suprow(d):
    a = d['A']; M = a['M']; g = lambda k: clean(d.get(k))
    allfig = '; '.join(f"{S.LABEL.get(clean(f.get('metric')), clean(f.get('metric')))}: {clean(f.get('value_orig'))} = USD {f.get('usd_m')}M, {clean(f.get('period'))}, {clean(f.get('kind'))}, {clean(f.get('source'))}" for f in (d.get('fin') or []) if isinstance(f, dict))
    alt = '; '.join(clean(x.get('indicator')) + ': ' + clean(x.get('evidence')) + ' (' + clean(x.get('source')) + ')' for x in (d.get('alt_indicators') or []) if isinstance(x, dict) and clean(x.get('indicator')))
    sp = '; '.join(', '.join(f"{k.replace('_', ' ')}: {clean(s.get(k))}" for k in ('rights_holder', 'sport', 'designation', 'announced', 'duration', 'value', 'source') if clean(s.get(k))) for s in (d.get('sponsorships') or []) if isinstance(s, dict))
    sg = '; '.join(f"[{clean(s.get('category'))}, {clean(s.get('status'))}] {clean(s.get('what'))} ({clean(s.get('date'))}; {clean(s.get('source'))})" for s in (d.get('signals') or []) if isinstance(s, dict) and clean(s.get('what')))
    fit = d.get('fit') or {}; acc = d.get('access') or {}
    sheet = d.get('_sheet') or ''
    c = [g('name'), g('website'), '; '.join(clean(x) for x in (d.get('aliases') or []) if clean(x)), d['sector'], g('subsector'), d.get('_secondary', ''), g('desc'), g('products'), g('model'), g('customers'), g('ownership_type'),
         g('parent_immediate'), g('parent_ultimate'), g('parent_listed'), g('pe_swf_owner'), g('minority_investors'), g('marketing_autonomy'), g('marketing_autonomy_basis'), g('parent_backing'),
         ', '.join(b for b in (g('hq_city'), g('hq_country')) if b), d.get('employees') if isinstance(d.get('employees'), (int, float)) else g('employees'), d.get('countries') if isinstance(d.get('countries'), (int, float)) else g('countries'),
         g('stores_or_sites'), g('markets'), g('expansion_markets'), g('reach').title(), g('f1_markets')] + [figline(M, k) or 'Undisclosed' for k in ('revenue', 'arr', 'ebitda', 'net_income', 'equity_funding', 'debt_funding', 'valuation', 'transaction_value', 'aum', 'marketing_spend')] + [
         allfig, alt, a['route'] if a['route'] != 'none' else 'None met', a['route_why'], g('exception_note'), g('profitability') + (': ' + g('profitability_basis') if g('profitability_basis') else ''), g('distress'), a['conf'], a['conf_why'],
         a['tier_txt'], a['tier_why'], a['type'], sp, sg, g('fit_rationale'), g('customer_overlap'), ', '.join(f"{k} {fit.get(k, 0)}" for k in ('b2b', 'ecosystem', 'technical', 'hospitality', 'geography', 'brand', 'consumer', 'category')),
         g('category_conflict'), clean(acc.get('roles')), clean(acc.get('owner_led')), clean(acc.get('structure')), a['fin'], a['fin_parts']['affordability'], a['fin_parts']['reliability'], a['fin_parts']['strength'],
         a['fin_parts']['marketing'], a['fit'], a['intent'], a['access'], a['total'], a['priority'], d.get('rank_sector', ''), d.get('rank_all', ''), g('compliance'), g('outstanding'),
         '; '.join(clean(u) for u in (d.get('sources') or []) if clean(u)), g('verified') or '2026-11-27',
         f'Checked {DATE}: not on the master spreadsheet' + ('; it is on your older 48-tab sheet' if sheet else ''), CLUSTER.get(d['_cluster'], d['_cluster']), d.get('_via') or 'Independent web research', clean(d.get('discovery_source'))]
    assert len(c) == len(SUPCOLS) == len(SUPW), (len(c), len(SUPCOLS), len(SUPW))
    return c
if __name__ == '__main__':
    D = load(sys.argv[3] if len(sys.argv) > 3 else None); Q, W, I, tab = classify(D['recs'])
    print('lines read', D['raw'], '| removed by the duplicate and eligibility check', len(D['excluded']), Counter(e[1].split(':')[0] for e in D['excluded']), '| repeated across clusters', len(D['xdup']), '| companies', len(D['recs']))
    print('discovered from a ranking only, not yet assessed', len(classify.discovered))
    print('qualified', len(Q), Counter(d['A']['conf'] for d in Q), '| verification watchlist', len(W), '| insufficient', len(I))
    print('priority', Counter(d['A']['priority'] for d in Q), '| routes', Counter(d['A']['route'] for d in Q), '| tiers', Counter(d['A']['tier_txt'].split(':')[0] for d in Q))
    print('tabs', {t: len(L) for t, L in tab.items()})
    for d in Q[:12]: a = d['A']; print(f"  {d['rank_all']:3d} {a['total']:5.1f} {a['priority']:9s} fin {a['fin']:4.1f} fit {a['fit']:4.1f} int {a['intent']:4.1f} acc {a['access']:2d} | {clean(d['name'])[:30]:30s} | {d['sector'][:26]:26s} | {a['conf'][:10]} {a['tier_txt'][:6]} R{a['route']}")
    if len(sys.argv) > 2 and sys.argv[1] == 'xlsx':
        import write as Wr
        Wr.write(D, Q, W, I, tab, sys.argv[2], classify.discovered); print(sys.argv[2])
