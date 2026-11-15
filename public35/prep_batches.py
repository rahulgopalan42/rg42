"""Writes the input files for the research passes on companies that still need one.
  prep_batches.py classify [per file] [again]   classify/in_NN.txt for companies in either universe with no sector yet
                                        ('again' also re-does those left without a sector before sectors 36-46 were added)
  prep_batches.py enrich [per file]     enrich/in_NN.jsonl for companies that pass the screen but have no profile yet
Numbering continues after the files that already exist."""
import glob, gzip, html, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build
from qualify import fm
def nxt(pattern):
    n = [int(re.search(r'_(\d+)\.', os.path.basename(f)).group(1)) for f in glob.glob(os.path.join(H, pattern))]
    return max(n) + 1 if n else 1
def universe():
    U = {c['sym']: c for c in json.load(gzip.open(os.path.join(H, 'data', 'universe.json.gz'), 'rt'))}
    U.update({c['sym']: c for c in json.load(gzip.open(os.path.join(H, 'data', 'universe2.json.gz'), 'rt')) if c['sym'] not in U})
    return U
cmd = sys.argv[1]; per = int(sys.argv[2]) if len(sys.argv) > 2 else (900 if cmd == 'classify' else 120)
if cmd == 'classify':
    U = universe(); done = set()
    for f in glob.glob(os.path.join(H, 'classify', 'out_*.txt')):
        for line in open(f):
            p = line.strip().split('|')
            if len(p) == 2: done.add(p[0])
    code = {}
    for f in sorted(glob.glob(os.path.join(H, 'classify', 'out_*.txt'))):
        for line in open(f):
            p = line.strip().split('|')
            if len(p) == 2: code[p[0]] = p[1].strip()
    def worth(c):                                      # could pass at least one sector's capacity test
        rev = c.get('revenue') or 0; pt = c.get('earnings') or 0; cash = c.get('cash') or 0; mc = c.get('mcap') or 0
        return rev >= 1.87e8 or pt >= 2e8 or cash >= 3.33e8 or mc >= 5e9 or (not rev and not pt and mc >= 1e9)
    again = 'again' in sys.argv                         # also re-do companies that got no sector before sectors 36-46 existed
    todo = sorted([c for s, c in U.items() if s not in done or (again and code.get(s) in ('00', '??') and c['country'] != 'Russia' and worth(c))], key=lambda c: -(c.get('revenue') or 0)); n0 = nxt('classify/in_*.txt')
    import random; random.Random(7).shuffle(todo)          # mix markets and sizes across files
    for i in range(0, len(todo), per):
        with open(os.path.join(H, 'classify', f'in_{n0 + i // per:02d}.txt'), 'w', encoding='utf-8') as fh:
            for c in todo[i:i + per]:
                name = re.sub(r'[\s|]+', ' ', html.unescape(c['name'])).strip(); sa = c.get('sa') or {}
                hint = f"revenue {fm(c.get('revenue')) or 'n/a'}, market value {fm(c.get('mcap')) or 'n/a'}" + (f", listed on {sa['exchange']}" if sa else '')
                if not sa: hint = ','.join(c.get('cats') or [])             # first universe: the database categories and SIC industry are the hints
                fh.write(f"{c['sym']} | {name} | {c['country']} | {hint} | {((c.get('sec') or {}).get('sicd') or '').title()} | {(c.get('clay') or {}).get('industry', '')}\n")
    print(len(todo), 'companies to classify in', (len(todo) + per - 1) // per, 'files starting at', n0)
else:
    A = build.assemble(); U = A['U']; cls = {}
    for f in sorted(glob.glob(os.path.join(H, 'classify', 'out_*.txt'))):
        for line in open(f):
            p = line.strip().split('|')
            if len(p) == 2: cls[p[0]] = p[1].strip()
    # a sector that is already over the 400 cap: skip a company that could not reach the current 400th score even with a good profile
    from sectors35 import SECTORS
    from qualify import financials, capacity, cap_score
    cutoff = {c: min(r['score'] for r in A['bysec'][c]) for c, n in A['cut'].items() if n > 0}
    def best_case(s):
        code = cls[s]; f = financials(U[s], SECTORS[code]['grp']); k = capacity(f, code)
        return 0.6 * (0.25 * SECTORS[code]['fit'] * 10 + 0.5 * 60 + 0.25 * 80) + 0.4 * cap_score(k, f)          # relevance 3, international reach
    skip = [s for s in A['missing'] if cls[s] in cutoff and best_case(s) < cutoff[cls[s]]]
    print('skipped (sector over the cap and the company could not reach the cut-off):', len(skip), {c: sum(1 for s in skip if cls[s] == c) for c in cutoff})
    todo = sorted([s for s in A['missing'] if s not in set(skip)], key=lambda s: (cls[s], -(U[s].get('mcap') or 0))); n0 = nxt('enrich/in_*.jsonl')
    for i in range(0, len(todo), per):
        with open(os.path.join(H, 'enrich', f'in_{n0 + i // per:02d}.jsonl'), 'w', encoding='utf-8') as fh:
            for s in todo[i:i + per]:
                c = U[s]; sec = c.get('sec') or {}; cl = c.get('clay') or {}; sa = c.get('sa') or {}
                hq = f"{sec['city'].title()}, {sec.get('state', '')}" if sec.get('city') else cl.get('city', '')
                hints = '; '.join(x for x in [','.join(c.get('cats') or []), (sec.get('sicd') or '').title(), cl.get('industry', ''), ('listed on ' + sa['exchange']) if sa else ''] if x)
                fh.write(json.dumps({'sym': s, 'name': re.sub(r'\s+', ' ', html.unescape(c['name'])).strip(), 'country': c['country'], 'sector': cls[s], 'hq_hint': hq, 'hints': hints,
                                     'revenue': fm(c.get('revenue')) if c.get('revenue') else '', 'market_cap': fm(c.get('mcap')) if c.get('mcap') else ''}, ensure_ascii=False) + '\n')
    print(len(todo), 'companies to profile in', (len(todo) + per - 1) // per, 'files starting at', n0)
