"""Texts and small tables for the all-sector non-listed prospects workbook."""
import json, os, re
from collections import Counter, defaultdict
import bp_build as b
H = os.path.dirname(os.path.abspath(__file__))
BCOLS = ['Company', 'Headquarters', 'Sector', 'What It Does', 'Ownership', 'Published Revenue (USD bn)', 'Year', 'Ranking It Comes From', 'Source', 'On Your Sheet?', 'Parameter 3: Can It Pay?']
SCOLS = ['Sector or Group', 'On Your Sheet Today', 'Why the Sheet Misses It', 'Examples', 'How to Add It']
# owners of current F1 partners that a name match does not catch (checked by hand, 16 Nov 2026)
F1_OWNERS = {'MSC Group': 'MSC Cruises', 'CMA CGM Group': 'CEVA Logistics', 'J.C.B. Service': 'JCB', 'Suntory Holdings Ltd.': 'Jim Beam'}
def beyond(rows, A):
    p = os.path.join(H, 'data', 'large_private.jsonl'); out = []
    if not os.path.exists(p): return out
    names = {b.loose(x['name']) for x in rows} | {b.loose(x['r']['brand']) for x in rows} | {b.loose(d['name']) for d in A['f1x']}
    seen = set()
    for l in open(p, encoding='utf-8'):
        try: d = json.loads(l)
        except Exception: continue
        k = b.loose(d.get('name', ''))
        if not k or k in seen or b.f1_link(d['name'])[0] or d['name'] in F1_OWNERS: continue          # current F1 partners and their owners are left out
        seen.add(k); rev = d.get('revenue_usd_bn')
        if not isinstance(rev, (int, float)) or rev < 0.3: continue
        out.append([d['name'], d.get('hq', ''), d.get('sector', ''), d.get('what_it_does', ''), d.get('ownership', ''), rev, str(d.get('revenue_year', '')), d.get('ranking', ''), d.get('source', ''),
                    'Yes' if k in names else 'No', 'Yes: published revenue of USD 300M or more (ranking figure)'])
    out.sort(key=lambda r: (r[9] != 'No', -r[5]))
    return out
def sectors(rows, B):
    P = [x for x in rows if x['status'] == 'private' and x['stage'] in ('commercial', 'pre-revenue')]
    th = Counter(x['theme'] for x in P)
    bysec = defaultdict(list)
    for r in B:
        if r[9] == 'No': bysec[r[2]].append(r[0])
    top = lambda *keys, n=8: ', '.join([nm for s, v in bysec.items() if any(k.lower() in s.lower() for k in keys) for nm in v][:n]) or 'See the Beyond Your Sheet tab'
    nb = sum(1 for r in B if r[9] == 'No')
    return [
     ['Family- and founder-owned consumer groups (food, drink, retail, fashion)', 'Only where Crunchbase recorded a funding round', 'They never raised venture money, so a funding search does not return them', top('food', 'beverage', 'retail', 'consumer', 'fashion', 'apparel'),
      f'Public revenue rankings: the Beyond Your Sheet tab holds {nb} such companies not on your sheet. Next: national rankings country by country.'],
     ['Large private industrial, automotive, construction and commodity groups', 'Partly', 'Same reason: self-funded or family-owned', top('automotive', 'industrial', 'construction', 'engineering', 'manufactur', 'agricult', 'commodit', 'energy', 'logistics'),
      'Same rankings; then filed accounts in Europe and the UK to confirm revenue.'],
     ['Self-funded online brokers and trading platforms', 'A handful', 'No outside funding; revenue comes from trading',
      'Already in F1, which shows the category buys: IC Markets, Pepperstone, AvaTrade, FxPro, Libertex. Their unlisted rivals are the prospects.', 'Regulator registers (UK, Cyprus, Australia) and industry volume rankings.'],
     ['Crypto exchanges without venture funding', 'Only the venture-backed ones', 'Several large exchanges are founder-funded', 'Already in F1: Gate.io, Zoomex, BingX, Nexo. Prospects are the other large exchanges by trading volume.', 'Public exchange-volume rankings, then a licence check per race market.'],
     ['Betting operators and prediction markets', f"{th['Prediction markets, betting & iGaming']} private companies", 'Most operators are self-funded; Polymarket is not on the sheet', 'On the sheet: Kalshi, Superbet, Tipico. F1 named Betway and FanDuel as official betting operators in 2026.',
      'Regulator licence lists and industry rankings; legal check per market before any approach.'],
     ['Private-equity-owned companies', 'Where a buyout was recorded as funding', 'Buyout money goes to the previous owners; many have no "funding" on record', 'Already in F1: Solera, UKG, Emburse. Prospects are other large PE-owned software, services and consumer companies.',
      'Portfolio pages of the large PE firms; credit-rating notes for revenue.'],
     ['Professional partnerships (accounting, consulting, law)', 'Almost none', 'Partnerships take no outside funding', 'Already in F1: Deloitte, PwC, Ashurst, Morrison Foerster. Prospects: ' + top('professional', 'consult', 'account', 'legal', 'law'),
      'Published firm revenues (annual reviews, legal and consulting league tables).'],
     ['State-backed commercial brands', f"{sum(1 for x in rows if x['status'] == 'state-owned' and x['stage'] == 'commercial')} companies", 'Recorded only when they raised debt or equity', ', '.join(list(dict.fromkeys(re.sub(r'^.*\((\w+)\)$', r'\1', x['name']) for x in sorted([x for x in rows if x['status'] == 'state-owned' and x['stage'] == 'commercial' and x['reach'] in ('Global', 'International') and x['rel'] >= 3], key=lambda x: -x['amt'])))[:8]),
      'Portfolio pages of the sovereign funds (Gulf, Singapore, others) for consumer and travel brands being built internationally.'],
     ['Private aviation and luxury travel', 'A few', 'Mostly founder- or family-owned', 'Already in F1: Flexjet, VistaJet, Jet365. On the sheet: Abercrombie & Kent, Four Seasons, Soho House.', 'Industry fleet rankings and luxury-travel trade lists.'],
     ['Frontier technology: quantum, space, nuclear and fusion, defence', f"{th['Quantum computing']} quantum, {th['Space & satellites']} space, {th['Nuclear & fusion energy']} nuclear and fusion, {th['Defence technology']} defence",
      'On the sheet, but changing fast: over two thirds raised money in the last 12 months', 'Tagged in the Theme column of every prospects tab.', 'Re-run the Crunchbase search each quarter; these now stay in as pre-revenue where they have no sales.'],
     ['AI infrastructure, AI chips, robotics and autonomous driving', f"{th['AI infrastructure: data centres & GPU cloud']} AI infrastructure, {th['AI chips & semiconductors']} chips, {th['Robotics, humanoids & autonomous driving']} robotics",
      'On the sheet under Software, IT Services, Semiconductors and Industrial tabs rather than as their own sectors', 'Tagged in the Theme column.', 'Filter the Theme column; consider giving each its own tab on your sheet.'],
    ]
