"""Usage: found.py "Company A | companya.com" "Company B" ...
For the completeness cross-check: says where a company already stands. First the master / delivered / F1 / listed check (check.py),
then whether batch 3 has it anywhere (researched, left out, or on the discovery register), then the user's older-sheet list.
NOT FOUND ANYWHERE means no stream has seen the name: a real gap."""
import glob, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import check as C
from register import norm, loose
def index():
    ix = {}
    def add(name, where):
        for k in {norm(name), loose(name)}:
            if len(k) >= 2: ix.setdefault(k, where)
    for p in sorted(glob.glob(os.path.join(H, 'batches', 'b03', '*.jsonl'))):
        b = os.path.basename(p)[:-6]
        if b.startswith(('in_', 'sig_')): continue
        where = 'left out by batch 3 research' if b.startswith('dups_') else 'on the batch 3 discovery register (not researched yet)' if b.startswith('disc_') else 'batch 3 watchlist' if b.startswith('watch_') else 'researched in batch 3'
        for line in open(p, encoding='utf-8', errors='replace'):
            try: d = json.loads(line)
            except Exception: continue
            if isinstance(d, dict) and d.get('name'): add(str(d['name']), where + ' (' + b + ')')
    for p in sorted(glob.glob(os.path.join(H, 'discovery', '*', '*.jsonl'))):
        for line in open(p, encoding='utf-8', errors='replace'):
            try: d = json.loads(line)
            except Exception: continue
            if isinstance(d, dict) and d.get('name'): add(str(d['name']), 'database lead, not verified (' + os.path.basename(p)[:-6] + ')')
    try:
        import older as O
        for d in O.SHEET:
            if d.get('brand'): add(str(d['brand']), "on the user's older sheet")
    except Exception: pass
    return ix
if __name__ == '__main__':
    IX = index()
    for a in sys.argv[1:]:
        name = a.split('|')[0].strip(); st, disp, src, hits = C.lookup(a)
        if st in ('dup', 'f1', 'listed'):
            print(f"{name}: " + {'dup': 'ALREADY DELIVERED' if src.startswith('delivered') else 'IN MASTER', 'f1': 'F1 PARTNER', 'listed': 'LISTED?'}[st] + f' ({disp})'); continue
        w = IX.get(norm(name)) or IX.get(loose(name))
        print(f"{name}: " + (('KNOWN: ' + w) if w else 'NOT FOUND ANYWHERE') + (f' [close to master name {disp}]' if st == 'possible' else ''))
