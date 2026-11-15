"""Same output as fetch_wiki.py, but asks Wikipedia's query API for 20 titles per request (far fewer requests).
Usage: fetch_wiki_batch.py <ids file> <out.jsonl> [names.json]     (resumes; declared user agent; one request at a time)"""
import gzip, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
H = os.path.dirname(os.path.abspath(__file__))
UA = 'research-client/1.0 (company research)'
B = json.load(gzip.open(os.path.join(H, 'data', 'brands.json.gz'), 'rt', encoding='utf-8'))
want = set(l.strip() for l in open(sys.argv[1]) if l.strip()); out = sys.argv[2]
NAMES = json.load(open(sys.argv[3], encoding='utf-8')) if len(sys.argv) > 3 else {}
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        try: done.add(json.loads(l)['id'])
        except Exception: pass
todo = [r for r in B if r['id'] in want and r['id'] not in done]
print(len(todo), 'to fetch', flush=True)
def variants(r):
    v = []
    for n in (NAMES.get(r['id'], ''), r['brand']):
        n = re.sub(r'\.{2,}\s*$', '', n).strip()
        if n and (not r['brand'].rstrip().endswith('..') or n == NAMES.get(r['id'], '')):
            for t in (n, re.sub(r'\s*\([^)]*\)', '', n).strip()):
                t = re.sub(r'[\[\]{}|#<>_]', ' ', t).strip()
                if t and t not in v: v.append(t)
    v = v[:3]
    return v + ([v[0] + ' (company)'] if v else [])
def query(titles):
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'formatversion': '2', 'redirects': '1',
        'prop': 'extracts|description|pageprops', 'ppprop': 'disambiguation', 'exintro': '1', 'explaintext': '1', 'exlimit': '20', 'titles': '|'.join(titles)})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40) as r: return json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as x: time.sleep(min(int(x.headers.get('retry-after') or 20), 90) + 1 if x.code == 429 else 5)
        except Exception: time.sleep(5)
    return None
fh = open(out, 'a', encoding='utf-8'); fail = 0
for i in range(0, len(todo), 5):
    grp = todo[i:i + 5]; V = {r['id']: variants(r) for r in grp}; titles = []
    for r in grp:
        for t in V[r['id']]:
            if t not in titles: titles.append(t)
    d = query(titles[:20]) if titles else {'query': {}}
    if d is None or 'query' not in d: fail += len(grp); print('FAIL', [r['id'] for r in grp], flush=True); continue
    q = d['query']; norm = {x['from']: x['to'] for x in q.get('normalized', [])}; red = {x['from']: x['to'] for x in q.get('redirects', [])}
    pages = {p['title']: p for p in q.get('pages', [])}
    for r in grp:
        hits = []
        for t in V[r['id']]:
            t2 = norm.get(t, t); t2 = red.get(t2, t2); p = pages.get(t2)
            if not p or p.get('missing') or p.get('invalid') or 'disambiguation' in (p.get('pageprops') or {}): continue
            text = re.sub(r'\s+', ' ', p.get('extract', '') or '').strip()[:650]
            if text and p['title'] not in [h['title'] for h in hits]: hits.append({'title': p['title'], 'what': p.get('description', ''), 'text': text})
            if len(hits) >= 2: break
        fh.write(json.dumps({'id': r['id'], 'brand': r['brand'], 'wiki': hits}, ensure_ascii=False) + '\n')
    fh.flush(); time.sleep(0.5)
print('done; failed', fail, flush=True)
