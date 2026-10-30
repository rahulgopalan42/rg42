# New-brand verification and scoring brief (knowledge only: no web, no Clay/Apollo/Lusha/Crunchbase; do not run git)

SPORTFIVE sells Formula 1 sponsorship (team partnerships, hospitality, race-level deals; typical cheque about USD 2.5M
a year). Rahul wants NEW brands for his pipeline. Every input row is a company that is NOT on his existing sheets.
Your job: for each row, say what it really is, whether it meets his money rule, whether it already has an F1 deal, and
score it like an experienced sponsorship salesperson. Today is 30 Oct 2026; use what you know up to mid-2026. Facts
from memory only. Never invent a figure: unknown = null and lower confidence.

## Rahul's money rule (exactly one of these must hold; nothing else counts)
- FUNDING: total equity funding raised above USD 200 million (venture, growth, PE investment; not debt, not revenue).
  Any ownership type (public, private, founder/self-owned, family, partnership, PE-backed, cooperative).
- LISTED REVENUE: the company is publicly listed on a stock exchange AND has annual revenue (or ARR) of USD 100 million
  or more.
A private company with big revenue but no funding above USD 200M does NOT qualify. A listed company with revenue below
USD 100M does NOT qualify, however large its market cap.

## Input
`/home/user/rg42/brands200/verify_in/chunk_NNN.json`: rows `[key, name, domain, country_hint, exchange_or_ticker_hint,
revenue_hint, market_cap_hint_bn, owner_hint, source]`. Hints come from Apollo or a market-cap listing; they may be
empty or wrong. `source` "apollo_funding_100m+" means Apollo lists total funding of at least USD 100M (not 200M).

## Output
`/home/user/rg42/brands200/verify_out/chunk_NNN.json`: EXACTLY one output row per input row, same order, each row
exactly these 38 fields:

`[key, status, brand, parent, hq_country, domain, type, ticker, revenue_m, revenue_year, funding_m, qualifies, rule,
sector, approach, why, a, s, l, n, fin, f1_status, f1_deal, headcount, fund_recency, pe_owned, brand_hires,
competitor_f1, motorsport, expansion, race_footprint, founder, evidence, ceo, conf, note, sport_deals, cmo_or_marketing]`

1. `key` - copied exactly from the input.
2. `status` - "P" independent company (its own ultimate parent, or a group in its own right with its own marketing
   budget); "S" brand, subsidiary or regional unit of another group (name it in `parent`); "X" not worth listing
   (fund or investment vehicle, SPAC, government body or regulator, university, hospital charity, non-profit, sports
   club or league or race promoter, defunct, acquired and absorbed, tobacco, sanctioned country); "U" you do not
   recognise it - do not guess.
3. `brand` - the consumer- or buyer-facing brand to pitch (usually the company itself).
4. `parent` - ultimate parent (the company itself if status P).
5. `hq_country` 6. `domain` - main website domain (e.g. "brand.com"), "" if unsure.
7. `type` - "listed" / "private" / "founder" / "family" / "PE-backed" / "state" / "partnership" / "cooperative".
8. `ticker` - "EXCHANGE:CODE" for listed companies, else "".
9. `revenue_m` - latest annual revenue or ARR in USD millions (number) or null. 10. `revenue_year` - e.g. 2025.
11. `funding_m` - total equity funding raised in USD millions (number) or null (null for listed incumbents that never
    raised venture money).
12. `qualifies` - "Y" the money rule holds on figures you are fairly sure of; "N" it clearly fails; "?" unsure.
13. `rule` - "funding" or "listed_revenue" (the one that holds), "" if none.
14. `sector` - 1-48 from the list below. 15. `approach` - "G" group-level or "B" brand-level deal.
16. `why` - <= 18 words: the commercial reason this brand would buy F1 (audience, markets, launch, B2B hospitality).
17-20. `a` audience overlap with F1, `s` commercial synergies, `l` brand alignment (performance, technology,
    precision, luxury), `n` international / race-market relevance: integers 0-4.
21. `fin` - <= 12 words of affordability evidence (profitable, recent raise, big marketing spend, sponsors other sport).
22. `f1_status` - "current" (an F1, F1-team or Grand Prix sponsorship or partnership active in 2025 or 2026, held by
    this company or its parent group), "former", "none" or "unsure". Formula E, IndyCar, broadcast rights and game
    licences are NOT F1 sponsorships: mention them in `sport_deals` instead. 23. `f1_deal` - <= 15 words naming the
    deal ("" if none).
