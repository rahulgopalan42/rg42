"""Usage: disc_check.py <rows.jsonl> [more.jsonl ...]
Runs the duplicate and eligibility check over discovery rows (name + domain/website) and writes the status into each row as "check"."""
import json, os, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import check as C
LAB = {'dup': 'IN MASTER', 'f1': 'F1 PARTNER', 'listed': 'LISTED', 'possible': 'POSSIBLE', 'new': 'NEW'}
for p in sys.argv[1:]:
    rows = []; c = Counter()
    for l in open(p, encoding='utf-8'):
        l = l.strip()
        if not l: continue
        try: d = json.loads(l)
        except Exception: c['unreadable line'] += 1; continue
        if not isinstance(d, dict) or not str(d.get('name') or '').strip(): continue
        site = str(d.get('domain') or d.get('website') or '').strip()
        st, disp, src, hits = C.lookup(str(d['name']).strip() + (' | ' + site if site else ''))
        lab = 'ALREADY DELIVERED' if st == 'dup' and src.startswith('delivered') else LAB[st]
        d['check'] = lab; d['check_note'] = (src or disp or '')[:160]; c[lab] += 1; rows.append(d)
    with open(p, 'w', encoding='utf-8') as f:
        for d in rows: f.write(json.dumps(d, ensure_ascii=False) + '\n')
    print(os.path.basename(p), len(rows), dict(c))
