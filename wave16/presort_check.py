"""Validate pre-sort outputs: same length as input and i = 0..N-1 in order; list files to redo."""
import glob, json, os
bad = []
for f in sorted(glob.glob('/home/user/rg42/wave16/presort/out_*.json')):
    fi = f.replace('/out_', '/in_')
    try:
        o = json.load(open(f)); n = len(json.load(open(fi)))
        ok = len(o) == n and all(int(r[0]) == j and len(r) == 10 for j, r in enumerate(o))
    except Exception:
        ok = False
    if not ok: bad.append(os.path.basename(f)[4:8])
print('checked', len(glob.glob('/home/user/rg42/wave16/presort/out_*.json')), 'bad', bad)
