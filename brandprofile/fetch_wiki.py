"""Reference text for the cross-check: the English Wikipedia summary of a brand, where an article with that title exists
(Wikipedia's public REST summary endpoint; a few requests a second, declared user agent). Not every brand has an article,
and an article with the same title may be a different company: the checker decides from the text.
Usage: fetch_wiki.py <ids file> <out.jsonl> [names.json: id -> proper name from the first pass]     (resumes)"""
import gzip, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, threading, queue
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
def summary(title):
    url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(title.replace(' ', '_'), safe='') + '?redirect=true'
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r: d = json.loads(r.read().decode('utf-8'))
            if d.get('type') != 'standard': return None
            return {'title': d.get('title', ''), 'what': d.get('description', ''), 'text': re.sub(r'\s+', ' ', d.get('extract', '')).strip()[:650]}
        except urllib.error.HTTPError as x:
            if x.code == 404: return None
            time.sleep(min(int(x.headers.get('retry-after') or 20), 90) + 1 if x.code == 429 else 4)
        except Exception: time.sleep(4)
    return 'error'
def variants(r):
    v = []
    for n in (NAMES.get(r['id'], ''), r['brand']):
        n = re.sub(r'\.{2,}\s*$', '', n).strip()
        if n and not r['brand'].rstrip().endswith('..') or n == NAMES.get(r['id'], ''):
            for t in (n, re.sub(r'\s*\([^)]*\)', '', n).strip()):
                if t and t not in v: v.append(t)
    return v[:3]
q = queue.Queue(); lock = threading.Lock(); fh = open(out, 'a', encoding='utf-8')
for r in todo: q.put(r)
def work():
    while True:
        try: r = q.get_nowait()
        except queue.Empty: return
        hits = []; err = False
        for t in variants(r) + [x + ' (company)' for x in variants(r)[:1]]:
            s = summary(t); time.sleep(0.15)
            if s == 'error': err = True; break
            if s and s['title'] not in [h['title'] for h in hits]: hits.append(s)
            if len(hits) >= 2: break
        with lock:
            if not err: fh.write(json.dumps({'id': r['id'], 'brand': r['brand'], 'wiki': hits}, ensure_ascii=False) + '\n'); fh.flush()
            else: print('FAIL', r['id'], flush=True)
th = [threading.Thread(target=work) for _ in range(5)]
for t in th: t.start()
for t in th: t.join()
print('done', flush=True)
