"""Public-information evidence gathering without web-tool budgets: for every company in the given input chunks fetch the
homepage (title, meta/og description, h1, first text) with curl and the Wikipedia summary via the public API.
Usage: peek_sites.py score 80 98   -> parents/peek/score_NN.json aligned with parents/score_in/chunk_NN.json
       peek_sites.py verify 1 5    -> parents/peek/verify_NN.json aligned with parents/verify_in/chunk_NN.json"""
import html, json, re, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
R = '/home/user/rg42'
kind, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
def curl(url, limit=600000):
    try:
        out = subprocess.run(['curl', '-sL', '-m', '15', '--max-filesize', str(limit), '-A', 'Mozilla/5.0 (research; SPORTFIVE prospecting)', url],
                             capture_output=True, timeout=25).stdout
        return out.decode('utf-8', 'ignore')
    except Exception: return ''
def strip(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()
def homepage(domain):
    d = re.sub(r'^https?://', '', str(domain or '').strip().lower()).split('/')[0]
    if not d or '.' not in d: return {}
    h = curl('https://' + d) or curl('http://' + d)
    if not h: return {'domain': d, 'error': 'no response'}
    body = re.sub(r'<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', h, flags=re.S | re.I)
    g = lambda p: (re.search(p, h, re.S | re.I) or [None, ''])[1]
    title = strip(g(r'<title[^>]*>(.*?)</title>'))
    desc = html.unescape(g(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)') or g(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+name=["\']description["\']'))
    og = html.unescape(g(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)'))
    h1 = strip(g(r'<h1[^>]*>(.*?)</h1>'))
    text = strip(body)[:700]
    lang = g(r'<html[^>]+lang=["\']([a-zA-Z-]+)')
    return {'domain': d, 'title': title[:200], 'description': desc[:400], 'og': og[:400], 'h1': h1[:200], 'text': text, 'lang': lang}
def wikipedia(name):
    n = re.sub(r'\s*\(.*?\)\s*', ' ', str(name or '')).strip()
    if not n: return {}
    q = urllib.parse.quote(n)
    j = curl(f'https://en.wikipedia.org/w/api.php?action=opensearch&search={q}&limit=1&namespace=0&format=json', 200000)
    try:
        titles = json.loads(j)[1]
    except Exception: return {}
    if not titles: return {}
    t = urllib.parse.quote(titles[0].replace(' ', '_'))
    s = curl(f'https://en.wikipedia.org/api/rest_v1/page/summary/{t}', 200000)
    try:
        d = json.loads(s); return {'wiki_title': d.get('title', ''), 'wiki_desc': d.get('description', ''), 'wiki_extract': (d.get('extract') or '')[:600]}
    except Exception: return {'wiki_title': titles[0]}
def one(row):
    if kind == 'score': name, dom = row[0], row[1]
    else: name, dom = row[1], row[2]
    out = {'name': name}; out.update(homepage(dom)); out.update(wikipedia(name)); return out
for n in range(a, b + 1):
    src = f'{R}/parents/score_in/chunk_{n:02d}.json' if kind == 'score' else f'{R}/parents/verify_in/chunk_{n:02d}.json'
    try: rows = json.load(open(src))
    except FileNotFoundError: continue
    with ThreadPoolExecutor(16) as ex: res = list(ex.map(one, rows))
    json.dump(res, open(f'{R}/parents/peek/{kind}_{n:02d}.json', 'w'), ensure_ascii=False)
    ok = sum(1 for r in res if r.get('title') or r.get('wiki_extract'))
    print(kind, n, len(res), 'rows,', ok, 'with evidence', flush=True)
