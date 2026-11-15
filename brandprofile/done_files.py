"""Prints the out files that are complete (same ids, in order, as their input file) and untouched for four minutes. Usage: done_files.py [out|check]"""
import glob, json, os, re, sys, time
H = os.path.dirname(os.path.abspath(__file__)); D = sys.argv[1] if len(sys.argv) > 1 else 'out'; src = 'in' if D == 'out' else 'check_in'
for f in sorted(glob.glob(os.path.join(H, src, 'in_*.jsonl'))):
    n = re.search(r'in_(\d+)', f).group(1); o = os.path.join(H, D, f'out_{n}.jsonl')
    if not os.path.exists(o) or time.time() - os.path.getmtime(o) < 240: continue      # still being written or corrected
    ids = [json.loads(l)['id'] for l in open(f, encoding='utf-8') if l.strip()]; got = []
    for l in open(o, encoding='utf-8'):
        try: got.append(json.loads(l).get('id'))
        except Exception: pass
    if got == ids: print(os.path.relpath(o, os.path.dirname(H)))
