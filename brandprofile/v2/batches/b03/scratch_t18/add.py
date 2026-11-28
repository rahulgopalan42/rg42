import json,sys
# usage: python3 add.py main|watch < json (one object or list)
D='/home/user/rg42/brandprofile/v2/batches/b03/'
f={'main':D+'t18_oil_gas.jsonl','watch':D+'watch_t18_oil_gas.jsonl','dups':D+'dups_t18_oil_gas.jsonl','disc':D+'disc_t18_oil_gas.jsonl'}[sys.argv[1]]
data=json.load(sys.stdin)
if isinstance(data,dict): data=[data]
tmpl={"name":"","website":"","aliases":[],"hq_city":"","hq_country":"","sector":"Oil, Gas & Fuels","subsector":"","desc":"","products":"","model":"B2B","customers":"","ownership_type":"","parent_immediate":"","parent_ultimate":"","parent_listed":"","pe_swf_owner":"","minority_investors":"","marketing_autonomy":"unknown","marketing_autonomy_basis":"","parent_backing":"","employees":None,"countries":None,"stores_or_sites":"","markets":"","expansion_markets":"","reach":"","route":"","fin":[],"qualifying_metric":"","alt_indicators":[],"exception_note":"","profitability":"unknown","profitability_basis":"","distress":"","sponsorships":[],"signals":[],"fit":{"b2b":0,"ecosystem":0,"technical":0,"hospitality":0,"geography":0,"brand":0,"consumer":0,"category":0},"fit_rationale":"","customer_overlap":"","category_conflict":"none found","f1_markets":"","access":{"owner_led":"unknown","marketing_head_identified":"no","structure":"mid","roles":""},"compliance":"","outstanding":"","sources":[],"verified":"2026-11-28","conf":"medium","discovered_via":"Independent web research","discovery_source":"","signals_checked":"no"}
with open(f,'a',encoding='utf-8') as o:
    for d in data:
        if sys.argv[1] in('main','watch'):
            r=dict(tmpl); r.update(d)
            if sys.argv[1]=='watch': r['route']='none'
        else: r=d
        o.write(json.dumps(r,ensure_ascii=False)+'\n'); print('added',r.get('name'))
