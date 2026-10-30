"""Fetch dated news headlines (Google News RSS) for each candidate: one query on valuation/funding, one on IPO/acquisition.
Usage: news.py <list.json of [key, brand, domain, country]>. Writes unicorns/news/<safe key>.json; skips keys already fetched."""
import json, os, re, sys, time, urllib.parse, urllib.request, html
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, 'news')
COMMON = set('flex side arena odyssey bolt opn ovo merama ltk kry pigment wonderful human interest nerdio devo story vast ramp rippling notion figure apex atlas nova echo zeta beta alpha harvey glean sierra writer replit cursor clay attio'.split())
def safe(k): return re.sub(r'[^A-Za-z0-9]+', '_', k)[:80]
def q(brand, domain, kind):
    b = f'"{brand}"'
    if len(brand) <= 5 or brand.lower() in COMMON:
        stem = (domain or '').split('.')[0]
        b += f' ({stem} OR startup)' if stem and stem.lower() != brand.lower() else ' startup'
    tail = '(valuation OR raises OR funding OR "Series")' if kind == 'v' else '(IPO OR acquired OR acquires OR acquisition OR "goes public" OR listing OR merger OR bankrupt)'
    return f'{b} {tail}'
def fetch(query):
    url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': query, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'})
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            t = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'ignore')
            out = []
            for it in re.findall(r'<item>(.*?)</item>', t, re.S)[:12]:
                ti = re.search(r'<title>(.*?)</title>', it, re.S); d = re.search(r'<pubDate>(.*?)</pubDate>', it); src = re.search(r'<source[^>]*>(.*?)</source>', it)
                out.append([html.unescape(ti.group(1)) if ti else '', d.group(1)[5:16] if d else '', html.unescape(src.group(1)) if src else ''])
            return out
        except Exception as e:
            time.sleep(2 + attempt * 3)
    return None
def one(row):
    key, brand, domain, country = row
    f = os.path.join(OUT, safe(key) + '.json')
    if os.path.exists(f): return 'skip'
    v = fetch(q(brand, domain, 'v')); time.sleep(0.4); x = fetch(q(brand, domain, 'x'))
    if v is None and x is None: return 'fail'
    json.dump({'key': key, 'brand': brand, 'domain': domain, 'country': country, 'funding_news': v or [], 'status_news': x or []}, open(f, 'w'))
    time.sleep(0.4); return 'ok'
if __name__ == '__main__':
    rows = json.load(open(sys.argv[1])); res = {}
    with ThreadPoolExecutor(3) as ex:
        for i, r in enumerate(ex.map(one, rows)):
            res[r] = res.get(r, 0) + 1
            if i % 100 == 0: print(i, res, flush=True)
    print('done', res)
