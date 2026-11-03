# News verification of private unicorns (do not run git; write only your own output file)
Rahul (SPORTFIVE F1 sales) needs PRIVATE, independent companies that have raised USD 200M+ in EQUITY (any valuation:
USD 1B+, under USD 1B, or never disclosed). He warned that connector/research data can be wrong, so every company is now checked against dated news.
Today is 30 Oct 2026.

Input `/home/user/rg42/unicorns/newscheck_in/<chunk>.json`: a list of objects, one per company:
- `key`, `brand`, `domain`, `country`;
- `claims`: what our sources say now (CB Insights listing, valuation, Apollo funding, research status / figures);
- `funding_news` and `status_news`: up to 12 Google-News headlines each, as [title, date, outlet], from queries on
  "<brand> valuation/raises/funding" and "<brand> IPO/acquired/listing/merger/bankrupt".

For each company decide, using the headlines first and your own knowledge second:
1. `same_company`: do the headlines (and claims) refer to the company we mean (check domain/country/sector)? "Y", "N"
   (headlines are about a different firm with the same name) or "?" (no relevant headlines).
2. `status` as of today: "private", "public" (completed IPO / direct listing / SPAC merger CLOSED - a filing, plan or
   rumour is NOT a listing), "acquired" (deal completed, or signed and announced as a full acquisition; a minority
   stake is not), "defunct", or "unknown".
3. `valuation_bn`: the latest valuation in USD billions that a HEADLINE (or the CB Insights listing in claims) supports,
   any size (e.g. 0.45); null if no headline states one - do NOT carry over an unsourced research estimate.
   `valuation_month` "YYYY-MM" or null.
4. `funding_ok`: "Y" if total equity raised is clearly >= USD 200M (Apollo ">=200" in claims counts unless headlines
   contradict it; a single round >= 200M counts; sum of rounds in headlines counts), "N" if clearly below, "?" if unknown.
5. `check`: "confirmed" (headlines show the company is private and operating, with no IPO / acquisition / shutdown /
   majority owner), "corrected" (you changed status, valuation or funding: say why in note), "unconfirmed" (no relevant
   headlines or nothing reliable). Debt facilities do not count towards funding; say so in note when a headline round
   is debt.
6. `evidence`: the ONE headline (title + date + outlet) that best supports your status/valuation call, <= 160 chars.
7. `note`: <= 20 words.

Output `/home/user/rg42/unicorns/newscheck_out/<chunk>.json`: one row per input object, same order:
[key, same_company, status, valuation_bn, valuation_month, funding_ok, check, evidence, note].
Validate with `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I` (row
count and key order match). Write in pieces if long. Reply in 2 lines: counts by status and by check; anything odd.
