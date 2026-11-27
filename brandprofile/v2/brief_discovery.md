# Brief: new non-public companies for a Formula 1 sponsorship prospect list (revised methodology, 27 Nov 2026)

Today is 27 November 2026. The user sells Formula 1 sponsorships for SPORTFIVE. Their existing lists lean towards venture-backed
technology companies. Your job is to find **genuinely new** non-public operating companies in ONE sector cluster (named in your task),
world-wide, and to record the evidence for each. Be broad in discovery and strict about evidence: every fact must come from a page
you open in this session. `""` or `null` is an acceptable answer for a field; an invented or remembered fact is not.

Work from `/home/user/rg42/brandprofile`. Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

## 1. The duplicate check comes first (mandatory)

The user must not receive any brand that is already on their master spreadsheet. Before you spend time on a candidate, run

    <python> -I v2/check.py "Company A | companya.com" "Company B" ...

(many names per call; the website is optional but helps).
- `IN MASTER` = already on the user's master spreadsheet (or already delivered). **Leave it out.** Write one line to your DUPS
  file: `{"name": "...", "why": "<the text check.py printed>"}`.
- `F1 PARTNER` = the brand holds a current Formula 1 deal. Leave it out and log it in DUPS.
- `LISTED?` = the name matches a listed company. If it is that company, leave it out and log it in DUPS. If it is a different,
  unlisted company with the same name, keep going.
- `POSSIBLE` = close to a name on the master. Same company, an alias, an old name, or the same brand under a different legal
  suffix: leave it out and log it in DUPS. A clearly different company: keep going.
