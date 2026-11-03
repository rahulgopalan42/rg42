# Wave 16 quick triage (knowledge only - NO web search, NO Apollo/Clay)

Rows are companies from Clay exports (database data is noisy: junk LinkedIn pages, news sites, people, retired brands,
product pages, regional offices and mislabelled "10,001+ staff" records are common). For each row decide from your own
knowledge and the row text:

t:   "real"     = a real operating company / brand that could be a sponsorship prospect
     "division" = a real unit, product line, regional office or sub-page of a bigger company (name the parent)
     "junk"     = person, community/group page, news/spam site, stealth/placeholder, defunct or absorbed brand
fit: 0-4 quick F1-fit guess for "real" rows only (1 point each: sells in 3+ F1 markets; affluent or senior-B2B
     audience; performance/tech/precision/luxury/global story; category not crowded in F1 - banking, airlines,
     logistics, oil, tyres, watches, crypto, cyber, beer, spirits, automotive, cloud score 0 for this point). Else 0.
scale: "large" (clearly > USD 1B revenue or valuation), "mid" (likely USD 75M-1B), "small" (likely < USD 75M),
       "unknown". Guess honestly; do not invent.
parent: controlling owner if you know one, else "".
When unsure whether a real company is big enough, use "real" + scale "unknown" (do not mark junk).

Input: JSON arrays at the paths in your task (fields id, company, sector, country, type, staff, description).
Output for each in_NNNN.json: /home/user/rg42/wave16/triage/out_NNNN.json - JSON array, one object per input row,
same order: {"id","t","fit","scale","parent","note"} (note <= 8 words). Write with python3 -I (json.dump,
ensure_ascii=False). Skip batches whose out file exists. Helper files only in
/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/t16_<first batch>/.
Report only: real / division / junk totals for your range. Under 30 words.
