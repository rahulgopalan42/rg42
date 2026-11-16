"""Sector and theme screen of the private companies in the brand workbook, against the user's 'Private' selection sheet:
where are fundable, internationally active private brands that are not on the selection yet, and which themes are growing fastest.
Usage: expand_screen.py [check|xlsx]"""
import json, os, re, statistics, sys
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b
OUT = os.path.join(b.R, 'reports', 'F1-PRIVATE-EXPANSION-SCREEN-2026-11-16.xlsx')
WIDE = ('International', 'Global')
THEMES = [   # (theme, pattern on industry + description + Crunchbase industries); first match wins
 ('Quantum computing', r'quantum'),
 ('Nuclear & fusion energy', r'nuclear|fusion (energy|power|reactor)|small modular reactor|\bsmrs?\b|microreactor|fission'),
 ('Prediction markets, betting & iGaming', r'prediction market|event contracts|sports betting|sportsbook|igaming|online casino|betting|gambling|lotter|fantasy sports|sweepstakes'),
 ('Digital assets, stablecoins & crypto', r'crypto|blockchain|stablecoin|bitcoin|digital asset|web3|tokeni[sz]|\bdefi\b|decentrali[sz]ed finance'),
 ('Defence technology', r'defen[cs]e|military|weapon|munition|missile|counter-drone|national security|warfare'),
 ('Space & satellites', r'satellite|space (launch|technology|company|infrastructure|station|systems|tech)|rocket|launch vehicle|spacecraft|earth observation|in-orbit|orbital'),
 ('Robotics, humanoids & autonomous driving', r'robot|humanoid|autonomous (vehicle|driving|truck|system|mobility|machine)|self-driving|driverless|unmanned|\bdrones?\b'),
 ('AI infrastructure: data centres & GPU cloud', r'data cent(re|er)|gpu cloud|neocloud|ai cloud|ai infrastructure|hyperscale|colocation|ai compute|compute infrastructure|inference (cloud|infrastructure)|high-performance computing|\bhpc\b'),
 ('AI chips & semiconductors', r'\bchips?\b|chipmaker|semiconductor|photonic|processor|\basic\b|wafer|foundry'),
 ('AI models, agents & applications', r'foundation model|language model|\bllm|generative ai|\bai\b|artificial intelligence|agentic|machine learning'),
 ('Cybersecurity', r'cyber|security (software|platform|company)|identity (security|management|verification)|zero trust|endpoint|threat (detection|intelligence)'),
 ('EVs, charging & new mobility', r'electric (vehicle|car|truck|bus|motorcycle|scooter|bike|aircraft)|\bevs?\b|charging|evtol|air taxi|micromobility|ride-hailing|e-scooter|e-bike'),
 ('Energy storage, renewables & grid', r'battery|energy storage|solar|wind (farm|power|developer|energy)|renewable|\bgrid\b|clean energy|independent power'),
 ('Consumer health, GLP-1, wearables & longevity', r'glp-1|weight[- ]loss|telehealth|longevity|wearable|smart ring|supplement|wellness|digital health|mental health|fitness|sleep|nutrition'),
 ('Sports, gaming, creator & entertainment', r'sports|creator|streaming|esports|video game|gaming|game (studio|developer|publisher)|music|live (events|entertainment)|ticketing|fan engagement|collectible|trading card|film|entertainment'),
 ('Neobanks, payments & trading apps', r'neobank|digital bank|challenger bank|payment|buy now|bnpl|remittance|money transfer|trading (app|platform)|brokerage|wealth|robo-advis|fintech|digital lending|expense management|spend management'),
 ('Consumer brands: beauty, fashion, food & drink', r'beauty|skincare|skin care|cosmetic|fragrance|apparel|fashion|footwear|sneaker|eyewear|beverage|energy drink|drinks|spirits|tequila|coffee|snack|restaurant|luxury|jewel|watch'),
 ('Travel, aviation & hospitality', r'travel|hotel|hospitality|airline|private (jet|aviation)|cruise|vacation rental|tourism|aviation'),
 ('Climate & industrial decarbonisation', r'carbon (capture|removal)|hydrogen|green steel|sustainable aviation fuel|critical mineral|recycling|circular|climate|geothermal|low-carbon'),
 ('Insurance, property & mortgage tech', r'insurtech|insurance|proptech|real estate|mortgage|property'),
 ('Biotech & drug development', r'biotech|drug|therapeutic|clinical-stage|pharma|gene|cell therapy|oncology'),
 ('Healthcare services & medical technology', r'healthcare|health care|medical|hospital|clinic|diagnostic|dental|care provider'),
 ('Logistics & supply chain', r'logistics|freight|supply chain|delivery|warehouse|shipping|trucking'),
 ('Education & training', r'edtech|education|learning|training|school|universit'),
]
TH = [(n, re.compile(p, re.I)) for n, p in THEMES]
def theme(x):
    for t in (b.clean(x['e'].get('industry')), b.clean(x['e'].get('desc')), b.clean(x['r'].get('subsector'))):   # the short industry label decides; the description and Crunchbase tags only if it says nothing
        for n, rx in TH:
            if rx.search(t): return n
    return 'Enterprise software (other)' if x['sector'] in ('Software, Internet & AI', 'IT Services & Consulting') else 'Other / traditional industry'
