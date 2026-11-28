import json
FS="https://forbes.kz/ranking/75-krupneyshih-chastnyh-kompaniy-kazahstana-2025-ac7ea1"
KZT=0.0021
TEMPLATE={"name":"","website":"","aliases":[],"hq_city":"","hq_country":"","sector":"","subsector":"","desc":"","products":"","model":"B2B","customers":"",
"ownership_type":"","parent_immediate":"","parent_ultimate":"","parent_listed":"none","pe_swf_owner":"","minority_investors":"",
"marketing_autonomy":"unknown","marketing_autonomy_basis":"","parent_backing":"","employees":None,"countries":None,"stores_or_sites":"",
"markets":"","expansion_markets":"","reach":"Domestic","route":"A","fin":[],"qualifying_metric":"","alt_indicators":[],"exception_note":"",
"profitability":"unknown","profitability_basis":"","distress":"","sponsorships":[],"signals":[],
"fit":{"b2b":0,"ecosystem":0,"technical":0,"hospitality":0,"geography":0,"brand":0,"consumer":0,"category":0},
"fit_rationale":"","customer_overlap":"","category_conflict":"none found","f1_markets":"",
"access":{"owner_led":"unknown","marketing_head_identified":"no","structure":"mid","roles":""},
"compliance":"","outstanding":"","sources":[],"verified":"2026-11-28","conf":"medium",
"discovered_via":"Independent web research","discovery_source":"","signals_checked":"yes"}
def kzfin(rev,ni=None,period="FY2024"):
    f=[{"metric":"revenue","value_orig":f"KZT {rev} bn","usd_m":round(rev*1000*KZT),"period":period,"published":"2025","kind":"reported","source":FS}]
    if ni is not None:
        f.append({"metric":"net_income","value_orig":f"KZT {ni} bn","usd_m":round(ni*1000*KZT),"period":period,"published":"2025","kind":"reported","source":FS})
    return f
def fit(s):
    k=["b2b","ecosystem","technical","hospitality","geography","brand","consumer","category"]
    return dict(zip(k,[int(c) for c in s]))
def W(kind,**kw):
    r=json.loads(json.dumps(TEMPLATE))
    for a,b in kw.items():
        if a=="fit" and isinstance(b,str): b=fit(b)
        if a=="access" and isinstance(b,tuple): b=dict(zip(["owner_led","marketing_head_identified","structure","roles"],b))
        r[a]=b
    if kind=="watch": r["route"]="none"
    fn={"main":"k29_levant_central_asia.jsonl","watch":"watch_k29_levant_central_asia.jsonl"}[kind]
    open(fn,"a").write(json.dumps(r,ensure_ascii=False)+"\n")
def D(name,why):
    open("dups_k29_levant_central_asia.jsonl","a").write(json.dumps({"name":name,"why":why},ensure_ascii=False)+"\n")
