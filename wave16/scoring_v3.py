"""Sponsorship Priority Score (0-100) = F1 Fit (60) + Financial Capacity (40).
F1 fit: audience 20, commercial synergies 20, brand alignment 10, international relevance 10.
Financial capacity: revenue & scale 20, valuation & funding 10, other credible indicators 10.
Researched brands use the research agents' evidence-based component scores, rescaled from the old 50/50 sheet.
Everyone else gets a PRELIMINARY score from company-specific database evidence (Clay description, LinkedIn industry,
staff, listing, country, Clay revenue band, Apollo funding) blended with the knowledge pre-sort where one exists."""
import re

# sector priors (audience, synergy, alignment) on 0-1; company-specific signals move them
PRIOR = {
 'Automotive & Mobility': (.8, .8, .9), 'Aerospace, Defence & Space': (.5, .7, .9), 'Airlines & Air Travel': (.8, .7, .6),
 'Travel, Hotels & Leisure': (.8, .7, .6), 'Gambling & Gaming Venues': (.6, .5, .4), 'Sports, Fitness & Events': (.8, .7, .7),
 'Video Games & Esports': (.8, .7, .7), 'Media, Entertainment & Publishing': (.7, .6, .5), 'Telecommunications': (.6, .8, .7),
 'Semiconductors & Electronics': (.6, .8, .9), 'Software, Internet & AI': (.6, .8, .8), 'IT Services & Consulting': (.6, .7, .6),
 'Banking & Lending': (.6, .6, .5), 'Insurance': (.5, .5, .4), 'Investment & Capital Markets': (.7, .5, .5),
 'Financial Services & Payments': (.6, .6, .6), 'Oil, Gas & Fuels': (.4, .6, .5), 'Utilities & Renewable Energy': (.4, .6, .6),
 'Mining & Metals': (.3, .4, .4), 'Chemicals & Materials': (.3, .6, .6), 'Industrial Machinery & Equipment': (.4, .6, .7),
 'Shipping, Maritime & Shipbuilding': (.3, .5, .4), 'Logistics & Transportation': (.4, .7, .5), 'Construction & Engineering': (.3, .4, .4),
 'Building Products & Materials': (.3, .4, .4), 'Real Estate': (.5, .4, .4), 'Home & Furniture': (.5, .4, .4),
 'Luxury, Jewellery & Watches': (.9, .7, .9), 'Beauty & Personal Care': (.7, .6, .6), 'Fashion, Apparel & Footwear': (.7, .6, .6),
 'Food & Beverage': (.7, .6, .4), 'Alcoholic Drinks': (.7, .6, .5), 'Tobacco & Nicotine': (.3, .2, .2), 'Consumer Products': (.6, .5, .4),
 'Retail & E-commerce': (.6, .5, .4), 'Pharma & Biotech': (.3, .3, .4), 'Medical Devices & Diagnostics': (.3, .4, .6),
 'Healthcare Services': (.2, .2, .2), 'Agriculture & Agribusiness': (.2, .3, .3), 'Packaging & Printing': (.2, .4, .3),
 'Environmental & Waste Services': (.2, .4, .4), 'Security Services': (.3, .4, .4), 'Staffing & HR': (.3, .4, .3),
 'Marketing, Advertising & PR': (.4, .5, .4), 'Professional & Business Services': (.5, .5, .4), 'Education & Training': (.2, .2, .2),
 'Government, Non-profit & Associations': (.1, .1, .1), 'Diversified & Other': (.3, .3, .3)}
K = lambda p: re.compile(p, re.I)
PREMIUM = K(r'luxury|premium|high-end|prestig|exclusive|five-star|5-star|boutique|designer|haute|couture|fine jewel|watchmak|yacht|private jet|supercar|wealth management|private bank|first[- ]class')
CONSUMER = K(r'\bconsumers?\b|customers worldwide|shoppers|\bbrand(s)?\b|lifestyle|fashion|beauty|cosmetic|fragrance|hotel|resort|travel|airline|restaurant|beverage|drinks|snack|apparel|footwear|sportswear|gaming|streaming|entertainment|e-commerce|online store|smartphone|consumer electronics|\bfans\b')
B2B = K(r'enterprise|b2b|corporate clients|fortune 500|blue-chip|oems?\b|industrial customers|clients in \d+|businesses worldwide')
TECH = K(r'technolog|innovat|digital|software|\bai\b|artificial intelligence|cloud|data|analytics|semiconductor|robot|automation|r&d|research and development|patent|cutting-edge|advanced|electric vehicle|\bevs?\b|battery|aerospace|precision|high-performance|engineering')
PERF = K(r'performance|precision|speed|fastest|engineering excellence|innovat|cutting-edge|high-tech|motorsport|racing|formula|luxury|premium|world-class|world class|pioneer|leader in')
GLOBAL = K(r'global|worldwide|international|multinational|\b\d{2,3}\+? countries|continents|offices in|presence in|across the world|world\'s|world leader|export')
LOCAL = K(r'\blocal\b|regional|community|county|municipal|family-owned|in the (city|town) of|serving the .{0,40} area|statewide|nationwide in')
NEG = K(r'\bhospital\b|\bclinic\b|\bschool\b|\buniversity\b|\bchurch\b|\bcharity\b|non-?profit|association|cooperative|co-op\b|municipal|government|ministry|public sector agency')
F1MKT = {'United States', 'United Kingdom', 'Germany', 'Italy', 'France', 'Netherlands', 'Spain', 'Japan', 'China', 'Saudi Arabia',
         'United Arab Emirates', 'Qatar', 'Bahrain', 'Singapore', 'Australia', 'Brazil', 'Mexico', 'Canada', 'Austria', 'Belgium',
         'Hungary', 'Monaco', 'Switzerland', 'Azerbaijan', 'South Korea', 'India', 'Sweden', 'Denmark', 'Norway', 'Finland', 'Ireland', 'Hong Kong', 'Taiwan'}
