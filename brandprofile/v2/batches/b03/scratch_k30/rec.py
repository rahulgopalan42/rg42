"""Append full records. Usage: python rec.py < file.json (a JSON list of partial records). Each needs 'route' (A|B|C|none)."""
import sys, json
D = '/home/user/rg42/brandprofile/v2/batches/b03/'
KEY = 'k30_taiwan_hk_anz'
T = {"name": "", "website": "", "aliases": [], "hq_city": "", "hq_country": "", "sector": "", "subsector": "", "desc": "",
     "products": "", "model": "B2B", "customers": "", "ownership_type": "requires verification", "parent_immediate": "",
     "parent_ultimate": "", "parent_listed": "requires verification", "pe_swf_owner": "", "minority_investors": "",
     "marketing_autonomy": "unknown", "marketing_autonomy_basis": "", "parent_backing": "", "employees": None, "countries": None,
     "stores_or_sites": "", "markets": "", "expansion_markets": "", "reach": "Domestic", "route": "none", "fin": [],
     "qualifying_metric": "", "alt_indicators": [], "exception_note": "", "profitability": "unknown", "profitability_basis": "",
     "distress": "", "sponsorships": [], "signals": [],
     "fit": {"b2b": 0, "ecosystem": 0, "technical": 0, "hospitality": 0, "geography": 0, "brand": 0, "consumer": 0, "category": 0},
     "fit_rationale": "", "customer_overlap": "", "category_conflict": "none found", "f1_markets": "",
     "access": {"owner_led": "unknown", "marketing_head_identified": "no", "structure": "mid", "roles": ""},
     "compliance": "", "outstanding": "", "sources": [], "verified": "2026-11-28", "conf": "medium",
     "discovered_via": "Independent web research", "discovery_source": "", "signals_checked": "no"}
FITK = ["b2b", "ecosystem", "technical", "hospitality", "geography", "brand", "consumer", "category"]
recs = json.load(sys.stdin)
for r in recs:
    o = json.loads(json.dumps(T))
    if isinstance(r.get('fit'), list): r['fit'] = dict(zip(FITK, r['fit']))
    if isinstance(r.get('access'), list): r['access'] = dict(zip(["owner_led", "marketing_head_identified", "structure", "roles"], r['access']))
    o.update(r)
    for f in o['fin']:
        f.setdefault('published', ''); f.setdefault('kind', 'reported')
    if not o['sources']:
        o['sources'] = sorted({f['source'] for f in o['fin']} | {s['source'] for s in o['signals']} | {a['source'] for a in o['alt_indicators']})
    path = D + (KEY if o['route'] in ('A', 'B', 'C') else 'watch_' + KEY) + '.jsonl'
    with open(path, 'a') as fh: fh.write(json.dumps(o, ensure_ascii=False) + '\n')
    print(o['route'], o['name'], '->', path.split('/')[-1])
