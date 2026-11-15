"""Merge the downloaded data into one table of listed companies: public35/data/universe.json.gz
 - companiesmarketcap.com CSVs: market cap, revenue (TTM), earnings (TTM), operating margin, cash, debt, employees, categories
 - SEC EDGAR (US filers, joined on ticker): FY2025 / FY2024 revenue, operating income, D&A, operating cash flow, capex,
   advertising / marketing expense, SIC industry, business address, website, fiscal year end
 - Clay company exports already in the repo (wave15/clay_export_*.tsv): HQ city and LinkedIn industry, joined on name + country
Usage: build_universe.py <raw dir>"""
import csv, glob, gzip, json, os, re, sys
from collections import defaultdict
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); RAW = sys.argv[1]
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose
def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None
U = {}
for r in csv.DictReader(open(os.path.join(RAW, 'cmc', 'rank_mcap.csv'), encoding='utf-8')):
    U[r['Symbol']] = {'sym': r['Symbol'], 'name': r['Name'], 'country': r['country'], 'mcap': num(r['marketcap']), 'cats': []}
for key, col in (('revenue', 'revenue_ttm'), ('earnings', 'earnings_ttm'), ('opmargin', None), ('cash', None), ('debt', None), ('employees', None), ('assets', None)):
    f = os.path.join(RAW, 'cmc', f'rank_{key}.csv')
    if not os.path.exists(f): continue
    rows = list(csv.DictReader(open(f, encoding='utf-8'))); c = col or [k for k in rows[0] if k not in ('Rank', 'Name', 'Symbol', 'price (USD)', 'country')][0]
    for r in rows:
        if r['Symbol'] in U: U[r['Symbol']][key] = num(r[c])
for f in sorted(glob.glob(os.path.join(RAW, 'cmc', 'cat_*.csv'))):
    cat = os.path.basename(f)[4:-4]
    try: rows = list(csv.DictReader(open(f, encoding='utf-8')))
    except Exception: continue
    for r in rows:
        if r.get('Symbol') in U: U[r['Symbol']]['cats'].append(cat)
# ---- SEC
S = os.path.join(RAW, 'sec'); fr = defaultdict(dict)
def frame(tag, y):
    f = os.path.join(S, f'{tag}_{y}.json')
    return json.load(open(f))['data'] if os.path.exists(f) else []
for y in ('CY2025', 'CY2024'):
    for tag in ('Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax', 'RevenuesNetOfInterestExpense'):
        for x in frame(tag, y):
            k = 'rev' + y[-2:]
            if x['val'] and x['val'] > fr[x['cik']].get(k, 0): fr[x['cik']][k] = x['val']; fr[x['cik']]['end' + y[-2:]] = x['end']; fr[x['cik']]['accn' + y[-2:]] = x['accn']
    for tag, k in (('OperatingIncomeLoss', 'opinc'), ('IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'pretax'), ('NetIncomeLoss', 'netinc'),
                   ('DepreciationDepletionAndAmortization', 'da'), ('DepreciationAndAmortization', 'da2'), ('NetCashProvidedByUsedInOperatingActivities', 'cfo'),
                   ('PaymentsToAcquirePropertyPlantAndEquipment', 'capex'), ('AdvertisingExpense', 'adv'), ('MarketingAndAdvertisingExpense', 'mktadv'), ('MarketingExpense', 'mkt'),
                   ('SellingAndMarketingExpense', 'sellmkt')):
        for x in frame(tag, y): fr[x['cik']][k + y[-2:]] = x['val']
tick = {}
for f in glob.glob(os.path.join(S, 'subs', '*.json')):
    d = json.load(open(f))
    for t in d.get('tickers') or []: tick.setdefault(t.upper().replace('.', '-'), d)
nsec = 0
for sym, c in U.items():
    d = tick.get(sym.upper().replace('.', '-'))
    if not d or '.' in sym and c['country'] != 'United States': continue
    x = fr.get(int(d['cik']), {})
    c['sec'] = {'cik': int(d['cik']), 'name': d['name'], 'sic': d.get('sic'), 'sicd': d.get('sicDescription'), 'city': d.get('city'), 'state': d.get('state'),
                'web': d.get('website'), 'fye': d.get('fiscalYearEnd'), 'exch': (d.get('exchanges') or [''])[0], **x}
    nsec += 1
# ---- Clay exports: HQ city and LinkedIn industry
clay = {}
CN = {'usa': 'united states', 'uk': 'united kingdom', 'korea': 'south korea', 'uae': 'united arab emirates'}
for f in sorted(glob.glob(os.path.join(R, 'wave15', 'clay_export_*.tsv'))):
    with open(f, encoding='utf-8', errors='ignore') as fh:
        hdr = fh.readline().rstrip('\n').split('\t')
        for line in fh:
            p = line.rstrip('\n').split('\t')
            if len(p) < len(hdr): continue
            r = dict(zip(hdr, p)); k = (loose(r['name']), r['country'].lower())
            if k[0] and (k not in clay or r['type'] == 'Public Company'): clay[k] = r
nclay = 0
for c in U.values():
    r = clay.get((loose(c['name']), CN.get(c['country'].lower(), c['country'].lower())))
    if r: c['clay'] = {'city': r['locality'], 'industry': r['industry'], 'domain': r['domain'], 'type': r['type'], 'size': r['size']}; nclay += 1
os.makedirs(os.path.join(H, 'data'), exist_ok=True)
json.dump(list(U.values()), gzip.open(os.path.join(H, 'data', 'universe.json.gz'), 'wt'), ensure_ascii=False)
q = [c for c in U.values() if (c['mcap'] or 0) >= 2.5e8]
print('companies', len(U), '| mcap >= 250M', len(q), '| with revenue', sum(1 for c in q if c.get('revenue')), '| revenue >= 100M', sum(1 for c in q if (c.get('revenue') or 0) >= 1e8),
      '| SEC joined', nsec, '| Clay joined', nclay, '| with a category', sum(1 for c in q if c['cats']))
