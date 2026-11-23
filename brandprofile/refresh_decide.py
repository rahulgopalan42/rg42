"""Refresh of 23 Nov 2026: the hand-judged effect of each event on the two lists.
Reads newsec/refresh/resolved.json (events), talks_in_*.jsonl and talks_out_*.jsonl.
Writes newsec/refresh/decisions.json, talks_status.json and info_rows.json, which newsectors.py and allsector.py read.
Rules: a closed equity round = "raised" confirmed; debt only = note; a report of talks or bank hires = lead only;
a regulator approval or a filing = "preparing an IPO" confirmed; own shares now trade = removed;
bought and completed = parent set; bought but not completed = note; a new top-tier sponsorship = marketing confirmed."""
import glob, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); RD = os.path.join(H, 'newsec', 'refresh')
R = json.load(open(os.path.join(RD, 'resolved.json'), encoding='utf-8'))
def ev(f, company, event=None, n=0):
    hit = [d for d in R if d['file'] == f and d['company'] == company and (event is None or d['event'] == event)]
    if not hit: raise SystemExit(f'no event {f} / {company} / {event}')
    return hit[n]
DEC = {'new': {}, 'sheet': {}}; USED = set()
def _add(kind, name, e, d):
    USED.add((e['file'], e['line']))
    d['date'] = d.get('date') or e.get('date') or ''; d['source'] = e.get('source_url') or ''
    DEC[kind].setdefault(name, []).append(d)
def sig(kind, name, key, e, why, lead=False, date=''):
    when = date or e.get('date') or 'Nov 2026'
    txt = ('Reportedly: ' if lead else '') + why + f" ({when}; {e.get('source_url')})"
    _add(kind, name, e, {'action': 'signal', 'why': ('Reported, not confirmed: ' if lead else '') + why, 'signals': {key: txt}, 'lead': lead, 'date': when})
def note(kind, name, e, why, date=''): _add(kind, name, e, {'action': 'note', 'why': why, 'date': date})
def drop(kind, name, e, why): _add(kind, name, e, {'action': 'drop', 'why': why})
def parent(kind, name, e, why, par, listed): _add(kind, name, e, {'action': 'parent', 'why': why, 'parent': par, 'parent_listed': listed, 'parent_stake': ''})
N, S = 'new', 'sheet'

# ---- new-brands list of 18 Nov
sig(N, 'Sand.ai', 'raise', ev('apac', 'Sand.ai'), 'Raised USD 200M in a Series A extension, its third round of 2026')
sig(N, 'Q-CTRL', 'raise', ev('apac', 'Q-CTRL'), 'Raised USD 290M (AUD 425M) Series C led by Salesforce Ventures, valued above USD 1B')
sig(N, 'HOUMO.AI', 'raise', ev('apac', 'Houmo.ai'), 'Raised a Series B round of undisclosed size')
sig(N, 'Genesis AI', 'raise', ev('europe', 'Genesis AI'), 'Raised USD 500M Series A at a USD 3.5B valuation')
sig(N, 'Model ML', 'raise', ev('europe', 'Model ML'), 'Raised USD 250M Series B at a USD 1.5B valuation')
sig(N, 'UFORCE', 'raise', ev('europe', 'UFORCE'), 'Raised USD 700M Series A at a USD 6B valuation')
sig(N, 'Sentra', 'raise', ev('us_ai', 'Sentra'), 'Raised USD 150M Series C led by Capital One Ventures')
sig(N, 'Traversal', 'raise', ev('us_ai', 'Traversal'), 'Raised USD 120M at a USD 1B valuation')
sig(N, 'Rox', 'raise', ev('us_ai', 'Rox'), 'Raised USD 100M Series B at a USD 1.3B valuation')
sig(N, 'Mavria', 'raise', ev('us_ai', 'Mavria'), 'Round led by Paradigm valuing it at about USD 1B, per press reporting', lead=True)
sig(N, 'Blue J', 'raise', ev('us_ai', 'Blue J'), 'Raised USD 176M Series E led by JMI Equity, to fund UK and international expansion')
sig(N, 'Mapletree Investments', 'ipo', ev('ipo', 'Mapletree Investments'), 'Tapped banks for a Singapore IPO', lead=True)
sig(N, 'Novig', 'marketing', ev('sponsorships', 'Novig'), 'New sponsorship: authorised prediction-market partner of the NBA, and partnerships with seven NHL clubs')
sig(N, 'Kaufland', 'marketing', ev('sponsorships', 'Kaufland'), 'New sponsorship: multi-year NHL partnership (Official Grocery Retail Partner in Germany, the Czech Republic and Slovakia)')
sig(N, 'JYSK', 'marketing', ev('sponsorships', 'JYSK'), 'New sponsorship: official home furnishing retail partner of Everton Women')
sig(N, 'engelbert strauss', 'marketing', ev('europe', 'engelbert strauss'), "New sponsorship: UEFA Refereeing's first official sponsorship partner")
note(N, 'Converse', ev('f1', 'Nike'), "Its parent Nike becomes Formula 1's official apparel and uniform supplier from 2027: check the category conflict before outreach")

