"""Scratch helper for f01_queue: fill schema defaults and append a record to MAIN or WATCH."""
import json, sys, os

D = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(D, "f01_queue.jsonl")
WATCH = os.path.join(D, "watch_f01_queue.jsonl")

TEMPLATE = {
    "name": "", "website": "", "aliases": [], "hq_city": "", "hq_country": "", "sector": "", "subsector": "",
    "desc": "", "products": "", "model": "", "customers": "", "ownership_type": "requires verification",
    "parent_immediate": "", "parent_ultimate": "", "parent_listed": "none", "pe_swf_owner": "", "minority_investors": "",
    "marketing_autonomy": "unknown", "marketing_autonomy_basis": "", "parent_backing": "", "employees": None,
    "countries": None, "stores_or_sites": "", "markets": "", "expansion_markets": "", "reach": "", "route": "none",
    "fin": [], "qualifying_metric": "", "alt_indicators": [], "exception_note": "", "profitability": "unknown",
    "profitability_basis": "", "distress": "", "sponsorships": [], "signals": [],
    "fit": {"b2b": 0, "ecosystem": 0, "technical": 0, "hospitality": 0, "geography": 0, "brand": 0, "consumer": 0, "category": 0},
    "fit_rationale": "", "customer_overlap": "", "category_conflict": "none found", "f1_markets": "",
    "access": {"owner_led": "unknown", "marketing_head_identified": "no", "structure": "mid", "roles": ""},
    "compliance": "", "outstanding": "", "sources": [], "verified": "2026-11-28", "conf": "medium",
    "discovered_via": "", "discovery_source": "", "signals_checked": "no",
}

FITKEYS = ["b2b", "ecosystem", "technical", "hospitality", "geography", "brand", "consumer", "category"]


def write(rec):
    r = dict(TEMPLATE)
    r.update(rec)
    if isinstance(r["fit"], (list, tuple)):
        r["fit"] = dict(zip(FITKEYS, r["fit"]))
    if isinstance(r["access"], (list, tuple)):
        r["access"] = dict(zip(["owner_led", "marketing_head_identified", "structure", "roles"], r["access"]))
    path = WATCH if r["route"] == "none" else MAIN
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", r["name"], "->", os.path.basename(path))


if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if line:
            write(json.loads(line))