def summary(A, rows, L, core, other):
    n = len(A['B']); listed = sum(1 for x in rows if x['status'] == 'listed'); rk = Counter(x['rank'] for x in core); rc = Counter(x['reach'] for x in core)
    web = [x for x in L if x['webchecked']]; dropped = [x for x in rows if x.get('dropped')]
    S = lambda k, v: sum(1 for x in core if x['S'][k][0] == v)
    import allsector
    ins = {id(x) for x in L}; oc = Counter(allsector.reason_out(x, None).split(' ')[0] for x in rows if id(x) not in ins)
    out = [('Non-listed prospects across all sectors - parameter check of every brand on your sheet (16 Nov 2026)',),
           [f"Sheet: F1-SCREEN-RECORDINGS-ALL-BRANDS-RANKED-2026-11-02-2 (unchanged since 15 Nov). {n:,} brands on 48 sector tabs, each checked against the parameter set agreed on 16 Nov 2026."], [],
           ('Parameters 1 and 2: who is in scope',),
           [f"{len(L):,} brands are operating companies not listed on a stock exchange: {sum(1 for x in L if x['status'] == 'private'):,} private, {sum(1 for x in L if x['status'] == 'state-owned')} state-owned, "
            f"{sum(1 for x in L if x['status'] == 'subsidiary')} owned by a parent that is not a listed company in my data, {sum(1 for x in L if x['status'] == 'unknown'):,} whose ownership is not confirmed."],
           [f"Out of scope ({sum(oc.values()) + len(A['f1x']):,}): {oc['Listed']:,} listed; {oc['Owned']:,} owned by a listed group; {oc['Closed']} closed or absorbed; {oc['Investment'] + oc['Single-project']} funds and single-project vehicles; "
            f"{oc['Public']} public bodies and non-profits; {len(A['f1x'])} current F1 partners or their owners"
            + (f"; {oc['Now']} found by the web check to be listed or publicly traded ({', '.join(x['name'] for x in dropped)})." if dropped else '.')],
           ['The "All Brands - Parameters" tab lists every brand with the parameters it meets and, where it is out of scope, the reason.'], [],
           ('Parameter 3: can it pay',),
           [f"{len(core):,} private and state-owned companies pass on funding: USD 150M or more raised in total, any date. {sum(1 for x in core if x['stage'] == 'pre-revenue')} of them have no revenue yet and are labelled Pre-revenue."],
           ['The figure is the Crunchbase total, which includes debt where Crunchbase counts it. Equity-only figures, published revenue, valuations and existing sponsorships have not been collected for these brands yet.'], [],
           ('Parameter 4: reason to buy now',),
           [f"Raised money in the past 12 months: {S('raise', 'Confirmed'):,} confirmed from the Crunchbase round date."],
           [f"Preparing an IPO, opening in new regions, marketing activity: looked up on the web for {len(web)} companies (the strongest two per sector, then the next strongest overall). Confirmed: IPO preparation {S('ipo', 'Confirmed')}, "
            f"new regions {S('regions', 'Confirmed')}, marketing activity {S('marketing', 'Confirmed')}. For all other companies these three signals read \"Not yet checked\" or \"Lead only\"."], [],
           ('Parameter 5: reach',),
           [f"Global {rc['Global']:,}; International {rc['International']:,}; Regional {rc['Regional']:,}; Domestic {rc['Domestic']:,}. Domestic brands are on their own tab; the sector tabs hold Global, International and Regional brands."], [],
           ('Result',),
           [f"High (two or more confirmed reasons): {rk['High']}. Medium (one confirmed reason): {rk['Medium']:,}. To Verify (no reason confirmed yet): {rk['To Verify']:,}."],
           [f"A further {len(other):,} brands are on the \"Ownership To Confirm\" tab: their owner or listing status could not be confirmed, or they fall short on recorded funding."], [],
           ('Sectors beyond the sheet',),
           ['The sheet was built from a Crunchbase funding search, so it under-covers companies that never raised venture money. The "Sectors To Add" tab lists the groups it misses and how to add each.'],
           ['The "Beyond Your Sheet" tab is a first tranche: large unlisted companies with a published revenue figure taken from public rankings. They pass parameter 3 on revenue; their signals and reach have not been checked yet.'], [],
           ('Limits',),
           ['Only the companies looked up on the web can reach High, because three of the four signals need a public source. The web-search allowance covers about 90 companies per message at two searches each.'],
           ['Reach, description and ownership of most brands are desk assessments from the earlier profiling; the Verification Notes say what to check.'],
           ['"Lead only" means the earlier profile mentions it but no public source was checked. It does not count towards the result.']]
    return out
