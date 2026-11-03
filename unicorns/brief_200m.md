# Discovery brief, round 2: private companies with USD 200M+ raised, valued UNDER USD 1B or valuation not disclosed
(do not run git; write only your own output file)

Rahul (SPORTFIVE, Formula 1 sponsorship sales) now wants every PRIVATE, independent company worldwide that has raised
USD 200 million or more in total EQUITY funding (venture, growth, PE growth/minority investment; NOT debt, loans or
grants), whatever its valuation. Round 1 already collected the unicorns (valued USD 1B+), so this round is about the
others: companies with USD 200M+ raised whose latest valuation is BELOW USD 1B or was NEVER DISCLOSED, including
former unicorns that have since been marked down below USD 1B but are still private and operating.

Read `/home/user/rg42/unicorns/brief.md` for the 37-field row format, the scales and the sector list, and follow it,
with these changes:
- List only companies you believe have raised >= USD 200M in equity in total AND are still private and independent
  today (30 Oct 2026). Majority-owned subsidiaries of other groups are out. Funds, SPACs, government bodies,
  universities and non-profits are out.
- Skip companies whose latest valuation is USD 1B or more (round 1 has them) unless you are unsure (then include).
- `valuation_bn`: latest known valuation in USD billions if any (e.g. 0.6), else null; `status`: "private" (use
  "below_1b" only for a former unicorn now marked below USD 1B); `funding_m` is REQUIRED (best estimate of total
  equity raised; say "approx" in note when estimated).
- Verify with the web. WebSearch is capped and shared, so ALSO use the uncapped Google News RSS feed with Bash, e.g.
  `curl -sS "https://news.google.com/rss/search?q=%22Company+Name%22+raises&hl=en-US&gl=US&ceid=US:en"`
  (parse <item><title>/<pubDate> with python), and WebFetch of Dealroom / Crunchbase News / Wikipedia / company pages.
  Use them to confirm totals raised, latest rounds and that the company has not listed, been acquired or shut down.
- Aim for completeness in your segment: the target is roughly 80-200 rows depending on segment size. Prefer real,
  checkable companies; never pad with guesses.
Output: `/home/user/rg42/unicorns/discover2_out/<your code>.json` (JSON array of 37-field rows or objects with the 37
keys). Write in pieces, validate with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`, keep helper scripts in
your own scratchpad folder. Reply in 2 lines: rows written, anything odd.
