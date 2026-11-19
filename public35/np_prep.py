"""New-parameters run (19 Nov 2026): input files for the research passes.
  np_prep.py us <raw dir>     adds US-listed companies missing from the first universe to data/universe3.json.gz (new floor)
  np_prep.py classify [per]   np/classify/in_NN.txt: companies with no usable sector that meet the new entry criteria
Entry criteria (any one): revenue USD 100M+, market value USD 500M+, cash USD 150M+, disclosed marketing spend USD 20M+."""
import glob, gzip, html, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from qualify import fm, financials
from sectors35 import SECTORS
def load(n): 
    p = os.path.join(H, 'data', n)
    return json.load(gzip.open(p, 'rt')) if os.path.exists(p) else []
def norm(s): return re.sub(r'[^a-z0-9]', '', re.sub(r'\b(inc|incorporated|corp|corporation|company|co|ltd|limited|plc|holdings?|group|the|class [abc]|sa|nv|ag|s\.a\.b\. de c\.v\.)\b\.?', '', html.unescape(str(s)).lower()))
MULT = {'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3}
def num(x):
    x = str(x).replace(',', '').replace('$', '').strip(); m = re.fullmatch(r'(-?[\d.]+)([TBMK]?)', x)
    return float(m.group(1)) * MULT.get(m.group(2), 1) if m else None
def entry(c, f=None):
    rev = (f or {}).get('rev') or c.get('revenue') or 0; mc = c.get('mcap') or 0; cash = (f or {}).get('cash') or c.get('cash') or 0; mkt = (f or {}).get('mkt') or 0
    return rev >= 1e8 or mc >= 5e8 or cash >= 1.5e8 or mkt >= 2e7
cmd = sys.argv[1]
if cmd == 'us':
    D = os.path.join(sys.argv[2], 'lists'); U1 = load('universe.json.gz') + load('universe2.json.gz'); syms = {c['sym'] for c in U1}; names = {norm(c['name']) for c in U1}
    rows = {}
    for f in sorted(glob.glob(os.path.join(D, 'NASDAQ_*.html')) + glob.glob(os.path.join(D, 'NYSE_*.html')) + glob.glob(os.path.join(D, 'AMEX_*.html'))):
        t = open(f, encoding='utf-8').read(); ex = os.path.basename(f).split('_')[0]
        th = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<th[^>]*>(.*?)</th>', t, re.S)]
        rank = bool(th) and th[0].startswith('#')
        for r in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S):
            c = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]
            if len(c) < 5: continue
            if rank:
                m = re.match(r'^\S\s+(.*)\s+([A-Z][A-Z.\-]{0,6})$', c[1])
                if not m: continue
                sym, name, mc, rev, ctry = m.group(2), m.group(1), num(c[2]), None, (c[6] if len(c) > 6 else '')
            else: sym, name, mc, rev, ctry = c[1], c[2], num(c[3]), (num(c[6]) if len(c) > 6 else None), ''
            if sym in syms or sym.replace('.', '-') in syms or norm(name) in names: continue
            if not ((mc or 0) >= 5e8 or (rev or 0) >= 1e8): continue
            k = norm(name)
            if k not in rows or (mc or 0) > (rows[k]['mcap'] or 0):          # one line per company: the larger share class
                rows[k] = {'sym': sym, 'name': name, 'country': ctry or 'United States (listing)', 'mcap': mc, 'revenue': rev, 'cats': [], 'src': 'us3',
                           'sa': {'exchange': {'NASDAQ': 'Nasdaq', 'NYSE': 'New York Stock Exchange', 'AMEX': 'NYSE American'}[ex], 'code': ex, 'cur': 'USD', 'fx': 1.0, 'url': 'https://stockanalysis.com/stocks/' + sym.lower().replace('.', '-') + '/'}}
    U3 = [c for c in load('universe3.json.gz') if c.get('src') != 'us3']; have = {c['sym'] for c in U3} | syms
    add = [c for c in rows.values() if c['sym'] not in have]
    json.dump(U3 + add, gzip.open(os.path.join(H, 'data', 'universe3.json.gz'), 'wt'), ensure_ascii=False)
    print('US-listed companies added', len(add), '| third universe now', len(U3) + len(add))
if cmd == 'classify':
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 550
    U = {c['sym']: c for c in load('universe.json.gz')}; U.update({c['sym']: c for c in load('universe2.json.gz') if c['sym'] not in U})
    cls = {}
    for f in sorted(glob.glob(os.path.join(H, 'classify', 'out_*.txt'))):
        for line in open(f):
            p = line.strip().split('|')
            if len(p) == 2: cls[p[0]] = p[1].strip()
    E = set()
    for f in glob.glob(os.path.join(H, 'enrich', 'out_*.jsonl')):
        for l in open(f, encoding='utf-8'):
            try: d = json.loads(l)
            except Exception: continue
            if str(d.get('sector') or '') in SECTORS: E.add(d.get('sym'))
    done = set()
    for f in glob.glob(os.path.join(H, 'np', 'classify', 'in_*.txt')):
        for line in open(f, encoding='utf-8'): done.add(line.split(' | ')[0].strip())
    todo = []
    for sym, c in U.items():                                   # earlier universes: no sector (00 or ??) and no profile that gives one
        if cls.get(sym, '') in SECTORS or sym in E or sym in done: continue
        if c['country'] == 'Russia' or sym.endswith('.ME'): continue
        if entry(c, financials(c, 'ind', None)): todo.append(c)
    n_old = len(todo)
    todo += [c for c in load('universe3.json.gz') if c['sym'] not in done]
    import random; random.Random(11).shuffle(todo)
    n0 = max([int(re.search(r'_(\d+)\.', os.path.basename(f)).group(1)) for f in glob.glob(os.path.join(H, 'np', 'classify', 'in_*.txt'))] or [0]) + 1
    for i in range(0, len(todo), per):
        with open(os.path.join(H, 'np', 'classify', f'in_{n0 + i // per:02d}.txt'), 'w', encoding='utf-8') as fh:
            for c in todo[i:i + per]:
                name = re.sub(r'[\s|]+', ' ', html.unescape(c['name'])).strip(); sa = c.get('sa') or {}
                hint = f"revenue {fm(c.get('revenue')) or 'n/a'}, market value {fm(c.get('mcap')) or 'n/a'}" + (f", listed on {sa['exchange']}" if sa else '')
                extra = ','.join(c.get('cats') or [])
                fh.write(f"{c['sym']} | {name} | {c['country']} | {hint} | {extra} {((c.get('sec') or {}).get('sicd') or '').title()} | {(c.get('clay') or {}).get('industry', '')}\n")
    print('to classify', len(todo), '(earlier universes with no sector:', n_old, ') in', (len(todo) + per - 1) // per, 'files from', n0)
