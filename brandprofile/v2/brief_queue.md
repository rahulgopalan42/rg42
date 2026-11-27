# Brief (batch 2): research the discovered names that nobody has researched yet

Today is 27 November 2026. Read `v2/brief_discovery.md` (eligibility, routes, money rules, the JSON record in section 4, sector names).
Work from `/home/user/rg42/brandprofile`. Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

Your INPUT file holds companies that the discovery streams found but nobody researched: `name`, `website`, `hq_country`, `sector`,
`figure` (as stated where it was found), `metric`, `usd_m`, `source`, `via` ("Independent web research", "Clay" or "Multiple
sources") and, for Clay rows, `employee_count`, `clay_revenue` (a modelled bracket) and `desc`. Work through ALL of them, in file order.

For each company:
1. `v2/check.py "Name | website"` (many per call). IN MASTER / ALREADY DELIVERED / F1 PARTNER: leave out, one line in DUPS
   `{"name": "", "why": ""}`. check.py does not know every listed company: you must check listing yourself in step 2.
2. Open the company's own site (About / Investors / History) or its Wikipedia article (local-language version if richer). Decide:
   - its OWN shares trade on an exchange: DUPS, why "listed (exchange)";
   - it is only the national sales or legal entity of a foreign multinational, a division, a single site, or a careers page, with no
     commercial identity of its own (for example "Renault España", "Nestlé Suisse"): DUPS, why "not a separate company: part of X";
   - closed, merged away or in liquidation: DUPS with why;
   - otherwise it is eligible. A subsidiary that trades as its own brand stays in: name `parent_immediate`, `parent_ultimate` and
     `parent_listed`. Record `ownership_type`; write "requires verification" if no page says who owns it.
3. Financials. Keep the input figure as a `fin` entry: `metric`, `value_orig` = the figure text, `usd_m`, `period` if known, `source` =
   the input source, `kind` = "reported" when it comes from a ranking of company-reported revenue, "estimated" for a Clay bracket or
   any modelled figure. Add a newer reported figure if a page you open states one. For Clay rows also add `alt_indicators`
   (employees, countries) so Route C can apply. Never present a Clay bracket as a reported figure.
4. Write the full record (`brief_discovery.md` section 4) to MAIN when a route is met, or to WATCH when none is shown. Include
   `website`, `hq_city`, `hq_country`, `desc`, `model`, `customers`, `employees`, `countries`, `reach`, `markets`, honest `fit` ratings
   and a `fit_rationale` specific to the company (a local B2B firm with no consumer brand rates low: say so), `category_conflict`,
   `access`, `outstanding`, `sources` (every page you opened), `verified`, `conf`, plus `"discovered_via": "<the input's via>"` and
   `"discovery_source": "<the input's source>"`. Record `sponsorships` and `signals` only where a page you open shows them.
If you cannot open any page about a company, do not write a line; list it in NOTES under "not researched".

Pace: about two page fetches per company; guess the domain from the name, then try Wikipedia. WebSearch is limited to the number in
your task. WebFetch is not limited. Public pages only. No Apollo. No invented facts. Append as you go.
NOTES: researched (MAIN / WATCH), left out (listed / not a separate company / duplicates / other), not researched (names and why).
Final report: under 150 words.
