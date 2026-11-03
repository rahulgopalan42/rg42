"""Merge the top-up pass (longer rewrites of short descriptions) into screenrec/desc/out_tNN.json.
Only rows whose text actually changed are taken; the original confidence is kept unless the rewrite lowered it to L.
Usage: desc_topup_merge.py <topup dir>   (expects in_N.json / out_N.json there)"""
import json, os, sys, glob
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'desc')
conf = {}
for f in sorted(glob.glob(os.path.join(D, 'out_[0-9]*.json'))):
    for r in json.load(open(f)): conf[r[0]] = r[2]
for f in sorted(glob.glob(os.path.join(sys.argv[1], 'out_*.json'))):
    n = os.path.basename(f)[4:-5]
    o = json.load(open(f)); i = json.load(open(os.path.join(sys.argv[1], f'in_{n}.json')))
    assert [r[0] for r in o] == [r[0] for r in i], f'id order differs in {f}'
    out = [[r[0], r[1], 'L' if r[2] == 'L' else conf.get(r[0], r[2])] for r, x in zip(o, i) if r[1].strip() and r[1].strip() != x[6].strip()]
    json.dump(out, open(os.path.join(D, f'out_t{int(n):02d}.json'), 'w'), ensure_ascii=False)
    print(f, 'changed rows', len(out), 'of', len(o))
