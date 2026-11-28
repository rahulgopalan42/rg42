"""Scratch helper for t13_real_estate: read TSV lines (name, website, hq_country, subsector, figure, metric, usd_m, source[, parent])
from stdin, run check.py on each, append a DISC line, print the check result. Skips names already in DISC."""
import json, os, sys, re
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(D, '..', '..')))
import check as C
OUT = os.path.join(D, 'disc_t13_real_estate.jsonl')
seen = set()
if os.path.exists(OUT):
    for l in open(OUT, encoding='utf-8'):
        try: seen.add(json.loads(l)['name'].lower())
        except Exception: pass
def code(s):
    for k, v in (('ALREADY DELIVERED', 'ALREADY DELIVERED'), ('IN MASTER', 'IN MASTER'), ('F1 PARTNER', 'F1 PARTNER'), ('LISTED?', 'LISTED'), ('POSSIBLE', 'POSSIBLE')):
        if ': ' + k in s: return v
    return 'NEW'
with open(OUT, 'a', encoding='utf-8') as f:
    for line in sys.stdin:
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#'): continue
        p = line.split('\t') + [''] * 9
        name, site = p[0].strip(), p[1].strip()
        if name.lower() in seen: print('SKIP dup in DISC:', name); continue
        arg = name + (' | ' + site if site else '')
        r = C.check(arg); st = code(r)
        base = re.sub(r'\b(Group|Holdings?|Company|Corp(oration)?|Ltd|Limited|Inc|LLC|S\.?A\.?|GmbH|AG|PLC|Pvt|Properties|Realty|Development|Developers)\b\.?', '', name).strip(' ,&')
        if st == 'NEW' and base and base.lower() != name.lower():
            r2 = C.check(base); s2 = code(r2)
            if s2 != 'NEW': r += ' || base: ' + r2; st = 'POSSIBLE' if s2 in ('POSSIBLE', 'LISTED') else s2
        try: usd = float(p[6]) if p[6].strip() else None
        except ValueError: usd = None
        rec = {"name": name, "website": site, "hq_country": p[2].strip(), "sector": "Real Estate", "subsector": p[3].strip(),
               "figure": p[4].strip(), "metric": p[5].strip() or "none", "usd_m": usd, "source": p[7].strip(),
               "check": st, "stage": "not researched", "why": r.split(': ', 1)[1] if st != 'NEW' else ''}
        if p[8].strip(): rec["parent"] = p[8].strip()
        f.write(json.dumps(rec, ensure_ascii=False) + '\n'); seen.add(name.lower())
        print(r)
