"""Copy finished description batches from the scratch folder into screenrec/desc/ (only complete, valid ones:
same row count and id order as the input, 3 fields per row, conf H/M/L)."""
import json, os, sys, glob, shutil
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'desc')
SRC = sys.argv[1]
for f in sorted(glob.glob(os.path.join(SRC, 'out_*.json'))):
    n = os.path.basename(f); dst = os.path.join(D, n)
    try:
        o = json.load(open(f)); i = json.load(open(os.path.join(D, n.replace('out_', 'in_'))))
        ok = [r[0] for r in o] == [r[0] for r in i] and all(len(r) >= 3 and r[1] and r[2] in ('H', 'M', 'L') for r in o)
    except Exception as e: ok = False
    if ok and (not os.path.exists(dst) or open(dst).read() != open(f).read()):
        shutil.copy(f, dst); print('copied', n)
    elif not ok: print('not ready', n)