amt = lambda x: b.funding(x['r'])[0] or 0
def load():
    A = b.assemble(); rows = A['rows']; sel = {r['id'] for r in json.load(open(os.path.join(H, 'data', 'selection.json'), encoding='utf-8'))}
    for x in rows:
        x['theme'] = theme(x); x['amt'] = amt(x); x['sel'] = x['r']['id'] in sel
        x['private'] = x['status'] == 'private' and x['stage'] in ('commercial', 'pre-revenue')
        x['cap_ok'] = x['private'] and x['stage'] == 'commercial' and x['cat'] != 'To Verify' and x['rel'] >= 3        # fundable under the funding rule, and a plausible F1 fit
        x['qual'] = x['cap_ok'] and x['reach'] in WIDE
        x['reach_tbc'] = x['cap_ok'] and x['reach'] not in WIDE and (x['basis'] == 'inferred' or x['conf'] == 'low')   # capacity yes, reach Domestic/Regional only by inference
    return A, rows
def stats(L):
    P = [x for x in L if x['private']]; d = [x for x in P if x['age'] is not None]
    return {'brands': len(L), 'private': len(P), 'raised': sum(x['amt'] for x in P), 'median': statistics.median([x['amt'] for x in P if x['amt']] or [0]),
            'recent12': sum(1 for x in d if x['age'] <= 12), 'dated': len(d), 'cap_ok': sum(x['cap_ok'] for x in P), 'qual': sum(x['qual'] for x in P), 'on_sheet': sum(x['qual'] and x['sel'] for x in P),
            'new': sum(x['qual'] and not x['sel'] for x in P), 'tbc': sum(x['reach_tbc'] and not x['sel'] for x in P),
            'top': [x['name'] for x in sorted([x for x in P if x['qual'] and not x['sel']], key=lambda x: (-x['score'], -x['amt']))[:8]]}
ONSHEET = {'Software, Internet & AI': 'Software', 'IT Services & Consulting': 'IT Services', 'Investment & Capital Markets': 'Investment & Capital', 'Financial Services & Payments': 'Financial Services',
           'Industrial Machinery & Equipment': 'Industrial Machinery', 'Luxury, Jewellery & Watches': 'Luxury, Jewellery', 'Beauty & Personal Care': 'Beauty & Personal Care', 'Staffing & HR': 'Staffing & HR'}
def table(rows, key, order=None):
    G = defaultdict(list)
    for x in rows: G[x[key]].append(x)
    T = [(k, stats(L)) for k, L in G.items()]
    return sorted(T, key=lambda t: (-t[1]['new'], -t[1]['cap_ok'], -t[1]['raised']))
