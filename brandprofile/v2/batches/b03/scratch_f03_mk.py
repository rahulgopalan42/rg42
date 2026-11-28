import json, sys
TPL = {"name": "", "website": "", "aliases": [], "hq_city": "", "hq_country": "", "sector": "", "subsector": "", "desc": "",
 "products": "", "model": "B2B", "customers": "", "ownership_type": "requires verification", "parent_immediate": "", "parent_ultimate": "",
 "parent_listed": "none", "pe_swf_owner": "", "minority_investors": "", "marketing_autonomy": "unknown", "marketing_autonomy_basis": "",
 "parent_backing": "", "employees": None, "countries": None, "stores_or_sites": "", "markets": "", "expansion_markets": "", "reach": "Domestic",
 "route": "A", "fin": [], "qualifying_metric": "revenue", "alt_indicators": [], "exception_note": "", "profitability": "unknown",
 "profitability_basis": "", "distress": "", "sponsorships": [], "signals": [],
 "fit": {"b2b": 1, "ecosystem": 0, "technical": 0, "hospitality": 1, "geography": 1, "brand": 1, "consumer": 0, "category": 3},
 "fit_rationale": "", "customer_overlap": "", "category_conflict": "none found", "f1_markets": "",
 "access": {"owner_led": "unknown", "marketing_head_identified": "no", "structure": "mid", "roles": "CEO; Head of Marketing"},
 "compliance": "", "outstanding": "", "sources": [], "verified": "2026-11-28", "conf": "medium",
 "discovered_via": "", "discovery_source": "", "signals_checked": "no"}
IN = {json.loads(l)['name']: json.loads(l) for l in open('in_f03.jsonl')}
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    d = json.loads(line); inp = d.pop('_in'); src = IN[inp]
    r = json.loads(json.dumps(TPL)); 
    for k, v in d.items():
        if k in ('fit', 'access'): r[k].update(v)
        else: r[k] = v
    r['discovered_via'] = src['via']; r['discovery_source'] = src['source']
    f0 = {"metric": src['metric'] if src['metric'] not in ('none', '') else "revenue", "value_orig": src['figure'], "usd_m": src['usd_m'], "period": "",
          "published": "", "kind": "estimated" if 'Clay' in src['figure'] or 'estimate' in src['figure'] else "reported", "source": src['source']}
    if d.get('_f0'): f0.update(d.pop('_f0')); r.pop('_f0', None)
    r['fin'] = [f0] + r['fin']
    if src['source'] not in r['sources'] and src['source'].startswith('http'): r['sources'].insert(0, src['source'])
    out = 'watch_f03_queue.jsonl' if r['route'] == 'none' else 'f03_queue.jsonl'
    open(out, 'a').write(json.dumps(r, ensure_ascii=False) + '\n'); print('wrote', r['name'], '->', out)
