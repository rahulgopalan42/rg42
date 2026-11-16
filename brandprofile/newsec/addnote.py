"""Usage: addnote.py "Company" "note" ["Company 2" "note 2" ...]  - cautions reported by second-pass researchers, shown in Verification Notes"""
import json, os, sys
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes2.json')
N = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
a = sys.argv[1:]
for i in range(0, len(a) - 1, 2): N[a[i]] = a[i + 1]
json.dump(N, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0); print(len(N), 'notes')