def pctv(a, n): return (a / n) if n else None
def write(A, rows, path):
    import write_xlsx as wx, expand_notes as N
    from openpyxl import Workbook
    from openpyxl.cell import WriteOnlyCell
    from openpyxl.utils import get_column_letter
    wb = Workbook(write_only=True)
    def grid(title, cols, widths, data, fmt=None, wrap=()):
        ws = wb.create_sheet(title); ws.freeze_panes = 'B2'
        for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
        ws.row_dimensions[1].height = 58; hdr = []
        for c in cols:
            x = WriteOnlyCell(ws, value=c); x.font = wx.HFONT; x.fill = wx.HEAD; x.alignment = wx.HALIGN; hdr.append(x)
        ws.append(hdr)
        for r in data:
            out = []
            for j, v in enumerate(r):
                x = WriteOnlyCell(ws, value=v); x.alignment = wx.WRAP
                if fmt and j in fmt and isinstance(v, (int, float)): x.number_format = fmt[j]
                if isinstance(v, str) and v in N.FILL: x.fill = wx.FILLS[N.FILL[v]]
                out.append(x)
            ws.append(out)
    new = sorted([x for x in rows if x['qual'] and not x['sel']], key=lambda x: (-x['score'], -x['amt'])); tbc = sorted([x for x in rows if x['reach_tbc'] and not x['sel']], key=lambda x: (-x['score'], -x['amt']))
    wx.text_sheet(wb, 'Summary', N.summary(rows, new, tbc), widths=(150,))
    S = table(rows, 'sector')
    grid('Sector Screen', ['Sector (by the company\'s actual business)', 'Tab on your Private sheet', 'F1 sector fit (0-10)', 'Private companies in the 48-tab sheet', 'Total funding raised by them (USD)',
                           'Share with a funding round in the last 12 months', 'Fundable and a plausible F1 fit', 'of which International / Global', 'of which already on your Private sheet', 'NEW candidates',
                           'More if reach is confirmed', 'Recommendation', 'Examples of new candidates (highest priority first)'],
         (36, 18, 9, 12, 14, 12, 12, 12, 12, 11, 11, 22, 90),
         [[k, ONSHEET.get(k, 'Not covered'), b.FIT.get(k), s['private'], s['raised'], pctv(s['recent12'], s['dated']), s['cap_ok'], s['qual'], s['on_sheet'], s['new'], s['tbc'], N.sector_call(k, s, ONSHEET), ', '.join(s['top'])] for k, s in S if s['private']],
         fmt={4: wx.MONEY, 5: '0%'})
    T = {k: s for k, s in table(rows, 'theme')}
    grid('Theme Screen', ['Theme', 'Verdict', 'Private companies in the 48-tab sheet', 'Total funding raised by them (USD)', 'Share with a funding round in the last 12 months', 'Share still pre-revenue',
                          'Fundable and a plausible F1 fit', 'of which International / Global', 'of which already on your Private sheet', 'NEW candidates', 'More if reach is confirmed',
                          'Private funding trend (web, Nov 2026)', 'Who in this category already buys F1 or top-tier sport (web and 2025-26 partner roster)', 'Limits and restrictions', 'What to do', 'Examples of new candidates on your sheets'],
         (34, 20, 11, 13, 11, 10, 11, 11, 11, 10, 10, 58, 70, 44, 52, 60),
         [[k, N.THEME[k]['verdict'], T[k]['private'], T[k]['raised'], pctv(T[k]['recent12'], T[k]['dated']), pctv(sum(1 for x in rows if x['theme'] == k and x['private'] and x['stage'] == 'pre-revenue'), T[k]['private']),
           T[k]['cap_ok'], T[k]['qual'], T[k]['on_sheet'], T[k]['new'], T[k]['tbc'], N.THEME[k]['funding'], N.THEME[k]['f1'], N.THEME[k]['limits'], N.THEME[k]['do'], ', '.join(T[k]['top'])] for k in N.ORDER if k in T],
         fmt={3: wx.MONEY, 4: '0%', 5: '0%'})
    cols = b.COLS + ['Theme']; width = b.WIDTH + [30]
    wx.sheet(wb, 'New Candidates', cols, width, [b.cells(x) + [x['theme']] for x in new])
    wx.sheet(wb, 'Reach To Confirm', cols, width, [b.cells(x) + [x['theme']] for x in tbc])
    wx.text_sheet(wb, 'Key', N.KEY)
    wb.save(path)
if __name__ == '__main__':
    A, rows = load()
    print('private', sum(x['private'] for x in rows), '| fundable + fit', sum(x['cap_ok'] for x in rows), '| + International/Global', sum(x['qual'] for x in rows), '| new (not on your sheet)', sum(x['qual'] and not x['sel'] for x in rows), '| reach to confirm', sum(x['reach_tbc'] and not x['sel'] for x in rows))
    for label, key in (('THEME', 'theme'), ('SECTOR', 'sector')):
        G = defaultdict(list)
        for x in rows: G[x[key]].append(x)
        print(f'--- {label}: private | raised $B | median $M | % round in last 12m | fundable+fit | Intl/Global | on sheet | NEW | reach tbc | examples')
        for k, L in sorted(G.items(), key=lambda kv: -stats(kv[1])['new']):
            s = stats(L)
            if s['private'] < 5: continue
            print(f"{k[:44]:44} {s['private']:5} {s['raised'] / 1e9:6.0f} {s['median'] / 1e6:6.0f} {100 * s['recent12'] // max(s['dated'], 1):4}% {s['cap_ok']:5} {s['qual']:5} {s['on_sheet']:4} {s['new']:4} {s['tbc']:4} | " + ', '.join(s['top'][:6]))
    if len(sys.argv) > 1 and sys.argv[1] == 'xlsx': write(A, rows, OUT); print(OUT)
