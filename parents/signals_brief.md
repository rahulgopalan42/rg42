# Sponsorship-signals brief (knowledge only: no web, no Clay/Apollo/Lusha; do not run git)

SPORTFIVE wants to judge whether a company could fund a Formula 1 sponsorship of about USD 2.5M per year and whether
F1 fits it, WITHOUT relying on valuation or revenue (often unknown for private companies). For every input row score
the nine signals below from what you know as of mid-2026. Today is 19 Oct 2026. Never invent evidence: if you know
nothing, score 0 and leave the evidence field empty. A 0 is a legitimate answer; a guessed 2 is not.

## Input
`/home/user/rg42/parents/signals_in/chunk_NNN.json`: rows
`[key, name, domain, hq_country, sector, type, val_bn, funding_m, revenue_hint, size_hint, tab]`
(`tab` A = new-prospect ranking, B = already in SPORTFIVE's databases; score both the same way).

## Output
`/home/user/rg42/parents/signals_out/chunk_NNN.json`: EXACTLY one row per input row, same order, 14 fields:
`[key, headcount, fund_recency, pe_owned, brand_hires, competitor_f1, motorsport, expansion, race_footprint, founder, evidence, ceo_name, conf, flag]`

Capacity signals (can they pay ~USD 2.5M/yr):
1. `headcount` 0-4: employees <100 = 0; 100-249 = 1; 250-999 = 2; 1,000-4,999 = 3; 5,000+ = 4. Use the size_hint if
   you know nothing better. Unknown = 0.
2. `fund_recency` 0-4: raised >= USD 50M in the last 18 months from tier-1 / sovereign / major growth investors = 4;
   raised >= USD 50M in the last 18 months = 3; last raise 18-36 months ago = 2; older raise only = 1; listed company
   with no raise needed or unknown = 0. (Listed groups score through headcount and PE fields instead.)
3. `pe_owned` 0-3: controlled by a large PE house (KKR, Blackstone, EQT, CVC, Carlyle, Apollo, TPG, Advent, Permira,
   Bain Capital, Hellman & Friedman, Cinven, PAI, Partners Group, Brookfield and peers) = 3; owned by a mid-size PE
   fund = 2; minority PE/growth investor only = 1; none/unknown = 0.
4. `brand_hires` 0-3: known recent CMO appointment or a public build-out of brand / partnerships / sponsorship roles
   = 3; visible marketing build-out (agency appointment, first big campaign) = 2; some brand-marketing activity = 1;
   unknown = 0.

Fit signals:
5. `competitor_f1` 0-3: a direct competitor is a current F1 or F1-team sponsor = 3; a competitor sponsors another
   top-tier motorsport or global sport property = 2; category has F1 history but no current rival = 1; none = 0.
6. `motorsport` 0-3: currently sponsors or supplies Formula E, WEC, IndyCar, MotoGP, F2/F3, NASCAR, Extreme E, sim
   racing or an F1 team supplier relationship = 3; past motorsport sponsorship (last 5 years) = 2; automotive /
   performance adjacency without a deal = 1; none = 0.
7. `expansion` 0-3: announced entry into new countries, pre-IPO / IPO within 18 months, rebrand, or a global product
   launch in 2025-26 = 3; one such moment but older or smaller = 2; steady growth, nothing announced = 1; none = 0.
8. `race_footprint` 0-3: active (offices, stores, customers) in 5+ F1 race-host countries = 3; 3-4 = 2; 1-2 = 1;
   none = 0. Host countries 2026: Australia, China, Japan, Bahrain, Saudi Arabia, USA, Canada, Monaco, Spain,
   Austria, UK, Belgium, Hungary, Netherlands, Italy, Azerbaijan, Singapore, Mexico, Brazil, Qatar, UAE.
9. `founder` 0-3 (founder / CEO / controlling-family affinity): 3 = documented participant (owns or owned a stake in
   a racing team or series, races, appears in the paddock or in Drive to Survive, known car collector); 2 = reported
   interest (interviews naming F1/motorsport as a passion, seen at Grands Prix); 1 = plausible through company
   culture (automotive or performance founders, publicly sporty leadership); 0 = nothing known.

Other fields: `evidence` <= 35 words naming the facts behind any non-zero score (e.g. "CEO X attends Monaco GP;
Series D USD 120M Mar 2026 led by Sequoia; competitor Y sponsors Team Z"); `ceo_name` the current CEO or founder
if known, else ""; `conf` "H"/"M"/"L"; `flag` "" or a short warning ("sanctioned", "defunct", "owned by W",
"current F1 sponsor: ...").

Validate with /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I:
row count and order, 14 fields, the nine scores integers in range. Helper scripts in the scratchpad folder named in
your task. Reply in 2 lines: rows written, count of rows with any non-zero signal.
