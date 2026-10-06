# Wave 14 verification brief — v3 parameters (rebuilt 6 Oct 2026)

You verify F1 sponsorship prospect candidates for SPORTFIVE. Input: a JSON array of ~10 candidates at the path in your task (fields: company, sector_tab, pool; verify from scratch). Output: a JSON array at the output path in your task, one object per candidate, schema EXACTLY:
{"company","sector_tab","domain","hq","ownership","sells","headcount_band","revenue","valuation","latest_raise","fit_score","fit_detail","up_and_coming","flags","verdict","verdict_reason","best_angle"}
Keep "company" EXACTLY as the input string. sector_tab = input's sector_tab. up_and_coming is true/false. flags is a list of short strings. fit_score is an integer 0-4. Date and source every figure in the field text; mark estimates "(est)".

## Hard filters (fail any = verdict "No", name the filter in verdict_reason)
1. Valuation USD 1 billion or above: market cap (listed), post-money of a TRANSACTED round, or EV, dated and sourced. Exactly USD 1.0B passes. Listed below USD 1B = No. Private with no published valuation: VC-backed = No; family-, foundation-, co-op-, state- or employee-owned passes on revenue > USD 1B or clear market leadership, capped at Stretch with flag "no published valuation". A valuation from a round that has not closed does not count.
2. Headcount 51 or more.
3. Capacity ~USD 2.5M/yr: fail ONLY on genuine distress (going-concern doubt, insolvency/judicial recovery, wind-down, acquired/absorbed, layoffs >15% with shrinking revenue). Cost programmes at profitable companies = flag "cost programme", not a fail.
4. No F1 tie: team partner/sponsor/supplier/licensing deal with a current team, F1 global/regional partner, Grand Prix or promoter partner (any GP), F1 Academy partner, or driver personal sponsor/ambassador. Counts if direct or via a CONTROLLING parent (>50% or joint control) or a controlled brand/subsidiary. A minority holder (<50%) that sponsors F1 = flag "minority holder sponsors F1", cap at Stretch. A lapsed deal with no evidence of renewal = flag, cap at Stretch, say "confirm before outreach". Sibling companies under a common owner = flag only.
5. Not sanctioned (OFAC SDN, EU/UK), not on the US Entity List, not HQ in Russia or Iran. US DoD Section 1260H listing and DHS UFLPA Entity List = treat as No (precedents: CXMT, Quectel, NIO, CRRC, COSCO, Zijin). A sanctioned subsidiary makes the group No. Record "Entity List status not confirmed" as a flag when you could not check the official list.
6. Duplicate: if the candidate is the same company as one already verified in this wave or on the master sheets (same domain, renamed, or the parent of an already-listed entity), verdict "No" with verdict_reason "duplicate of excluded name". A generic-token name clash alone is NOT a duplicate.

## Flags only, never a reason to reject
revenue unknown or < USD 100M; concentrated customers; ownership type (PE, family, state, sovereign, royal); state-linked (majority government); PEP-linked owner; gambling; PE-owned 4+ years; valuation > 50x revenue; recent ownership change; pre-revenue (passes if valued >= USD 1B and funded within 24 months). Alcohol: no flag.

## Fit score 0-4 (one point each)
sells in 3+ F1 markets; buyers affluent 25-54 or senior decision makers; brand story maps to performance, technology, precision or global ambition; category not already taken on the grid (banking, airline, logistics, oil, tyres, watches, crypto, cyber, beer, spirits, automotive, cloud are crowded: score 0).

## Verdicts
Yes = passes, fit >= 2, credible marketing motive. Stretch = passes with one real reservation (unpublished valuation, recent ownership change, capacity doubt, minority-holder or lapsed tie, fit exactly 2 with weak angles). Low-value = passes but fit 0-1, or pre-revenue with no marketing function, or pure B2B supplier with concentrated customers and no brand ambition, or state entity with no consumer brand, or single-country mass-market retailer/utility/regional bank with no F1 motive. No = a hard filter failed.

## up_and_coming (true/false)
crossed USD 1B within 24 months; revenue or headcount growing > 40%/yr; 2025-26 IPO; visible challenger taking share; or an announced 2025-26 entry into a new country/region, recorded in flags as "market expansion: from -> to".

## Known controlling-parent ties (see f1_ties_found.json in the same directory for the full list)
Alibaba (Chinese GP), ByteDance/TikTok (Aston Martin), Suntory (Jim Beam/Cadillac), SBI (Las Vegas GP), Krafton, Genting (Singapore GP), stc (Saudi GP), Hinduja/Gulf Oil (Williams), e& (Abu Dhabi GP), ADNOC/XRG, Mubadala, TWG Global (Cadillac), Unilever, Pernod Ricard, M&S, Sanofi, L'Oreal, William Grant, Deutsche Telekom/T-Mobile, Richemont/IWC, EssilorLuxottica, Flutter, Entain, Monster, Brown-Forman, PVH, RH, Energizer, MGM Resorts, Las Vegas Sands, Sphere, Couche-Tard, Grupo BAL, Banamex, Aeromexico, Authentic Brands/Reebok. Heineken, Qatar Airways, Aramco, Santander, Salesforce, Accenture, CrowdStrike, Oracle, AWS, DHL, Pirelli, LVMH, Lenovo, MSC, American Express, Mastercard, Visa are F1 or team partners: a company they CONTROL = No; a company where they hold a minority stake = flag.

## Search budget
At most 2 WebSearch per listed company (one for market cap/headcount/revenue, one for F1 ties), at most 3 per private company. WebFetch is free (use stockanalysis.com, companiesmarketcap, Wikipedia, team partner pages, formula1.com partners page, GP partner pages). Write ALL records before stopping; if the budget runs out, write what you have and say which remain. Report tally and hard-filter failures.
