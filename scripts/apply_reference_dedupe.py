#!/usr/bin/env python3
"""Take companies already in the user's reference workbooks out of the prospect list.

A match counts as a repeat when it is a confident automatic match (same website with a similar
name, or the same multi-word name), or when the manual decision for that exact pairing says
"same company or group". Repeats move to an "Already in your files" tab that shows where each
one was found; everything else stays on its tab.

Usage: apply_reference_dedupe.py <prospects.csv> <matches.csv> <decisions.csv> <output_base>
"""
import csv
import os
import sys
from collections import Counter

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from match_reference import norm_name  # noqa: E402

HOW = {"website": "Same website", "name": "Same name", "derived": "Brand or parent named in your file",
       "fuzzy": "Near-identical name"}
HEADERS = ["Company", "Sector", "F1 sponsorship category", "Total funding (range)", "Largest 2025-26 round",
           "Round ($M)", "Announced", "Round source", "Source", "Check", "Clay industry", "Clay company type",
           "Country", "City", "Size", "Employees", "Annual revenue", "Website", "LinkedIn"]
WIDTHS = [34, 30, 26, 18, 22, 10, 12, 40, 13, 44, 30, 18, 18, 20, 13, 11, 15, 26, 44]


def values(r):
    emp = r["employees"]
    return [r["name"], r["sector"], r["f1_category"], r["funding_range"], r["round"],
            float(r["round_amount_m"]) if r["round_amount_m"] else "", r["announced"], r["news_url"],
            r["source"], r["check"], r["industry"], r["clay_type"], r["country"], r["city"], r["size"],
            int(emp) if str(emp).isdigit() else emp, r["revenue"], r["domain"], r["linkedin"]]


def sheet(ws, rows, extra=()):
    ws.append(list(extra and [h for h, _ in extra]) + HEADERS)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append([f(r) for _, f in extra] + values(r))
    ws.freeze_panes = ws.cell(row=2, column=len(extra) + 2)
    ws.auto_filter.ref = ws.dimensions
    for i, w in enumerate([w for w in (34, 40, 28, 16)[:len(extra)]] + WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def main(prospects_path, matches_path, decisions_path, out_base):
    rows = list(csv.DictReader(open(prospects_path, newline="")))
    matches = {(m["name"], m["domain"]): m for m in csv.DictReader(open(matches_path, newline=""))}
    decisions = {(d["name"], d["domain"]): d for d in csv.DictReader(open(decisions_path, newline=""))}

    repeats, undecided = [], 0
    for r in rows:
        if r["tab"] == "Removed":
            continue
        m = matches.get((r["name"], r["domain"]))
        if not m:
            continue
        single_word_name = m["match_type"] == "name" and len(norm_name(r["name"]).split()) == 1
        if m["verdict"] == "definite" and not single_word_name:
            same = True
        else:
            d = decisions.get((r["name"], r["domain"]))
            if d is None or d["ref_name"] != m["ref_name"]:
                undecided += 1
                r["check"] = (r["check"] + "; " if r["check"] else "") + f"Check: possibly in your files as {m['ref_name']}"
                continue
            same = d["decision"] == "same company or group"
        if same:
            r["from_tab"], r["tab"] = r["tab"], "Already in your files"
            r["ref_name"], r["ref_where"], r["how"] = m["ref_name"], m["ref_where"], HOW[m["match_type"]]
            repeats.append(r)

    tabs = ["Private & other", "Public"]
    by = {t: [r for r in rows if r["tab"] == t] for t in tabs}
    wb = Workbook()
    s = wb.active
    s.title = "Summary"
    s.append(["Fresh list: companies with $100M+ funding that are NOT in your two reference files"])
    s[1][0].font = Font(bold=True)
    s.append([])
    s.append(["Sector", *tabs, "Total"])
    for c in s[3]:
        c.font = Font(bold=True)
    counts = Counter((r["sector"], r["tab"]) for t in tabs for r in by[t])
    sectors = sorted({r["sector"] for t in tabs for r in by[t]}, key=lambda x: -sum(counts[(x, t)] for t in tabs))
    for sec in sectors:
        n = [counts[(sec, t)] for t in tabs]
        s.append([sec, *n, sum(n)])
    s.append(["Total", *[len(by[t]) for t in tabs], sum(len(by[t]) for t in tabs)])
    s[s.max_row][0].font = Font(bold=True)
    s.append([])
    s.append(["Taken out because they are already in your files", len(repeats)])
    for how, n in Counter(r["how"] for r in repeats).most_common():
        s.append(["  " + how, n])
    for t, n in Counter(r["from_tab"] for r in repeats).most_common():
        s.append([f"  from the {t} tab", n])
    s.append([])
    s.append(["Notes"])
    s[s.max_row][0].font = Font(bold=True)
    for note in [
        "Checked against every tab of 'templates for week of 26th Nov.xlsx' and 'MASTER REFERENE OCT.xlsx' "
        "(company, parent company, brand/subsidiary and website columns, plus brands named in brackets).",
        "A company counts as already worked when its website matches, its name matches, or one of its brands "
        "or its parent group appears in your files (one conversation per group).",
        "Same-name matches that turned out to be different companies (e.g. Spire the utility vs Spire Global) "
        "were checked one by one and kept in this list.",
        "The 'Already in your files' tab shows each company taken out and where it was found.",
        "The earlier clean-up (subsidiaries, current F1 partners, bankrupt or sanctions-risk) is unchanged.",
    ]:
        s.append([note])
    s.column_dimensions["A"].width = 60
    for col in "BCD":
        s.column_dimensions[col].width = 16

    for t in tabs:
        sheet(wb.create_sheet(t), by[t])
    sheet(wb.create_sheet("Already in your files"), repeats,
          extra=(("Found in your files as", lambda r: r["ref_name"]), ("Where (file: tab)", lambda r: r["ref_where"]),
                 ("How matched", lambda r: r["how"]), ("Was on tab", lambda r: r["from_tab"])))
    wb.save(out_base + ".xlsx")

    fields = ["name", "tab", "sector", "f1_category", "funding_range", "round", "round_amount_m", "announced",
              "news_url", "source", "check", "industry", "clay_type", "country", "city", "size", "employees",
              "revenue", "domain", "linkedin", "entityId"]
    with open(out_base + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(r for t in tabs for r in by[t])

    print("repeats taken out:", len(repeats), "| left with a Check note (no decision):", undecided)
    print({t: len(by[t]) for t in tabs}, "| total fresh:", sum(len(by[t]) for t in tabs))
    print(Counter(r["how"] for r in repeats))


if __name__ == "__main__":
    main(*sys.argv[1:5])
