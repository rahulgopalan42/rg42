"""Wider universe: the public exchange lists on stockanalysis.com (ticker, company name, market cap and revenue in the
exchange's currency, 500 rows a page). The first source (companiesmarketcap.com, 11,396 companies) is thin for Asia, so
this pulls every home-market exchange in full. Cross-listing venues (Frankfurt, Stuttgart, OTC ...) are left out.
Usage: fetch_lists.py <raw dir>      (one request every 1.2 s, declared user agent; writes <raw>/lists/<code>_<page>.html)"""
import html, json, os, re, sys, time, urllib.request
RAW = sys.argv[1]; D = os.path.join(RAW, 'lists'); os.makedirs(D, exist_ok=True)
UA = 'research-client/1.0 (listed-company research)'
SKIP = {'OTC', 'FRA', 'BST', 'MUN', 'DUSE', 'HAM', 'LUX', 'CHIX', 'BCBA', 'TSXV', 'CSE', 'NEO', 'AQU', 'NGM', 'XSAT', 'XKON', 'SGXC', 'XNGO', 'FKSE', 'SPSE', 'NSX', 'MOEX', 'UKR',
        'BUL', 'CCSE', 'ZMSE', 'BDB', 'PEX', 'JMSE', 'TTSE', 'MUSE', 'BRVM', 'NMSE', 'BSM', 'DAR', 'LUSE', 'UGSE', 'MAL', 'GHSE', 'COSE', 'DSE', 'HNX', 'BELEX', 'ZSE', 'CYS', 'MSE',
        'LJSE', 'BSSE', 'RSE', 'VSE', 'TAL', 'KASE', 'BVMT', 'NASE', 'ASE', 'BVL', 'VIE'}
def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r: return r.read().decode('utf-8', 'replace')
idx = os.path.join(D, 'index.html')
if not os.path.exists(idx): open(idx, 'w', encoding='utf-8').write(get('https://stockanalysis.com/list/exchanges/')); time.sleep(1.2)
ex = []
for r in re.findall(r'<tr[^>]*>(.*?)</tr>', open(idx, encoding='utf-8').read(), re.S):
    c = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]; l = re.findall(r'href="(/list/[^"]+)"', r)
    if c and l and c[2] not in SKIP and c[4].replace(',', '').isdigit(): ex.append({'path': l[0], 'name': c[0], 'country': c[1], 'code': c[2], 'cur': c[3], 'n': int(c[4].replace(',', ''))})
json.dump(ex, open(os.path.join(D, 'exchanges.json'), 'w'), indent=0)
print(len(ex), 'exchanges,', sum(e['n'] for e in ex), 'stocks,', sum((e['n'] + 499) // 500 for e in ex), 'pages', flush=True)
for e in sorted(ex, key=lambda e: -e['n']):
    for p in range(1, (e['n'] + 499) // 500 + 1):
        f = os.path.join(D, f"{e['code']}_{p}.html")
        if os.path.exists(f) and os.path.getsize(f) > 20000: continue
        try: open(f, 'w', encoding='utf-8').write(get('https://stockanalysis.com' + e['path'] + (f'?page={p}' if p > 1 else ''))); print(e['code'], p, flush=True)
        except Exception as x: print('FAIL', e['code'], p, x, flush=True)
        time.sleep(1.2)
print('done', flush=True)
