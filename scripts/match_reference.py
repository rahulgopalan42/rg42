#!/usr/bin/env python3
"""Find companies in the prospect list that already appear in the reference workbooks.

Match types, strongest first:
- website: same registrable domain (with similar names, otherwise sent to review)
- name: same normalised name in a company/brand column (sent to review if both sides have
  different websites)
- derived: same normalised name as a brand named inside brackets or in a brand list (review)
- fuzzy: near-identical multi-word names (review)

Usage: match_reference.py <prospects.csv> <reference_names.csv> <out_matches.csv>
"""
import csv
import difflib
import re
import sys
import unicodedata
from collections import defaultdict

TWO_LEVEL = {"co.uk", "org.uk", "ac.uk", "com.au", "net.au", "com.br", "co.in", "co.jp", "com.cn", "com.sg",
             "co.za", "com.mx", "co.id", "com.tr", "co.kr", "com.hk", "com.tw", "com.ar", "com.co", "com.my",
             "co.nz", "com.pe", "com.ph", "com.vn", "co.il", "com.eg", "com.sa", "com.pk", "com.ng", "co.th",
             "bank.in", "com.ec", "com.uy", "com.py", "com.gt", "co.ke"}
# e.g. npci.org.in, kpc.com.kw, gea.gov.sa: the registrable part is three labels
COUNTRY_SECOND_LEVEL = {"com", "co", "org", "net", "gov", "ac", "edu", "or", "ne", "go", "gob", "mil", "nic",
                        "ltd", "plc", "sch", "info", "biz", "gv", "in", "bank"}
GENERIC_DOMAINS = {"linkedin.com", "facebook.com", "twitter.com", "x.com", "instagram.com", "crunchbase.com",
                   "wikipedia.org", "bit.ly", "linktr.ee", "medium.com", "github.io", "google.com", "youtube.com",
                   "wordpress.com", "wixsite.com", "beehiiv.com", "substack.com", "notion.site", "workable.com",
                   "bank.in", "go.link", "shor.by", "hubs.la", "utm.io"}
SUFFIXES = r"\b(inc|incorporated|llc|l l c|ltd|limited|plc|corp|corporation|co|company|group|holdings?|" \
           r"s a|sa|ag|se|nv|n v|bv|b v|spa|s p a|gmbh|kg|ab|asa|oyj|as|pte|pty|sas|srl|the|international|" \
           r"global|hq)\b"


def norm_name(n):
    n = unicodedata.normalize("NFKD", n or "").encode("ascii", "ignore").decode().lower()
    n = n.replace("&", " and ")
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    n = re.sub(SUFFIXES, " ", n)
    return " ".join(n.split())


def reg_domain(d):
    d = re.sub(r"^https?://", "", (d or "").lower().strip()).split("/")[0].split("?")[0].strip(".")
    d = re.sub(r"^www\d?\.", "", d)
    if not d or "." not in d or " " in d:
        return ""
    labels = d.split(".")
    country_second_level = len(labels[-1]) == 2 and labels[-2] in COUNTRY_SECOND_LEVEL
    if len(labels) >= 3 and (".".join(labels[-2:]) in TWO_LEVEL or country_second_level):
        d = ".".join(labels[-3:])
    else:
        d = ".".join(labels[-2:])
    return "" if d in GENERIC_DOMAINS else d


def similar(a, b):
    a, b = norm_name(a), norm_name(b)
    if not a or not b:
        return False
    if a == b or a in b or b in a:
        return True
    ta, tb = set(a.split()), set(b.split())
    return len(ta & tb) / max(1, min(len(ta), len(tb))) >= 0.5


def main(prospects_path, ref_path, out_path):
    refs = list(csv.DictReader(open(ref_path, newline="")))
    by_dom, by_name, by_derived = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in refs:
        dom = reg_domain(r["domain"])
        if dom:
            by_dom[dom].append(r)
        nn = norm_name(r["name"])
        if len(nn) >= 2:
            (by_derived if r["kind"] == "derived" else by_name)[nn].append(r)
    multi_word_names = defaultdict(list)
    for nn, lst in by_name.items():
        if len(nn.split()) >= 2:
            multi_word_names[nn.split()[0]].append(nn)

    prospects = [p for p in csv.DictReader(open(prospects_path, newline="")) if p["tab"] != "Removed"]
    out = []
    for p in prospects:
        pdom, pn = reg_domain(p["domain"]), norm_name(p["name"])
        hit = None
        if pdom and pdom in by_dom:
            r = by_dom[pdom][0]
            ok = similar(p["name"], r["name"] or r["domain"]) or not r["name"]
            hit = ("website", "definite" if ok else "review", r)
        if hit is None and pn in by_name:
            cands = by_name[pn]
            r = cands[0]
            rdoms = {reg_domain(c["domain"]) for c in cands} - {""}
            conflict = bool(pdom and rdoms and pdom not in rdoms)
            hit = ("name", "review" if conflict else "definite", r)
        if hit is None and pn in by_derived:
            hit = ("derived", "review", by_derived[pn][0])
        if hit is None and len(pn.split()) >= 2:
            pool = multi_word_names.get(pn.split()[0], [])
            close = difflib.get_close_matches(pn, pool, n=1, cutoff=0.88)
            if close:
                hit = ("fuzzy", "review", by_name[close[0]][0])
        if hit:
            kind, verdict, r = hit
            sheets = sorted({(x["workbook"], x["sheet"]) for x in (by_dom.get(pdom, []) if kind == "website" else
                             by_name.get(pn, []) if kind == "name" else by_derived.get(pn, []) if kind == "derived"
                             else [r])})
            out.append({"name": p["name"], "tab": p["tab"], "domain": p["domain"], "entityId": p["entityId"],
                        "match_type": kind, "verdict": verdict, "ref_name": r["name"], "ref_domain": r["domain"],
                        "ref_where": " | ".join(f"{w}: {s}" for w, s in sheets[:4]) + (" …" if len(sheets) > 4 else "")})
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    print("prospects checked:", len(prospects), "| matches:", len(out))
    print(Counter((o["match_type"], o["verdict"]) for o in out))


if __name__ == "__main__":
    main(*sys.argv[1:4])
