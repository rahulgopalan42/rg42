# Wave 16 research brief v2 - F1 Fit (50) + Financial Capacity (50)

You research ~10 new F1 sponsorship prospects for SPORTFIVE. Information must be current as of 18 Oct 2026.
Web research (WebSearch/WebFetch) and your own knowledge only - NEVER Apollo, Clay, Lusha or paid tools.
Prefer official reports, filings, investor pages, then credible press. Never invent a figure: write "unknown".
Do not give a parent's finances to the brand (if it is a division/brand of a group, say so; parent figures go in
the parent fields only and the brand is scored on what is known about the brand itself).

Input: JSON array at the path in your task (id = website, company, sector, country, type, staff,
clay_revenue_band = Clay DATABASE ESTIMATE used for the original >=USD 75M filter, apollo_funding_100m, parent_hint,
triage_note). Reuse these; do not re-research fields that are already adequate.

Financial qualification (any ONE): revenue >= USD 75M | valuation >= USD 1B | cumulative funding >= USD 100M.

SCORES (integers). Unknown => use the "unknown" value given, never assume strength or weakness.
F1 FIT (50)
- audience (0-15): overlap with F1's consumer (affluent 25-54, global, tech/auto/luxury minded) and B2B
  (senior decision-makers) audiences. 13-15 strong direct overlap; 9-12 good; 5-8 partial; 0-4 weak.
- synergy (0-15): concrete commercial benefits from a partnership (B2B hospitality/client entertainment, product
  showcase/tech partner role, market-entry visibility, activation potential). 13-15 obvious; 9-12 good; 5-8 some; 0-4 little.
- alignment (0-10): brand story fits performance, innovation, precision, technology, luxury or global ambition.
- international (0-5): operates/sells in many major F1 markets (5 = global; 3 = several; 1 = one region; 0 = domestic).
- category (0-5): sponsorship whitespace / competitive positioning on the grid (5 = open category or rival already
  in F1 creating a reason to respond; 0 = saturated category like banking, airlines, logistics, oil, tyres, watches,
  crypto, cyber, beer, spirits, automotive, cloud - unless a clear niche angle).
FINANCIAL CAPACITY (50) - conservative
- revenue_scale (0-15): <75M=0, 75-200M=4, 200-500M=7, 500M-1B=9, 1-5B=12, 5B+=15. Unverified: use the Clay band
  value minus 1 and say "Clay estimate".
- capital (0-10): market cap/valuation 50B+=10, 10-50B=8, 1-10B=6; cumulative funding 1B+=7, 100M-1B=4;
  unknown=2; evidence of being small/strained=0-1.
- profitability (0-15): consistently profitable with strong cash flow 13-15; profitable 9-12; breakeven/mixed 5-8;
  loss-making 2-4; unknown=5.
- marketing (0-10): evidence of big sponsorship/marketing spend (major sports deals, global campaigns) 8-10; some
  sponsorship or brand marketing 5-7; little evidence 2-4; unknown=3.

Also record any CURRENT F1 deal (team/F1/GP/driver) for the brand or its parent - information only, do not reject.

Output: JSON array at the output path in your task, one object per input row, same order, exactly these keys:
{"id","company","revenue","revenue_source","valuation","valuation_source","funding","funding_source",
 "profitability","profitability_source","marketing_evidence","criteria_met","verification",
 "audience","synergy","alignment","international","category",
 "revenue_scale","capital","profitability_score","marketing",
 "rationale","confidence","parent","parent_source","f1_current","sector_override","not_a_prospect","sources"}
- figures like "USD 1.2B (FY2025)" or "unknown"; *_source "URL (date)" or "".
- criteria_met: "Revenue", "Revenue + Valuation", "Funding", "Clay estimate only" or "None confirmed".
- verification: "Verified" / "Partially verified" / "Not verified". confidence: "High" / "Medium" / "Low".
- rationale: one or two evidence-based sentences. not_a_prospect: "" or a short reason if it is junk, defunct,
  a person, or only a sub-page of another company (then scores may be 0).
- sector_override: better sector tab name if clearly wrong, else "". sources: list of URLs actually used.
Budget: WebSearch is capped per turn and shared by all agents, so use it sparingly (at most 1 per company, often 0).
Prefer WebFetch of known pages first: the company's English Wikipedia article (infobox revenue / owner / founded),
its investor-relations or "about" page, companiesmarketcap.com or stockanalysis.com for listed companies.
Use WebSearch only when those do not settle revenue/ownership or the F1/sponsorship check.
If WebSearch says the limit is reached, continue with WebFetch and knowledge; mark anything you could not confirm
as unknown and lower confidence - do not stop the batch.
Write ALL rows with python3 -I (json.dump, ensure_ascii=False). Helper files only in
/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/v2_<batch>/.
Report only: rows researched, Verified/Partial/Not, and the top scorer per batch. Under 40 words.
