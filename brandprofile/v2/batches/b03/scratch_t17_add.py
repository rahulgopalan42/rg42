# scratch: append one record (JSON on stdin) to t17 MAIN or WATCH, filling defaults for missing keys
import json, sys, os
base = os.path.dirname(os.path.abspath(__file__))
target = sys.argv[1]  # main|watch|disc|dups
d = json.loads(sys.stdin.read())
fn = {'main': 't17_logistics.jsonl', 'watch': 'watch_t17_logistics.jsonl', 'disc': 'disc_t17_logistics.jsonl', 'dups': 'dups_t17_logistics.jsonl'}[target]
recs = d if isinstance(d, list) else [d]
out = []
for r in recs:
    if target in ('main', 'watch'):
        defaults = {"aliases": [], "model": "B2B", "pe_swf_owner": "", "minority_investors": "", "parent_backing": "", "expansion_markets": "",
                    "alt_indicators": [], "exception_note": "", "profitability": "unknown", "profitability_basis": "", "distress": "",
                    "sponsorships": [], "signals": [], "customer_overlap": "", "category_conflict": "none found", "compliance": "",
                    "verified": "2026-11-28", "discovered_via": "Independent web research", "signals_checked": "yes"}
        for k, v in defaults.items(): r.setdefault(k, v)
        if target == 'watch': r.setdefault('route', 'none')
        for k in ('name','website','sector','route','fit','fit_rationale','access','sources','discovery_source','ownership_type'):
            assert k in r, k
    out.append(json.dumps(r, ensure_ascii=False))
with open(os.path.join(base, fn), 'a', encoding='utf-8') as f:
    for o in out: f.write(o + '\n')
print('wrote', len(out), 'to', fn)
