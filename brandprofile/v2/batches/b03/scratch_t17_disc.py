# scratch: build DISC lines. stdin: JSON list of [name, website, hq_country, subsector, figure, metric, usd_m, source, (parent)] ; argv[1]=sector
import json, sys, os, subprocess
base = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(base, '..', '..', '..'))
rows = json.loads(sys.stdin.read()); sector = sys.argv[1]
args = [(r[0] + (' | ' + r[1] if r[1] else '')) for r in rows]
res = subprocess.run([sys.executable, '-I', os.path.join(root, 'v2', 'check.py')] + args, capture_output=True, text=True, cwd=root).stdout.strip().split('\n')
assert len(res) == len(rows), (len(res), len(rows))
out = open(os.path.join(base, 'disc_t17_logistics.jsonl'), 'a', encoding='utf-8')
for r, line in zip(rows, res):
    st = line.split(': ', 1)[1] if ': ' in line else line
    chk = 'NEW'
    for k in ('IN MASTER', 'ALREADY DELIVERED', 'F1 PARTNER', 'LISTED', 'POSSIBLE'):
        if st.startswith(k): chk = k
    d = {"name": r[0], "website": r[1], "hq_country": r[2], "sector": sector, "subsector": r[3], "figure": r[4], "metric": r[5], "usd_m": r[6],
         "source": r[7], "check": chk, "stage": "not researched" if chk == 'NEW' else "left out", "why": "" if chk == 'NEW' else st[:160]}
    if len(r) > 8 and r[8]: d["parent"] = r[8]
    out.write(json.dumps(d, ensure_ascii=False) + '\n')
    print(r[0], '|', chk)
