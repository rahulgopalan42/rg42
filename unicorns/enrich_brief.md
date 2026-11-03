# Scoring pass for private unicorns (knowledge only - no web search needed; do not run git)
Read `/home/user/rg42/unicorns/brief.md` for context, the 37-field row format, the scales and the sector list.
These companies are already confirmed by independent sources (CB Insights' current unicorn list and/or Apollo) as
private unicorns; your job is to DESCRIBE and SCORE each one as an experienced F1 sponsorship seller would.
Input `/home/user/rg42/unicorns/ref/enrich_in_<n>.json`: rows [key, brand, domain, hq_country, hq_city, industry_or_what,
valuation_bn, funding_m, investors, latest_round].
Output `/home/user/rg42/unicorns/ref/enrich_out_<n>.json`: one row per input row, same order, 38 fields = the 37 fields of
brief.md followed by `key` copied from the input. Rules:
- Make sure you know which company it is (use domain, city, industry, investors). If you do not recognise it, still
  write the row: copy the input facts, sector from the industry, scores 0-1, conf "L", note "not recognised".
- Copy valuation_bn and funding_m from the input unless you are sure they are wrong (then say so in note); status
  "private" unless you KNOW it has listed or been acquired (then set that status and say when in note).
- Fill `what`, `sector`, `why`, all scores and signals (`a`,`s`,`l`,`n`, headcount, fund_recency, brand_hires,
  competitor_f1, motorsport, expansion, race_footprint, founder), `f1_status`/`f1_deal` (current only if you are sure),
  `sport_deals`, `evidence`, `ceo`, `conf`. Company-specific, not sector defaults.
Write in pieces, validate with `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`
(row count and key order match the input, 38 fields, scores in range). Reply in 1 line: rows written, how many not recognised.
