"""Append DISC lines for k30. Input TSV on stdin: name<TAB>website<TAB>hq_country<TAB>sector<TAB>subsector<TAB>figure<TAB>metric<TAB>usd_m<TAB>source[<TAB>parent]
Runs check.py's check() and writes check result. Skips names already in the DISC file."""
import sys, json, os
sys.path.insert(0, '/home/user/rg42/brandprofile/v2')
from check import check
OUT = '/home/user/rg42/brandprofile/v2/batches/b03/disc_k30_taiwan_hk_anz.jsonl'
seen = set()
if os.path.exists(OUT):
    for l in open(OUT):
        try: seen.add(json.loads(l)['name'].lower())
        except Exception: pass
n = 0
with open(OUT, 'a') as f:
    for line in sys.stdin:
        if not line.strip(): continue
        p = line.rstrip('\n').split('\t') + [''] * 10
        name = p[0].strip()
        if name.lower() in seen: continue
        arg = name + (' | ' + p[1] if p[1] else '')
        res = check(arg)
        st = res.split(': ', 1)[1]
        code = 'IN MASTER' if st.startswith('IN MASTER') else 'ALREADY DELIVERED' if st.startswith('ALREADY') else 'F1 PARTNER' if st.startswith('F1') else 'LISTED' if st.startswith('LISTED') else 'POSSIBLE' if st.startswith('POSSIBLE') else 'NEW'
        usd = float(p[7]) if p[7].strip() else None
        rec = {"name": name, "website": p[1], "hq_country": p[2], "sector": p[3], "subsector": p[4], "figure": p[5], "metric": p[6] or 'none',
               "usd_m": usd, "source": p[8], "check": code,
               "stage": "left out" if code in ('IN MASTER', 'ALREADY DELIVERED', 'F1 PARTNER') else "not researched",
               "why": st if code != 'NEW' else ''}
        if p[9].strip(): rec['parent'] = p[9].strip()
        f.write(json.dumps(rec, ensure_ascii=False) + '\n'); seen.add(name.lower()); n += 1
        print(code, '|', name, '|', st[:90])
print('written', n, file=sys.stderr)
