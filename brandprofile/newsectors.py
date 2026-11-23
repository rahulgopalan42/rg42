"""New brands (not on the 48-tab sheet), filed under the tab for their category (16 Nov 2026).
New tabs for the sectors the sheet has no tab for (quantum, nuclear, defence technology, space, robotics, AI infrastructure, crypto,
betting and prediction markets, brokers ...); the sheet's own tab names for everything else.
Sources: public revenue rankings of unlisted companies (newsec/ranking_rows.json, profiled in newsec/out), one web research file per
group (newsec/web/*.jsonl, each company with a capacity proof and its source) and the public unicorn list. Same parameter set as allsector.py.
Usage: newsectors.py [check|xlsx]"""
import glob, html, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b, allsector as a, allsector_notes as AN
SUBS = a.SUBS      # rule change of 18 Nov 2026: subsidiaries are in scope and every row names its parent company
REFRESH = '23 Nov 2026'      # refresh of the 18 Nov list: events since 1 Nov 2026 applied (newsec/refresh/decisions.json), new brands added (web2/refresh23_*.jsonl). '' = the 18 Nov build
OUT = os.path.join(b.R, 'reports', 'F1-NEW-BRANDS-BY-CATEGORY-v4-2026-11-23.xlsx' if REFRESH else 'F1-NEW-BRANDS-BY-CATEGORY-v3-2026-11-18.xlsx' if SUBS else 'F1-NEW-BRANDS-BY-CATEGORY-v2-2026-11-16.xlsx')
RDIR = os.path.join(H, 'newsec', 'refresh')
def _rj(n, default):
    q = os.path.join(RDIR, n)
    return json.load(open(q, encoding='utf-8')) if REFRESH and os.path.exists(q) else default
DEC = _rj('decisions.json', {}).get('new', {})       # company name on the 18 Nov list -> list of {action: drop|parent|signal|note, ...}, written by hand from the events files
CHANGES = []                                          # rows of the 'Changes Since 18 Nov' tab
RORD = a.RORD
# how each research group is described in the "How Found" column
GROUPS = {'rank': 'Public revenue rankings of unlisted companies', 'brokers': 'Web research: brokers and trading platforms', 'crypto': 'Web research: crypto and prediction markets',
          'betting': 'Web research: betting and iGaming', 'pe_owned': 'Web research: private-equity-owned companies', 'professional': 'Web research: professional partnerships',
          'state_backed': 'Web research: state-backed brands', 'luxury_travel': 'Web research: luxury, private aviation and travel', 'sport_sponsors': 'Web research: unlisted sponsors of top-tier sport',
          'quantum_chips': 'Web research: quantum and AI chips', 'nuclear_energy': 'Web research: nuclear, fusion and energy transition', 'defence': 'Web research: defence technology',
          'space': 'Web research: space and satellites', 'robotics_mobility': 'Web research: robotics, autonomy and new mobility', 'ai_infra': 'Web research: AI infrastructure and data centres',
          'ai_models': 'Web research: AI models and applications', 'cyber_fintech': 'Web research: cybersecurity and fintech', 'consumer_creator': 'Web research: consumer health, creator and consumer brands',
          'unicorn_1': 'Public unicorn list, each company checked', 'unicorn_2': 'Public unicorn list, each company checked'}
# new tabs, in workbook order: (tab name, what it covers, pattern on the theme text)
NEW = [('NEW Quantum Computing', 'Quantum hardware, software and networking', r'quantum'),
       ('NEW AI Chips & Semiconductors', 'AI chips, photonics, chip start-ups and unlisted chip-equipment makers', r'chip|semiconductor'),
       ('NEW AI Infra & Data Centres', 'Data centres, GPU cloud and AI compute', r'infrastructure|data cent|gpu'),
       ('NEW AI Models & Applications', 'AI model developers, agents and applications', r'ai model|agents|application'),
       ('NEW Cybersecurity', 'Cybersecurity companies', r'cyber'),
       ('NEW Robotics & Autonomy', 'Robots, humanoids and self-driving', r'robot|humanoid|autonomous'),
       ('NEW EVs & New Mobility', 'Electric vehicles, charging and electric aircraft', r'\bevs?\b|charging|new mobility'),
       ('NEW Defence Technology', 'Defence technology and unlisted defence groups', r'defen[cs]e'),
       ('NEW Space & Satellites', 'Launch, satellites and space infrastructure', r'space|satellite'),
       ('NEW Nuclear & Fusion', 'Fusion, advanced reactors and nuclear fuel', r'nuclear|fusion'),
       ('NEW Energy Storage & Climate', 'Batteries, storage, renewables and industrial decarbonisation', r'storage|renewable|grid|climate|decarbon'),
       ('NEW Brokers & Trading', 'Online brokers and trading platforms', r'broker'),
       ('NEW Crypto & Digital Assets', 'Crypto exchanges, stablecoins and digital assets', r'crypto|digital asset|stablecoin'),
       ('NEW Betting & Prediction Mkts', 'Betting, iGaming and prediction markets', r'prediction|betting|igaming'),
       ('NEW Neobanks & Payments', 'Neobanks, payments and trading apps', r'neobank|payment|trading app'),
       ('NEW Consumer Health & Wearables', 'Telehealth, wearables, longevity and sports nutrition', r'health|glp|wearable|longevity')]
# consumer brands, games, media and sport have tabs on the sheet already (Fashion, Food & Beverage, Beauty, Video Games, Media, Sports), so brands in those themes go there
GROUP_TAB = {'brokers': 'NEW Brokers & Trading', 'crypto': 'NEW Crypto & Digital Assets', 'betting': 'NEW Betting & Prediction Mkts'}
TEST = {'a': 'Equity raised of USD 150M or more', 'b': 'Published revenue of USD 300M or more', 'c': 'Valued at or bought for USD 1B or more since Nov 2023',
        'd': 'Already pays for a top-tier sports sponsorship', 'e': 'Owned by a state fund building the brand internationally'}
FLOOR = {'a': 150, 'b': 300, 'c': 1000}
CONF = {'high': 3, 'medium': 2, 'low': 1}
RAISED = re.compile(r'(?i)\b(raised|raise|round|series [a-k]\b|funding|investment|invested|financing)')
RECENT = re.compile(r'(?i)\b((nov|dec)[a-z]*\.? 2025|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov)[a-z]*\.? 2026|in 2026|\(2026\))')
NOT_RAISE = re.compile(r'(?i)purchase of|agreed to buy|to acquire|acquires|acquired|buys |bought ')
BUYOUT = re.compile(r'(?i)taken private|take-private|acquired by|bought by|acquisition of|buyout|sold to|agreed sale|sale by')
REV = re.compile(r'(?i)^[^;:.]{0,45}?\b(revenues?|sales|turnover|total income|net trading income|trading income|net revenue)\b')
# decisions made by hand after reading the lists: name -> reason it is left out
DROP = {'Juniper Networks': 'Absorbed into Hewlett Packard Enterprise (now HPE Juniper Networking): it no longer trades as its own company', 'Dorna Sports (MotoGP)': 'Owned by Liberty Media, which owns Formula 1 itself', 'Dorna Sports': 'Owned by Liberty Media, which owns Formula 1 itself', 'Mode Transportation': 'Ownership could not be established', 'Kaspersky': 'Under United States sanctions; Ferrari paused its partnership in 2022',
        'Qatar Sports Investments': 'Investment fund, not an operating company', 'Semikron Danfoss': 'Majority-owned by Danfoss, which is on the list',
        'Diesel': 'Owned by OTB, which is on the list', 'MACIF': 'Part of Aéma Groupe, which is on the list', 'TGI Fridays': 'Filed for bankruptcy', "TGI Friday's": 'Filed for bankruptcy', 'Doğuş Group': 'The only revenue figure found is from 1999', 'Doğuş Holding': 'The only revenue figure found is from 1999',
        'Eucalyptus': 'Reported bought by Hims & Hers (listed), completed June 2026', 'Eucalyptus Health': 'Reported bought by Hims & Hers (listed), completed June 2026'}
# left out earlier only because another company owns them: back in under the subsidiaries rule, name -> parent
SUB_BACK = {'Semikron Danfoss': 'Danfoss', 'Diesel': 'OTB', 'MACIF': 'Aéma Groupe', 'Eucalyptus': 'Hims & Hers Health (listed)', 'Eucalyptus Health': 'Hims & Hers Health (listed)'}
# "private: ..." ownership lines that name people, families, trusts or lenders, not a parent company
OWNER_PEOPLE = {'New York Yankees (Yankee Global Enterprises)', 'Bose', 'Edrington', 'Savino Del Bene', 'Mitel', 'Kempinski Hotels', 'BMC Otomotiv', 'Smoothie King', 'Las Vegas Raiders', 'Kolkata Knight Riders (Knight Riders Group)',
                'ABANCA', 'Thalia', 'Agrofert', 'Rajasthan Royals', 'Banco Comafi', 'Rural King', 'Indigo Books & Music', 'Atlanta Falcons', 'Cleveland Browns', 'Punjab Kings', 'Kutxabank',
                'Cloudnine Hospitals (Kids Clinic India)', 'Guardian Media Group', 'Black Red White', 'Togg'}
PARENT_HAND = {'Guess': 'Authentic Brands Group (51% of the brand rights, with the Marciano founders)', 'Liverpool FC': 'Fenway Sports Group', 'Wayne-Sanderson Farms': 'Joint venture of Cargill and Continental Grain',
               'ebm-papst': 'Madison Air (purchase agreed Aug 2026)', 'Gulf States Toyota, Inc.': 'The Friedkin Group'}
SUBS_LABEL = {'acq_tech': 'technology companies bought since Nov 2023', 'acq_consumer': 'consumer and media companies bought since Nov 2023', 'acq_other': 'finance, health, industrial and energy companies bought since Nov 2023',
              'funded_subs': 'subsidiaries with their own outside investors', 'brands_americas': 'subsidiaries of listed groups, North and Latin America', 'brands_europe': 'subsidiaries of listed groups, Europe',
              'brands_apac_mea': 'subsidiaries of listed groups, Asia-Pacific, Middle East and Africa', 'sport_subs': 'subsidiaries that sponsor top-tier sport', 'f1_sisters': 'sister brands of groups that have an F1 partner',
              'unlisted_groups': 'subsidiaries of unlisted, family and state groups', 'manual': 'added by hand'}
