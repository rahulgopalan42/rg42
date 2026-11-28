import json, sys, os
H = os.path.dirname(os.path.abspath(__file__))
BASE = {"name": "", "website": "", "aliases": [], "hq_city": "", "hq_country": "", "sector": "Semiconductors & Electronics", "subsector": "",
 "desc": "", "products": "", "model": "B2B", "customers": "", "ownership_type": "", "parent_immediate": "", "parent_ultimate": "",
 "parent_listed": "none", "pe_swf_owner": "", "minority_investors": "", "marketing_autonomy": "unknown", "marketing_autonomy_basis": "",
 "parent_backing": "", "employees": None, "countries": None, "stores_or_sites": "", "markets": "", "expansion_markets": "", "reach": "",
 "route": "", "fin": [], "qualifying_metric": "", "alt_indicators": [], "exception_note": "", "profitability": "unknown",
 "profitability_basis": "", "distress": "", "sponsorships": [], "signals": [], "fit": {}, "fit_rationale": "", "customer_overlap": "",
 "category_conflict": "none found", "f1_markets": "", "access": {"owner_led": "unknown", "marketing_head_identified": "no", "structure": "mid", "roles": ""},
 "compliance": "", "outstanding": "", "sources": [], "verified": "2026-11-28", "conf": "medium",
 "discovered_via": "Independent web research", "discovery_source": "", "signals_checked": "no"}
FK = ["b2b","ecosystem","technical","hospitality","geography","brand","consumer","category"]
def rec(**kw):
    r = dict(BASE); r.update(kw)
    if isinstance(r["fit"], (list, tuple)): r["fit"] = dict(zip(FK, r["fit"]))
    f = "t15_semis_hardware.jsonl" if r["route"] in ("A","B","C") else "watch_t15_semis_hardware.jsonl"
    if r["route"] not in ("A","B","C"): r["route"] = "none"
    open(os.path.join(H, f), "a").write(json.dumps(r, ensure_ascii=False) + "\n"); print("wrote", r["name"], "->", f)
def disc(rows):
    with open(os.path.join(H, "disc_t15_semis_hardware.jsonl"), "a") as fh:
        for d in rows:
            x = {"name": "", "website": "", "hq_country": "", "sector": "Semiconductors & Electronics", "subsector": "", "figure": "", "metric": "none", "usd_m": None, "source": "", "check": "NEW", "stage": "not researched", "why": ""}
            x.update(d); fh.write(json.dumps(x, ensure_ascii=False) + "\n")
def dup(rows):
    with open(os.path.join(H, "dups_t15_semis_hardware.jsonl"), "a") as fh:
        for n, w in rows: fh.write(json.dumps({"name": n, "why": w}, ensure_ascii=False) + "\n")