# ---- brands on the 48-tab sheet: rounds closed
for name, f, co, why in [
    ('MegaRobo', 'apac', 'MegaRobo', "Raised nearly USD 200M, with Oman's sovereign wealth fund among the investors"),
    ('Approaching.AI', 'apac', 'Approaching AI', 'Raised more than RMB 1.3B (about USD 195M) in a Series B'),
    ('GIVA', 'apac', 'GIVA', 'Raised USD 103M led by Multiples'),
    ('Pragmatik Labs', 'apac', 'Pragmatik Labs', 'Raised funding at a USD 5B valuation (amount: tens of millions of dollars)'),
    ('Payhawk', 'europe', 'Payhawk', 'Raised USD 280M Series C led by Goldman Sachs at a USD 2B valuation'),
    ('Agile Robots', 'europe', 'Agile Robots', 'Raised USD 500M Series F led by SoftBank at a USD 8.5B valuation'),
    ('Sennder', 'europe', 'Sennder', 'Raised EUR 228M: EUR 73M equity plus EUR 155M debt'),
    ('Fractile', 'europe', 'Fractile', 'Raised a Series C of more than GBP 500M at a valuation above GBP 5B'),
    ('Clara', 'mena_latam', 'Clara', 'Raised USD 105M: a USD 65M Series C plus a USD 40M facility'),
    ('fal', 'us_ai', 'fal', 'Raised USD 1.3B Series F at about a USD 16B valuation'),
    ('Mirendil', 'us_ai', 'Mirendil', 'Raised USD 1B Series A'),
    ('Mercor', 'us_ai', 'Mercor', 'Raised USD 750M Series D at a USD 20B valuation'),
    ('LangChain', 'us_ai', 'LangChain', 'Raised USD 300M Series C at a USD 3B valuation'),
    ('Nominal', 'us_ai', 'Nominal', 'Raised USD 240M Series C at a USD 3B valuation'),
    ('Applied Compute', 'us_ai', 'Applied Compute', 'Raised USD 350M at a USD 3.25B valuation'),
    ('Ocient', 'us_ai', 'Ocient', 'Raised USD 100M Series C'),
    ('Re:Build Manufacturing', 'us_other', 'Re:Build Manufacturing', 'Raised USD 2.1B in equity led by General Catalyst and JPMorganChase (week of 2 Nov 2026)'),
    ('Shield AI', 'us_other', 'Shield AI', 'Raised USD 1B Series H within USD 2.5B of financing at a USD 28.8B valuation, and agreed to buy radar maker Echodyne for up to USD 5.3B (week of 2 Nov 2026)'),
    ('CesiumAstro', 'us_other', 'CesiumAstro', 'Raised USD 730M Series D at a valuation above USD 4.5B'),
    ('Northwood Space', 'us_other', 'Northwood Space', 'Raised USD 375M Series C'),
    ('Harbinger', 'us_other', 'Harbinger', 'Raised USD 240M Series D'),
    ('Galvanize Therapeutics', 'us_other', 'Galvanize Therapeutics', 'Raised USD 130M Series D'),
    ('Emulate', 'us_other', 'Emulate', 'Raised USD 700M at a reported valuation of about USD 3.7B (week of 9 Nov 2026)'),
    ('VulcanForms', 'us_other', 'VulcanForms', 'Raised USD 500M in equity led by J.P. Morgan and Apollo funds (week of 9 Nov 2026)'),
    ('Torus', 'us_other', 'Torus', 'Raised USD 500M led by Magnetar'),
    ('Path Robotics', 'us_other', 'Path Robotics', 'Raised USD 300M Series E at a USD 2.45B valuation'),
    ('Modern Wealth Management', 'us_other', 'Modern Wealth Management', 'Raised USD 200M in hybrid debt and equity led by Centerbridge (week of 9 Nov 2026)'),
    ('Imprint', 'us_other', 'Imprint', 'Raised USD 130M at a valuation of about USD 1.9B (week of 9 Nov 2026)'),
    ('Collective', 'us_other', 'Collective', 'Raised USD 100M: a USD 40M Series B plus a USD 60M facility'),
    ('Zipline International', 'us_other', 'Zipline', 'Raised USD 1.5B at a USD 21.5B valuation and signed a multi-year Walmart drone-delivery deal'),
]: sig(S, name, 'raise', ev(f, co, 'raised'), why)
sig(S, 'Wonder', 'raise', ev('us_other', 'Wonder'), 'Raised USD 650M Series D at a USD 9B pre-money valuation (dated Jul 2026 on one page and Nov 2026 on another)', date='Jul-Nov 2026')
# rounds reported, not closed
sig(S, 'OpenAI', 'raise', ev('us_ai', 'OpenAI'), 'About USD 11B committed at about a USD 1.25T valuation; the round is still open', lead=True)
sig(S, 'Sierra', 'raise', ev('us_ai', 'Sierra'), 'Raising a new round at about a USD 30B valuation, not yet closed', lead=True)
sig(S, 'Cyera', 'raise', ev('us_ai', 'Cyera'), 'Raising about USD 800M at a USD 20B valuation, not yet closed', lead=True)
sig(S, 'Platform Accounting Group', 'raise', ev('us_other', 'Platform Accounting Group'), 'USD 355M of "strategic growth financing" led by Treville Capital; the page does not say whether it is equity (week of 2 Nov 2026)', lead=True)
# debt and other financing: a note, not a round
note(S, 'Tamara', ev('mena_latam', 'Tamara'), 'Added USD 400M of asset-backed debt facilities (MUFG, Standard Chartered): debt, not an equity round')
note(S, 'Jeeves', ev('us_other', 'Jeeves'), 'Announced USD 300M of financing capacity from Neuberger Berman; the page does not say whether it is debt or equity')
note(S, 'Return', ev('europe', 'Return'), 'Secured EUR 835M of financing for battery storage in Germany; the page does not say what kind of financing')
# IPO preparation
sig(S, 'Wonder', 'ipo', ev('ipo', 'Wonder'), 'Confidentially submitted a draft Form S-1 to the SEC for a US IPO')
sig(S, 'Razorpay', 'ipo', ev('apac', 'Razorpay'), 'SEBI approved its IPO (about USD 530-630M at a valuation of about USD 5B), targeting a February 2027 listing')
sig(S, 'Veritas Finance', 'ipo', ev('ipo', 'Veritas Finance'), 'Indian regulators approved its listing plans')
sig(S, 'Nscale', 'ipo', ev('europe', 'Nscale'), 'Has an amended IPO filing for a New York listing targeting a USD 35B valuation; it is deciding between listing this year and in 2027')
sig(S, 'Zhuanzhuan', 'ipo', ev('ipo', 'Zhuanzhuan'), 'Filed confidentially for a Hong Kong IPO', lead=True)
sig(S, 'Sakana AI', 'ipo', ev('ipo', 'Sakana AI'), 'Hired banks for an IPO', lead=True)
sig(S, 'Logisteed', 'ipo', ev('ipo', 'Logisteed'), 'Invited more banks for a Tokyo IPO', lead=True)
sig(S, 'Rohlik Group', 'ipo', ev('ipo', 'Rohlik Group'), 'Picking advisers for an IPO', lead=True)
sig(S, 'Envision Group', 'ipo', ev('ipo', 'Envision Group'), 'Tapped banks for a Hong Kong listing', lead=True)
# now listed: out of scope
drop(S, 'Windward Bio', ev('ipo', 'Windward Bio'), 'Now listed: began trading on Nasdaq (WWB) on 13 Nov 2026 after a USD 175M IPO')
drop(S, 'Banque du Caire', ev('ipo', 'Banque du Caire'), 'Now listed: debuted on the Egyptian exchange in the week to 6 Nov 2026 after a USD 660M IPO')
# bought, completed
parent(S, 'OpenRouter', ev('ma', 'OpenRouter'), 'Bought by Stripe: the deal closed on 10 Nov 2026 (about USD 7.5B as reported by the New York Times). Stripe is a current F1 partner (Mercedes), so check the category conflict', 'Stripe (unlisted; a current F1 partner of Mercedes)', 'no')
parent(S, 'EIS Group', ev('ma', 'EIS'), 'Bought by Amdocs for about USD 340M: completed 4 Nov 2026', 'Amdocs', 'yes')
note(S, 'Firebolt', ev('ma', 'Firebolt'), "MongoDB (listed) is buying Firebolt for an undisclosed price (17 Nov 2026); one page reports the deal as done and another as announced. Its engine is being folded into MongoDB's platform, so the brand may not continue")
parent(S, 'Aviation Capital Group', ev('ma', 'Aviation Capital Group'), 'ITOCHU closed its USD 1.95B purchase of a 50% interest on 12 Nov 2026; Tokyo Century keeps the other 50%', 'Tokyo Century and ITOCHU (50% each, both listed)', 'yes')
note(S, 'HUMAIN', ev('ma', 'HUMAIN'), 'Aramco, a current F1 partner, closed its purchase of 49% (about USD 2.6B in cash plus AI assets); PIF keeps 51%. HUMAIN also bought Riyadh services firm CNTXT on 4 Nov 2026')
note(S, 'Bilt Rewards', ev('ma', 'LAVA'), 'Bought sports loyalty technology company LAVA for USD 300M (completed)')
# bought, agreed or reported: not completed
note(S, 'Cresta', ev('ma', 'Cresta'), 'Salesforce, a current F1 partner, signed an agreement to buy it (about USD 2.7B as reported); close expected in early 2027. Not completed')
note(S, 'Echodyne', ev('ma', 'Echodyne'), 'Shield AI agreed to buy it for up to USD 5.3B. Not completed')
note(S, 'Applied Compute', ev('ma', 'Applied Compute'), 'Palo Alto Networks agreed to buy it in an all-stock deal valued at USD 4.5B. Not completed')
note(S, 'Decart', ev('europe', 'Decart'), "Amazon signed a USD 7.5B deal for Decart's Optimization Stack technology, its founders and its AI team, subject to regulatory clearance: confirm what remains of the company before outreach")
note(S, 'Ollin Biosciences', ev('ma', 'Ollin Biosciences'), 'Johnson & Johnson is reported to be buying it for up to USD 3.3B; neither company has confirmed')
note(S, 'Taalas', ev('ma', 'Taalas'), 'AMD announced it is buying the company for about USD 2.9B; the page does not say whether the deal has closed or whether the brand continues')
note(S, 'Classiq Technologies', ev('europe', 'Classiq'), 'Intel, a current F1 partner (McLaren), agreed to buy it for about USD 1.9B plus up to USD 350M in performance payments (announced 26 Oct 2026); closing expected in H1 2027. Not completed')
note(S, 'Ada', ev('ma', 'Ada'), 'Agreed to merge with Dialpad in an all-share deal valuing Ada at about USD 430M. Not completed; the combined name is not stated')
note(S, 'Dialpad', ev('ma', 'Ada'), 'Agreed to merge with customer-service AI company Ada in an all-share deal. Not completed')
note(S, 'Oura Health', ev('europe', 'Oura'), 'Agreed to buy AI health platform Counsel Health for USD 625M; closing expected before the end of 2027')
note(S, 'Gropyus', ev('ma', 'Gropyus'), 'Several subsidiaries filed for insolvency on 3 Nov 2026 after a liquidity shortage; the parent Gropyus AG is not affected. Check its standing before outreach')
# listed on the sheet on 18 Nov, since taken private or bought for USD 1B or more: now in scope (full lines in newsec/subs/was_listed_refresh23.jsonl)
note(S, 'Integer Holdings', ev('buyouts', 'Integer Holdings'), 'Now in scope: taken private by KKR for USD 5.7B, completed 19 Nov 2026. It was listed, and so out of scope, on the 18 Nov list')
note(S, 'LXP Industrial Trust', ev('buyouts', 'LXP Industrial Trust'), 'Now in scope: taken private by Brookfield and CPP Investments for USD 5.2B, completed 7 Nov 2026. It was listed on the 18 Nov list')
note(S, 'Utz Brands', ev('buyouts', 'Utz Brands'), 'Now in scope: bought by the unlisted snack group Intersnack for USD 2.9B, completed Nov 2026. It was listed on the 18 Nov list')
note(S, 'Irish Continental Group', ev('buyouts', 'Irish Continental Group'), 'Now in scope: management buyout at EUR 1.2B completed; the Dublin and London listings were due to be cancelled on 23 Nov 2026. It was listed on the 18 Nov list')
note(S, 'Arcosa', ev('buyouts', 'Arcosa'), 'Now in scope as a subsidiary: bought by CRH (listed) for USD 8.5B, completed 26 Oct 2026. It was listed on the 18 Nov list')
note(S, 'Roku', ev('buyouts', 'Roku'), 'Fox completed its USD 22B acquisition of Roku on 9 Nov 2026')
parent(S, 'DigitalBridge', ev('buyouts', 'DigitalBridge'), 'Bought by SoftBank for USD 4B: completed 6 Oct 2026', 'SoftBank', 'yes')
note(N, 'Restaurant Brands Europe', ev('buyouts', 'Restaurant Brands Europe'), "A consortium led by Gregorio Jiménez agreed to buy Cinven's 51% stake in a EUR 2.33B deal. Not completed")
# expansion, sponsorship, people
sig(S, 'TEKEVER', 'regions', ev('europe', 'TEKEVER'), "Opened its first Nordic operation in Odense, Denmark; Denmark's EIFO joined its USD 580M Series D")
note(S, 'ICEYE', ev('europe', 'ICEYE'), 'Launched an all-cash tender offer for Milan-listed rocket maker Avio (about EUR 2.05B) and pledged EUR 1B of further investment in Italy')
note(S, 'Swile', ev('mena_latam', 'Swile'), 'Plans to invest BRL 600M in Brazil over five years and to enter travel and expense management there in H1 2027 (Brazil is an existing market)')
sig(S, 'Harvey', 'marketing', ev('sponsorships', 'Harvey'), 'New sponsorship: official legal assistant partner of Wimbledon, multi-year from the 2027 Championships')
note(S, 'Heidi Health', ev('apac', 'Heidi Health'), 'Cutting about 18% of its workforce; two co-founders are leaving')
note(S, 'Unacademy', ev('apac', 'Unacademy'), 'New chief executive: Akhilendra Kumar; founder Gaurav Munjal becomes executive chairman')
note(S, 'Sarvam AI', ev('apac', 'Sarvam AI'), 'Appointed a President and Chief Business Officer (Sashikumar Sreedharan, formerly Google Cloud India)')
note(S, 'Ultraviolette Automotive', ev('apac', 'Ultraviolette'), 'Appointed a new head of marketing (Abhijit Singh Brar, formerly Royal Enfield)')
note(S, 'Porter', ev('apac', 'Porter'), 'New chief marketing officer (Mohit Rathi) and chief financial officer (Gaurav Jain)')
note(S, 'CarDekho', ev('apac', 'CarDekho'), "New chief executive for the group's auto classifieds business (Sudhir Pai)")