PARENT_F1_HAND = {'Moeve': 'Carlyle, a current F1 partner, holds a minority stake', 'Group 1001': 'its parent TWG Global owns TWG Motorsports, which is behind the Cadillac F1 team'}
def f1_clean(t):
    """what the lookup tool printed about the parent, in plain words"""
    t = re.sub(r'(?i)^.*?(already known|possibly known)\s*[-:]\s*', '', t).strip(); t = re.sub(r'\s*\(not flagged by on_sheet\.py\)', '', t); t = re.sub(r'\s+as\s+[A-Z][\w&. \'-]*$', '', t)
    t = t.replace(' - parent / owner', '')
    m = re.match(r'(?i)^owner of a current F1 partner\s*\((.*)\)$', t)
    if m: return 'the parent owns an F1 partner or team (' + m.group(1) + ')'
    m = re.match(r'(?i)^current F1 partner or owner of one\s*\((.*)\)$', t)
    if m: return 'the parent is, or owns, an F1 partner (' + m.group(1) + ')'
    m = re.match(r'(?i)^current F1 partner\s*(?:\((.*)\))?$', t)
    if m: return 'the parent is a current F1 partner' + (' (' + m.group(1) + ')' if m.group(1) else '')
    m = re.match(r'^([^()]+?) - (.+)$', t)
    if m: return 'the parent is a current F1 partner (' + m.group(2) + ')' if m.group(1) else t
    return t
def parent_txt(x):
    """the Parent Company column for a new brand"""
    par = clean(x.get('parent')) or PARENT_HAND.get(x['name'], ''); o = x['ownership']; ol = o.lower()
    if x.get('pe_parent'): return 'None: owned by an investment firm (' + x['pe_parent'] + ')'
    if not par and x['name'] not in OWNER_PEOPLE and re.match(r'(?i)private:\s*\S', o):
        par = re.sub(r'(?i)^private:\s*(majority-owned by|subsidiary of|owned by)?\s*', '', o).strip()
    if par:
        pl = PARENT_LISTED_FIX.get(x['name'], clean(x.get('parent_listed'))); stake = clean(x.get('parent_stake'))
        listed = pl.lower().startswith('listed') or (not pl and any(k in getattr(load, 'listed', ()) for k in a.par_keys(par)))
        ex = re.match(r'(?i)listed\s*\(([A-Za-z0-9 /&.]{2,22}:\s*[^();]{1,40}(?:;\s*[A-Za-z0-9 ]{2,12}:\s*[^();]{1,20})?)\)', pl)
        t = par + ((' (listed, ' + ex.group(1).strip() + ')' if ex else ' (listed)') if listed and 'listed' not in par.lower() else '') + (f', {stake}' if stake and stake not in par and len(stake) <= 30 else '')
        f1 = PARENT_F1_HAND.get(x['name']) or next((t for pat, t in PARENT_F1 if pat.search(par)), '') or f1_clean(clean(x.get('parent_f1')))
        if not f1:
            l = b.f1_link(re.sub(r'\s*\(.*$', '', par))[0] or F1_EXTRA.get(re.sub(r'\s*\(.*$', '', par), '')
            f1 = f1_clean(str(l)) if l else ''
        if not f1:
            m = re.search(r'(?i)(whose|which also owns)\s+([^;]*?F1 partner[^;,)]*)', o)
            f1 = ('the parent ' + ('also owns ' + re.sub(r'(?i)^F1 partner\s+', '', m.group(2)) + ', an F1 partner' if m.group(1).lower().startswith('which') else 'has a brand that is an F1 partner (' + re.sub(r'(?i)\s*(brand)?\s*is an F1 partner.*$', '', m.group(2)).strip() + ')')) if m else ''
        return (t.rstrip('.') + '. F1 link in the group: ' + f1.rstrip('.')) if f1 else t
    if ol.startswith('private equity'): return 'None: owned by an investment firm (' + o.split(':', 1)[-1].strip() + ')'
    if ol.startswith(('state fund', 'state-owned', 'municipal')): return 'None: state-owned (' + o.split(':', 1)[-1].strip() + ')'
    if 'owner not stated' in ol: return 'Not stated on the pages read'
    if x['name'] in OWNER_PEOPLE: return 'None (owned by individuals, a family or a trust: see Ownership Type)'
    return 'None (independent company)'
# research lines that share a short name with a different company on the sheet or on a stock exchange: not the same company
NOT_SHEET = {'Science Corporation (neurotech)', 'ICON (3D-printed construction)', 'Bridge (stablecoin platform)', 'MHP (management and IT consultancy)', 'Empower (retirement services)', 'Also (Rivian spinout)'}
# F1 links of a parent group that the roster match does not catch from the parent's name
PARENT_F1 = [(re.compile(r'\bNTT\b'), 'NTT becomes a McLaren partner from 2027 (announced 4 Nov 2026)'), (re.compile(r'(?i)unilever'), 'Unilever brands Clear and Liquid I.V. are F1 partners'),
             (re.compile(r'(?i)toyota'), 'Toyota Gazoo Racing is the Haas title partner'), (re.compile(r'(?i)liberty media'), 'Liberty Media owns Formula 1'),
             (re.compile(r'(?i)\btata (sons|group)\b'), 'Tata Communications is a Formula 1 partner'), (re.compile(r'(?i)\bSHV\b'), 'SHV also owns Mammoet, an F1 partner'),
             (re.compile(r"(?i)l'occitane"), "L'Occitane also owns ELEMIS, an F1 partner"), (re.compile(r'(?i)carlyle'), 'Carlyle is an F1 partner')]
PARENT_F1 += a.F1_PARENT_EXTRA
# F1 deals announced since the roster was compiled (events research of 23 Nov 2026, newsec/refresh/events_f1.jsonl)
PARENT_F1 += [(re.compile(r'(?i)\bnike\b'), "Nike becomes Formula 1's apparel and uniform supplier from 2027 (announced 20 Nov 2026)"),
              (re.compile(r'(?i)^archer aviation'), 'Archer became a Formula 1 official supporter (announced 13 Nov 2026)'), (re.compile(r'(?i)^elastic\b'), 'Elastic is an Audi F1 partner from 2027 (reported 23 Oct 2026)'),
              (re.compile(r'(?i)^klaviyo'), 'Klaviyo is a Williams partner from 2027 (reported 23 Oct 2026)'), (re.compile(r'(?i)^ondas'), 'Ondas is an Aston Martin partner (announced 18 Nov 2026)'),
              (re.compile(r'(?i)^insight enterprises'), 'Insight Enterprises is a Las Vegas Grand Prix sponsor (announced 19 Oct 2026)')]
# a "parent" that is an investment firm: the company is privately held, not a subsidiary of an operating group
PE_PARENT = re.compile(r'(?i)\b(Brookfield and CPP Investments|STG|Symphony Technology|GTCR|Ascendent Capital|Japan Investment Corporation|Bridgepoint|Advent International|Blackstone|Hg|TA Associates|Bain Capital|KKR|CVC|Permira|EQT|Clayton|Cinven|PAI Partners|Ardian|Partners Group|Warburg Pincus|TPG|Silver Lake|Thoma Bravo|Vista Equity|Francisco Partners|Insight Partners|General Atlantic|Stonepeak|Apollo Sports Capital|Clearlake|Veritas Capital|Platinum Equity|Sycamore|Leonard Green|Hellman & Friedman|L Catterton|3G Capital)\b')
PARENT_LISTED_FIX = {'Sol de Janeiro': 'not listed'}
# an importer or distributor of an F1 carmaker's vehicles is not an F1 partner: kept, with the link in Verification Notes
F1_KEEP = {'Pon Holdings B.V.'}
# names that only look like a listed company (a listed namesake or a listed subsidiary); the company itself is unlisted
NOT_LISTED = {'WeTrade', 'IDOM', 'Cactus', 'InPost'}                      # the broker; the listed WeTrade Group is a different company
# extra F1 links the roster match does not catch by name
F1_EXTRA = dict(AN.F1_OWNERS, **{'Cognition AI': 'Cognition (Aston Martin)', 'Arctic Wolf Networks': 'Arctic Wolf', 'Jet365': 'Alpine', 'Intel': 'McLaren', 'Gucci': 'Alpine title partner from 2027', 'Electronic Arts': 'EA SPORTS (official F1 video game)', 'Padeltek': 'Aston Martin (announced 19 Oct 2026)', 'Paddletek': 'owner of Padeltek, an Aston Martin partner', 'Dynamo Capital': 'Haas (reported 23 Oct 2026)', 'Doha Oasis': 'Qatar Grand Prix (announced 18 Nov 2026)'})
# same company as a brand already on the sheet under a longer or shorter name: name -> name on the sheet
SAME = {'Roquette Frères S.A.': 'Roquette', 'Louis Dreyfus Company B.V.': 'Louis Dreyfus Company', 'Farmers Insurance Exchange': 'Farmers Insurance', "Jersey Mike's": "Jersey Mike's Subs",
        'Skechers': 'Skechers U.S.A.', 'Walgreens': 'Walgreens Boots Alliance', 'Fanatics Betting & Gaming': 'Fanatics',
        'Temporal': 'Temporal Technologies', 'Aman': 'Aman Resorts', 'Erebor Bank': 'Erebor', 'Jeppesen': 'Jeppesen ForeFlight', 'Envision Energy': 'Envision Group', 'Eurostar': 'Eurostar International'}
# research lines whose short name collides with a different company on the sheet: (file, name) -> fuller name
RENAME = {('unicorn_1', 'Branch'): 'Branch Metrics', ('unicorn_1', 'Hello (Hellobike)'): 'Hellobike', ('ai_models', 'Vinci'): 'Vinci AI',
          ('subs_acq_tech', 'Bridge'): 'Bridge (stablecoin platform)', ('subs_sport_subs', 'MHP'): 'MHP (management and IT consultancy)', ('subs_sport_subs', 'Empower'): 'Empower (retirement services)'}      # Vinci AI is not the listed construction group VINCI
