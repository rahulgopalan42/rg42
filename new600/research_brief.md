# Brief: find genuinely NEW big companies (F1 sponsorship prospect list for SPORTFIVE)

Goal: find companies that (a) qualify and (b) are NOT already in any list we have. Return up to the target count
given in your task (more is fine) of verified NEW qualifying companies.

## Qualifies (needs ONE, with a dated public source you actually read)
- Valuation / market cap >= USD 1B (latest funding-round post-money valuation, a reported valuation, an acquisition
  price, or a listed market cap), OR
- Total equity funding raised >= USD 150M.
- Must be an operating company or brand that could buy a sponsorship: NOT a joint venture, project company / SPV,
  fund / REIT / BDC, government body, development bank, university, non-profit, sports club or league.
- Not defunct, not absorbed into another company (acquired companies that still trade under their own brand are OK).
- Not a current Formula 1 team sponsor/partner.

## NEW = not already covered (this is the hard part - most big names ARE covered)
Check EVERY candidate with the checker (run it from /home/user/rg42, many names per call):
  /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I new600/check_new.py "Name|website" "Name2|website2" ...
Only `NEW` counts. Also check the company's other names (legal name, former name, English/pinyin name, parent
brand); if ANY version is EXCLUDED the company is covered - drop it. Expect most famous names to be EXCLUDED;
the new ones are usually in the long tail: 2025-2026 new unicorns, regional champions, recent large rounds,
non-US markets. Check candidates in bulk (30-60 per call), keep going until you hit your target or run out.

## Output
Write a JSON list to the output file named in your task (nothing else in that file). One object per NEW company:
{"name": "...", "website": "domain.com", "hq_country": "...", "hq_city": "...",
 "what": "2-4 sentences: what it does, main products/brands, customers, scale (revenue/users/staff if known)",
 "basis": "valuation" | "funding" | "market cap",
 "valuation_usd_bn": number or null, "valuation_date": "YYYY-MM", "funding_usd_m": number or null,
 "last_round": "e.g. Series C, USD 200M, 2026-09" or "", "listed": true/false, "ticker": "",
 "investors": "main investors / owner", "source_url": "URL of the article/page you read that shows the figure",
 "source_note": "the exact figure as the source states it", "confidence": "high|medium"}
Rules: no figure from memory alone - every company needs a source you opened in this task. Do not invent websites;
leave "" if unknown. Do not include anything the checker says is EXCLUDED. Keep the file valid JSON at all times
(rewrite the whole list as you go so progress is saved). Work only in your own output file.
Reply at the end with: count written, and how many candidates you checked in total.