KEY = [('Parameter 1: scope', 'Any operating company, any country, not listed on a stock exchange. All 48 sector tabs of your sheet are covered.'),
       ('Parameter 2: removed', 'Current F1 championship, team or Grand Prix partners and their owners; investment funds; single-project vehicles; closed companies; companies owned by a listed group. Companies with no revenue yet stay in, labelled Pre-revenue.'),
       ('Parameter 3: can it pay', 'Any one of: equity raised of USD 150M or more in total (any date); published revenue of USD 300M or more; valued at or bought for USD 1B or more in the past three years; already pays for a top-tier sports sponsorship; owned by a state fund building the brand internationally. In this workbook the brands from your sheet are tested on the first (Crunchbase total funding); the Beyond Your Sheet tab is tested on the second.'),
       ('Parameter 4: reason to buy now', 'Raised money in the past 12 months; preparing an IPO; opening in new regions; marketing activity (five or more open marketing roles of any kind, a marketing role in a country where it has no office, a new marketing chief, or a rebrand).'),
       ('Signal status', 'Confirmed = a source states it (the source and date are in the cell). Lead only = mentioned in the earlier profile, not checked. Not yet checked = not looked up. Checked: nothing found = looked up on the web on 16 Nov 2026 with no result. Not met = the Crunchbase round date is older than 12 months.'),
       ('Parameter 5: reach', 'Global = North America, Europe and Asia-Pacific at real scale. International = two or more world regions. Regional = several countries in one region. Domestic = essentially one country. "Expanding?" says Yes (confirmed) or Possibly (lead only).'),
       ('Outreach Priority', 'High = passes parameter 3 and has two or more confirmed reasons. Medium = one confirmed reason. To Verify = no reason confirmed yet, or capacity not shown.'),
       ('F1 Investment Category', '"Qualifies" = passes parameter 3. "To Verify" = not shown.'),
       ('Fit Score (0-100)', 'Sector fit (25%), relevance of the company to F1 (50%) and reach (25%). Used only to order brands inside the same priority.'),
       ('Ownership Type', 'Private; private and owned by an investment firm; state-owned; owned by a parent that is not a listed company in my data; ownership not confirmed.'),
       ('Theme', 'A cross-sector tag (for example quantum computing, robotics, AI infrastructure), assigned automatically from the company\'s industry label.'),
       ('Other columns', 'As in the earlier brand workbook: headquarters, description, sector, markets, rationale, sources, verification notes, profile confidence, your x mark, and the brand name and tab as on your sheet.')]
