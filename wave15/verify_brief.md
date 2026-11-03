# Wave 15 full verification brief (stage 2) - v4 rules

You fully verify ~10 F1 sponsorship prospects for SPORTFIVE that already passed a quick screen. Today is
13 October 2026. Verify from scratch with sources; the screen's figures may be wrong.

Input: JSON array at the path in your task (fields include id, company/name, website, country, scale_route,
scale_evidence, parent, f1_tie, sector, fit, verdict_guess, note).
Output: JSON array at the output path in your task, one object per input row, same order, schema EXACTLY:
{"id","company","sector_tab","domain","hq","ownership","sells","headcount_band","revenue","valuation",
 "latest_raise","fit_score","fit_detail","up_and_coming","flags","verdict","verdict_reason","best_angle","sources"}
id and company: copy from input. sector_tab: two-digit code + name from the list in
/home/user/rg42/wave15/screen_brief.md (or an X tab). fit_score integer 0-4. up_and_coming true/false.
flags: list of short strings. sources: list of URLs actually used. Date every figure; mark estimates "(est)".

Hard filters (any fail = verdict "No", name it in verdict_reason)
1. Scale - pass on ANY: valuation/market cap/EV USD 1B+ (dated, sourced); USD 100M+ equity raised with a priced
   round in the last 36 months; revenue USD 500M+; revenue USD 150-500M (then verdict max Stretch, flag
   "USD 150-500M revenue route").
2. Headcount 51+.
3. No genuine distress (insolvency, restructuring, going-concern doubt, wind-down, acquired/absorbed).
4. No F1 tie - FAIL ONLY WHEN A TIE IS FOUND: current team partner/sponsor/supplier/licensee, F1 global or
   regional partner, Grand Prix/promoter partner, F1 Academy partner, driver personal sponsor - directly or via a
   controlling (>50% / joint) parent or a controlled brand. Minority holder that sponsors F1 = flag + cap Stretch.
   Lapsed deal = flag + cap Stretch ("confirm before outreach"). Check the brand AND its parent.
5. Not sanctioned (OFAC/EU/UK), not US Entity List / 1260H / UFLPA (group-wide), not HQ in Russia/Belarus/Iran.
6. Independent brand: a subsidiary/regional arm is "No" ("subsidiary of X") unless it is a separately marketed
   consumer brand (then flag "group brand: X").

Fit 0-4 (one point each): sells in 3+ F1 markets; affluent 25-54 or senior B2B buyers; story maps to
performance/technology/precision/global ambition; category not crowded on the grid (banking, airline, logistics,
oil, tyres, watches, crypto, cyber, beer, spirits, automotive, cloud = 0).
Verdicts: Yes = passes, fit >= 2, credible marketing motive; Stretch = passes with one real reservation;
Low-value = passes but fit 0-1 or domestic/B2B with no brand ambition; No = a hard filter failed.
up_and_coming: crossed USD 1B in 24 months, >40%/yr growth, 2025-26 IPO, visible challenger, or announced
2025-26 market expansion (flag "market expansion: from -> to").
best_angle: one sentence on why F1 now (market entry, launch, audience match) or "".

Search budget: about 2-3 WebSearch per company (scale/ownership; F1 tie for brand and parent). WebFetch is fine.
Helper files only in /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/verify_<batch>/.
Write ALL rows before stopping (json.dump ensure_ascii=False). Report only: Yes/Stretch/Low-value/No counts and
any F1 ties found. Under 50 words.
