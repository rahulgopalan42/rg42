"""Current Formula 1 involvement: the 2025-26 roster of championship, team and Grand Prix partners
(unicorns/ref/f1_sponsors_2026.json, 424 entries with source links) plus the listed parent companies of roster brands
and the listed companies that own or supply teams. A listed company matching any of these is excluded."""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, regdom
ROSTER = json.load(open(os.path.join(R, 'unicorns', 'ref', 'f1_sponsors_2026.json')))
# listed parent / owner -> the roster brand(s) that make it an existing F1 sponsor
PARENTS = {
 'Alphabet': 'Google (McLaren)', 'Amazon': 'AWS (Formula 1), Zoox', 'Meta Platforms': 'WhatsApp, Meta AI', 'Block': 'Cash App (Racing Bulls)',
 'Deutsche Post': 'DHL (Formula 1)', 'DHL Group': 'DHL (Formula 1)', 'Saudi Aramco': 'Aramco (Formula 1, Aston Martin)', 'Saudi Arabian Oil': 'Aramco',
 'Nestlé': 'KitKat, S.Pellegrino', 'Nestle': 'KitKat, S.Pellegrino', 'Pernod Ricard': 'Chivas Regal, G.H. Mumm', 'Brown-Forman': "Jack Daniel's",
 'Suntory Beverage & Food': 'Jim Beam (Suntory group)', 'Asahi Group': 'Peroni Nastro Azzurro', 'Asahi Group Holdings': 'Peroni Nastro Azzurro',
 'Monster Beverage': 'Monster Energy', 'Celsius Holdings': 'Celsius', 'Procter & Gamble': 'Gillette', 'Berkshire Hathaway': 'Duracell',
 'Edgewell Personal Care': 'Wilkinson Sword', "L'Oréal": 'SkinCeuticals', 'LOreal': 'SkinCeuticals', 'EssilorLuxottica': 'Ray-Ban, Oakley', 'Kering': 'Maui Jim (Kering Eyewear)',
 'Samsonite': 'TUMI', 'Samsonite Group': 'TUMI', 'Topgolf Callaway Brands': 'TravisMathew', 'Callaway': 'TravisMathew', 'Glanbia': 'Optimum Nutrition',
 'Philip Morris International': 'ZYN', 'Philip Morris': 'ZYN', 'Richemont': 'IWC Schaffhausen', 'Compagnie Financière Richemont': 'IWC Schaffhausen',
 'PVH': 'Tommy Hilfiger', 'Hugo Boss': 'BOSS, HUGO', 'Next': 'Reiss', 'Next plc': 'Reiss', 'Exxon Mobil': 'Mobil 1, Esso Synergy', 'ExxonMobil': 'Mobil 1, Esso Synergy',
 'BASF': 'Glasurit', 'AkzoNobel': 'Sikkens', 'Akzo Nobel': 'Sikkens', 'Stanley Black & Decker': 'DeWalt', 'Adecco': 'Akkodis', 'Adecco Group': 'Akkodis',
 'Recruit Holdings': 'Indeed', 'Recruit': 'Indeed', 'Paramount Skydance': 'Paramount+', 'Paramount Global': 'Paramount+', 'Comcast': 'CNBC', 'Versant Media': 'CNBC',
 'Krafton': 'PUBG Mobile', 'Tencent': 'PUBG Mobile (publisher)', 'Flutter Entertainment': 'FanDuel', 'Super Group': 'Betway, Jackpot City',
 'Norwegian Cruise Line Holdings': 'Regent Seven Seas Cruises', 'Norwegian Cruise Line': 'Regent Seven Seas Cruises', 'StubHub': 'viagogo', 'StubHub Holdings': 'viagogo',
 'Niterra': 'NGK Spark Plugs', 'Marsh & McLennan': 'Marsh', 'Marsh McLennan': 'Marsh', 'Bank of New York Mellon': 'BNY', 'Deutsche Telekom': 'T-Mobile',
 'T-Mobile US': 'T-Mobile', 'Saudi Telecom': 'STC', 'Saudi Telecom Company': 'STC', 'Saudi Arabian Mining': 'Maaden', "Ma'aden": 'Maaden',
 'Qualcomm': 'Snapdragon', 'Cisco': 'Webex', 'Cisco Systems': 'Webex', 'Synopsys': 'Ansys', 'CommScope': 'Ruckus Networks', 'Tata Communications': 'Tata Communications',
 'Petronas Chemicals': 'Petronas group', 'Petronas Gas': 'Petronas group', 'Petronas Dagangan': 'Petronas group', 'MISC Berhad': 'Petronas group', 'KLCC Property': 'Petronas group',
 'Volkswagen': 'Audi F1 team', 'Porsche Automobil Holding': 'Audi F1 team (Volkswagen parent)', 'Porsche SE': 'Audi F1 team (Volkswagen parent)', 'Porsche': 'Volkswagen group (Audi F1 team)',
 'Traton': 'Volkswagen group (Audi F1 team)', 'Mercedes-Benz': 'Mercedes F1 team', 'Mercedes-Benz Group': 'Mercedes F1 team', 'Renault': 'Alpine F1 team',
 'Ferrari': 'Ferrari F1 team', 'Exor': 'Ferrari (controlling shareholder)', 'Aston Martin': 'Aston Martin F1 team', 'Aston Martin Lagonda': 'Aston Martin F1 team',
 'Honda': 'Aston Martin power unit', 'Honda Motor': 'Aston Martin power unit', 'Toyota': 'Haas (Toyota Gazoo Racing)', 'Toyota Motor': 'Haas (Toyota Gazoo Racing)',
 'Ford': 'Red Bull Ford Powertrains', 'Ford Motor': 'Red Bull Ford Powertrains', 'General Motors': 'Cadillac F1 team', 'Liberty Media': 'owner of Formula 1',
 'Formula One Group': 'owner of Formula 1', 'Liberty Formula One': 'owner of Formula 1', 'Geely': 'part-owner of Aston Martin', 'Geely Automobile': 'Geely group (Aston Martin shareholder)',
 'Stellantis': 'Maserati / Alfa Romeo F1 links via Ferrari supply (verify)', 'Iveco Group': 'Iveco (Ferrari)', 'CNH Industrial': 'Exor group (Ferrari)',
 'Marriott International': 'Marriott Bonvoy (Mercedes)', 'Hyatt Hotels': 'World of Hyatt', 'Hyatt': 'World of Hyatt', 'Hilton Worldwide': 'Hilton (McLaren)',
 'Arcos Dorados': "McDonald's (Arcos Dorados)", 'Nu Holdings': 'Nu (Mercedes)', 'Nubank': 'Nu (Mercedes)', 'Snap-on': '', 'Sony': '',
}
PARENTS = {k: v for k, v in PARENTS.items() if v and 'verify' not in v}
NAMES = {}; DOMS = {}
for nm, dom, team, role, seasons, src in ROSTER:
    for part in re.split(r'[()]', nm):
        k = loose(part)
        if len(k) >= 3: NAMES.setdefault(k, (nm, team, src))
    d = regdom(dom)
    if d: DOMS.setdefault(d, (nm, team, src))