# ---- funding talks of the 18 Nov watch list: what happened since
TI = {}; TO = {}
for f in sorted(glob.glob(os.path.join(RD, 'talks_in_*.jsonl'))):
    for l in open(f, encoding='utf-8'):
        if l.strip(): d = json.loads(l); TI[d['name']] = d
for f in sorted(glob.glob(os.path.join(RD, 'talks_out_*.jsonl'))):
    for l in open(f, encoding='utf-8'):
        if l.strip(): d = json.loads(l); TO[d['name']] = d
TALK_SHEET = {'Zipline': None, 'Modal Labs': 'Modal Labs', 'Devoted Health': 'Devoted Health', 'Harvey': 'Harvey', 'Helsing': 'Helsing', 'Isomorphic Labs': 'Isomorphic Labs'}      # confirmed rounds of brands on the sheet (Zipline is already above)
def cap(s): s = (s or '').strip(); return s[:1].upper() + s[1:]
talk_rows = []
for nm, o in TO.items():
    i = TI.get(nm, {}); st = (o.get('status') or '').lower()
    lab = {'confirmed': 'Since confirmed', 'unconfirmed': 'Still unconfirmed', 'collapsed': 'Talks ended', 'acquired': 'Since acquired'}.get(st, cap(st))
    what = cap(o.get('status_detail')); nr = cap(o.get('newer_report'))
    if nr and nr not in what: what += ' Newer report: ' + nr
    talk_rows.append([nm, 'Yes' if i.get('on_users_lists') else 'No', cap(i.get('talks')), ' '.join(x for x in (i.get('talks_outlet'), i.get('talks_date')) if x), lab, what, o.get('status_date') or '', o.get('status_url') or o.get('newer_report_url') or i.get('talks_url') or ''])
    sn = TALK_SHEET.get(nm)
    if sn and st == 'confirmed' and o.get('status_url'):
        when = o.get('status_date') or '2026'
        DEC[S].setdefault(sn, []).append({'action': 'signal', 'why': 'Round confirmed: ' + what, 'signals': {'raise': f"{what} ({when}; {o['status_url']})"}, 'lead': False, 'date': when, 'source': o['status_url']})
