# F1 Sponsorship Parent-Company Prospects - project state and how to resume

Workbook: `reports/2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS.xlsx` (built by the scripts below; rebuild any time).
Branch: `claude/f1-sponsorship-prospects-3esslw`. Everything needed to resume is committed in `parents/`.

## Qualification and scoring (agreed with Rahul, 19 Oct 2026)
- A parent qualifies if it meets ANY ONE of: valuation / market cap >= USD 1B, cumulative funding >= USD 100M,
  annual revenue >= USD 100M. No restriction by ownership type or industry. Organised at ULTIMATE PARENT level.
- F1 Fit /60 = audience overlap (0-4 x5) + commercial synergies (0-4 x5) + brand alignment (0-4 x2.5) +
  international / F1-market relevance (0-4 x2.5). Scored by research judgement per parent.
- Financial Capacity /40 = scale 20 (valuation bands; Apollo revenue lifts it) + valuation & funding 10 +
  other indicators 10 (affordability evidence, listed/state ownership, confidence, sports-sponsorship record).
- Ranked by Total /100, never by size alone. Rows with memory-only figures or connector-filter-only
  qualification are flagged Preliminary (amber). Confirmed current F1 sponsors go to a red tab; unsure links are
  flagged red in-row. Sports clubs / team owners, fund vehicles, public bodies, defunct and sanctioned
  companies are excluded with the reason.
- Categories: A genuinely new (no parent, alias, subsidiary, brand or website in ANY existing dataset) ->
  MASTER RANKING + industry tabs; B corporate-group overlap -> EXISTING GROUP OVERLAPS (ranked separately,
  4 overlap types, dataset and sheet named); C uncertain -> MANUAL REVIEW.
- Existing datasets cross-referenced: Old Google Drive master files (all worksheets), every previous prospect
  workbook/CSV (all worksheets, incl. the Wave 16 final ranking), Friday Clay export CSVs.

## Sources already collected (do not redo)
- `parents/discover/cat_01..58.json` - 58 knowledge-research category/region briefs (`discover_brief.md`,
  `categories.json`), 21-field rows.
- `parents/apollo/page_NNN.json` - Apollo company search, total funding >= USD 100M, 100/page. Pages pulled:
  1-120, 131-161, 171-230 (+ a few stragglers). NOT pulled: 121-130, 162-170, 232-250 (and 251-273 exist).
  Apollo returns owner, exchange, revenue_printed but no funding amount.
- `parents/lusha/page_000..029.json` - Lusha company search, total funds >= USD 100M, 50/page (60 credits).
- `parents/score_in/chunk_NN.json` -> `parents/score_out/chunk_NN.json` - knowledge scoring of connector-only
  records (`score_brief.md`, 25-field rows). Chunks 1-74 = Apollo/Lusha records; 75-79 = market-cap listing
  companies absent from all datasets; 80-98 = previously unrecognised records re-identified from gathered public
  evidence (`identify_brief.md`, `parents/peek/`); 99-133 = Apollo records whose parent was already in the datasets.
- `parents/checkpoints/` - compact copies of the scratchpad-only inputs: existing-dataset indexes (Old Drive +
  workbooks; Friday Clay export), the Wave 16 brand ranking (for the DRIVE CSV BRANDS tab), the market-cap
  listing fetched 2026-10-19 (used to verify listed parents' market caps and as a discovery source).

## Pipeline (run from the repo root with a Python 3.11 venv: pandas, openpyxl)
1. `python parents/consolidate.py`   - merges all sources into one record per ultimate parent, applies the
   scoring outputs (P/S/X/U), cross-references against the existing datasets, writes parents.pkl/dups.pkl/
   excluded.pkl to the scratchpad `parents/` folder (set `F1_SCRATCH` to choose the folder).
2. `python parents/verify_mcap.py`   - overrides memory market caps with the verified listing (2026-10).
3. `python parents/build_workbook.py` - scores, categorises, writes the workbook (+ summary.json).
4. `python parents/qc.py`            - 13 QC checks, appends the QC tab.
Optional: `python parents/split_score.py <first_chunk> 160` writes new scoring chunks for unscored connector
records; `python parents/mcap_candidates.py <first_chunk> 160` does the same for listed companies missing from
all datasets. Each chunk is scored by a Sonnet agent with `score_brief.md`; discovery briefs use
`discover_brief.md`. Apollo pulls use `apollo_brief.md` (needs `.claude/settings.json` allow rule
`mcp__Apollo_io`, already committed - effective in a fresh session).

## State at last build (19 Oct 2026, evening run: sponsorship-signals pass + Apollo additions)
- Master ranking (Category A, genuinely new parents): 2,361 (305 added this round, listed on the NEW BRANDS THIS ROUND
  tab; baseline of the earlier sheet in parents/baseline_master.json) | Existing group overlaps (B): 9,372 |
  Manual review (C): 2,904 | Confirmed current F1 sponsors set aside: 122 | QC: 13/13 checks pass.
- Scoring now 60/40 with signals (Rahul's 19 Oct instruction, cheque size USD 2.5M/yr): Fit 60 = core fit 40 + fit
  signals 20 (competitor already in F1, motorsport adjacency, expansion moment, race-market footprint, founder/CEO
  affinity); Capacity 40 = financial evidence 20 + capacity signals 20 (headcount band, funding recency/investor
  quality, PE ownership, brand-building hires). Removed: sponsorship spend, operating proxies, debt ratings, B2B story.
  Signals come from parents/signals_out (Sonnet agents, signals_brief.md; inputs parents/signals_in chunk_001-060).
  Most rows are low-confidence (L): headcount and HQ-country driven; category-level "competitor in F1" defaults.
  build_workbook.py writes new signals_in chunks for any ranked parent still without a signals row.
- Apollo funded-company universe (total_funding >= USD 100M, 27,236 records, 273 pages) pulled in full except page
  231; all new records knowledge-scored (score_out chunk_001-150). Revenue-sorted Apollo searches and Clay
  revenue-bracket searches were probed (parents/apollo/rev_*.json, parents/clay/probe_001.json): ~0% new, so not
  pursued. parents/novelty.py measures the novelty of any Apollo page against the user files. Lusha unused (12 credits).
- Same-group aliases merged in consolidate.py (ANA, DMGT/dmg media, Schwarz, Nord Security, Fila/Misto).

## Open items
- Apollo page 231 (1 credit) not pulled; 3,280 connector records whose parent is already listed remain unscored (split_score.py variant needed).
- Manual Review tab: unrecognised connector records (status U) and parents inferred only from a funded
  subsidiary; a web-verification pass would move many into A/B.
