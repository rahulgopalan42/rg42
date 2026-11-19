"""Checks one profile output file against its input.  Usage: np_check.py <in.jsonl> <out.jsonl> [extra]"""
import json, sys
inp = [json.loads(l)['sym'] for l in open(sys.argv[1], encoding='utf-8') if l.strip()]; out = []; bad = []
for i, l in enumerate(open(sys.argv[2], encoding='utf-8'), 1):
    if not l.strip(): continue
    try: out.append(json.loads(l))
    except Exception: bad.append(f'line {i}: not valid JSON')
syms = [d.get('sym') for d in out]
if syms != inp: bad.append(f'symbols differ from the input: {len(syms)} lines out, {len(inp)} in; first mismatch at ' + str(next((i for i, (a, b) in enumerate(zip(syms, inp)) if a != b), min(len(syms), len(inp)))))
need = ('sports', 'signals', 'b2b', 'act') if len(sys.argv) > 3 else ('sector', 'hq', 'desc', 'reach', 'markets', 'rationale', 'rel', 'f1', 'flags', 'conf', 'sports', 'signals', 'b2b', 'act')
for d in out:
    miss = [k for k in need if k not in d]
    if miss: bad.append(f"{d.get('sym')}: missing {miss}")
    if 'desc' in need and not 8 <= len(str(d.get('desc', '')).split()) <= 22: bad.append(f"{d.get('sym')}: desc has {len(str(d.get('desc', '')).split())} words")
    if 'reach' in need and d.get('reach') not in ('Domestic', 'Regional', 'International', 'Global'): bad.append(f"{d.get('sym')}: reach {d.get('reach')!r}")
    for k in ('b2b', 'act') + (('rel',) if 'rel' in need else ()):
        if d.get(k) not in (1, 2, 3, 4, 5): bad.append(f"{d.get('sym')}: {k} {d.get(k)!r}")
print('OK' if not bad else 'PROBLEMS:\n' + '\n'.join(bad[:40]))
