import sys,json
# usage: add.py main|watch  < json (one object or list)
target={'main':'k03_nordics.jsonl','watch':'watch_k03_nordics.jsonl'}[sys.argv[1]]
tmpl={"name":"","website":"","aliases":[],"hq_city":"","hq_country":"","sector":"","subsector":"","desc":"","products":"","model":"B2B","customers":"","ownership_type":"","parent_immediate":"","parent_ultimate":"","parent_listed":"none","pe_swf_owner":"","minority_investors":"","marketing_autonomy":"unknown","marketing_autonomy_basis":"","parent_backing":"","employees":None,"countries":None,"stores_or_sites":"","markets":"","expansion_markets":"","reach":"","route":"","fin":[],"qualifying_metric":"","alt_indicators":[],"exception_note":"","profitability":"unknown","profitability_basis":"","distress":"","sponsorships":[],"signals":[],"fit":{},"fit_rationale":"","customer_overlap":"","category_conflict":"none found","f1_markets":"","access":{"owner_led":"unknown","marketing_head_identified":"no","structure":"mid","roles":""},"compliance":"","outstanding":"","sources":[],"verified":"2026-11-28","conf":"medium","discovered_via":"Independent web research","discovery_source":"","signals_checked":"yes"}
d=json.loads(sys.stdin.read())
for r in (d if isinstance(d,list) else [d]):
    o=dict(tmpl); o.update(r)
    srcs=set(o['sources'])
    for f in o['fin']: srcs.add(f.get('source',''))
    for s in o['signals']+o['sponsorships']+o['alt_indicators']: srcs.add(s.get('source',''))
    o['sources']=[s for s in o['sources']]+[s for s in srcs if s and s not in o['sources']]
    with open(target,'a') as fh: fh.write(json.dumps(o,ensure_ascii=False)+'\n')
    print('added',o['name'],'->',target)
