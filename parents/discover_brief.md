# Parent-company discovery brief (knowledge only: no web, no Clay/Apollo/Lusha)

You are building a new-business pipeline for SPORTFIVE's Formula 1 sponsorship sales team. Think like an
experienced sponsorship salesperson: which corporate groups have the money AND a commercial reason to put
their brand on an F1 car, a race or F1 hospitality? Today is 19 Oct 2026. Use what you know up to mid-2026.

## Your task
Your task names ONE category/region. List as many financially qualified ULTIMATE PARENT companies in that
category as you can (target 100-120; fewer is fine if the category is small, never pad with unqualified
or made-up companies). Write them to the output file named in your task.

## Financial qualification (at least ONE must hold; revenue does NOT count)
- Valuation >= USD 1 billion: market capitalisation for listed groups, last-round or credible reported
  valuation for private groups. Give your best-known figure and its date.
- OR cumulative funding raised >= USD 100 million (venture / growth / PE funding; not debt, not revenue).
If you do not know either figure for a company, do NOT include it.

## Parent level, not subsidiaries
- One record per ultimate parent or independently controlled group (e.g. "LVMH", not "Louis Vuitton"
  and "Sephora" separately; "Alphabet", not "YouTube"). State-owned groups count as parents.
- A company with a minority investor is still its own parent (Ferrari is NOT a subsidiary of Exor).
- Skip companies that are themselves current Formula 1 or F1-team sponsors/partners/owners, unless you are
  unsure; if unsure, include them and fill the `f1` field.

## Output format
A JSON array, one array per parent company, exactly these 21 fields in this order:

`[name, hq_country, domain, type, ticker, val_bn, val_basis, val_date, funding_m, sector, brand, approach, why, a, s, l, n, fin, f1, subs, conf]`

1. `name` - ultimate parent company name (English).
2. `hq_country` - headquarters country.
3. `domain` - parent website domain (e.g. "lvmh.com"); "" if unknown.
4. `type` - "listed" / "private" / "family" / "founder" / "PE-backed" / "state" / "cooperative" / "partnership".
5. `ticker` - exchange:ticker for listed parents (e.g. "EPA:MC"), else "".
6. `val_bn` - valuation in USD billions (number, 1 decimal) or null if unknown.
7. `val_basis` - "market cap" / "last funding round" / "reported valuation" / "estimate" / "".
8. `val_date` - "YYYY-MM" of the figure you know, or "" (use your best memory; never later than 2026-06).
9. `funding_m` - cumulative funding raised in USD millions (number) or null if unknown/not applicable.
10. `sector` - number 1-48 of the parent's PRIMARY sector (list below).
11. `brand` - the subsidiary or consumer-facing brand that makes the most commercial sense for an F1 deal
    (the parent's own name if the parent is the strongest candidate).
12. `approach` - "G" (group-level partnership is better) or "B" (brand-level is better).
13. `why` - <= 18 words: why that brand / that approach (audience, markets, launch, B2B showcase, etc.).
14. `a` audience overlap with F1 (0-4): F1 fans skew affluent, 18-54, global; plus senior B2B buyers.
15. `s` commercial synergies (0-4): hospitality for clients, technology showcase, product placement, retail
    activation, data/technology partner, market entry.
16. `l` brand alignment (0-4): performance, innovation, technology, precision, luxury, global ambition.
17. `n` international / F1-market relevance (0-4): active in several F1 race markets?
18. `fin` - <= 12 words of affordability evidence beyond valuation (profitable, cash-rich, big marketing
    spend, sponsors other sports, recent large raise) or "".
19. `f1` - "" if no current F1 link you know of; otherwise the deal (e.g. "McLaren partner", "owns Alpine F1").
20. `subs` - up to 6 well-known subsidiaries / brands / former names, as a list of strings (used to
    cross-check against existing databases). [] if none.
21. `conf` - "H" (figures well known), "M", or "L" (from memory, uncertain).

Example row:
`["Kering", "France", "kering.com", "listed", "EPA:KER", 30.0, "market cap", "2026-05", null, 28, "Gucci", "B",
 "Gucci's global affluent 25-45 audience and Italian racing heritage; group deal dilutes brand story", 4, 3, 4, 4,
 "profitable; large global marketing budgets", "", ["Gucci", "Saint Laurent", "Bottega Veneta", "Balenciaga", "Boucheron"], "H"]`

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
- Facts from memory only; mark uncertain figures conf "L". Never invent a valuation or funding figure: use null.
- Prefer companies with a real commercial reason to be in F1 over the merely large; include mid-sized qualified
  groups (USD 1-5B) with strong fit, not only giants.
- No sanctioned companies (Russia, Iran, Belarus, Syria, North Korea); no tobacco (F1 advertising limits).
- Valid JSON, double quotes, one Write call for the whole file. Then validate with Python (21 fields per row,
  numbers numeric, sector 1-48, a/s/l/n 0-4) using
  /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I.
  Keep any helper script inside the scratchpad folder named in your task. Reply in 2 lines: count written, validated.
