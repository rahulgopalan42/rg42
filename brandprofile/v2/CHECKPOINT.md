# Continuation checkpoint: non-public prospecting (state on 27 Nov 2026, end of batch 2)

Read `GOVERNING-METHODOLOGY-NON-PUBLIC.md`, `INSTRUCTION-MULTI-SOURCE-DISCOVERY.md` and `README.md` first.

## Delivered so far

| Batch | Workbook | Ranked | Watchlist | Other |
|---|---|---|---|---|
| b01 | `reports/F1-NON-PUBLIC-NEW-PROSPECTS-REVISED-METHOD-BATCH-1-2026-11-27.xlsx` | 714 | 75 | 569 read off rankings (assessed in b02) |
| b02 | `reports/F1-New-Non-Public-Prospects-Batch-2.xlsx` | 1,581 | 393 | 1,749 unconfirmed Clay leads; 10 read off rankings |

Delivered names are in `delivered/b01.json` and `delivered/b02.json` and count as duplicates from now on, with the master.

## The discovery register after batch 2 (10,373 companies)

- Left out: 1,592 on the master, 214 delivered in batch 1, 129 holding a current F1 deal, 441 listed, 550 for another reason.
- Ranked 1,581; watchlist 393; insufficient 5; read off a ranking only 10.
- **New, not yet researched: 5,331** (3,582 from web research, 1,555 from Clay, 194 from both). This is the research queue.
- 112 more are probably listed or part of a listed group (name match or Clay description) and need a decision either way.

## Stream by stream

**Crunchbase: not run.** `cb_metering_get_state` showed 500,000 of 500,000 data tokens used; it resets on 1 Dec 2026 00:00 UTC.
The user was told that running it will use part of the December allowance and has not yet said to go ahead: ask first.
When it runs: (1) operating companies with total equity funding of USD 100M+ that are not listed; (2) last valuation of USD 1B+;
(3) funding rounds of USD 75M+ announced since 1 Dec 2024; (4) the same by region outside the US. Write rows to
`discovery/crunchbase/*.jsonl` in the Clay row format, with `funding_total` and `valuation`, and run `disc_check.py` on them.
`batch2.py` already has a Crunchbase column; add the reader for that folder next to the Clay one in `build.load`.

**Clay: sampled, not exhausted.** 188 result pages, 3,482 rows, 2,842 different companies (`discovery/clay/clay_a..e.jsonl`).
Search only; no paid enrichment was used. Every query still had more pages except Breweries, Distilleries, Wineries, Cosmetics 1B+,
Hotels and Motels 1B+, Gambling 1B+ and Thailand. Next, in this order:
1. Page 2 onwards of the 1B+ group for the industries in `notes_clay_a/b/c.txt` (most had only page 1).
2. The 500M-1B group for the 30 industries that were not reached (14 in `notes_clay_b.txt`, 16 in `notes_clay_c.txt`).
3. The 200M-500M group (not run at all) for the consumer-facing industries.
4. Page 2 onwards for the 29 countries in `notes_clay_d.txt`, and the 12 pages not used in `clay_e` query 6.
Clay marks listed companies and local arms of multinationals as privately held: never rank a Clay name without a web check.

**Independent web research.** Sector runs done in b02: gambling, video games, tobacco and alcohol, environmental services, marketing,
education, conglomerates, healthcare, retail, automotive, payments and banking, consumer/beauty/home, food and agriculture, media
and sport, travel and airlines, telecom/electronics/IT, luxury and fashion, energy/logistics/building products. Country rankings:
Europe (7 of 21 countries opened) and the rest of the world (Australia, Mexico, Arab family groups, part of the US, China, Japan,
Korea, India). Every `notes_<key>.txt` in `batches/b02/` ends with what was not reached. Not given a depth run yet: software and AI,
industrial machinery, investment firms, aerospace and defence, mining and metals, chemicals, professional services, insurance,
utilities, packaging, staffing, real estate. Country rankings not opened: France, Portugal, Belgium, the Nordics, Czechia, Hungary,
Romania, Greece, Turkey, Ireland, the UK, Latin America outside Mexico, South-East Asia, Japan and Korea (unlisted rankings), Africa.

## How to start batch 3

1. Check the master in the user's Drive folder for changes (`register.py <fresh download>`), then `mkdir batches/b03`.
2. Carry the queue over: copy `batches/b02/disc_*.jsonl` and `batches/b02/dups_*.jsonl` into `batches/b03/`
   (delivered names then show as "delivered in an earlier batch", names already left out stay left out, the rest is the queue).
3. `queue.py b03 80 <files> 1` writes `in_q01.jsonl` onwards, round-robin across streams. Brief: `brief_queue.md`.
   Yield in b02 was about 25 to 45 qualified companies per 80 names; a file takes one researcher about 20 minutes.
4. New sector or country runs: `brief_b02.md`. New Clay pulls: `brief_clay.md`.
5. Before delivery: `fuzzy.py b03`, review the pairs, put confirmed duplicates in `batches/b03/manual_dups.json`
   (`[name, reason]` for a master name, `[name, reason, "batch"]` for the same company entered twice), search the top-ranked names
   for a current F1 deal, then `deliver.py b03 <xlsx>` and `validate.py <xlsx> b03 <master.xlsx>`.

## Still open from batch 2

- 37 of the 569 ranking companies could not be assessed (sites block automated requests): named in `notes_a05_assess.txt`.
- 34 ranked or watchlist companies are subsidiaries whose parent is on the master or was delivered in batch 1; they are flagged in
  the "On Your Sheet?" column. The user has been asked whether to keep such subsidiaries.
- Many qualifying figures are older than three years, and ownership is "requires verification" on 515 ranked rows.
- Grand Prix partner pages not read: Saudi Arabia, Qatar (partners added from press), Azerbaijan, China, Las Vegas, São Paulo,
  Hungary, Barcelona, Monaco.
- No company in "Aerospace, Defence & Space" was added in batch 2.