# research lines not used: the same company is carried from another file with firmer evidence
SKIP_LINE = {('unicorn_1', 'Tether')}       # the unicorn list's USD 350bn is a press valuation; the crypto file's line rests on reported profit
# cautions the researchers reported, shown in Verification Notes
NOTE = {'Youibot': 'Filed for a Hong Kong listing in Mar 2026: check whether it has listed', 'Leju Robotics': 'Shenzhen ChiNext listing application accepted in May 2026: check whether it has listed',
        'TAILG': 'Filed for a Hong Kong listing in Feb 2026: check whether it has listed', 'Alpitronic': 'No page found naming its owners: unlisted status to confirm',
        'Cult.fit': 'IPO approved in Oct 2026: may list soon', 'atNorth': 'USD 4bn deal announced Feb 2026 and may not have closed; Equinix (listed) takes a 40% minority',
        'NorthC': 'The EUR 2bn price comes from unconfirmed press reports', 'Altera': 'Intel (listed) keeps 49%; Silver Lake holds 51%', 'ZEISS Semiconductor Manufacturing Technology': 'ASML (listed) owns 24.9%',
        'Dubizzle Group': 'OLX Group (part of listed Prosus) holds about 39%, a minority', 'Kaizen Gaming (Betano)': 'Allwyn, an F1 team partner, holds a 37% minority stake',
        'BoyleSports': 'Its West Ham shirt deal covered 2025-26; check that a top-tier deal is still running', 'Lottoland': 'The only revenue figure found is from 2016',
        'Trulioo': 'Only about USD 150M of its 2021 round went to the company: at the threshold', 'Egon Zehnder': 'Sources conflict on whether it is listed: confirm (it is generally described as a partnership)',
        'Urenco': 'E.ON and RWE (both listed) own a third between them; the UK and Dutch states own the rest',
        'Kraken Technologies': 'Majority-owned by Octopus Energy (unlisted, already on your sheet). Not the crypto exchange Kraken, which is an F1 partner',
        'Looop': 'Revenue is only just at the USD 300M line; Chubu Electric (listed) has a capital alliance with it',
        'micro1': 'The source gives no date for the USD 1B+ valuation: confirm it is since Nov 2023', 'AfterQuery': 'The source gives no date for the USD 1B+ valuation: confirm it is since Nov 2023',
        'webAI': 'The source gives no date for the USD 1B+ valuation: confirm it is since Nov 2023', 'Zendesk': 'The revenue figure found is from 2018, before it was taken private in 2022',
        '01.AI': 'Valuation dates from Nov 2023, at the cut-off; it has since stopped training its own models', 'Invisible Technologies': 'The USD 2B valuation appears only in a news headline',
        'Mistral AI': 'ASML holds about 11% and Samsung a stake: minority investors',
        'MoneyGram': 'Former title sponsor of the Haas F1 team (through 2025); not on the current roster', 'Infoblox': 'The figure found is annual recurring revenue, not total revenue',
        'Stake (Easygo)': 'Former title sponsor of the Sauber F1 team (through 2025); not on the current roster', 'Bybit': 'Former Red Bull Racing partner (replaced in Feb 2025); not on the current roster',
        'Medvi': 'Its 2025 revenue is press-reported and disputed, and it has received an FDA warning letter', 'Head': 'The revenue figure found is from 2014',
        'Pentland Group': 'The revenue figure is from 2018 and probably includes its stake in listed JD Sports', 'RSG Group': 'The revenue figure found is from 2021',
        'Qiddiya Investment Company': 'Pre-revenue; Qiddiya is building a circuit intended to host the Saudi Arabian Grand Prix, so it may become an F1 race host',
        'Qiddiya': 'Pre-revenue; Qiddiya is building a circuit intended to host the Saudi Arabian Grand Prix, so it may become an F1 race host',
        'Naval Group': 'State-controlled; Thales (listed) owns 35%', 'Patria': 'State-controlled; Kongsberg (listed) owns 49.9%', 'Nammo': 'Half owned by Patria, half by the Norwegian state',
        'Roketsan': 'State-controlled; Aselsan (listed) owns 15%', 'Marshall Group': 'The only turnover figure found is from about 2012', 'Pilatus Aircraft': 'The revenue figure found is from 2018',
        'Kela Technologies': 'Valuation reports differ: USD 1.2bn post-money or USD 1bn pre-money',
        'Hotwire Communications': 'Owned by Brookfield funds', 'Alcatel Submarine Networks': '80% owned by the French state'}
# signals read by hand and judged not to be the thing the parameter asks for: shown as "Lead only"
SIG_DOWN = {('dnata', 'marketing'), ('VGW', 'marketing'), ('Air Serbia', 'marketing'), ('EDGE Group', 'regions'), ('Eurostar', 'regions'), ('atNorth', 'raise')}
# a company found by two groups keeps one line; where that line came from the less fitting group, the tab is set by hand
TAB_FIX = {'Tether': 'NEW Crypto & Digital Assets', 'Hargreaves Lansdown': 'NEW Brokers & Trading', 'Zerodha': 'NEW Brokers & Trading', 'Trading 212': 'NEW Brokers & Trading'}
# headquarters the research did not find on a page, added from general knowledge and flagged as such in Verification Notes
HQ_KNOWN = {'Axi': 'Sydney, Australia', 'Peregrine Technologies': 'San Francisco, United States', 'Simon-Kucher': 'Bonn, Germany', 'Hudson River Trading': 'New York, United States',
            'Prime Hydration': 'Louisville, United States', 'Trading 212': 'London, United Kingdom', 'Speak': 'San Francisco, United States', 'PowerSchool': 'Folsom, United States',
            'Hotwire Communications': 'Fort Lauderdale, United States'}
HQ_NONE = {'DLA Piper', 'Dentons', 'Norton Rose Fulbright'}      # international law firms whose pages state no single headquarters
# the same company under two names
ALIAS = {'Atlético Madrid': 'Atlético de Madrid', 'Swiss International Air Lines': 'SWISS', 'Tata AIG': 'Tata AIG General Insurance', 'Tata AIA Life': 'Tata AIA Life Insurance', 'CJ Olive Young': 'Olive Young', 'Merkur Group': 'Gauselmann Group (Merkur)', 'Massachusetts Mutual Life Insurance Company (MassMutual)': 'MassMutual', 'Koninklijke Jumbo Food Groep (Jumbo)': 'Jumbo', 'Dirk Rossmann GmbH': 'Rossmann', "Raising Cane's Chicken Fingers": "Raising Cane's", 'Young Living Essential Oils': 'Young Living', 'M.A. Mortenson Companies, Inc.': 'Mortenson', 'Robert Bosch GmbH': 'Bosch', 'Dr. August Oetker KG': 'Dr. Oetker', 'SPAR Österreich': 'SPAR Holding AG', 'Coop Danmark': 'Coop amba', 'Eti': 'Eti Gıda',
         'Veronesi Holding S.p.A.': 'Gruppo Veronesi', 'PHW Group (Lohmann & Co. AG)': 'PHW-Gruppe (Wiesenhof)', 'Panera Bread': 'Panera Brands', 'Chiesi Group': 'Chiesi Farmaceutici', 'Foodstuffs North Island': 'Foodstuffs', 'Kedrion Biopharma': 'Kedrion', 'Kempinski Hotels': 'Kempinski',
         'Laboratoires Pierre Fabre': 'Pierre Fabre', 'C.H. Boehringer Sohn AG & Co. KG (Boehringer Ingelheim)': 'Boehringer Ingelheim', 'Eurostars Hotel Company (Grupo Hotusa)': 'Hotusa',
         'Grupo Hotusa (Eurostars Hotel Company)': 'Hotusa', 'DVAG (Deutsche Vermögensberatung)': 'DVAG', 'Deutsche Vermögensberatung (DVAG)': 'DVAG', 'Mills Fleet Farm': 'Fleet Farm', 'GALLO (E&J Gallo Winery)': 'E. & J. Gallo Winery', 'E&J Gallo Winery': 'E. & J. Gallo Winery', 'Jumbo Supermarkten': 'Jumbo', 'Eurostars/Grupo Hotusa': 'Hotusa', 'Grupo Hotusa': 'Hotusa', 'Eurostars Hotel Company': 'Hotusa'}
FORMS = re.compile(r'(?i)\b(groupe?|gruppo|grupo|holding|holdings|technology|technologies|athletics|stiftung|international|company|companies|corporation|enterprises|industries|limited|ltd|inc|llc|gmbh|kgaa|kg|se|ag|co|cie|sa|spa|bv|nv|as|a/s|ab|asa|pty|plc|lp|l\.p\.|the|and|mbh|og|b\.v\.|s\.a\.|s\.p\.a\.)\b')
import unicodedata
def fold(s): return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
def core(n):
    n = fold(ALIAS.get(n, n))                          # accents folded, so "Postobon" and "Postobón" are one company
    n = re.sub(r'(?i)\b(b\.v\.?|n\.v\.?|s\.a\.?|s\.p\.a\.?|l\.p\.?|s\.l\.?|a\.s\.?|a/s)(?=\s|,|$)', ' ', n)      # dotted company forms
    return b.loose(FORMS.sub('', re.sub(r'\(.*?\)', '', n))) or b.loose(n)
# owners of current F1 partners, and family holdings whose main operating business is itself listed (that business is covered in the listed-company work)
F1_PAT = [(re.compile(r'(?i)^rolex'), 'Owner of TUDOR, a Racing Bulls partner'), (re.compile(r'(?i)w[üu]rth'), 'Owner of Liqui Moly, a Formula 1 partner'), (re.compile(r'(?i)^CMA CGM'), 'Owner of CEVA Logistics, a Ferrari partner')]
HOLDS_LISTED = {'INA-Holding Schaeffler': 'Schaeffler AG', 'John Swire & Sons': 'Swire Pacific', 'Murugappa Group': 'its group companies (Cholamandalam, Tube Investments, Coromandel)', 'Zorlu Holding': 'Vestel',
                'Yıldız Holding': 'Ülker (its unlisted biscuit business pladis is on the list)', 'Borusan Holding': 'its Istanbul-listed group companies', 'Hengli Group': 'Hengli Petrochemical',
                'Shandong Weiqiao Pioneering Group': 'China Hongqiao and Weiqiao Textile', 'Hailiang Group': 'Zhejiang Hailiang', 'Wanxiang Group': 'Wanxiang Qianchao', 'Jiangsu Shagang Group': 'Jiangsu Shagang Co.',
                'Zhejiang Geely Holding Group': 'Geely Automobile and Volvo Cars (it also holds minority stakes in Aston Martin and Mercedes-Benz)'}
def group_label(key):
    if key in GROUPS: return GROUPS[key]
    if key.startswith('region_'): return 'Second pass: regional rankings and company pages'
    if key.startswith('confirm_'): return 'Second pass: proof found on a second attempt'
    if key.startswith('pe_'): return 'Second pass: private-equity portfolios'
    if key.startswith('clayproof_'): return 'Second pass: found through Clay, proven from a public page'
    if key == 'manual': return 'Added on request after a check of public pages'
    if key == 'found_subs_pass': return 'Found during the subsidiaries pass (18 Nov), source read'
    if key.startswith('subs_was_listed'): return 'Subsidiaries pass (18 Nov): formerly listed companies bought since Nov 2023'
    if key.startswith('subs_'): return 'Subsidiaries pass (18 Nov): ' + SUBS_LABEL.get(key[5:], key[5:])
    if key.startswith('refresh23_'): return 'Refresh of 23 Nov 2026: round, deal or sponsorship announced since 1 Nov 2026, source read'
    if key == 'talks_added': return 'Found during the funding-talks research; round or deal since announced, source read'
    return key
