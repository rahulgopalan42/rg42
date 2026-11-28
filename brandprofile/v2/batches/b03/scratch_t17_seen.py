# scratch helper for t17_logistics: which candidate names already appear in any b03 file (other researchers)
import json, glob, re, sys, os
def norm(s):
    s = s.lower()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'\b(inc|llc|ltd|limited|co|corp|corporation|company|group|gmbh|ag|sa|s\.a\.|spa|plc|holdings?|cos|the|of|logistics|transport|transportation)\b', ' ', s)
    return re.sub(r'[^a-z0-9]', '', s)
base = os.path.dirname(os.path.abspath(__file__))
seen = {}
for f in glob.glob(base + '/*.jsonl'):
    b = os.path.basename(f)
    if 't17_logistics' in b: continue
    for l in open(f, encoding='utf-8'):
        try: d = json.loads(l)
        except Exception: continue
        n = d.get('name') if isinstance(d, dict) else None
        if n: seen.setdefault(norm(n), set()).add(b)
for n in sys.argv[1:]:
    k = norm(n.split('|')[0])
    print(n, '=>', ','.join(sorted(seen.get(k, [])))[:150] or '-')
