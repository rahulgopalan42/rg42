# Wave 16 verification brief (financial + ownership + F1 fit)

You verify ~10 new F1 sponsorship prospects for SPORTFIVE. Today is 18 October 2026. Do NOT use Apollo, Clay, Lusha
or any paid enrichment tool - web research (WebSearch/WebFetch) and your own knowledge only.

Input: JSON array at the path in your task. Fields: id (website domain), company, sector, country, type, staff,
clay_revenue_band (a Clay DATABASE ESTIMATE, not verified), apollo_funding_100m (database flag), parent_hint, description.

Financial qualification - a company qualifies on ANY ONE (independent tests):
  revenue >= USD 75M (latest annual) | valuation >= USD 1B (market cap or last priced round) | total funding raised >= USD 100M (cumulative, all rounds)
Record every figure you find with its source URL and reporting date. Never invent a figure. Do not assign a parent's
finances to the brand (if the brand is a division, say so and give the parent's figure only in parent fields).
If you cannot confirm any figure, write "unverified" and set verification "Not verified".

F1 fit 0-4 (one point each, judged on THIS company, not just its industry):
  1 sells/operates in 3+ major F1 markets; 2 reaches affluent consumers or senior B2B decision-makers;
  3 brand story fits performance / innovation / technology / precision / luxury / global ambition;
  4 category whitespace on the F1 grid (crowded = banking, airlines, logistics, oil, tyres, watches, crypto, cyber,
    beer, spirits, automotive, cloud -> 0 here unless a clear niche).
Also note any CURRENT F1 deal (team / F1 / GP / driver) for the brand or its parent - informational only, do not reject.

financial_points (0-30) from VERIFIED figures only, take the highest:
  revenue 75-200M=8, 200-500M=14, 500M-1B=20, 1-10B=26, 10B+=30; valuation 1-10B=20, 10-50B=26, 50B+=30;
  funding 100-500M=14, 500M-1B=20, 1B+=24. If nothing verified, use 0.

Output: JSON array at the output path in your task, one object per input row, same order, exactly these keys:
{"id","company","revenue","revenue_source","valuation","valuation_source","funding","funding_source",
 "criteria_met","verification","financial_points","fit_score","fit_detail","parent","parent_source",
 "f1_current","sector_override","reason","sources"}
- revenue/valuation/funding: e.g. "USD 1.2B (FY2025)" or "unverified" or "n/a (listed, no funding)".
- *_source: "URL (date)" or "".
- criteria_met: e.g. "Revenue" / "Revenue + Valuation" / "Funding" / "None confirmed".
- verification: "Verified" (at least one qualifying figure with a source), "Partially verified" (figure found but
  source weak/old or only near the threshold), "Not verified".
- fit_detail: one short line covering the 4 fit points. reason: one sentence on why it ranks where it does.
- parent: controlling owner (>50%) or "" if independent; parent_source: URL or "".
- sector_override: a better sector tab name from the input's list style if the given sector is clearly wrong, else "".
- sources: list of URLs actually used.
Search budget: about 1-2 WebSearch per company; skip searching when you are certain AND can cite a known
source URL (e.g. the company's investor-relations page). Write ALL rows with python3 -I (json.dump,
ensure_ascii=False). Helper files only in /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/v16_<batch>/.
Report only: Verified / Partial / Not verified counts per batch. Under 40 words.
