# Brief (batch 2): verify Clay leads on the web and write full records

Today is 27 November 2026. Read `v2/brief_discovery.md` (eligibility, routes, money rules, the JSON record in section 4, sector names).
Work from `/home/user/rg42/brandprofile`. Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

Your INPUT file holds companies pulled from Clay's company search: name, domain, country, industry, employee count, a modelled revenue
bracket and a short description. Clay is only a lead: its revenue is a modelled bracket, and it marks many listed companies and
subsidiaries of listed groups as "Privately Held". Verify each one on the web, largest first, in file order.

For each company:
1. `v2/check.py "Name | domain"` (many per call). IN MASTER / ALREADY DELIVERED / F1 PARTNER: leave out, one line in DUPS
   `{"name": "", "why": ""}`.
2. Open its own site (About / Investors / History) or its Wikipedia article (local-language version if richer). Establish whether its
   OWN shares trade. If they do: DUPS, why "listed (exchange)". If it is a division or a local branch with no commercial identity of
   its own (for example one casino, one country office, a careers page of a parent): DUPS, why "not a separate company: part of X".
   A subsidiary that trades as its own brand is eligible; name the immediate and ultimate parent and whether the parent is listed.
3. Financials: look for a reported figure (annual report, registry, Wikipedia infobox with a source, credible ranking). If you find one,
   record it. If not, record Clay's bracket as `{"metric": "revenue", "value_orig": "<bracket> (Clay estimate)", "usd_m": <lower bound>,
   "kind": "estimated", "source": "<the LinkedIn url from the input>"}` and add other indicators (employees, countries) under
   `alt_indicators` so Route C can apply. A Clay bracket alone is an estimate, never a reported figure.
4. Write the full record to MAIN (a route is met) or WATCH (no route shown), with a company-specific `fit_rationale`, honest `fit`
   ratings, `category_conflict`, `access`, `sources` (every page you opened), `"discovered_via": "Clay"` and
   `"discovery_source": "Clay company search"`. Set `discovered_via` to "Multiple sources" only if your task says so.
If you cannot open any page about a company, do not write a line; list it in NOTES under "not verified".

Pace: about two fetches per company. WebSearch is limited to the number in your task. WebFetch is not limited. Public pages only.
No Apollo. No invented facts. Append as you go. NOTES: verified, left out (listed / not a separate company / duplicates), not verified.
Final report: under 150 words.
