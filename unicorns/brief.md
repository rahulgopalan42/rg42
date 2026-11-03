# Private unicorn discovery brief (for research agents; do not run git; write only your own output file)

SPORTFIVE sells Formula 1 sponsorship (team partnerships, hospitality, race-level deals; typical cheque about
USD 2.5M a year). Rahul wants a list of PRIVATE companies worldwide that meet ALL of:
1. Valuation of USD 1 billion or more (latest priced round, or a credibly reported round / tender at >= USD 1B).
2. Total equity funding raised of USD 200 million or more (venture, growth, PE minority/growth equity; not debt).
3. Still private (not listed on a stock exchange) as of today, 30 Oct 2026; independent (not acquired and absorbed).
Any sector, any country. He especially wants FRESH, fast-rising names like CodeRabbit (AI code review, Series C
USD 143M at USD 1.5B, Aug 2026), Emerald AI (AI data-centre power flexibility, USD 150M Series A at USD 1.05B,
Aug 2026) and Mariana Minerals (software-driven mining, USD 310M Series B at USD 1.5B, Aug 2026). Long-standing
unicorns (Stripe, Databricks, Revolut ...) are also wanted - the list must be complete for your segment.

## How to work
- Start from your own knowledge: list every private company in your segment you believe is valued >= USD 1B.
- Then USE WebSearch / WebFetch (budget about 25-40 searches) to: (a) find 2025-2026 new unicorns and up-rounds in
  your segment (search e.g. "new unicorns <month> 2026", "<segment> raises Series C valuation billion 2026",
  Crunchbase News monthly unicorn round-ups, TechCrunch, Axios Pro, Reuters, Sifted, Inc42, 36Kr, etc.);
  (b) check status for names you are unsure about (IPO'd in 2025-26? acquired? down-round below USD 1B?);
  (c) fill missing valuation / funding figures for the most important names.
- Also include companies that FAIL one test if you know them (e.g. unicorn with only USD 120M raised, or IPO'd in
  2025, or acquired): list them with the correct status / figures; the build script filters them out. This is how
  we prove they were checked.
- Never invent a figure: unknown = null and lower confidence. Today is 30 Oct 2026.

## Output
`/home/user/rg42/unicorns/discover_out/<your code>.json`: a JSON array; each row EXACTLY these 37 fields:

`[brand, legal_name, parent, hq_country, hq_city, domain, sector, what, valuation_bn, valuation_date, valuation_basis,
funding_m, latest_round, status, investors, revenue_m, why, a, s, l, n, f1_status, f1_deal, sport_deals, headcount,
fund_recency, brand_hires, competitor_f1, motorsport, expansion, race_footprint, founder, evidence, ceo, conf,
source_url, note]`

- `brand` buyer-facing name; `legal_name` company name if different else ""; `parent` majority owner if any else "".
- `hq_country` (e.g. "USA", "UK", "China", "India", "Germany"); `hq_city`; `domain` main website domain ("brand.com").
- `sector` integer 1-48 (list below); `what` <= 12 words: what the company does.
- `valuation_bn` latest valuation in USD billions (number) or null; `valuation_date` "YYYY-MM"; `valuation_basis`
  "round" (priced round), "reported" (credible press report of round/talks/tender), "secondary" or "".
- `funding_m` total equity funding raised to date, USD millions (number) or null.
- `latest_round` <= 14 words, e.g. "Series C USD 143M, Aug 2026, Atomico & Smash Capital".
- `status` one of "private" (meets test 3), "public" (listed; say when in note), "acquired", "defunct",
  "below_1b" (latest valuation under USD 1B).
- `investors` <= 8 words, top investors. `revenue_m` latest revenue or ARR, USD millions, or null.
- `why` <= 18 words: the commercial reason this brand would buy F1 (audience, markets, launch, B2B hospitality).
- `a` audience overlap with F1, `s` commercial synergies, `l` brand alignment (performance, technology, precision,
  luxury), `n` international / race-market relevance: integers 0-4.
- `f1_status` "current" (F1, F1-team or Grand Prix sponsorship active in 2025 or 2026), "former", "none", "unsure".
  Formula E, IndyCar, NASCAR, esports, broadcast or game licences are NOT F1: put them in `sport_deals`.
  `f1_deal` <= 15 words naming the F1 deal or "". `sport_deals` <= 15 words on other sports sponsorships or "".
- Signals, integers: `headcount` 0-4 (0 <100 staff, 1 100-499, 2 500-1,999, 3 2,000-9,999, 4 10,000+);
  `fund_recency` 0-4 (raise in 2026 with top-tier investors 4, 2025 3, 2024 2, 2022-23 1, older 0);
  `brand_hires` 0-3 (new CMO / brand push 2025-26); `competitor_f1` 0-3 (a direct named competitor sponsors F1 now 3,
  same category on the grid 2, adjacent 1); `motorsport` 0-3 (product tied to motorsport/automotive performance);
  `expansion` 0-3 (new markets, launches, rebrand, IPO prep in 2025-26); `race_footprint` 0-3 (operates in many F1
  race markets 3, several 2, home market only 1); `founder` 0-3 (founder/CEO documented motorsport affinity 3,
  reported 2, plausible 1).
- `evidence` <= 30 words of facts behind non-zero signals. `ceo` CEO/founder name. `conf` "H"/"M"/"L" for the row.
- `source_url` one URL backing the valuation (from your web search) or "". `note` <= 15 words.

Sector numbers: 1 Automotive & Mobility; 2 Aerospace, Defence & Space; 3 Airlines & Air Travel; 4 Travel, Hotels &
Leisure; 5 Gambling & Gaming Venues; 6 Sports, Fitness & Events; 7 Video Games & Esports; 8 Software, Internet & AI;
9 Media, Entertainment & Publishing; 10 Telecommunications; 11 Semiconductors & Electronics; 12 IT Services &
Consulting; 13 Banking & Lending; 14 Insurance; 15 Investment & Capital Markets; 16 Financial Services & Payments
(incl. crypto); 17 Oil, Gas & Fuels; 18 Utilities & Renewable Energy; 19 Mining & Metals; 20 Chemicals & Materials;
21 Industrial Machinery & Equipment (incl. robotics); 22 Shipping & Maritime; 23 Logistics & Transportation;
24 Building Products; 25 Construction & Engineering; 26 Real Estate; 27 Home & Furniture; 28 Luxury, Jewellery &
Watches; 29 Beauty & Personal Care; 30 Fashion, Apparel & Footwear; 31 Alcoholic Drinks; 32 Food & Beverage;
33 Tobacco & Nicotine; 34 Consumer Products; 35 Retail & E-commerce; 36 Pharma & Biotech; 37 Medical Devices &
Diagnostics; 38 Healthcare Services (incl. digital health); 39 Agriculture; 40 Packaging; 41 Environmental & Waste;
42 Security Services; 43 Staffing & HR; 44 Marketing & Advertising; 45 Government & Non-profit; 46 Professional &
Business Services; 47 Education & Training; 48 Diversified & Other.

## Finish
- Write the file in pieces (append to partial JSON files in your own scratchpad folder, then merge) so no single
  answer hits an output limit. Validate with
  `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I <script>`:
  37 fields per row, integer scores in range, status in the allowed set, numbers numeric or null, no duplicate brands.
- Reply in 3 lines at most: rows written, how many status "private" with valuation >= 1 and funding >= 200, anything odd.
