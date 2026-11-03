# Sector discovery round 2 - new brands on the NEW parameters (knowledge only: no web, no Clay/Apollo/Lusha)

Read `/home/user/rg42/parents/discover_brief.md` first: the output format, the parent-level rule, the sector list and
the rules there all apply, with the changes below. Your task names ONE sector; every row must use that sector number.

## What changed (Rahul, 19 Oct 2026)
1. Qualification: at least ONE of valuation >= USD 1B, cumulative funding >= USD 100M, OR annual revenue >= USD 100M.
   Revenue now counts. Add a 22nd field `revenue_m` (latest annual revenue in USD millions, number, or null).
   Row = 22 fields: `[name, hq_country, domain, type, ticker, val_bn, val_basis, val_date, funding_m, sector, brand,
   approach, why, a, s, l, n, fin, f1, subs, conf, revenue_m]`. If you know none of the three figures, do not include it.
2. Selection is driven by SPONSORSHIP SIGNALS (cheque size about USD 2.5M per year), not by size. Prefer parents with:
   - a direct competitor already sponsoring F1 or an F1 team;
   - motorsport adjacency (performance parts, tyres, lubricants, sim racing, EV charging, logistics for events, etc.);
   - an expansion moment in 2025-26 (new countries, IPO or large raise, rebrand, flagship launch, first global campaign);
   - a footprint in several race markets (US, UK, Italy, Monaco, Spain, Japan, Singapore, Australia, Gulf, Mexico, Brazil, Canada, China);
   - a founder / CEO with documented motorsport or F1 affinity;
   - capacity signals: 100+ staff, funding in 2024-26 from strong investors, private-equity ownership, brand-building hires.
   Put the concrete facts in `why` (<= 18 words) and `fin` (<= 12 words). Mid-sized groups (USD 100M-5B) with strong
   signals are wanted; giants with no reason to be in F1 are not.
3. Only NEW names. The well-known global groups are already in SPORTFIVE's databases. The file named in your task
   (`known_*.txt`) lists the parents already in our pipeline for this sector: do not repeat any of them (nor their
   subsidiaries, brands or former names). Skip global household brands and members of the S&P 500, DAX 40, CAC 40,
   FTSE 100, Nikkei 225 top 50 and Hang Seng top 30; they are already covered. Target 40-80 rows; fewer is fine.
4. Never invent a figure: unknown = null and conf "L". No current F1 / F1-team sponsors (if unsure, fill `f1`).

Validate as in the main brief (22 fields per row, numbers numeric, sector = your sector, a/s/l/n 0-4) with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`, keeping helper
scripts in the scratchpad folder named in your task. Reply in 2 lines: count written, validated.
