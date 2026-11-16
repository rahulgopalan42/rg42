# Brief: unlisted companies for a Formula 1 sponsorship prospect list (sectors a funding database misses)

Today is 16 November 2026. The user sells Formula 1 sponsorships. Their existing list was built from a venture-funding database, so it
misses companies that never raised venture money. Your job is to find such companies in ONE group (named in your task), across ALL
regions of the world (North America, Europe, Middle East, Asia-Pacific, Latin America, Africa), and to prove each one qualifies.
The user has asked for the result to be HIGHLY ACCURATE: every fact must come from a page you find in this session. "" (empty) is an
acceptable answer for a field; an invented or remembered fact is not.

A company goes on the list only if ALL of these hold:
1. It is an operating company that is NOT listed on a stock exchange and is not owned by a stock-market-listed group.
2. It is not a current Formula 1 championship, team or Grand Prix partner, and does not own one. The current roster is at the end of
   /home/user/rg42/brandprofile/brief_check.md (the paragraph starting "Current Formula 1 roster"): read it and leave those out.
3. It can pay: at least ONE of the following is stated on a page you found (give the page):
   a. it has raised USD 150M or more in equity in total;
   b. published revenue of USD 300M or more (filed accounts, a figure stated by the company, or a public ranking);
   c. it was valued at, or bought for, USD 1B or more since November 2023;
   d. it currently pays for a top-tier sports sponsorship: a team, series or event in Formula 1's peer group (MotoGP, Formula E, IndyCar,
      NASCAR Cup, WEC), a club or competition in the Premier League, La Liga, Bundesliga, Serie A, Ligue 1 or UEFA Champions League, the
      NBA, NFL, MLB or NHL, the ATP / WTA tours or golf majors, the Olympics or FIFA, the IPL, or the UFC;
   e. it is owned by a state investment fund that is building the brand internationally.

For every qualifying company write ONE JSON object on ONE line:
{"name": "...",                    // the company's usual name
 "hq": "City, Country",            // "" for the city if not found
 "group": "...",                   // the group named in your task
 "sector": "...",                  // one of the 48 sector names listed in brief_check.md (the line starting "- `sector` must be one of")
 "industry": "...",                // 2-6 words, e.g. "online forex and CFD broker"
 "desc": "...",                    // what it does: one plain factual sentence of 10-20 words
 "ownership": "...",               // "founder-owned", "family-owned", "private equity: <firm>", "partnership", "co-operative", "state fund: <fund>", or "private, owner not stated"
 "capacity_basis": "a|b|c|d|e",    // which test in point 3 it passes (the strongest one you can prove)
 "capacity_detail": "...",         // the fact, e.g. "Revenue GBP 3.7bn in the year to March 2025" or "Front-of-shirt sponsor of X since 2024"
 "capacity_usd_m": 4800,           // the figure in USD millions for a, b or c (GBP 1.30, EUR 1.10); null for d and e
 "capacity_year": "2025",
 "capacity_source": "url",
 "sponsorships": "...",            // sports sponsorships you found (partner and year), or ""
 "reach": "Global|International|Regional|Domestic",   // Domestic = essentially one country; Regional = several countries in one region; International = two or more world regions; Global = North America, Europe and Asia-Pacific at real scale
 "markets": "...",                 // where it sells or operates, 8-25 words, from what you found
 "signals": {"raise": "", "ipo": "", "regions": "", "marketing": ""},   // only if you came across it, each as "what happened (Mon YYYY; url)": raised money since Nov 2025; IPO filed or announced since Nov 2025; opened in a new country since Nov 2025; new marketing chief or rebrand since Nov 2025. Otherwise ""
 "rationale": "...",               // why an F1 partnership could make commercial sense for THIS company, 12-25 words, specific
 "rel": 3,                         // 1-5 relevance to F1: 5 = brand-led company with international ambitions and rivals already in F1; 3 = plausible; 1 = very unlikely or restricted
 "conf": "high|medium|low"}        // how sure you are that the whole line is right

Rules
- Do not include a company you could not show to be unlisted, or whose capacity test you could not prove from a page.
- Prefer list pages (rankings, league tables, sponsor lists, portfolio pages, regulator registers): one page gives many companies. Fetch
  them with WebFetch; you may fetch as many list pages as you need. WebSearch calls are strictly limited (see your task).
- Do not write any financial figure you did not read on a page. Do not use third-party "estimated revenue" sites.
- Write the output file in chunks (append) so nothing is lost, then check it: valid JSON on every line, no company twice, desc 10-20 words.