BIG = {'1,001-5,000', '5,001-10,000', '10,001+'}
clip = lambda x: max(0.0, min(1.0, x))

def prog_fit(sector, desc, name, size, typ, country):
    t = f'{name} {desc or ""}'
    a, s, l = PRIOR.get(sector, PRIOR['Diversified & Other'])
    neg = bool(NEG.search(t))
    a += .15 * bool(PREMIUM.search(t)) + .10 * bool(CONSUMER.search(t)) + .05 * (size in BIG) - .2 * neg
    s += .15 * bool(TECH.search(t)) + .05 * bool(CONSUMER.search(t) or B2B.search(t)) - .2 * neg
    l += .20 * bool(PERF.search(t)) - .2 * neg
    i = .3 + .3 * bool(GLOBAL.search(t)) + .2 * (size in ('5,001-10,000', '10,001+')) + .1 * (typ == 'Public Company') \
        + .1 * (country in F1MKT) - .2 * bool(LOCAL.search(t))
    return clip(a), clip(s), clip(l), clip(i)

REV20 = {'75M-200M': 6, '200M-500M': 9, '200M-1B': 10, '500M-1B': 12, '500M+': 12, '1B+': 15, '1B-10B': 15, '10B-100B': 18, '100B-1T': 20, '': 5}
BANDTXT = {'': 'USD 75M+ (Clay search filter)'}

def prog_fin(band, funding100, public, size, t_scale='', t_kind=''):
    rev = REV20.get(band, 5)
    if t_kind == 'real' and t_scale == 'large': rev = max(rev, 15)
    if t_scale == 'small': rev = min(rev, 6)
    if t_kind == 'division': rev = min(rev, 9)          # Clay band on a division page often reflects the parent
    cap = 2 + 3 * bool(funding100) + 2 * bool(public)
    oth = 3 + 2 * bool(public) + {'10,001+': 3, '5,001-10,000': 2, '1,001-5,000': 1}.get(size, 0)
    return rev, min(cap, 10), min(oth, 10)

def gi(d, k, default=0):
    try: return int(float(d.get(k, default)))
    except Exception: return default

def researched(v):
    """old 50/50 components -> 60/40"""
    aud = round(gi(v, 'audience') * 20 / 15); syn = min(20, gi(v, 'synergy') + gi(v, 'category'))
    aln = gi(v, 'alignment'); itl = min(10, gi(v, 'international') * 2)
    rev = round(gi(v, 'revenue_scale') * 20 / 15); cap = gi(v, 'capital'); oth = round((gi(v, 'profitability_score', 5) + gi(v, 'marketing', 3)) * 10 / 25)
    return [min(20, aud), syn, min(10, aln), itl], [min(20, rev), min(10, cap), min(10, oth)]

def preliminary(prog, presort=None, tri_fit=None, w_ps=.65, w_tri=.5):
    a, s, l, i = prog
    if presort:                       # new pre-sort: four 0-4 sub-scores
        pa, pss, pl, pi = [x / 4 for x in presort]
        a, s, l, i = [w_ps * p + (1 - w_ps) * q for p, q in ((pa, a), (pss, s), (pl, l), (pi, i))]
    elif tri_fit is not None:         # earlier pre-sort: one 0-4 fit judgement
        f = tri_fit / 4
        a, s, l = [w_tri * f + (1 - w_tri) * q for q in (a, s, l)]
    return [round(a * 20), round(s * 20), round(l * 10), round(i * 10)]

def prog_fit_df(df):
    """vectorised prog_fit over a DataFrame with sector, description, name, size, type, country -> (a, s, l, i) arrays"""
    import numpy as np
    t = (df['name'].fillna('') + ' ' + df['description'].fillna('')).astype(str)
    f = {k: t.str.contains(rx, regex=True).to_numpy() for k, rx in
         (('prem', PREMIUM), ('cons', CONSUMER), ('b2b', B2B), ('tech', TECH), ('perf', PERF), ('glob', GLOBAL), ('loc', LOCAL), ('neg', NEG))}
    pr = np.array([PRIOR.get(s, PRIOR['Diversified & Other']) for s in df['sector']])
    big = df['size'].isin(BIG).to_numpy(); vbig = df['size'].isin(['5,001-10,000', '10,001+']).to_numpy()
    pub = (df['type'] == 'Public Company').to_numpy(); mkt = df['country'].isin(F1MKT).to_numpy()
    a = pr[:, 0] + .15 * f['prem'] + .10 * f['cons'] + .05 * big - .2 * f['neg']
    s = pr[:, 1] + .15 * f['tech'] + .05 * (f['cons'] | f['b2b']) - .2 * f['neg']
    l = pr[:, 2] + .20 * f['perf'] - .2 * f['neg']
    i = .3 + .3 * f['glob'] + .2 * vbig + .1 * pub + .1 * mkt - .2 * f['loc']
    return [np.clip(x, 0, 1) for x in (a, s, l, i)]
