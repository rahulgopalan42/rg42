"""Download the public CSV rankings from companiesmarketcap.com (the site's own 'download CSV' feature): market cap,
revenue, earnings, employees, operating margin, cash, debt, assets, and every industry category list.
Usage: fetch_cmc.py <raw dir>   (skips files already downloaded; ~1 request per 1.3 s)"""
import os, re, sys, time, urllib.request
RAW = sys.argv[1]; os.makedirs(os.path.join(RAW, 'cmc'), exist_ok=True)
UA = 'research-client/1.0 (listed-company research)'
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r: return r.read()
RANK = {'mcap': '/', 'revenue': '/largest-companies-by-revenue/', 'earnings': '/most-profitable-companies/',
        'employees': '/largest-companies-by-number-of-employees/', 'opmargin': '/top-companies-by-operating-margin/',
        'cash': '/companies-with-the-highest-cash-on-hand/', 'debt': '/companies-with-the-highest-debt/',
        'netassets': '/top-companies-by-net-assets/', 'assets': '/top-companies-by-total-assets/', 'pe': '/top-companies-by-pe-ratio/',
        'liabilities': '/companies-with-the-highest-liabilities/'}
cats = sorted(set(re.findall(r'href="(/[a-z0-9-]+/largest-[a-z0-9-]+/)"', open(os.path.join(RAW, 'cats.html')).read())))
SKIP = re.compile(r'etf|/(australia|brazil|canada|chile|china|european-union|finland|france|germany|hong-kong|india|indonesia|israel|italy|japan|malaysia|mexico|'
                  r'netherlands|new-zealand|norway|poland|portugal|russia|saudi-arabia|singapore|south-africa|south-korea|spain|sweden|switzerland|taiwan|thailand|turkey|'
                  r'united-kingdom|usa|united-states|uae|qatar|kuwait|egypt|vietnam|philippines|pakistan|argentina|colombia|peru|greece|ireland|belgium|austria|denmark|'
                  r'cac-40|dax|dow-jones|nasdaq-100|sp-500|ftse-100|nikkei-225|hang-seng|euro-stoxx-50|tsx-60|asx-200|smi|ibex-35|[a-z-]*-index)/')
jobs = [('rank_' + k, v) for k, v in RANK.items()] + [('cat_' + c.split('/')[1], c) for c in cats if not SKIP.search(c)]
print(len(jobs), 'lists'); n = 0
for name, path in jobs:
    f = os.path.join(RAW, 'cmc', name + '.csv')
    if os.path.exists(f) and os.path.getsize(f) > 60: continue
    try:
        b = get('https://companiesmarketcap.com' + path + '?download=csv'); open(f, 'wb').write(b); n += 1
        print(name, len(b), flush=True)
    except Exception as e: print('FAIL', name, e, flush=True)
    time.sleep(1.3)
print('done', n)
