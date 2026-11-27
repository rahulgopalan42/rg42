# Brief (batch 2): finish the assessment of companies found on rankings

Today is 27 November 2026. Read `v2/brief_discovery.md` (eligibility, routes, JSON record in section 4, sector names).
Work from `/home/user/rg42/brandprofile`. Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

Your INPUT file holds records from batch 1 that carry a sourced revenue figure from a ranking page, but nobody checked who owns each
company or wrote a company-specific Formula 1 case, so they were not ranked. Finish them, in file order, all of them.

For each company:
1. `v2/check.py "Name | site"` (many per call). IN MASTER / ALREADY DELIVERED / F1 PARTNER: leave out, one line in DUPS
   `{"name": "", "why": ""}`. LISTED?: leave out if it is that listed company.
2. Open the company's own website (About / Ownership / History) or its Wikipedia article. Establish: website, HQ city and country,
   what it does (`desc`), `ownership_type`, `parent_immediate`, `parent_ultimate`, `parent_listed` (a subsidiary of a listed group is
   eligible, but the parent must be named), employees, countries, `reach`, `markets`, `model`, `customers`.
   If its own shares trade, or it was closed or absorbed into another company, leave it out and say why in DUPS.
3. Rate `fit` and write a `fit_rationale` specific to the company. Be honest: a regional contractor or local broker with no consumer
   brand and local customers rates low on most lines; say that plainly. Do not inflate.
4. `sponsorships` (sports teams, stadium naming, events) and `signals` only where a page you open shows them. Do not hunt for them.
5. Keep the input's `fin` entries unchanged; add a newer figure only if a page you open states it.
6. Fill `access`, `category_conflict`, `f1_markets`, `outstanding`, `sources` (add every page you opened), `verified`, `conf`.
   Add `"discovered_via": "Independent web research"` and `"discovery_source": "<the ranking url from the input>"`.
Write the finished record to MAIN (full record, `brief_discovery.md` section 4). If you cannot find any page for a company, do not
write a line for it; list it in NOTES under "not assessed".

Pace: about two page fetches per company. Guess the domain from the name, then try Wikipedia. WebSearch is limited to the number in
your task: keep it for large companies you cannot locate. WebFetch is not limited. Public pages only. No Apollo. No invented facts.
Append as you go. NOTES: how many assessed, left out (with reasons), not assessed (names), and ownership types found.
Final report: under 150 words.