for p, why in PARENTS.items(): NAMES.setdefault(loose(p), (why, 'parent / owner', 'roster brand: ' + why))
TWO = {'hp': 'HP - Ferrari title partner', 'bp': 'BP / Castrol - Audi and Alpine', '3m': '3M - roster partner', 'nu': 'Nu - Mercedes'}
GENERIC = {'public', 'clear', 'matrix', 'endless', 'floyd', 'mission', 'octave', 'perk', 'neat', 'lumi', 'aleph', 'delphi', 'roland', 'vantage', 'next', 'block', 'ferrari'}
def f1_link(name, domain=''):
    """('', '') or (what the link is, source) for a listed company name / website"""
    k = loose(name)
    if k in TWO: return TWO[k], 'https://rtrsports.com/en/blog/formula-1-sponsors-and-partners/'
    if k in NAMES and (k not in GENERIC or k in ('ferrari', 'next', 'block', 'roland')): return NAMES[k][0] + ' - ' + NAMES[k][1], NAMES[k][2]
    d = regdom(domain or '')
    if d and d in DOMS: return DOMS[d][0] + ' - ' + DOMS[d][1], DOMS[d][2]
    for j in range(len(k) - 1, 5, -1):                    # "Heineken Holding", "Lenovo Group", "Oracle Corporation Japan"
        if k[:j] in NAMES and k[:j] not in GENERIC and len(k) - j <= 14: return NAMES[k[:j]][0] + ' - ' + NAMES[k[:j]][1], NAMES[k[:j]][2]
    return '', ''
if __name__ == '__main__':
    for n in ('Heineken Holding', 'Oracle', 'Alphabet (Google)', 'Diageo', 'Lenovo', 'Apple', 'Pirelli', 'Brembo', 'Next plc', 'Volkswagen', 'HP', 'Uber'): print(n, '->', f1_link(n))
