# Brief: verify Crunchbase finds for the NEW-brands list (F1 sponsorship prospects, SPORTFIVE)

Each input row is a company Crunchbase shows with total funding >= USD 150M or a funding round valued >= USD 1B,
and which is not on any of our existing lists. Crunchbase data can be wrong (debt counted as funding, estimated or
mistyped valuations, stale entries). For EACH row decide keep or drop, using WebSearch/WebFetch (the Crunchbase URL
is for identification only - do not rely on it as the source).

KEEP only if ALL are true:
- Real operating company or brand that could buy a sponsorship (NOT a joint venture, project company/SPV, fund/REIT/
  BDC, government body, development bank, university, non-profit, sports club/league).
- Still operating and still trading under this name (if renamed, give the CURRENT name in "name" and the old name in
  "former_name"; if absorbed into another company or defunct -> drop).
- Qualifies: valuation / market cap >= USD 1B (round post-money, reported valuation, acquisition price, or current
  listed market cap) OR total EQUITY funding >= USD 150M (debt facilities, loans, bonds, grants don't count), with a
  dated public source you opened.
- Not a current Formula 1 team sponsor/partner.
After verifying, run the checker on the CURRENT name, former names and website (from /home/user/rg42):
  /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I new600/check_new.py "Name|website" ...
If any version is EXCLUDED -> drop with reason "already covered as <name>".

## Output: JSON list written to the output file named in your task, one object per INPUT row (keep and drop):
{"input_name": "...", "verdict": "keep" | "drop", "drop_reason": "" or short reason,
 "name": "current brand name", "former_name": "", "website": "domain.com", "hq_country": "...", "hq_city": "...",
 "what": "2-4 sentences: what it does, main products/brands, customers, scale (revenue/users/staff if known)",
 "basis": "valuation" | "funding" | "market cap",
 "valuation_usd_bn": number or null, "valuation_date": "YYYY-MM", "funding_usd_m": number or null (equity only),
 "last_round": "e.g. Series C, USD 200M, 2026-09" or "", "listed": true/false, "ticker": "",
 "investors": "main investors / owner", "source_url": "URL you opened that shows the qualifying figure",
 "source_note": "the exact figure as the source states it", "confidence": "high|medium"}
For drops, the descriptive fields can be brief. No figures from memory alone. Keep the file valid JSON at all times
(rewrite the whole list as you go). Reply at the end with: kept N, dropped M.
