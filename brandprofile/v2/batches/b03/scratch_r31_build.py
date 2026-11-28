import json, sys
B = "/home/user/rg42/brandprofile/v2/batches/b03/"
IN = {json.loads(l)["name"]: json.loads(l) for l in open(B + "in_q31.jsonl")}
KEYS = ["name","website","aliases","hq_city","hq_country","sector","subsector","desc","products","model","customers","ownership_type",
 "parent_immediate","parent_ultimate","parent_listed","pe_swf_owner","minority_investors","marketing_autonomy","marketing_autonomy_basis",
 "parent_backing","employees","countries","stores_or_sites","markets","expansion_markets","reach","route","fin","qualifying_metric",
 "alt_indicators","exception_note","profitability","profitability_basis","distress","sponsorships","signals","fit","fit_rationale",
 "customer_overlap","category_conflict","f1_markets","access","compliance","outstanding","sources","verified","conf",
 "signals_checked","discovered_via","discovery_source"]
DEF = dict(website="", aliases=[], hq_city="", hq_country="", subsector="", desc="", products="", model="B2B", customers="",
 ownership_type="requires verification", parent_immediate="", parent_ultimate="", parent_listed="none", pe_swf_owner="",
 minority_investors="", marketing_autonomy="unknown", marketing_autonomy_basis="", parent_backing="", employees=None, countries=None,
 stores_or_sites="", markets="", expansion_markets="", reach="Domestic", route="none", fin=[], qualifying_metric="", alt_indicators=[],
 exception_note="", profitability="unknown", profitability_basis="", distress="", sponsorships=[], signals=[],
 fit_rationale="", customer_overlap="", category_conflict="none found", f1_markets="", compliance="", outstanding="", sources=[],
 verified="2026-11-28", conf="low", signals_checked="no")
def infin(name, kind="reported", period=""):
    d = IN[name]
    if not d.get("figure"): return []
    return [{"metric": d.get("metric") or "revenue", "value_orig": d["figure"], "usd_m": d.get("usd_m"), "period": period,
             "published": "", "kind": kind, "source": d["source"]}]
def rec(name, fit, access, **kw):
    r = dict(DEF); r.update(kw); r["name"] = name
    r["fit"] = dict(zip(["b2b","ecosystem","technical","hospitality","geography","brand","consumer","category"], fit))
    r["access"] = dict(zip(["owner_led","marketing_head_identified","structure","roles"], access))
    d = IN.get(name, {})
    r.setdefault("sector", d.get("sector",""))
    if not r.get("sector"): r["sector"] = d.get("sector","")
    r["discovered_via"] = d.get("via",""); r["discovery_source"] = d.get("source","")
    if d.get("source") and d["source"].startswith("http") and d["source"] not in r["sources"]: r["sources"] = r["sources"] + [d["source"].split(" ")[0]]
    out = {k: r.get(k, DEF.get(k)) for k in KEYS}
    fn = B + ("r31_queue.jsonl" if r["route"] in ("A","B","C") else "watch_r31_queue.jsonl")
    with open(fn, "a") as f: f.write(json.dumps(out, ensure_ascii=False) + "\n")
