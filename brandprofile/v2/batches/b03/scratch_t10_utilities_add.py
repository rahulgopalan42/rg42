import json,sys
# usage: python add.py main|watch|disc|dups  < json (one object or list)
kind=sys.argv[1]
fn={'main':'t10_utilities.jsonl','watch':'watch_t10_utilities.jsonl','disc':'disc_t10_utilities.jsonl','dups':'dups_t10_utilities.jsonl'}[kind]
data=json.load(sys.stdin)
if isinstance(data,dict): data=[data]
TPL={"name":"","website":"","aliases":[],"hq_city":"","hq_country":"","sector":"Utilities & Renewable Energy","subsector":"","desc":"","products":"","model":"B2B","customers":"","ownership_type":"","parent_immediate":"","parent_ultimate":"","parent_listed":"","pe_swf_owner":"","minority_investors":"","marketing_autonomy":"unknown","marketing_autonomy_basis":"","parent_backing":"","employees":None,"countries":None,"stores_or_sites":"","markets":"","expansion_markets":"","reach":"Domestic","route":"","fin":[],"qualifying_metric":"","alt_indicators":[],"exception_note":"","profitability":"unknown","profitability_basis":"","distress":"","sponsorships":[],"signals":[],"fit":{"b2b":0,"ecosystem":0,"technical":0,"hospitality":0,"geography":0,"brand":0,"consumer":0,"category":3},"fit_rationale":"","customer_overlap":"","category_conflict":"none found","f1_markets":"","access":{"owner_led":"unknown","marketing_head_identified":"no","structure":"mid","roles":""},"compliance":"","outstanding":"","sources":[],"verified":"2026-11-28","conf":"medium","discovered_via":"Independent web research","discovery_source":"","signals_checked":"no"}
with open(fn,'a') as f:
    for d in data:
        if kind in('main','watch'):
            r=dict(TPL); r.update(d)
            if kind=='watch': r['route']='none'
            if not r['discovery_source'] and r['sources']: r['discovery_source']=r['sources'][0]
        else: r=d
        f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(data),'written to',fn)