24-32. Sponsorship signals, integers: `headcount` 0-4 (0 under 100 staff, 1 100-499, 2 500-1,999, 3 2,000-9,999,
    4 10,000+); `fund_recency` 0-4 (raise or IPO in 2025-26 with top-tier investors 4 ... none known 0; listed
    incumbents without a recent raise 0); `pe_owned` 0-3 (owned by a large PE house 3, mid-size 2, minority PE 1);
    `brand_hires` 0-3 (new CMO or brand chief or big brand push in 2025-26); `competitor_f1` 0-3 (a direct named
    competitor currently sponsors F1: 3; same category on the grid: 2; adjacent: 1); `motorsport` 0-3 (product or
    history tied to motorsport); `expansion` 0-3 (new markets, IPO, rebrand, launch in 2025-26); `race_footprint`
    0-3 (operates in many F1 race markets 3, several 2, home market only 1); `founder` 0-3 (founder or CEO with
    documented motorsport or F1 affinity 3, reported 2, plausible 1).
33. `evidence` - <= 35 words naming the facts behind non-zero signals (no facts -> keep the score at 0).
34. `ceo` - CEO or founder name, or "". 35. `conf` - "H", "M" or "L" for the row as a whole.
36. `note` - <= 15 words (e.g. "acquired by X in 2025", "Apollo funding looks like parent's").
37. `sport_deals` - <= 15 words on other sports sponsorships known ("" if none).
38. `cmo_or_marketing` - CMO / marketing head name if known, else "".

## Rules
- Parent level matters: if the row is a subsidiary, set status "S" and name the ultimate parent. Do NOT swap the row
  for its parent; keep the row's own brand.
- Apollo funding on a subsidiary often reflects funding raised before it was acquired: if the brand was acquired and
  absorbed, status "X" with a note.
- Current F1 sponsors must still be listed (status as normal) with f1_status "current"; they will be set aside.
- Sector numbers: 1 Automotive & Mobility; 2 Aerospace, Defence & Space; 3 Airlines & Air Travel; 4 Travel, Hotels &
  Leisure; 5 Gambling & Gaming Venues; 6 Sports, Fitness & Events; 7 Video Games & Esports; 8 Software, Internet & AI;
  9 Media, Entertainment & Publishing; 10 Telecommunications; 11 Semiconductors & Electronics; 12 IT Services &
  Consulting; 13 Banking & Lending; 14 Insurance; 15 Investment & Capital Markets; 16 Financial Services & Payments;
  17 Oil, Gas & Fuels; 18 Utilities & Renewable Energy; 19 Mining & Metals; 20 Chemicals & Materials; 21 Industrial
  Machinery & Equipment; 22 Shipping, Maritime & Shipbuilding; 23 Logistics & Transportation; 24 Building Products &
  Materials; 25 Construction & Engineering; 26 Real Estate; 27 Home & Furniture; 28 Luxury, Jewellery & Watches;
  29 Beauty & Personal Care; 30 Fashion, Apparel & Footwear; 31 Alcoholic Drinks; 32 Food & Beverage; 33 Tobacco &
  Nicotine; 34 Consumer Products; 35 Retail & E-commerce; 36 Pharma & Biotech; 37 Medical Devices & Diagnostics;
  38 Healthcare Services; 39 Agriculture & Agribusiness; 40 Packaging & Printing; 41 Environmental & Waste Services;
  42 Security Services; 43 Staffing & HR; 44 Marketing, Advertising & PR; 45 Government, Non-profit & Associations;
  46 Professional & Business Services; 47 Education & Training; 48 Diversified & Other.
- Write the output in two or three pieces (append to a partial JSON file in your scratchpad folder, then merge) so one
  long answer does not hit an output limit. Then validate with
  `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`: same row count
  and key order as the input, 38 fields per row, integer scores in range, qualifies in Y/N/?, status in P/S/X/U.
  Keep helper scripts in the scratchpad folder named in your task.
- Reply in 3 lines at most: rows written, counts by status and by qualifies, anything odd.
