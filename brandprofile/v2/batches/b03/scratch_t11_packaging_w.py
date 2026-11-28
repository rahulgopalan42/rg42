import json,sys
TEMPLATE={"name":"","website":"","aliases":[],"hq_city":"","hq_country":"","sector":"Packaging & Printing","subsector":"","desc":"","products":"","model":"B2B","customers":"","ownership_type":"","parent_immediate":"","parent_ultimate":"","parent_listed":"none","pe_swf_owner":"","minority_investors":"","marketing_autonomy":"unknown","marketing_autonomy_basis":"","parent_backing":"","employees":None,"countries":None,"stores_or_sites":"","markets":"","expansion_markets":"","reach":"","route":"","fin":[],"qualifying_metric":"","alt_indicators":[],"exception_note":"","profitability":"unknown","profitability_basis":"","distress":"","sponsorships":[],"signals":[],"fit":{"b2b":0,"ecosystem":0,"technical":0,"hospitality":0,"geography":0,"brand":0,"consumer":0,"category":3},"fit_rationale":"","customer_overlap":"","category_conflict":"none found","f1_markets":"","access":{"owner_led":"unknown","marketing_head_identified":"no","structure":"mid","roles":""},"compliance":"","outstanding":"","sources":[],"verified":"2026-11-28","conf":"medium","discovered_via":"Independent web research","discovery_source":"","signals_checked":"yes"}
# input: python w.py FILE < json-lines (partial dicts)
out=sys.argv[1]
with open(out,'a') as f:
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        d=json.loads(line); r=dict(TEMPLATE); r.update(d)
        if 'fit' in d: ff=dict(TEMPLATE['fit']); ff.update(d['fit']); r['fit']=ff
        if 'access' in d: a=dict(TEMPLATE['access']); a.update(d['access']); r['access']=a
        f.write(json.dumps(r,ensure_ascii=False)+'\n'); print('wrote',r['name'],r['route'])
