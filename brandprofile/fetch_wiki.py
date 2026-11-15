"""Reference text for the cross-check: the two best English Wikipedia matches (title + start of the article) for a brand name,
from Wikipedia's public search API. One request at a time with a pause between requests (the API allows only a slow rate), declared user agent.
Usage: fetch_wiki.py <ids file> <out.jsonl> [pause seconds]     (resumes: ids already in the output are skipped)"""
import gzip, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, threading, queue
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
UA = 'research-client/1.0 (company research)'; PAUSE = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
B = json.load(gzip.open(os.path.join(H, 'data', 'brands.json.gz'), 'rt', encoding='utf-8'))
want = set(l.strip() for l in open(sys.argv[1]) if l.strip()); out = sys.argv[2]
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        try: done.add(json.loads(l)['id'])
        except Exception: pass
todo = [r for r in B if r['id'] in want and r['id'] not in done]
print(len(todo), 'to fetch', flush=True)
def get(name):
    q = re.sub(r'\.{2,}\s*$', '', name).strip()
    q = re.sub(r'\([^)]*\)', ' ', q).strip() or q
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'generator': 'search', 'gsrsearch': q + ' company', 'gsrlimit': 2, 'prop': 'extracts', 'exintro': 1,
          'explaintext': 1, 'exchars': 480, 'exlimit': 2, 'format': 'json', 'redirects': 1})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r: d = json.loads(r.read().decode('utf-8'))
            pages = sorted((d.get('query') or {}).get('pages', {}).values(), key=lambda p: p.get('index', 9))
            return [{'title': p.get('title', ''), 'text': re.sub(r'\s+', ' ', p.get('extract', '')).strip()} for p in pages]
        except urllib.error.HTTPError as x:
            err = str(x); wait = int(x.headers.get('retry-after') or 30) if x.code == 429 else 5
            time.sleep(min(wait, 90) + 1)                      # rate limit: wait as long as the server asks
        except Exception as x:
            err = str(x); time.sleep(5)
    return {'error': err}
q = queue.Queue(); lock = threading.Lock(); fh = open(out, 'a', encoding='utf-8')
for r in todo: q.put(r)
def work():
    while True:
        try: r = q.get_nowait()
        except queue.Empty: return
        res = get(r['brand'])
        with lock:
            if isinstance(res, list): fh.write(json.dumps({'id': r['id'], 'brand': r['brand'], 'wiki': res}, ensure_ascii=False) + '\n'); fh.flush()
            else: print('FAIL', r['id'], res, flush=True)
        time.sleep(PAUSE)
th = [threading.Thread(target=work) for _ in range(1)]
for t in th: t.start()
for t in th: t.join()
print('done', flush=True)