talk_rows.sort(key=lambda r: ({'Since confirmed': 0, 'Since acquired': 1, 'Talks ended': 2}.get(r[4], 3), r[0].lower()))

# ---- for information: events that touch no row of either list
def info(name, what, e, where): USED.add((e['file'], e['line'])); return [name, 'For information', what, e.get('date') or '', e.get('source_url') or '', where]
INFO = [
    info('Nike', "New F1 partner: Formula 1's official apparel and uniform supplier from 2027 and partner of F1 Academy, replacing Puma. Listed, so not on this list; its subsidiary Converse is", ev('f1', 'Nike'), 'Listed company'),
    info('Puma', "Its role as Formula 1's apparel and uniform supplier ends: Nike takes over from 2027", ev('f1', 'Puma'), 'Listed company'),
    info('NTT', 'New F1 partner: Official Partner of McLaren from 2027. Listed, so not on this list; its subsidiaries are flagged in the Parent Company column', ev('f1', 'NTT'), 'Listed company'),
    info('Archer Aviation', "New F1 partner: Formula 1's first 'official supporter'. Listed, so not on this list", ev('f1', 'Archer'), 'Listed company'),
    info('Ondas', 'New F1 partner: Global Partner of Aston Martin. Listed, so not on this list', ev('f1', 'Ondas'), 'Listed company'),
    info('Elastic', 'New F1 partner: Audi, team partner from 2027. Listed, so not on this list', ev('f1', 'Elastic'), 'Listed company'),
    info('Klaviyo', 'New F1 partner: Williams, from 2027. Listed, so not on this list', ev('f1', 'Klaviyo'), 'Listed company'),
    info('Insight Enterprises', 'New F1 partner: Las Vegas Grand Prix. Listed, so not on this list', ev('f1', 'Insight Enterprises'), 'Listed company'),
    info('Ooredoo', 'New F1 partner: Founding Partner of the 2026 Qatar Grand Prix. Listed, so not on this list', ev('f1', 'Ooredoo'), 'Listed company'),
    info('Padeltek (Paddletek Group)', 'New F1 partner: Aston Martin. Unlisted, and kept off the list because it now holds an F1 deal', ev('f1', 'Padeltek'), 'Not on any list'),
    info('Dynamo Capital', 'New F1 partner: Haas. Unlisted, and kept off the list because it now holds an F1 deal', ev('f1', 'Dynamo Capital'), 'Not on any list'),
    info('Doha Oasis', 'New F1 partner: Official Partner of the 2026 Qatar Grand Prix. Unlisted, and kept off the list because it now holds an F1 deal', ev('f1', 'Doha Oasis'), 'Not on any list'),
    info('Anthropic', 'Listed on Nasdaq (ANT) on 19 Nov 2026 after raising USD 81.3B. Already off the list as a current F1 partner (Williams)', ev('ipo', 'Anthropic'), 'Current F1 partner'),
    info('Waygate Technologies', 'Bought by Hexagon, a current F1 partner (USD 1.45B, completed 2 Nov 2026). Not on any list', ev('ma', 'Waygate Technologies'), 'Not on any list'),
    info('Perfect Corp.', 'Taken private by its founder (merger effective 23 Oct 2026; shares no longer trade). No purchase price of USD 1B or more was found, so it is not added to the prospects; your sheet-wide workbook still shows it as listed', ev('buyouts', 'Perfect Corp.'), 'Your sheet (shown as listed)'),
    info('Weave', 'Taken private by Francisco Partners for about USD 650M (completed 27 Oct 2026). Below the USD 1B test, so it is not added to the prospects; your sheet-wide workbook still shows it as listed', ev('buyouts', 'Weave'), 'Your sheet (shown as listed)'),
    info('Tribe Capital', 'Being bought by Payward, the parent of Kraken, a current F1 partner. Not on any list', ev('ma', 'Tribe Capital'), 'Not on any list'),
]
if __name__ == '__main__':
    json.dump(DEC, open(os.path.join(RD, 'decisions.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(talk_rows, open(os.path.join(RD, 'talks_status.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(INFO, open(os.path.join(RD, 'info_rows.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    from collections import Counter
    print('new-list decisions', len(DEC[N]), '| sheet decisions', len(DEC[S]), Counter(d['action'] for v in DEC[S].values() for d in v), '| talks rows', len(talk_rows), Counter(r[4] for r in talk_rows), '| info rows', len(INFO))
    left = [d for d in R if (d['file'], d['line']) not in USED and d['target'][0] in ('new', 'sheet')]
    print('events on a listed company with no decision:', len(left))
    for d in left: print('   ', d['file'], '|', d['company'], '->', d['target'][0], d['target'][1], '|', d['event'], '|', (d.get('detail') or '')[:90])