def is_pass2(key): return key.startswith(('region_', 'confirm_', 'pe_us', 'pe_intl', 'clayproof_'))
_n2 = os.path.join(H, 'newsec', 'notes2.json')
if os.path.exists(_n2): NOTE.update(json.load(open(_n2, encoding='utf-8')))
# lines whose evidence was judged too weak when read: shown on the Capacity To Confirm tab instead
DEMOTE = {'Dalian Wanda Group': 'Revenue figure is from 2018, the group has been selling assets since, and part of its business is listed',
          'Creed': 'The USD 4.6bn price found was for all of Kering Beauté, not for Creed alone; no figure for Creed itself was read',
          'SimCorp': 'The purchase by Deutsche Börse closed in autumn 2023; whether it falls on or after 1 Nov 2023 was not shown, and no revenue figure was read',
          'Airtel Money': 'One researcher found that it listed on a stock exchange in October 2026; its listing status needs checking',
          'Shanghai Mahexin Technology': 'The valuation comes from a news-flash page and depends on an option being exercised; the English name of the company is uncertain',
          'British Gas': 'Passes only on a national Olympic team partnership (Team GB), which is not a top-tier property; its own revenue was not read',
          'Optus': 'Passes only on a national Olympic team partnership (Australian Olympic Team), which is not a top-tier property; its own revenue was not read'}
clean = b.clean
def tab_for(theme, key, sector, what='', grp=''):
    g = grp.lower()
    if key in ('crypto', 'betting') and re.search(r'prediction market', what, re.I): return 'NEW Betting & Prediction Mkts'
    if key.startswith('confirm'):
        if 'betting' in g: return 'NEW Betting & Prediction Mkts'
        if 'broker' in g: return 'NEW Brokers & Trading'
        if 'cybersecurity and fintech' in g and not theme: return 'NEW Cybersecurity' if re.search(r'(?i)cyber|security', what) else 'NEW Neobanks & Payments'
        if not theme and re.search(r'infrastructure|robotics|ai models|space|defence|nuclear|quantum', g): theme = grp
    if key in GROUP_TAB and not re.search(r'prediction', theme, re.I): return GROUP_TAB[key]
    t = theme.lower()
    for name, _, pat in NEW:
        if t and re.search(pat, t): return name
    return sector
CTRY = {'Türkiye': 'Turkey', 'Turkiye': 'Turkey', 'UK': 'United Kingdom', 'USA': 'United States', 'US': 'United States', 'U.S.': 'United States', 'UAE': 'United Arab Emirates', 'Czechia': 'Czech Republic',
        'Republic of Korea': 'South Korea', 'Korea': 'South Korea', "People's Republic of China": 'China', 'The Netherlands': 'Netherlands'}
def hq_fix(hq):
    parts = [p.strip() for p in clean(hq).strip(',').split(',') if p.strip()]
    if parts: parts[-1] = CTRY.get(parts[-1], parts[-1])
    return (parts[0] + ', ' + parts[-1] if len(parts) >= 2 and parts[0] != parts[-1] else parts[-1] if parts else 'Not recorded')
