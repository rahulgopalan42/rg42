# Knowledge-scoring brief for connector-sourced parent companies (no web, no Clay/Apollo/Lusha)

Context: SPORTFIVE is building a Formula 1 sponsorship pipeline of ULTIMATE PARENT companies. The rows in
your input file came from Apollo / Lusha searches filtered on "total funding >= USD 100M"; the connectors
returned no funding or valuation figures, so we need your knowledge to (1) confirm each row is a real
ultimate parent, (2) confirm it is financially qualified, and (3) score it like an experienced sponsorship
salesperson. Today is 19 Oct 2026; use what you know up to mid-2026. Facts from memory only; never invent a
figure (use null).

## Input
Your task names ONE input file `/home/user/rg42/parents/score_in/chunk_NN.json`: a JSON array of rows
`[name, domain, hq_country_hint, exchange_hint, revenue_hint, industry_hint, naics_hint, children, connector_funding_flag]`.
`children` are companies Apollo says this company owns. Hints may be empty or wrong; trust your knowledge.

## Output
Write `/home/user/rg42/parents/score_out/chunk_NN.json` (same NN): a JSON array with EXACTLY one output row
per input row, in the same order, each row exactly these 25 fields:

`[in_name, status, parent_name, hq_country, domain, type, ticker, val_bn, val_basis, val_date, funding_m, sector, brand, approach, why, a, s, l, n, fin, f1, subs, conf, qualifies, note]`

1. `in_name` - the input name, copied exactly (used to join).
2. `status` - "P" this IS an ultimate parent / independently controlled group; "S" it is a subsidiary, brand,
   division or regional unit of another group (give that group in `parent_name`); "X" not a company worth
   listing (government body, university, fund vehicle, investment vehicle/SPV, defunct, acquired and absorbed,
   duplicate of a well-known parent under another name, sanctioned, tobacco); "U" you do not recognise it.
3. `parent_name` - the ultimate parent's name (same as input if status P; the controlling group if S; "" if X/U).
4. `hq_country` - HQ country of the parent (or "" if unknown).
5. `domain` - parent website domain, e.g. "siemens.com" ("" if unknown).
6. `type` - "listed" / "private" / "family" / "founder" / "PE-backed" / "state" / "cooperative" / "partnership" / "".
7. `ticker` - exchange:ticker if listed (e.g. "NYSE:ABC"), else "".
8. `val_bn` - valuation in USD billions (number, 1 decimal): market cap for listed, last-round / credible
   reported valuation for private; null if unknown.
9. `val_basis` - "market cap" / "last funding round" / "reported valuation" / "estimate" / "".
10. `val_date` - "YYYY-MM" of the figure (never later than 2026-06) or "".
11. `funding_m` - cumulative venture/growth/PE funding raised, USD millions (number) or null.
12. `sector` - PRIMARY sector number 1-48 (list below).
13. `brand` - the subsidiary / consumer brand that makes most commercial sense for an F1 deal (parent's own
    name if that is the strongest candidate).
14. `approach` - "G" group-level partnership better, or "B" brand-level better.
15. `why` - <= 18 words: why that brand / approach (audience, markets, launch, B2B showcase, hospitality...).
16. `a` audience overlap with F1 (0-4): F1 fans skew affluent, 18-54, global, plus senior B2B buyers.
17. `s` commercial synergies (0-4): client hospitality, technology showcase, product placement, retail
    activation, data/technology partner, market entry.
18. `l` brand alignment (0-4): performance, innovation, technology, precision, luxury, global ambition.
19. `n` international / F1-market relevance (0-4): active in several F1 race markets?
20. `fin` - <= 12 words of affordability evidence beyond valuation (profitable, cash-rich, large marketing
    spend, sponsors other sports, recent large raise) or "".
21. `f1` - "" if no current F1 link you know of; otherwise the deal (e.g. "McLaren partner", "owns Alpine F1",
    "Aston Martin title partner"). Include past-only deals as "former: ...".
22. `subs` - up to 6 well-known subsidiaries / brands / former names (list of strings; [] if none).
23. `conf` - "H" figures well known / "M" / "L" from memory, uncertain.
24. `qualifies` - "Y" if you know val_bn >= 1 or funding_m >= 100; "N" if you are fairly sure it meets
    neither (e.g. small company, valuation clearly < USD 1B and funding < USD 100M); "?" if you cannot tell.
    Revenue does NOT count. A connector_funding_flag of true is weak evidence only; still answer from knowledge.
25. `note` - <= 15 words for anything a reviewer should know ("merged into X 2024", "state-owned", "SPV", ...), or "".

For status X or U, fill fields 4-23 with "" / null / 0 / [] as appropriate, sector 48, qualifies "?".
For status S, score the PARENT group (brand may still be the input company if it is the best F1 brand).

Example output row:
`["Capgemini", "P", "Capgemini", "France", "capgemini.com", "listed", "EPA:CAP", 28.0, "market cap", "2026-05", null, 12,
 "Capgemini", "G", "B2B technology showcase and client hospitality across European and US race markets", 2, 4, 3, 4,
 "profitable; EUR 22bn revenue; sponsors Ryder Cup and Peugeot WEC", "", ["Sogeti", "Altran", "frog", "WNS"], "H", "Y", ""]`

## Sectors
1 Automotive & Mobility; 2 Aerospace, Defence & Space; 3 Airlines & Air Travel; 4 Travel, Hotels & Leisure;
5 Gambling & Gaming Venues; 6 Sports, Fitness & Events; 7 Video Games & Esports; 8 Software, Internet & AI;
9 Media, Entertainment & Publishing; 10 Telecommunications; 11 Semiconductors & Electronics;
12 IT Services & Consulting; 13 Banking & Lending; 14 Insurance; 15 Investment & Capital Markets;
16 Financial Services & Payments; 17 Oil, Gas & Fuels; 18 Utilities & Renewable Energy; 19 Mining & Metals;
20 Chemicals & Materials; 21 Industrial Machinery & Equipment; 22 Shipping, Maritime & Shipbuilding;
23 Logistics & Transportation; 24 Building Products & Materials; 25 Construction & Engineering; 26 Real Estate;
27 Home & Furniture; 28 Luxury, Jewellery & Watches; 29 Beauty & Personal Care; 30 Fashion, Apparel & Footwear;
31 Alcoholic Drinks; 32 Food & Beverage; 33 Tobacco & Nicotine; 34 Consumer Products; 35 Retail & E-commerce;
36 Pharma & Biotech; 37 Medical Devices & Diagnostics; 38 Healthcare Services; 39 Agriculture & Agribusiness;
40 Packaging & Printing; 41 Environmental & Waste Services; 42 Security Services; 43 Staffing & HR;
44 Marketing, Advertising & PR; 45 Government, Non-profit & Associations; 46 Professional & Business Services;
47 Education & Training; 48 Diversified & Other

## Rules
- Score like a salesperson: a mid-sized group with a real reason to be in F1 can outscore a giant with none.
- Valid JSON, double quotes. Build the file with a Python script in the scratchpad folder named in your task
  and validate with /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I:
  same row count and order as the input, 25 fields per row, numbers numeric, sector 1-48, a/s/l/n 0-4,
  status in P/S/X/U, qualifies in Y/N/?. Do not run git. Reply in 2 lines: rows written, count by status.
