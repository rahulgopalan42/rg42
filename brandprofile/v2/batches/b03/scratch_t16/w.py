import json,sys
D={"name":"","website":"","aliases":[],"hq_city":"","hq_country":"","sector":"Telecommunications","subsector":"","desc":"","products":"","model":"Hybrid","customers":"",
"ownership_type":"","parent_immediate":"","parent_ultimate":"","parent_listed":"none","pe_swf_owner":"","minority_investors":"","marketing_autonomy":"unknown","marketing_autonomy_basis":"",
"parent_backing":"","employees":None,"countries":None,"stores_or_sites":"","markets":"","expansion_markets":"","reach":"Domestic","route":"A","fin":[],"qualifying_metric":"","alt_indicators":[],
"exception_note":"","profitability":"unknown","profitability_basis":"","distress":"","sponsorships":[],"signals":[],
"fit":{"b2b":0,"ecosystem":0,"technical":0,"hospitality":0,"geography":0,"brand":0,"consumer":0,"category":0},"fit_rationale":"","customer_overlap":"",
"category_conflict":"none found","f1_markets":"","access":{"owner_led":"unknown","marketing_head_identified":"no","structure":"mid","roles":""},"compliance":"","outstanding":"",
"sources":[],"verified":"2026-11-28","conf":"medium","discovered_via":"Independent web research","discovery_source":"","signals_checked":"no"}
d=json.loads(sys.stdin.read())
r=dict(D); r.update(d)
f=sys.argv[1]
names=set()
import os
for fn in ['../t16_telecom_ops.jsonl','../watch_t16_telecom_ops.jsonl']:
    if os.path.exists(fn):
        for l in open(fn):
            names.add(json.loads(l)['name'].lower())
if r['name'].lower() in names: sys.exit('DUPLICATE '+r['name'])
open(f,'a').write(json.dumps(r,ensure_ascii=False)+'\n'); print('ok',r['name'],f)
