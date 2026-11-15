"""SEC EDGAR official APIs (data.sec.gov): XBRL 'frames' = one reported figure for every filer for a year, and
'submissions' = each filer's tickers, exchange, SIC industry, business address, website and fiscal year end.
Usage: fetch_sec.py <raw dir> frames | subs      (under 8 requests a second, declared user agent)"""
import json, os, sys, time, urllib.request
RAW = sys.argv[1]; D = os.path.join(RAW, 'sec'); os.makedirs(os.path.join(D, 'subs'), exist_ok=True)
UA = 'listed-company-research/1.0 (automated research client)'
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(req, timeout=60) as r: return r.read()
TAGS = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax', 'RevenuesNetOfInterestExpense',
        'OperatingIncomeLoss', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'NetIncomeLoss',
        'DepreciationDepletionAndAmortization', 'DepreciationAndAmortization', 'NetCashProvidedByUsedInOperatingActivities',
        'PaymentsToAcquirePropertyPlantAndEquipment', 'AdvertisingExpense', 'MarketingAndAdvertisingExpense', 'MarketingExpense', 'SellingAndMarketingExpense']
if sys.argv[2] == 'frames':
    for y in ('CY2025', 'CY2024'):
        for t in TAGS:
            f = os.path.join(D, f'{t}_{y}.json')
            if os.path.exists(f): continue
            try: b = get(f'https://data.sec.gov/api/xbrl/frames/us-gaap/{t}/USD/{y}.json'); open(f, 'wb').write(b); print(t, y, len(b), flush=True)
            except Exception as e: print('FAIL', t, y, e, flush=True)
            time.sleep(0.4)
    for t, cur in [('Revenue', c) for c in ('USD', 'EUR', 'CNY', 'JPY', 'GBP', 'CAD', 'INR', 'BRL', 'KRW', 'TWD', 'CHF', 'MXN', 'ILS', 'AUD', 'HKD', 'SEK', 'DKK', 'NOK', 'ZAR', 'ARS')]:
        for y in ('CY2025', 'CY2024'):
            f = os.path.join(D, f'ifrs_{t}_{cur}_{y}.json')
            if os.path.exists(f): continue
            try: b = get(f'https://data.sec.gov/api/xbrl/frames/ifrs-full/{t}/{cur}/{y}.json'); open(f, 'wb').write(b); print('ifrs', cur, y, len(b), flush=True)
            except Exception as e: print('none', cur, y, e, flush=True)
            time.sleep(0.4)
else:
    from concurrent.futures import ThreadPoolExecutor
    ciks = [int(x) for x in open(os.path.join(D, 'ciks.txt')).read().split()]
    todo = [c for c in ciks if not os.path.exists(os.path.join(D, 'subs', f'{c}.json'))]
    def one(c):
        try:
            d = json.loads(get(f'https://data.sec.gov/submissions/CIK{c:010d}.json'))
            keep = {k: d.get(k) for k in ('cik', 'name', 'tickers', 'exchanges', 'sic', 'sicDescription', 'website', 'fiscalYearEnd', 'category', 'stateOfIncorporation', 'entityType')}
            b = (d.get('addresses') or {}).get('business') or {}
            keep['city'] = b.get('city'); keep['state'] = b.get('stateOrCountryDescription')
            json.dump(keep, open(os.path.join(D, 'subs', f'{c}.json'), 'w'))
        except Exception as e: print('FAIL', c, e, flush=True)
        time.sleep(0.5)                                    # 4 workers x (0.5 s pause + request time) = about 5 requests a second
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, todo))
    print('done', len(todo))
