"""Checks every out/out_NNN.jsonl against in/in_NNN.jsonl.  Usage: validate.py [dir=out]   Prints files that are missing, short or malformed."""
import glob, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); D = sys.argv[1] if len(sys.argv) > 1 else 'out'
src = 'in' if D == 'out' else 'check_in'
ALLOWED = {'reach': {'Domestic', 'Regional', 'International', 'Global'}, 'basis': {'stated', 'known', 'inferred'}, 'conf': {'high', 'medium', 'low'},
           'status': {'private', 'listed', 'subsidiary', 'state-owned', 'non-commercial', 'defunct', 'unknown'}, 'stage': {'commercial', 'pre-revenue', 'project', 'fund', 'non-commercial'}}
SECT = None
def sectors():
    global SECT
    if SECT is None:
        sys.path.insert(0, os.path.join(os.path.dirname(H), 'screenrec')); sys.path.insert(0, os.path.join(os.path.dirname(H), 'parents')); import sectors_cb; SECT = set(sectors_cb.NAMES)
    return SECT
tot = Counter(); bad_files = []; done = 0
for f in sorted(glob.glob(os.path.join(H, src, 'in_*.jsonl'))):
    n = re.search(r'in_(\d+)', f).group(1); o = os.path.join(H, D, f'out_{n}.jsonl')
    ids = [json.loads(l)['id'] for l in open(f, encoding='utf-8') if l.strip()]
    if not os.path.exists(o): tot['missing file'] += 1; continue
    got = []; errs = Counter()
    for line in open(o, encoding='utf-8'):
        if not line.strip(): continue
        try: d = json.loads(line)
        except Exception: errs['bad json'] += 1; continue
        got.append(d.get('id'))
        for k, ok in ALLOWED.items():
            if str(d.get(k, '')).strip() not in ok: errs[f'{k} value'] += 1
        if d.get('sector') not in sectors(): errs['sector value'] += 1
        if d.get('rel') not in (1, 2, 3, 4, 5): errs['rel value'] += 1
        w = len(str(d.get('desc', '')).split())
        if not 10 <= w <= 20: errs['desc length'] += 1
        for k, lo, hi in (('markets', 5, 30), ('rationale', 8, 30)):
            if not lo <= len(str(d.get(k, '')).split()) <= hi: errs[f'{k} length'] += 1
        if not str(d.get('name', '')).strip() or not str(d.get('hq', '')).strip(): errs['name or hq empty'] += 1
    if got != ids:
        miss = len(set(ids) - set(got)); extra = len(set(got) - set(ids)); errs[f'ids differ (missing {miss}, extra {extra}, order {"ok" if sorted(got) == sorted(ids) else "n/a"})'] += 1
    done += 1
    if errs: bad_files.append((n, dict(errs)))
    for k, v in errs.items(): tot[k] += v
print('files done', done, '| problems', dict(tot))
for n, e in bad_files: print(' ', n, e)