def load():
    A, rows, L = a.load()
    PA = b.pb.assemble(); listed = {b.loose(html.unescape(c['name'])) for c in PA['U'].values()} | {b.loose(x['name']) for x in rows if x['status'] == 'listed'}
    load.listed = listed
    load.sheetrow = sheetrow = {}
    onsheet = {}
    for x in rows:
        for k in (b.loose(x['name']), b.loose(x['r']['brand'])):
            onsheet.setdefault(k, x['name']); sheetrow.setdefault(k, x)
    for d in A['f1x']: onsheet.setdefault(b.loose(d['name']), d['name'])
    out = []; left = []; drop = Counter(); seen = {}; now_private = []; now_owned = {}
    for k0 in list(onsheet):
        kf = b.loose(fold(onsheet[k0]))
        if kf and kf not in onsheet: onsheet[kf] = onsheet[k0]; sheetrow.setdefault(kf, sheetrow.get(k0))
    def leave(rec, why, show=True):
        drop[why.split(':')[0]] += 1
        if show: left.append((rec['name'], group_label(rec.get('key', '')), why))
    def add(rec):
        k = b.loose(rec['name']); ck = core(rec['name'])
        if k not in onsheet and b.loose(fold(rec['name'])) in onsheet: k = b.loose(fold(rec['name']))
        if not k: return
        if ck in seen:                                   # found by two groups: keep the web-checked, better-evidenced line, carry over what the other one adds
            old = seen[ck]; drop['Found twice (kept once)'] += 1
            rank = lambda r: (1 if r.get('web') else 0, CONF.get(r.get('conf'), 0), r.get('usd_m') or 0)
            keep, other = (rec, old) if rank(rec) > rank(old) else (old, rec)
            if keep['basis'] in ('d', 'e') and other['basis'] == 'b' and other.get('usd_m'):      # a published revenue figure is the firmer capacity proof
                if keep['basis'] == 'd' and not keep.get('sponsorships'): keep['sponsorships'] = keep['detail']
                for f in ('basis', 'detail', 'usd_m', 'year', 'source'): keep[f] = other[f]
                keep['rank_fig'] = not other.get('web')
            if not keep.get('sponsorships'): keep['sponsorships'] = other.get('sponsorships', '')
            if len([p for p in clean(keep.get('hq')).split(',') if p.strip()]) < len([p for p in clean(other.get('hq')).split(',') if p.strip()]): keep['hq'] = other['hq']
            for sk, sv in (other.get('signals') or {}).items():
                if sv and not (keep.get('signals') or {}).get(sk): keep.setdefault('signals', {})[sk] = sv
            if keep is rec: out[out.index(old)] = rec; seen[ck] = rec
            return
        if SUBS and rec['name'] in SUB_BACK: rec['parent'] = rec.get('parent') or SUB_BACK[rec['name']]; rec['status'] = 'subsidiary'
        elif rec['name'] in DROP: return leave(rec, DROP[rec['name']])
        l, _ = b.f1_link(rec['name'])
        if rec['name'] in F1_KEEP: rec['f1note'] = rec.get('f1note') or rec.get('f1'); rec['f1'] = ''
        for pat, why in F1_PAT:
            if pat.search(rec['name']): return leave(rec, 'Current F1 partner or owner of one: ' + why)
        for nm, sub in HOLDS_LISTED.items():
            if rec['name'].startswith(nm): return leave(rec, 'Holding company whose main operating business is listed: ' + sub)
        if SUBS and rec.get('f1') and not l and rec['name'] not in F1_EXTRA and rec.get('status') == 'subsidiary' and clean(rec.get('parent')): rec['parent_f1'] = rec['f1']; rec['f1'] = ''
        if l or rec['name'] in F1_EXTRA or rec.get('f1'): return leave(rec, 'Current F1 partner or owner of one: ' + str(l or F1_EXTRA.get(rec['name']) or rec.get('f1')))
        if (k in onsheet and rec['name'] not in NOT_SHEET) or rec['name'] in SAME:
            sr = sheetrow.get(b.loose(SAME[rec['name']])) if rec['name'] in SAME else sheetrow.get(k)
            if sr is not None and rec.get('web') and (sr.get('was') or sr['status']) in ('listed', 'unknown', 'subsidiary') and not b.f1_link(sr['name'])[0]:
                now_private.append([sr['name'], sr['r'].get('tab', sr['sector']), {'listed': 'Listed', 'unknown': 'Ownership not confirmed', 'subsidiary': 'Owned by another company'}[sr.get('was') or sr['status']],
                                    rec['ownership'], TEST[rec['basis']], rec['detail'], rec['source'], rec['hq'], rec['reach']])
                if rec['key'].startswith('subs_') and (sr.get('was') or sr['status']) == 'listed':       # listed on the sheet, since bought: recorded so the sheet-wide workbook can treat it as a subsidiary
                    now_owned[sr['r']['id']] = {'name': sr['name'], 'parent': clean(rec.get('parent')), 'pe': clean(rec.get('pe_parent')), 'detail': rec['detail'], 'source': rec['source']}
            return leave(rec, 'Already on your sheet: ' + (SAME.get(rec['name']) or onsheet[k]), show=False)
        if rec.get('status') == 'listed': return leave(rec, 'Listed on a stock exchange')
        if k in listed and rec['name'] not in NOT_LISTED and rec['name'] not in NOT_SHEET and rec['key'] != 'pe_owned' and not rec['key'].startswith('subs_was_listed') and not (rec['key'] == 'rank' and rec.get('status') == 'private'): return leave(rec, 'Name matches a listed company: ' + rec['name'])
        if rec.get('status') in ('defunct', 'non-commercial'): return leave(rec, 'Closed or not a commercial company')
        if rec.get('status') == 'subsidiary':
            par = clean(rec.get('parent'))
            if not par: return leave(rec, 'Owned by another company, owner not named')
            if not SUBS and (b.loose(par) in listed or b.f1_link(par)[0]): return leave(rec, 'Owned by a listed group or an F1 partner: ' + par)
            if not rec.get('web'): rec['ownership'] = f'Subsidiary of {par}' if SUBS else f'Owned by {par} (unlisted)'
        seen[ck] = rec; out.append(rec)
    # 1. ranking companies, profiled from the ranking line
    R = {d['id']: d for d in json.load(open(os.path.join(H, 'newsec', 'ranking_rows.json'), encoding='utf-8'))}
    P = {}
    for f in sorted(glob.glob(os.path.join(H, 'newsec', 'out', 'out_*.jsonl'))):
        for l in open(f, encoding='utf-8'):
            try: d = json.loads(l); P[d['id']] = d
            except Exception: pass
    for rid, r in R.items():
        p = P.get(rid)
        if not p: continue
        rev = r.get('revenue_usd_bn'); f1 = clean(p.get('f1')); f1 = '' if f1.lower() in ('', 'none', 'no', 'n/a', '-') else f1
        dec = b.f1_decide(f1) if f1 else ('', '')
        add({'key': 'rank', 'name': clean(p.get('name')) or r['name'], 'hq': clean(p.get('hq')) or r.get('hq', ''), 'sector': p.get('sector') if p.get('sector') in b.FIT else 'Diversified & Other',
             'industry': clean(p.get('industry')), 'desc': clean(p.get('desc')), 'theme': '',
             'ownership': {'family': 'Family-owned', 'co-operative': 'Co-operative', 'partnership': 'Partnership'}.get(r.get('ownership'), 'Private, owner not stated in the ranking'),
             'basis': 'b', 'detail': f"Revenue about USD {rev} billion ({r.get('revenue_year')}), as published in: {r.get('ranking')}", 'usd_m': rev * 1000 if isinstance(rev, (int, float)) else None,
             'year': str(r.get('revenue_year', '')), 'source': r.get('source', ''), 'sponsorships': '', 'reach': clean(p.get('reach')).title() if clean(p.get('reach')).title() in RORD else 'Domestic',
             'reach_basis': clean(p.get('basis')).lower(), 'markets': clean(p.get('markets')), 'signals': {}, 'rationale': clean(p.get('rationale')), 'rel': p.get('rel') if p.get('rel') in (1, 2, 3, 4, 5) else 2,
             'conf': clean(p.get('conf')).lower() or 'low', 'status': clean(p.get('status')).lower(), 'parent': clean(p.get('parent')), 'changed': clean(p.get('changed')), 'stage': 'commercial',
             'f1': f1 if dec[0] == 'exclude' else '', 'f1note': f1 if f1 and dec[0] != 'exclude' else '', 'web': False})
    # 2. web research files, one per group
    subfiles = sorted(f for f in glob.glob(os.path.join(H, 'newsec', 'subs', '*.jsonl')) if not os.path.basename(f).startswith('unconfirmed_')) if SUBS else []
    for p in sorted(glob.glob(os.path.join(H, 'newsec', 'web', '*.jsonl'))) + sorted(f for f in glob.glob(os.path.join(H, 'newsec', 'web2', '*.jsonl')) if not os.path.basename(f).startswith('unconfirmed_')) + subfiles:
        key = ('subs_' if p in subfiles else '') + os.path.basename(p)[:-6]
        for l in open(p, encoding='utf-8'):
            if not l.strip(): continue
            try: d = json.loads(l)
            except Exception: drop['Unreadable line'] += 1; continue
            bas = clean(d.get('capacity_basis')).lower()[:1]; um = d.get('capacity_usd_m'); um = um if isinstance(um, (int, float)) else None
            rec = {'key': key, 'name': clean(d.get('name')), 'grp': clean(d.get('group'))}
            if not rec['name'] or (key, rec['name']) in SKIP_LINE: continue
            rec['name'] = RENAME.get((key, rec['name']), rec['name'])
            if bas not in TEST or not clean(d.get('capacity_source')).startswith('http'): leave(rec, 'Capacity not shown from a page'); continue
            if bas in FLOOR and (um is None or um < FLOOR[bas]): leave(rec, f'Capacity figure missing or below the threshold: {clean(d.get("capacity_detail"))}'); continue
            sector = d.get('sector') if d.get('sector') in b.FIT else 'Diversified & Other'
            rec.update({'hq': clean(d.get('hq')), 'sector': sector, 'industry': clean(d.get('industry')), 'desc': clean(d.get('desc')), 'theme': clean(d.get('theme')),
                        'ownership': clean(d.get('ownership')) or 'Private, owner not stated', 'basis': bas, 'detail': clean(d.get('capacity_detail')), 'usd_m': um, 'year': clean(d.get('capacity_year')),
                        'source': clean(d.get('capacity_source')), 'sponsorships': clean(d.get('sponsorships')), 'reach': clean(d.get('reach')).title() if clean(d.get('reach')).title() in RORD else 'Domestic',
                        'reach_basis': 'web', 'markets': clean(d.get('markets')), 'signals': d.get('signals') if isinstance(d.get('signals'), dict) else {}, 'rationale': clean(d.get('rationale')),
                        'rel': d.get('rel') if d.get('rel') in (1, 2, 3, 4, 5) else 2, 'conf': clean(d.get('conf')).lower() or 'medium', 'status': 'subsidiary' if SUBS and clean(d.get('parent')) else 'private',
                        'parent': clean(d.get('parent')) if SUBS else '', 'parent_listed': clean(d.get('parent_listed')), 'parent_stake': clean(d.get('parent_stake')), 'parent_f1': clean(d.get('parent_f1')), 'changed': '',
                        'pe_parent': '',
                        'stage': 'pre-revenue' if clean(d.get('stage')).lower().startswith('pre') else 'commercial', 'f1': '', 'f1note': '', 'web': True})
            if rec['parent'] and PE_PARENT.search(rec['parent']) and rec['name'] not in ('Bridge Investment Group',):      # owned by an investment firm: privately held, no parent company
                rec['pe_parent'] = rec['parent']; rec['parent'] = ''; rec['status'] = 'private'
                if rec['ownership'].lower().startswith('subsidiary of'): rec['ownership'] = 'private equity: ' + rec['pe_parent']
            add(rec)
    if REFRESH:
        snap = {core(d['name']): d['name'] for d in _rj('v3_snapshot.json', [])}; CHANGES.clear()
        for x in list(out):
            x['chg'] = []
            for d in DEC.get(x['name'], []):
                act = d.get('action'); why = clean(d.get('why')); src = clean(d.get('source')); when = clean(d.get('date'))
                if act == 'drop':
                    out.remove(x); drop['Changed since the 18 Nov list (see the Changes Since 18 Nov tab)'] += 1
                    left.append((x['name'], group_label(x['key']), 'Changed since the 18 Nov list: ' + why + (f' ({src})' if src else '')))
                    if core(x['name']) in snap: CHANGES.append([x['name'], 'Removed', why, when, src, 'New brands (18 Nov list)'])
                    break
                if act == 'parent':
                    x['parent'] = clean(d.get('parent')); x['status'] = 'subsidiary'; x['parent_listed'] = clean(d.get('parent_listed')); x['parent_stake'] = clean(d.get('parent_stake')); x['pe_parent'] = ''
                    x['ownership'] = 'Subsidiary of ' + x['parent']
                elif act == 'signal':
                    for k, v in (d.get('signals') or {}).items():
                        if d.get('lead') and (k == 'raise' or clean((x.get('signals') or {}).get(k))): continue      # a report of talks does not replace a confirmed signal
                        x['signals'] = dict(x.get('signals') or {}, **{k: clean(v)})
                elif act == 'sponsorship': x['sponsorships'] = (x.get('sponsorships') + '; ' if x.get('sponsorships') else '') + why
                elif act == 'note': NOTE[x['name']] = (NOTE[x['name']] + '; ' if NOTE.get(x['name']) else '') + why
                x['chg'].append(why + (f' ({when})' if when and when not in why else ''))
                if core(x['name']) in snap: CHANGES.append([x['name'], 'Updated', why, when, src, 'New brands (18 Nov list)'])
        have_now = {core(x['name']) for x in out} | {core(x['name']) for x in out for _ in [0]}
        load.lost = sorted(nm for ck, nm in snap.items() if ck not in have_now and not any(d.get('action') == 'drop' for d in DEC.get(nm, [])))
        for x in out:
            x['isnew'] = core(x['name']) not in snap
            x['chgtxt'] = ('New: added on 23 Nov 2026' if x['isnew'] else ('Updated on 23 Nov 2026: ' + '; '.join(x['chg'])) if x.get('chg') else 'No change found')
    stale = []
    for x in list(out):
        if x['name'] in DEMOTE: x['demote'] = DEMOTE[x['name']]; stale.append(x); out.remove(x); drop['Evidence judged too weak on review (moved to Capacity To Confirm)'] += 1; continue
        ym = re.search(r'(19|20)\d\d', str(x.get('year') or ''))
        if x['web'] and x['basis'] == 'b' and ym and int(ym.group(0)) < 2016:        # a revenue figure more than ten years old is not proof of capacity today
            stale.append(x); out.remove(x); drop['Only revenue figure found is more than ten years old (moved to Capacity To Confirm)'] += 1
    load.stale = stale
    np_ = os.path.join(H, 'newsec', 'now_owned.json'); old = json.load(open(np_, encoding='utf-8')) if os.path.exists(np_) else {}
    if SUBS and now_owned and now_owned != old: json.dump(now_owned, open(np_, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for x in out:
        sg = x['signals'] = dict(x['signals'] or {})
        if x['web'] and x['basis'] in ('a', 'c') and x['key'] != 'pe_owned' and not clean(sg.get('raise')) and RAISED.search(x['detail']) and RECENT.search(x['detail']) and not BUYOUT.search(x['detail']):
            sg['raise'] = f"{x['detail']} ({x['source']})"            # a round dated Nov 2025 or later is itself the signal
        S = {}
        for k in a.SIG:
            v = clean((x['signals'] or {}).get(k))
            ok = bool(v) and bool(re.search(r'https?://', v)) and bool(re.search(r'202[56]', v))
            if ok and k == 'raise' and (NOT_RAISE.search(v) or not (RAISED.search(v) or re.search(r'(?i)stake sale|valuation', v))): ok = False     # buying something is not raising money
            if ok and (re.search(r'(?i)reportedly|rumou?r|said to be|in talks', v) or (x['name'], k) in SIG_DOWN): ok = False
            S[k] = ('Not yet checked', '') if not v else ('Confirmed', v) if ok else ('Lead only', v)
        x['S'] = S; x['nconf'] = sum(1 for v in S.values() if v[0] == 'Confirmed')
        x['rank'] = 'High' if x['nconf'] >= 2 else 'Medium' if x['nconf'] == 1 else 'To Verify'
        x['fit'] = round(0.25 * b.FIT[x['sector']] * 10 + 0.50 * b.REL[x['rel']] + 0.25 * b.REACH[x['reach']], 1)
        x['hq'] = hq_fix(x['hq']); x['hq_known'] = False
        if x['hq'] == 'Not recorded' and x['name'] in HQ_KNOWN: x['hq'] = HQ_KNOWN[x['name']]; x['hq_known'] = True
        x['country'] = x['hq'].split(',')[-1].strip()
        if x['name'] in HQ_NONE and x['hq'] == 'Not recorded': x['hq'] = 'No single headquarters (international partnership)'; x['country'] = 'International'
        x['tab'] = TAB_FIX.get(x['name']) or tab_for(x['theme'], x['key'], x['sector'], x['industry'] + ' ' + x['desc'], x.get('grp', ''))
        m = REV.match(x['detail'])
        said_rev = bool(m) and m.start(1) <= 34 and not re.search(r'(?i)profit|stakes|result|recurring|estimat', x['detail'][:m.start(1)]) and not (m.group(1).lower() == 'turnover' and x['sector'] == 'Gambling & Gaming Venues') and not re.search(r'(?i)estimate', x['detail'])
        x['is_rev'] = x['basis'] == 'b' and bool(x['usd_m']) and (not x['web'] or bool(x.get('rank_fig')) or said_rev)
        if x['tab'].startswith('NEW '): x['theme'] = x['tab'][4:]
    out.sort(key=lambda x: ({'High': 0, 'Medium': 1, 'To Verify': 2}[x['rank']], RORD[x['reach']], -x['fit'], -(x['usd_m'] or 0), x['name']))
    newtabs = {n for n, _, _ in NEW}; have = []
    for x in L:                                          # in scope on the sheet, capacity passed, not Domestic, in a sector that gets a new tab
        if not x['cap_pass'] or x['reach'] == 'Domestic': continue
        t = tab_for(x['theme'], '', x['sector'])
        if t in newtabs: have.append((t, x))
    have.sort(key=lambda r: ({'High': 0, 'Medium': 1, 'To Verify': 2}[r[1]['rank']], RORD[r[1]['reach']], -a.fit(r[1]), r[1]['name']))
    load.have = have
    return out, left, drop, onsheet, now_private
def extras(L, onsheet):
    """what the second pass found but could not prove (shown, not counted), Clay leads, and announced deals to watch"""
    have = {core(x['name']) for x in L}; seen = set(); conf = []; outs = []; leads = []
    for f in sorted(glob.glob(os.path.join(H, 'newsec', 'web2', 'unconfirmed_*.jsonl'))) + (sorted(glob.glob(os.path.join(H, 'newsec', 'subs', 'unconfirmed_*.jsonl'))) if SUBS else []):
        for l in open(f, encoding='utf-8'):
            try: d = json.loads(l)
            except Exception: continue
            nm = clean(d.get('name')); ck = core(nm)
            if not nm or ck in have or ck in seen or b.loose(nm) in onsheet or b.loose(fold(nm)) in onsheet or b.f1_link(nm)[0]: continue
            seen.add(ck); miss = clean(d.get('missing')); par = clean(d.get('parent'))
            row = [nm, hq_fix(d.get('hq')), d.get('sector') if d.get('sector') in b.FIT else '', clean(d.get('group')), clean(d.get('what_is_known')) + (f' Parent: {par}.' if par else ''), miss, clean(d.get('pages_tried'))]
            (outs if miss.upper().startswith('OUT') else conf).append(row)
    for x in getattr(load, 'stale', []):
        ck = core(x['name'])
        if ck in seen: continue
        seen.add(ck); conf.append([x['name'], hq_fix(x['hq']), x['sector'], group_label(x['key']), x['detail'] + ' (' + x['source'] + ')', x.get('demote') or 'The only revenue figure found is more than ten years old', x['source']])
    gone = set(); owner = {}                           # Clay leads checked against public pages and found to be listed, closed or too small (and, before 18 Nov, subsidiaries)
    for f in glob.glob(os.path.join(H, 'newsec', 'leads_out', '*.jsonl')):
        for l in open(f, encoding='utf-8'):
            try: d = json.loads(l)
            except Exception: continue
            why = clean(d.get('reason')); ck = core(clean(d.get('name')))
            if SUBS and re.match(r'(?i)owned by', why) and not re.search(r'(?i)revenue below|tobacco|vaping|sanction', why):        # removed only because another company owns it: back as a lead, owner shown
                owner[ck] = re.sub(r'\s*[;(]?\s*https?://\S+\)?', '', why).strip(' ;') ; continue
            gone.add(ck)
    extras.gone = len(gone); extras.back = len(owner)
    for f in sorted(glob.glob(os.path.join(H, 'newsec', 'leads', '*.jsonl'))):
        for l in open(f, encoding='utf-8'):
            try: d = json.loads(l)
            except Exception: continue
            nm = clean(d.get('name')); ck = core(nm)
            if not nm or ck in have or ck in seen or ck in gone or b.loose(nm) in onsheet or b.loose(fold(nm)) in onsheet or b.f1_link(nm)[0]: continue
            seen.add(ck)
            leads.append([nm, clean(d.get('domain')), hq_fix(d.get('hq')), clean(d.get('industry')), clean(d.get('clay_revenue')), clean(d.get('clay_employees')), clean(d.get('clay_type')), owner.get(ck, 'Not checked')[:1].upper() + owner.get(ck, 'Not checked')[1:]])
    wp = os.path.join(H, 'newsec', 'watch_deals.json')
    watch = [[n, 'Take-private or sale announced but not completed when checked on 16 Nov 2026: it becomes an unlisted prospect if the deal closes'] for n in (json.load(open(wp)) if os.path.exists(wp) else [])]
    return sorted(conf, key=lambda r: (r[3], r[0])), sorted(outs), sorted(leads, key=lambda r: (r[2].split(',')[-1].strip(), r[0])), watch
CHGCOL = 'Change Since the 18 Nov List'
COLS = a.COLS[:23] + ['On Your Sheet?', 'Category Tab (This Workbook)', 'Closest Tab on Your Existing Sheet', 'Theme', 'Ownership Type', 'Parent Company', 'Stage', 'Parameter 3: Capacity Test Passed',
                      'Capacity Evidence', 'Capacity Source', 'Sports Sponsorships Found'] + a.COLS[30:35] + ['Expanding?', 'How Found']
WIDTH = b.WIDTH[:23] + [12, 26, 26, 28, 26, 36, 12, 34, 46, 46, 40, 36, 36, 40, 40, 11, 34, 34]
if REFRESH: COLS = COLS + [CHGCOL]; WIDTH = WIDTH + [48]
def cells(x):
    notes = []
    if x['stage'] == 'pre-revenue': notes.append('Pre-revenue: no sales yet, so any sponsorship would be paid from funding')
    if not x['web']: notes.append('Profile written from the ranking line and general knowledge, not looked up on the web: check headquarters, ownership and reach before outreach')
    if x['reach_basis'] == 'inferred': notes.append('Geographic reach inferred, not confirmed')
    if x['conf'] == 'low': notes.append('Low-confidence line: check before outreach')
    if x['changed']: notes.append(x['changed'])
    if x['f1note']: notes.append('F1 note: ' + x['f1note'])
    if re.search(r'(?i)estimate', x['detail']): notes.append('The capacity figure is a third-party estimate, not a figure published by the company')
    if x['basis'] == 'b' and not x['is_rev'] and not re.search(r'(?i)estimate', x['detail']): notes.append('The capacity figure is not revenue as such (see Capacity Evidence)')
    if x['name'] in NOTE: notes.append(NOTE[x['name']])
    if x.get('status') == 'subsidiary' and clean(x.get('parent')): notes.append('Subsidiary: the capacity shown is its own figure, not the parent\'s. Check whether sponsorship decisions sit with the subsidiary or with the parent')
    if re.search(r'(?i)F\.C\.|Super Kings|Punjab Kings|Rajasthan Royals|Knight Riders|Atlético de Madrid|Newcastle United|Al Nassr|Saint-Germain', x['name']): notes.append('A sports club: it qualifies on the tests but is an unlikely sponsor')
    if x['web'] and x['ownership'].lower().startswith('private, owner not stated') and 'unlisted' not in NOTE.get(x['name'], '').lower(): notes.append('Owner not named on the pages read: confirm it is unlisted')
    if x['web'] and x['basis'] == 'b' and not re.search(r'(19|20)\d\d', str(x['year'])) and 'no year' not in NOTE.get(x['name'], ''): notes.append('The revenue figure found carries no year')
    if x['key'] == 'pe_owned' and re.search(r'202[56]', x['year']): notes.append('Taken private or bought recently: confirm that the deal has completed and the shares are delisted')
    if x.get('hq_known'): notes.append('Headquarters added from general knowledge, not from a page read in this research')
    if x['hq'] == 'Not recorded': notes.append('Headquarters not found on the pages read')
    if 'iso500.org.tr' in x['source']: notes.append('Unlisted status and city come from the ISO 500 industrial ranking (100% private capital; chamber city): a listed parent group is not ruled out')
    if 'famcap.com' in x['source']: notes.append('Revenue is the 2018 figure from the Family Capital / PwC Middle East 150 ranking; the profile is thin: check before outreach')
    if 'newmarketpitch' in x['source']: notes.append('Funding figure comes from one third-party funding tracker: confirm with the company before outreach')
    if x['basis'] in ('d', 'e'): notes.append('No financial figure found: capacity rests on ' + ('an existing sports sponsorship' if x['basis'] == 'd' else 'state-fund ownership'))
    sig = lambda k: x['S'][k][0] + (': ' + x['S'][k][1] if x['S'][k][1] else '')
    liq = ('Valuation or deal value: ' + x['detail']) if x['basis'] == 'c' else ('Equity raised: ' + x['detail']) if x['basis'] == 'a' else 'Not found'
    exp = x['S']['regions']
    return [x['name'], x['hq'], 'Qualifies', x['rank'], x['desc'], x['sector'] + (': ' + x['industry'] if x['industry'] else ''), 'Subsidiary (not listed itself)' if x.get('status') == 'subsidiary' and clean(x.get('parent')) else 'Private (not listed)',
            x['usd_m'] * 1e6 if x['is_rev'] else 'No published revenue figure: see Capacity Evidence' if x['basis'] == 'b' else 'Not found in the sources used', 'Not applicable (not listed)', 'Not found', 'Not found', liq, 'Not Disclosed', x['reach'], x['markets'],
            x['rationale'], x['year'] or 'Not stated', x['source'], b.F1_NOTE, 'Plausible Capacity', '; '.join(notes) or 'None flagged', x['fit'], x['conf'].title(),
            'No (new brand)', x['tab'], x['sector'], x['theme'], x['ownership'], parent_txt(x), 'Pre-revenue' if x['stage'] == 'pre-revenue' else 'Selling', TEST[x['basis']], x['detail'], x['source'], x['sponsorships'] or ('None found' if x['web'] else 'Not checked')] + \
           [sig(k) for k in a.SIG] + [x['nconf'], ('Yes: ' + exp[1]) if exp[0] == 'Confirmed' else ('Possibly: ' + exp[1]) if exp[0] == 'Lead only' else 'Not yet checked', group_label(x['key'])] + ([x.get('chgtxt', 'No change found')] if REFRESH else [])
def cells_have(x, tab):
    """a brand already on the sheet, in this workbook's column layout (figures as in the all-sector workbook)"""
    c = a.cells(x)
    test = TEST['a'] + ' (funding as recorded, may include debt)' if str(c[29]).startswith('Total funding') else str(c[29])
    return c[:23] + ['Yes', tab, c[25], c[26], c[27], c[36], c[28], test, c[11] if str(c[29]).startswith('Total funding') else c[29], c[17], 'Not checked'] + c[30:35] + [c[35] or 'Not yet checked', 'Already on your sheet'] + ([x.get('chgtxt', 'No change found')] if REFRESH else [])
def tabs(L):
    """ordered list of (tab name, rows): new-sector tabs first, then the sheet's own tabs, each without Domestic brands"""
    new = [n for n, _, _ in NEW]; old = list(b.FIT)
    T = [(n, [x for x in L if x['tab'] == n and x['reach'] != 'Domestic']) for n in new + old]
    return [(n, r) for n, r in T if r or any(t == n for t, _ in load.have)]
def check(L, left, drop, onsheet):
    bad = []
    names = Counter(core(x['name']) for x in L)
    bad += [('twice', x['name']) for x in L if names[core(x['name'])] > 1]
    bad += [('on sheet', x['name']) for x in L if b.loose(x['name']) in onsheet and x['name'] not in NOT_SHEET]
    bad += [('F1', x['name']) for x in L if b.f1_link(x['name'])[0]]
    bad += [('no source', x['name']) for x in L if not x['source']]
    bad += [('tab', x['name']) for x in L if x['tab'] not in b.FIT and x['tab'] not in [n for n, _, _ in NEW]]
    n_tabs = sum(len(r) for _, r in tabs(L)) + sum(1 for x in L if x['reach'] == 'Domestic')
    if n_tabs != len(L): bad.append(('tab rows do not add up', n_tabs))
    return bad
def near(L, onsheet):
    """new names that begin like a name on the sheet (or the reverse): to be read by hand"""
    keys = sorted(onsheet); out = []
    for x in L:
        k = b.loose(x['name'])
        if len(k) < 4: continue
        hit = [onsheet[s] for s in keys if s != k and ((s.startswith(k) and len(s) <= len(k) + 14) or (len(s) >= 5 and k.startswith(s)))][:3]
        if hit: out.append((x['name'], x['tab'], hit))
    return out
def write(L, left, drop, now_private, path, onsheet=None):
    import write_xlsx as wx
    from openpyxl import Workbook
    from openpyxl.cell import WriteOnlyCell
    from openpyxl.utils import get_column_letter
    wb = Workbook(write_only=True)
    n = len(L); rc = Counter(x['reach'] for x in L); bc = Counter(x['basis'] for x in L); rk = Counter(x['rank'] for x in L); T = tabs(L)
    tc = Counter(x['tab'] for x in L); ctry = Counter(x['country'] for x in L if x['country'] not in ('Not recorded', 'International')); newn = [nm for nm, _, _ in NEW]
    nohq = sum(1 for x in L if x['hq'] == 'Not recorded')
    n_new = sum(tc[t] for t in newn); desk = sum(1 for x in L if not x['web']); hc = Counter(t for t, _ in load.have)
    conf, outs, leads, watch = extras(L, onsheet or {})
    p2 = [x for x in L if is_pass2(x['key'])]; p2k = Counter('regional rankings' if x['key'].startswith('region_') else 'second proof attempt' if x['key'].startswith('confirm_') else 'Clay leads proven' if x['key'].startswith('clayproof_') else 'private-equity portfolios' for x in p2)
    p2c = Counter(x['country'] for x in p2 if x['country'] not in ('Not recorded', 'International'))
    subs = [x for x in L if x.get('status') == 'subsidiary' and clean(x.get('parent'))]; sp = [x for x in L if x['key'].startswith('subs_')]
    spk = Counter('formerly listed companies bought since Nov 2023' if x['key'].startswith('subs_was_listed') else SUBS_LABEL.get(x['key'][5:], x['key'][5:]) for x in sp); f1s = [x for x in subs if 'F1 link' in parent_txt(x)]
    newb = [x for x in L if x.get('isnew')]; upd = [x for x in L if x.get('chg')]; allch = CHANGES + a.CHANGES
    rem = [c for c in allch if c[1] == 'Removed']; talk = _rj('talks_status.json', [])
    RS = [('New brands for your sheet, filed by category - refreshed on 23 Nov 2026',),
          [f"This is the 18 Nov 2026 list brought up to date. {len(newb)} brands are new (tab 'New Since 18 Nov'; last column reads 'New'). {len(upd)} brands on the list carry news since 1 Nov 2026 (last column reads 'Updated'). "
           f"{sum(1 for c in rem if c[5].startswith('New brands'))} brands were taken off this list. Every change, with its date and source, is on the 'Changes Since 18 Nov' tab."],
          [f"Brands on your own 48-tab sheet: {len({c[0] for c in a.CHANGES if c[1] == 'Updated'})} updated and {len({c[0] for c in a.CHANGES if c[1] == 'Removed'})} removed because their shares now trade ({'; '.join(sorted({c[0] for c in a.CHANGES if c[1] == 'Removed'})) or 'none'}). "
           "They are listed on the 'Changes Since 18 Nov' tab here and carried in full in the companion file F1-NON-LISTED-PROSPECTS-ALL-SECTORS-v3-2026-11-23.xlsx. "
           "Five brands that were listed on 18 Nov have since been taken private or bought for USD 1B or more and are now in scope: Integer Holdings, LXP Industrial Trust, Utz Brands, Irish Continental Group and Arcosa (tab 'On Your Sheet - Now Unlisted')."],
          ['What was checked on 23 Nov 2026: Formula 1 partner announcements since 1 Oct 2026 for the championship, each team and the Grands Prix; share listings and IPO filings since 1 Nov 2026; acquisitions, mergers and closures since 1 Nov 2026; '
           'equity rounds of USD 100M or more and new USD 1B valuations since 1 Nov 2026 by region; buyouts, carve-outs and take-privates; new top-tier sports sponsorships; and the companies on the funding-talks watch list.'],
          ['What was not done: the 2,039 brands were not re-checked one by one. A change is recorded only where the research of 23 Nov came across it, so "No change found" means no event was found, not that nothing happened. Crunchbase could not be used (allowance exhausted until 1 Dec 2026); Apollo was not used.'], []] if REFRESH else []
    S = RS + [('The list in full (rules of 18 Nov 2026, subsidiaries included)' if REFRESH else 'New brands for your sheet, filed by category - ' + ('subsidiaries included (18 Nov 2026)' if SUBS else 'second pass included (16 Nov 2026)'),),
         [f"{n:,} companies that are not on your 48-tab sheet. Each is unlisted, is not a current F1 partner or the owner of one, and passes the capacity test with a source. Headquarters in {len(ctry)} countries."]] + ([
         [f"Rule change of 18 Nov 2026: subsidiaries are in scope, and every row has a Parent Company column. {len(subs):,} of the new brands are subsidiaries of another company; {len(sp):,} lines come from a research pass for subsidiaries: " + '; '.join(f'{v} {k}' for k, v in spk.most_common()) + '.'],
         [f"{len(f1s)} of the subsidiaries belong to a group that has a current F1 partner brand. They are included and the Parent Company column states the link, so a category conflict can be checked. The brand that holds an F1 deal itself, and the owners of F1 partners, stay out."],
         ['A subsidiary passes the capacity test only on its own figure (its own revenue, funding, purchase price or sponsorship), never on its parent\'s size. For independent companies the Parent Company column reads "None".']] if SUBS else []) + [
         [f"{n_new:,} of the new brands belong to sectors your sheet has no tab for; they are on {sum(1 for t in newn if tc[t] or hc[t])} new tabs (names start with NEW). {n - n_new:,} are filed under {sum(1 for t in b.FIT if tc[t])} of your existing tab names."],
         [f"Each new sector tab is complete: the new brands come first (On Your Sheet? = No), followed by the {len(load.have):,} brands that are already on your sheet under other tabs and belong to that sector (On Your Sheet? = Yes). These are not counted as new."],
         ['Each new brand is on one tab only. Domestic brands are on the Domestic tab, not on the category tabs. The All New Brands tab holds every new brand and nothing else.'], [],
         ('What the second pass added',),
         [f"The list now holds {n:,} qualifying brands; the first workbook held 722. {len(p2):,} lines come from second-pass research: " + '; '.join(f'{v} from {k}' for k, v in p2k.most_common()) + '. A few of them replace first-pass lines with better-evidenced ones. The "How Found" column starts with "Second pass" for these.'],
         ['Second-pass brands by headquarters: ' + '; '.join(f'{c} {v}' for c, v in p2c.most_common(30)) + '.'],
         [f"{len(conf):,} companies that look like prospects but whose capacity or ownership could not be shown from a public page are on the Capacity To Confirm tab. They are not counted as qualifying."],
         [f"{len(leads):,} privately held companies returned by Clay and not otherwise known are on the Clay Leads tab. Clay's revenue bracket is right about half the time for private companies, so these are leads only. A further {getattr(extras, 'gone', 0)} Clay leads were checked against public pages and removed as listed, closed or too small" + (f"; {getattr(extras, 'back', 0)} that had been removed only because another company owns them are back on the tab, with the owner shown." if SUBS else ", or owned by a listed or foreign group.")],
         [f"{len(watch)} listed companies with a take-private or sale announced but not completed are on the Deals Announced tab."], [],
         ('New sector tabs: new brands (including Domestic) + brands already on your sheet (Global, International and Regional)',)] + [[f"{t[4:]}: {tc[t]} new + {hc[t]} already on your sheet - {what}"] for t, what, _ in NEW if tc[t] or hc[t]] + [[],
         ('Your existing tabs that gain new brands (including Domestic)',)] + [[f"{t}: {tc[t]}"] for t in b.FIT if tc[t]] + [[],
         ('How each company passes parameter 3 (can it pay)',)] + [[f"{TEST[k]}: {bc[k]}"] for k in 'abcde' if bc[k]] + [[],
         ('Reach',), [f"Global {rc['Global']}; International {rc['International']}; Regional {rc['Regional']}; Domestic {rc['Domestic']}."], [],
         ('Headquarters',), ['; '.join(f'{c} {v}' for c, v in ctry.most_common(25)) + ('; other countries ' + str(sum(v for c, v in ctry.most_common()[25:])) if len(ctry) > 25 else '') + f'; not found on the pages read {nohq}; no single headquarters 3.'], [],
         ('Priority under the parameters',),
         [f"High {rk['High']}; Medium {rk['Medium']}; To Verify {rk['To Verify']}. Most are To Verify because the four reasons to buy (parameter 4) have not been looked up for these companies yet. A reason is shown only where the research came across it."], [],
         ('Found but left out',)] + [[f"{v} - {k}"] for k, v in drop.most_common()] + [[],
         ('How the list was made',),
         [f"{n - desk:,} companies come from web research on 16 Nov 2026, one group at a time across all regions, and from the public unicorn list with each company checked. Each carries the fact that makes it qualify and the page it comes from."],
         [f"{desk:,} companies come from public revenue rankings of unlisted companies. The revenue is the ranking figure. Their headquarters city, description and reach were written from the ranking line and general knowledge, not looked up, and each is flagged in Verification Notes."],
         ['Second pass: unlisted companies region by region from national rankings and company pages; a second proof attempt on companies dropped in the first pass; the portfolios of the large investment firms; and a Clay sweep for leads.']] + ([
         ['Subsidiaries pass (18 Nov 2026): companies bought for USD 1B or more since Nov 2023 that still trade under their own name; subsidiaries with their own outside investors; subsidiaries of listed groups by region with their own published revenue; subsidiaries that sponsor top-tier sport; sister brands of groups that have an F1 partner; subsidiaries of unlisted, family and state groups.'],
         ['The earlier passes skipped subsidiaries on purpose, so before 18 Nov the research did not record them. One pass cannot list every subsidiary of every group: it covers the best-documented ones, and unproven ones are on the Capacity To Confirm tab.']] if SUBS else []) + [
         ['No complete register of unlisted companies exists, so this cannot be guaranteed complete. Before a company was researched it was checked against your sheet and the first pass, so brands you already have were skipped.']]
    wx.text_sheet(wb, 'Summary', S, widths=(170,))
    data = {id(x): cells(x) for x in L}
    if REFRESH:
        order = {'Added': 0, 'Removed': 1, 'Updated': 2, 'For information': 3}
        rows_c = sorted(allch + [[x['name'], 'Added', TEST[x['basis']] + ': ' + x['detail'], x['year'] or '', x['source'], 'New brand: ' + x['tab']] for x in newb] + _rj('info_rows.json', []), key=lambda r: (order.get(r[1], 9), r[5].split(':')[0], r[0].lower()))
        wx.sheet(wb, 'Changes Since 18 Nov', ['Company', 'Change', 'What Happened', 'Date', 'Source', 'Where It Sits'], [36, 16, 100, 16, 60, 40], rows_c)
        wx.sheet(wb, 'New Since 18 Nov', COLS, WIDTH, [data[id(x)] for x in newb])
        if talk: wx.sheet(wb, 'Funding Talks - Update', ['Company', 'On Your Lists?', 'Talks as Reported', 'Reported By', 'Status on 23 Nov 2026', 'What the Page Says', 'Date', 'Source'], [32, 16, 70, 22, 22, 80, 14, 60], talk)
    wx.sheet(wb, 'All New Brands', COLS, WIDTH, [data[id(x)] for x in L])
    for name, rows in T: wx.sheet(wb, name, COLS, WIDTH, [data[id(x)] for x in rows] + [cells_have(x, name) for t, x in load.have if t == name])
    wx.sheet(wb, 'Domestic', COLS, WIDTH, [data[id(x)] for x in L if x['reach'] == 'Domestic'])
    NPC = ['Company (on your sheet)', 'Tab on Your Sheet', 'Status in the Earlier Workbook', 'Ownership Found Now', 'Capacity Test Passed', 'Evidence', 'Source', 'Headquarters', 'Geographic Reach']
    if now_private: wx.sheet(wb, 'On Your Sheet - Now Unlisted', NPC, [34, 28, 24, 36, 34, 60, 50, 26, 14], sorted(now_private))
    if conf: wx.sheet(wb, 'Capacity To Confirm', ['Company', 'Headquarters', 'Sector', 'Found Under', 'What Is Known (from pages read)', 'What Could Not Be Shown', 'Pages Tried'], [34, 26, 28, 34, 70, 60, 50], conf)
    if leads: wx.sheet(wb, 'Clay Leads (Unconfirmed)', ['Company', 'Website', 'Headquarters (Clay)', 'Industry (Clay)', 'Revenue Bracket (Clay, unverified)', 'Employees (Clay)', 'Company Type (Clay)', 'Owner Found on a Public Page'], [36, 28, 28, 34, 26, 18, 20, 50], leads)
    if watch: wx.sheet(wb, 'Deals Announced - Watch', ['Company (still listed)', 'Note'], [34, 120], watch)
    ws = wb.create_sheet('Left Out')
    for j, w in enumerate((40, 48, 90), 1): ws.column_dimensions[get_column_letter(j)].width = w
    hdr = []
    for c in ['Company', 'How Found', 'Why it is not on the list']:
        x = WriteOnlyCell(ws, value=c); x.font = wx.HFONT; x.fill = wx.HEAD; x.alignment = wx.HALIGN; hdr.append(x)
    ws.append(hdr)
    for row in sorted(left + [(r[0], 'Second pass: proof attempt', (r[5] + (' - ' + r[4] if r[4] else ''))[:400]) for r in outs], key=lambda r: (r[2].split(':')[0], r[0])): ws.append(list(row))
    K = [('What this workbook is', 'New brands only: none of them is on your 48-tab sheet. Same parameter set as the all-sector workbook.'),
         ('Change Since the 18 Nov List (last column)', '"New: added on 23 Nov 2026" = not on the 18 Nov list. "Updated on 23 Nov 2026" = the research of 23 Nov found news about the company since 1 Nov 2026 (round closed, IPO filing, new owner, new sponsorship); the news is written in the cell and on the Changes Since 18 Nov tab. "No change found" = no event was found; the company was not re-checked one by one.'),
         ('Changes Since 18 Nov tab', 'Every company added, taken off or updated on 23 Nov 2026, with what happened, the date and the page. "For information" rows are listed companies that became Formula 1 partners: they are outside this workbook but matter for your public-company lists.'),
         ('New Since 18 Nov tab', 'The brands added on 23 Nov 2026, in full. They are also on All New Brands and on their category tabs.'),
         ('Funding Talks - Update tab', 'The companies on the funding-talks watch list that were followed up on 23 Nov 2026: whether the reported round or sale has since been announced.'),
         ('Tabs', 'Tabs starting with NEW are sectors your sheet has no tab for. Each holds the new brands first, then the brands already on your sheet that belong to that sector. The other category tabs carry your own tab names and hold new brands only, so the rows can be pasted under the matching tab.'),
         ('On Your Sheet?', 'No (new brand) = not on your sheet. Yes = already on your sheet under the tab named in "Closest Tab on Your Existing Sheet"; its figures are those of the all-sector workbook (funding as recorded by Crunchbase).'),
         ('Category Tab / Closest Tab on Your Existing Sheet', 'The tab the brand is filed under here, and the tab on your current sheet it would otherwise belong to.'),
         ('Parameter 3: capacity test passed', 'One of: equity raised of USD 150M or more in total (no limit on the date of the last round); published revenue of USD 300M or more; valued at or bought for USD 1B or more since Nov 2023; already pays for a top-tier sports sponsorship; owned by a state fund building the brand internationally. Capacity Evidence and Capacity Source give the fact and the page.'),
         ('Annual Revenue (USD)', 'Filled only where the test passed is published revenue; the figure is the one on the source page. Otherwise "Not found in the sources used".'),
         ('Parameter 4 columns', 'Confirmed = the research found it, with date and page. Lead only = found without a date or page. Not yet checked = not looked up. A full check takes two web searches per company.'),
         ('Outreach Priority', 'High = two or more confirmed reasons to buy; Medium = one; To Verify = none confirmed yet.'),
         ('Parent Company', 'For a subsidiary: the parent as stated on the page read, "(listed)" with the exchange where known, the stake where a page states it, and the F1 link where the parent or a sister brand is a current F1 partner. "None" for an independent company; where an investment firm or a state owns the company it says so. "Not stated on the pages read" where no owner was found.'),
         ('Stage', 'Pre-revenue companies are kept and labelled.'),
         ('Geographic Reach', 'Global, International, Regional or Domestic. Domestic brands are on the Domestic tab.'),
         ('Fit Score (0-100)', 'Sector fit (25%), relevance to F1 (50%) and reach (25%). Orders companies inside the same priority.'),
         ('On Your Sheet - Now Unlisted tab', 'Brands already on your sheet that the earlier workbook treated as listed, owned by another company or unconfirmed, and that this research found to be unlisted today (for example taken private in 2024-26). They are not new brands, so they are not counted here, but they now belong in scope.'),
         ('Capacity To Confirm tab', 'Companies found by the research that look like prospects but where no public page stated the funding, revenue or owner. Nothing found is dropped silently: check these directly (company accounts, a call) before treating them as prospects.'),
         ('Clay Leads (Unconfirmed) tab', 'Privately held companies returned by Clay with revenue brackets at or above about USD 250M that are not on your sheet or in this workbook. Unverified: Clay revenue and ownership tags are often wrong for private companies.'),
         ('Deals Announced - Watch tab', 'Listed companies with a take-private or sale announced but not completed on 16 Nov 2026. Each becomes an unlisted prospect if its deal closes.'),
         ('Left Out tab', 'Companies the research found that are current F1 partners or their owners, listed, closed, or whose capacity could not be shown from a page.' + ('' if SUBS else ' Also companies owned by a listed group.'))]
    wx.text_sheet(wb, 'Key', K)
    wb.save(path)
if __name__ == '__main__':
    L, left, drop, onsheet, now_private = load()
    print(len(L), 'new brands | by source', dict(Counter(x['key'] for x in L)))
    print('left out', dict(drop))
    print('reach', dict(Counter(x['reach'] for x in L)), '| basis', dict(Counter(x['basis'] for x in L)), '| rank', dict(Counter(x['rank'] for x in L)), '| countries', len(Counter(x['country'] for x in L)))
    print('tabs', [(n, len(r)) for n, r in tabs(L)], '| domestic', sum(1 for x in L if x['reach'] == 'Domestic'))
    print('on the sheet but now unlisted:', len(now_private), [r[0] for r in now_private][:30])
    ex = extras(L, onsheet); print('to confirm', len(ex[0]), '| out on second attempt', len(ex[1]), '| clay leads', len(ex[2]), '| watch', len(ex[3]), '| second-pass brands', sum(1 for x in L if is_pass2(x['key'])))
    bad = check(L, left, drop, onsheet); print('CHECK', 'ok' if not bad else bad[:20])
    if REFRESH: print('REFRESH | new', sum(1 for x in L if x.get('isnew')), '| updated', sum(1 for x in L if x.get('chg')), '| changes', Counter(c[1] for c in CHANGES + a.CHANGES), '| on the 18 Nov list but missing now without a decision:', getattr(load, 'lost', []))
    if len(sys.argv) > 1 and sys.argv[1] == 'near':
        for r in near(L, onsheet): print(r)
    if len(sys.argv) > 1 and sys.argv[1] == 'xlsx':
        if bad: sys.exit('not written: checks failed')
        write(L, left, drop, now_private, OUT, onsheet); print(OUT)
