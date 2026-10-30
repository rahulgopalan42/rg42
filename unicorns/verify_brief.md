# Private unicorn VERIFICATION brief (web-led; do not run git; write only your own output file)

Read `/home/user/rg42/unicorns/brief.md` first: Rahul's three tests, the 37-field row format, the scales and the
sector list there all apply. Rahul's warning: the connectors and earlier research contain inaccurate data (wrong
company behind a name, old valuations, companies that have since listed or been acquired, funding mixed up with a
parent's). Your job is to make every row in your chunk RIGHT, using the web.

## Input
`/home/user/rg42/unicorns/verify_in/<chunk>.json`: rows `[key, brand, domain, hq_country, valuation_bn, valuation_date,
funding_m, status, latest_round, source_url, what, hint]`. Values are claims to test, not facts. `hint` may hold
conflicting statuses from different researchers, or "pool" if the name came from the Apollo/Clay database only (then
most fields are empty and the company may well NOT be a unicorn).

## For every row (use WebSearch, and WebFetch where a search snippet is not enough)
1. Identity: is this the company we think it is? Confirm the official website domain and HQ country/city. If the
   domain belongs to a different company, fix it.
2. Status today (30 Oct 2026): still private and independent? Check for an IPO / direct listing / SPAC in 2024-26, an
   acquisition or merger, a shutdown or insolvency. Search e.g. "<brand> IPO", "<brand> acquired", "<brand> 2026".
3. Valuation: the latest reported valuation (priced round, credible press report, tender offer) with month/year.
4. Total equity funding raised to date (USD M). Do not count debt facilities; do not use a parent's figures.
5. Latest round (type, amount, month/year, lead investors).
Search at least once per row (pool rows with no known valuation: one search "<brand> valuation" is enough to rule
them in or out). Prefer sources dated 2025-2026 (Reuters, Bloomberg, TechCrunch, FT, company press release,
Crunchbase News, Sifted, Inc42, DealStreetAsia, 36Kr, etc.).

## Output
`/home/user/rg42/unicorns/verify_out/<chunk>.json`: EXACTLY one row per input row, same order, each row the 37 fields
of brief.md followed by 2 more fields (39 in total):
- field 38 `key`: copied from the input;
- field 39 `check`: "confirmed" (claims hold, source found), "corrected" (you changed valuation, funding, status,
  domain or HQ - say what in `note`), "unconfirmed" (no reliable source found; set conf "L").
Fill all 37 fields (scores too), `source_url` = the best URL you used for valuation/status, `conf` "H" only when a
dated 2025-26 source confirms valuation and status. Never invent a figure: unknown = null.

Write in pieces (scratchpad partial files, then merge). Validate with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I <script>`:
same row count and key order as the input, 39 fields, scores in range, status in the allowed set.
Reply in 3 lines: rows written; counts confirmed / corrected / unconfirmed; how many still pass all three tests.