- `NEW` = not on the master: eligible. A note may say the company is on the user's older 48-tab sheet or was seen in earlier
  research; **that does not exclude it** (user's instruction: only the master spreadsheet counts as a duplicate).
Also check trading names, former names and the parent's name. A regional entity or an alias of a registered company is a duplicate.
A subsidiary or operating brand is allowed only if that brand itself is not registered, has its own commercial identity, and you can
make an independent partnership case for it.

## 2. Who is eligible

Any commercially relevant operating company whose own shares are not publicly traded: venture-backed, bootstrapped, founder- or
family-owned, private equity-backed, privately held multinationals, state-owned, sovereign fund-backed, subsidiaries of listed or
private groups (the subsidiary's own shares must not trade), operating asset managers, wealth managers, private banks, private equity
and alternative investment firms, and joint ventures that trade as independent businesses.

Leave out: companies whose own shares trade; closed or in liquidation; passive funds with no operating business; single-project
vehicles; **Russian companies**; companies under sanctions or with established serious compliance problems; and any brand that holds
a current Formula 1 championship, team or Grand Prix deal (check.py flags these; the roster is the paragraph starting "Current Formula 1
roster" in `brief_check.md`). Do NOT leave a company out because a sister company or its parent sponsors F1: include it and say so in
`category_conflict`.

Do not leave a company out because it publishes no accounts, never raised venture money, has no recent funding, shows no buying
signal, sells mainly in one country, or gets little press.

## 3. Qualification: meeting ONE route is enough

**Route A (standard), any one of:** total equity funding USD 100M+ · annual revenue USD 150M+ · ARR USD 50M+ · annual EBITDA USD 20M+ ·
valuation USD 1B+ · acquisition/transaction value USD 1B+ · assets under management USD 5B+ · substantial paid sponsorship (credible
evidence) · documented parent-company or state financial backing with a commercial mandate.

**Route B (exceptional):** equity funding USD 75M to <100M, or revenue USD 75M to <150M, or valuation USD 500M to <1B, or a transaction
below USD 1B, **plus** stated supporting strength (profitability, high margins, cash flow, recurring revenue, fast growth, marketing
spend, backing, significant sports sponsorship). Write the support in `exception_note`.

**Route C (alternative, no financials published):** at least TWO independent, sourced indicators of real scale, for example a credible
third-party revenue estimate of USD 150M+, 500+ employees (fewer is fine for high-margin software or finance), operations in 3+
countries, 100+ stores, plants or fleet of evident scale, named enterprise customers or major contracts, an industry ranking, paid
sports sponsorships or major advertising. Two indicators that restate one fact count once.

If a company is strategically attractive but meets no route, write it to your WATCH file instead (same format, `"route": "none"`).

Money rules: equity is not debt. Record debt, project finance, credit facilities, secondary sales and acquisition price as what they
are; never count them as equity funding. Prefer figures from the last three financial years; flag older ones. Convert at these fixed
rates and keep the original figure: EUR 1.10, GBP 1.30, CHF 1.15, CAD 0.73, AUD 0.66, SGD 0.75, JPY 0.0067, CNY 0.14, INR 0.012,
KRW 0.00073, SEK 0.095, NOK 0.095, DKK 0.147, BRL 0.18, MXN 0.055, AED 0.272, SAR 0.267, ZAR 0.055, TRY 0.025, PLN 0.25.
Revenue, valuation, AUM, GMV, transaction volume and cash are different things: label each correctly.

## 4. Output: one JSON object per line

    {"name": "", "website": "", "aliases": [], "hq_city": "", "hq_country": "",
     "sector": "",            // one of the names in section 6
     "subsector": "",         // 2-6 words
     "desc": "",              // what it does, one factual sentence of 12-22 words
     "products": "", "model": "B2B|B2C|Hybrid", "customers": "",
     "ownership_type": "venture-backed|bootstrapped|founder-owned|family-owned|private equity-backed|privately held group|state-owned|sovereign fund-backed|subsidiary of listed group|subsidiary of private group|partnership|co-operative or mutual|joint venture|foundation-owned|requires verification",
     "parent_immediate": "", "parent_ultimate": "", "parent_listed": "listed|private|state|none|requires verification",
     "pe_swf_owner": "",      // controlling private equity or sovereign fund owner, if any
     "minority_investors": "",
     "marketing_autonomy": "yes|no|unknown", "marketing_autonomy_basis": "",
     "parent_backing": "",    // documented financial support from the parent or the state, with the page; "" if none found
     "employees": null, "countries": null, "stores_or_sites": "",
     "markets": "",           // where it operates today, 8-25 words
     "expansion_markets": "", // announced expansion, or ""
     "reach": "Global|International|Regional|Domestic",   // Global = North America, Europe and Asia-Pacific at scale; International = 2+ world regions; Regional = several countries in one region; Domestic = essentially one country
     "route": "A|B|C",
     "fin": [{"metric": "revenue|arr|ebitda|net_income|equity_funding|debt_funding|valuation|transaction_value|aum|marketing_spend|operating_budget",
              "value_orig": "EUR 1.2bn", "usd_m": 1320, "period": "FY2025", "published": "2026-04", "kind": "reported|estimated|inferred", "source": "url"}],
     "qualifying_metric": "", // the metric that meets the route, e.g. "revenue"
     "alt_indicators": [{"indicator": "", "evidence": "", "source": "url"}],   // Route C only
     "exception_note": "",    // Route B only
     "profitability": "profitable|loss-making|unknown", "profitability_basis": "",
     "distress": "",          // layoffs, restructuring, liquidity trouble found, or ""
     "sponsorships": [{"rights_holder": "", "sport": "", "designation": "", "announced": "", "duration": "", "value": "", "source": "url"}],
     "signals": [{"category": "capital|geographic|marketing|commercial|strategic", "what": "", "date": "YYYY-MM", "status": "confirmed|inferred", "source": "url"}],
     "fit": {"b2b": 0, "ecosystem": 0, "technical": 0, "hospitality": 0, "geography": 0, "brand": 0, "consumer": 0, "category": 0},
     "fit_rationale": "",     // 15-35 words, specific to THIS company; never "F1 gives global exposure"
     "customer_overlap": "",  // F1 teams, partners or suppliers that are its customers or partners, only if a page says so
     "category_conflict": "none found|potential: <current F1 partner(s) in the same category>|established: <what>",
     "f1_markets": "",        // Grand Prix countries that match its markets
     "access": {"owner_led": "yes|no|unknown", "marketing_head_identified": "yes|no", "structure": "lean|mid|complex", "roles": ""},
     "compliance": "",
     "outstanding": "",       // what still needs verifying
     "sources": ["url"], "verified": "2026-11-27", "conf": "high|medium|low"}

`signals`: only events of the past 24 months (since Dec 2024), each with a date and page. One corporate event = one signal, however
many articles report it. Categories: capital (equity round, growth or PE investment, IPO preparation, acquisition, ownership change,
spin-off); geographic (new market, office, plant, distribution); marketing (new CMO or senior marketing hire, rebrand, major campaign,
ambassador, new sponsorship, more marketing spend); commercial (major customer win, product launch, new division, distribution deal);
strategic (a direct competitor entered F1 or raised its sports spend, stated global brand ambition, leadership interest in motorsport).
Mark it `inferred` unless a page states it.

`fit` ratings: 0 = none, 1 = weak, 2 = credible, 3 = strong and specific. `b2b` = value of access to enterprise buyers and senior
decision-makers; `ecosystem` = its customers, distributors or partners are already in F1; `technical` = its product could really be
used by a team (do not assume); `hospitality` = race hospitality would help it win or keep customers; `geography` = the race calendar
matches its markets and expansion plans; `brand` = F1 would build awareness, credibility or premium positioning it needs;
`consumer` = it could run consumer campaigns, licensing or retail promotions; `category` = 3 if no current F1 partner sells the same
thing, 2 if one or two teams have a rival, 1 if the category is crowded, 0 if it is blocked.

`access`: `owner_led` = the founder, owner family or a named CEO visibly runs the company; `structure` = lean (one brand, one
management team), mid, or complex (many divisions, ministries or layers between you and the budget); `roles` = the job titles that
would own the decision (titles only, no personal contact details).

## 5. Files and budget

Your task names four files: MAIN (Routes A, B, C), WATCH (no route met), DUPS, and NOTES. In NOTES write plain text: the list pages
you used, regions covered, how many candidates you checked, how many were already registered, and what you did not get to.
Append to the files as you go so nothing is lost.

WebSearch calls are strictly limited to the number in your task; a refusal means stop searching, never work around it with search
engine or news-feed URLs. WebFetch is not limited: open ranking pages, league tables, association member lists, portfolio pages,
"largest private companies" lists, registries and company sites directly. One list page yields many candidates. Use only public pages.
Do not use Apollo. Cover North America, Europe, Asia-Pacific, the Middle East, Latin America and Africa as far as your cluster allows;
do not stop at the US and Western Europe. No quota: write every company you can prove, and none you cannot.
Before you finish, validate that every line parses as JSON and that no company appears twice in your files.

## 6. Sector names (use exactly one as `sector`)

Automotive & Mobility; Aerospace, Defence & Space; Airlines & Air Travel; Travel, Hotels & Leisure; Gambling & Gaming Venues;
Sports, Fitness & Events; Video Games & Esports; Software, Internet & AI; Media, Entertainment & Publishing; Telecommunications;
Semiconductors & Electronics; IT Services & Consulting; Banking & Lending; Insurance; Investment & Capital Markets;
Financial Services & Payments; Oil, Gas & Fuels; Utilities & Renewable Energy; Mining & Metals; Chemicals & Materials;
Industrial Machinery & Equipment; Shipping, Maritime & Shipbuilding; Logistics & Transportation; Building Products & Materials;
Construction & Engineering; Real Estate; Home & Furniture; Luxury, Jewellery & Watches; Beauty & Personal Care;
Fashion, Apparel & Footwear; Alcoholic Drinks; Food & Beverage; Tobacco & Nicotine; Consumer Products; Retail & E-commerce;
Pharma & Biotech; Medical Devices & Diagnostics; Healthcare Services; Agriculture & Agribusiness; Packaging & Printing;
Environmental & Waste Services; Security Services; Staffing & HR; Marketing, Advertising & PR; Professional & Business Services;
Education & Training; Diversified & Other.
Put the finer label (for example "wealth management", "industrial automation", "data centres", "private aviation") in `subsector`.
