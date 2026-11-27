# Brief (batch 2): independent web research, one sector in depth

Today is 27 November 2026. Read `v2/brief_discovery.md` first: eligibility, Routes A/B/C, money rules, the JSON record (section 4)
and the sector names all apply. This brief changes HOW you work. Work from `/home/user/rg42/brandprofile`.
Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

The user (Formula 1 sponsorship sales, SPORTFIVE) wants the widest credible universe of NEW non-public companies. Batch 1 reached only
the best-known names. Your job is depth in ONE area: go past the obvious brands to suppliers, service and technology providers,
distributors, commercially independent subsidiaries, family-owned, bootstrapped, state-backed and private equity-owned companies,
in every world region, using local-language sources outside English-speaking markets.

## Duplicates
`<python> -I v2/check.py "Name | site.com" ...` (40+ names per call). `IN MASTER` or `ALREADY DELIVERED` = leave out. `F1 PARTNER` = leave
out. `LISTED?` = leave out if it is that listed company. `POSSIBLE` = read it; same company, alias, old name or regional entity = leave
out. `NEW` = eligible (a note about the user's older 48-tab sheet does not exclude it; a note about a Grand Prix circuit page means
check for a current race deal first). Also check trading names, former names and the parent.

## Step 1: discover wide (the DISC file)
For every subsector in your task and every world region, open list-type sources and extract EVERY company named on them, not the first
few: largest-private-company rankings by country, trade-press sector rankings (top 50/100/250), family-business rankings, trade
association member lists, exhibitor lists of the main trade fairs, private equity and sovereign fund portfolio pages, government
export and investment promotion directories, registry-based rankings, acquisition announcements, sports sponsorship announcements,
manufacturer / supplier / distributor directories, regional business press. Search and read in the local language where it helps
(German, French, Italian, Spanish, Portuguese, Dutch, Nordic languages, Polish, Turkish, Japanese, Korean, Chinese, Arabic).
Write EVERY candidate you extract, whatever its check result, as one JSON line in DISC:

    {"name": "", "website": "", "hq_country": "", "sector": "", "subsector": "", "figure": "as stated on the page, e.g. EUR 2.1bn revenue 2024",
     "metric": "revenue|employees|aum|valuation|equity_funding|none", "usd_m": null, "source": "url of the list or page",
     "check": "NEW|IN MASTER|ALREADY DELIVERED|F1 PARTNER|LISTED|POSSIBLE", "stage": "researched|not researched|left out", "why": ""}

## Step 2: research (MAIN and WATCH)
Take the NEW candidates in order of size and Formula 1 relevance. For each, open the company's own site, annual report, registry page
or its Wikipedia article (local-language version if richer) and write the full record from `brief_discovery.md` section 4 to MAIN
(a route is met) or WATCH (attractive but no route shown). Add two fields to every record:
`"discovered_via": "Independent web research"` and `"discovery_source": "<url where you first found it>"`.
A company goes in MAIN only when you have (a) looked at who owns it and that its own shares do not trade, with the parent named for
a subsidiary, (b) a sourced Route A, B or C, and (c) a fit rationale specific to that company. A name you only read off a list stays in
DISC with stage "not researched": never write a MAIN line from a list alone. Do not lower the thresholds to add names.
If a page shows the brand already holds a Formula 1 championship, team or Grand Prix deal, leave it out and log it in DUPS.

## Step 3: keep going, then stop honestly
Work subsector by subsector and region by region. Stop a subsector when new sources give few new qualifying names. No quota.
NOTES (plain text): every source used with the number of names it gave; subsectors and regions covered; counts (names extracted,
run through check.py, IN MASTER, ALREADY DELIVERED, F1, listed, NEW, researched, MAIN, WATCH); and what remains unresearched: sources
you could not open, subsectors and regions not reached, DISC names not researched. Do not call anything exhaustive.

## Limits
WebSearch: the number in your task, in total; a refusal means stop searching, never route around it. WebFetch is not limited: use it
for everything else. Public pages only. No Apollo. No invented facts: `""` or `null` is fine. Append to files as you go.
Validate at the end: every line parses as JSON; no company twice in MAIN/WATCH. Final report: under 200 words, counts and main gaps.
