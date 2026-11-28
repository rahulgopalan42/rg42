# Revised non-public methodology: working files

Governing text: `GOVERNING-METHODOLOGY-NON-PUBLIC.md` (the user's master prompt of 27 Nov 2026, verbatim).

## Duplicate rule

Only the user's master spreadsheet counts as a duplicate (`PRIVATE NEW- 27_11.xlsx` in their Drive folder; user's instruction of
27 Nov 2026). The older 48-tab sheet and earlier waves do not exclude a company. Listed companies and brands holding a current
F1 deal are not eligible.

- `register.py [master.xlsx]` builds `register.json.gz`. Pass the master once; its names are kept in `master_names.json.gz`.
  Re-run with a fresh download when the user updates the master.
- `check.py "Name | website"` prints IN MASTER, F1 PARTNER, LISTED?, POSSIBLE or NEW.
- `delivered/<batch>.json` lists what has been delivered under this methodology; the register treats those as duplicates.
  They are held apart from the master names, so a batch can be rebuilt (`check.lookup(name, batch='b01')` ignores that batch's own names);
  check.py prints ALREADY DELIVERED for them.
- `f1_extra.json` and `f1_gp_partners_2026.json` add Grand Prix-level partners (promoters' own partner pages) to the F1 roster.
  The first roster was thin on these: ADNOC, a founding partner of the Abu Dhabi Grand Prix, was caught only by a spot check.
  Before any delivery, check the top-ranked names for a current F1 deal on the web.

## Research

- `brief_discovery.md` is the brief for discovery agents; one sector cluster per agent, four files per agent in `batches/<batch>/`
  (`<key>.jsonl` qualified, `watch_<key>.jsonl`, `dups_<key>.jsonl`, `notes_<key>.txt`).
- `brief_backtest.md` and `backtest.py` cover the backtest on privately owned F1 sponsors (`backtest/`).
- A company read off a ranking page only (the same list page cited by 15+ lines, or no page) is not scored or ranked: it goes to the
  workbook's `Discovered - To Assess` tab and to `batches/<batch>/to_assess.json`, and is NOT recorded as delivered, so a later
  batch can assess it properly.

## Scoring and the workbook

- `score.py` holds every rule: Routes A, B, C, financial confidence, investment tier bands by company type, and the
  35/30/25/10 score. `RUBRIC` there is the plain-words version printed on the workbook's Methodology tab.
- `build.py check` prints the counts; `build.py xlsx <file>` writes the workbook through `write.py`.
  Main tabs keep the master's 45 columns (`format.json`) with three added after Outreach Priority.

## Not available

PitchBook, Orbis, D&B Hoovers and Sales Navigator are not accessible. Apollo is not to be used. Check the Crunchbase allowance
before relying on it. Never invent a figure, an owner, a signal or a source.

## Batch record

- b01 (27 Nov 2026): 14 sector clusters, first depth. Workbook `reports/F1-NON-PUBLIC-NEW-PROSPECTS-REVISED-METHOD-BATCH-1-2026-11-27.xlsx`.
  Each `notes_<key>.txt` ends with the names that cluster did not get to; start batch 2 from those lists and from `to_assess.json`.
- b02 (27 Nov 2026): three discovery streams into one register. Workbook `reports/F1-New-Non-Public-Prospects-Batch-2.xlsx`.
  Continuation checkpoint: `CHECKPOINT.md`.

## Batch 2 onwards: three streams, one register

The user's instruction of 27 Nov 2026 (second message): run Clay, Crunchbase and independent web research in parallel, merge them
into one discovery register, deduplicate against the master AND every batch already delivered before any detailed research, track
which stream found each company, and report coverage by stream. The older 48-tab sheet still does not exclude a company.

- Web discovery: `brief_b02.md` (one sector in depth, or country rankings in local languages). Each researcher keeps a DISC file
  (`disc_<key>.jsonl`): every name read off a list, whatever became of it. MAIN and WATCH hold only researched companies.
- Clay: `brief_clay.md` (search only, no paid enrichment; rows in `discovery/clay/*.jsonl`). Clay marks listed companies and local arms
  of multinationals as privately held and its revenue is a modelled bracket, so a Clay name is never ranked without a web check.
  Unchecked new Clay names go to the `Clay Leads (Unconfirmed)` tab.
- Crunchbase: check `cb_metering_get_state` first. It was exhausted for the whole of batch 2.
- Research queue: `queue.py <batch> <rows> <files> <start>` writes `in_qNN.jsonl` from the register (new, not yet researched,
  round-robin across streams); `brief_queue.md` is the brief. About 25 to 45 of every 80 names qualify.
- `batch2.py` builds the register, the Research Coverage table and the Clay leads tab; `deliver.py <batch> <xlsx>` builds and records
  the delivery; `validate.py <xlsx> <batch> [master.xlsx]` checks the result.
- Second duplicate pass: `fuzzy.py <batch>` lists delivered names that share their distinctive words with a master or delivered name
  (the exact check misses "Storck" against "August Storck"). Review the pairs and put confirmed ones in
  `batches/<batch>/manual_dups.json` as `[[name, reason]]`. Do this before every delivery.
- A subsidiary whose parent is on the master or already delivered is kept only as a distinct brand, and its row says so
  (`_parent_master`); a regional trading brand of the same business is a duplicate.
- Researchers finish in about 10 to 20 minutes and leave most discovered names unresearched: plan follow-up queue files, not longer briefs.

## Older-sheet brands that are not on the master, and the template trackers

`older_sheet_gap.py <23 Nov all-sector list.xlsx> <out.xlsx>` writes `reports/F1-Older-Sheet-Brands-Not-On-Master.xlsx`: brands on the
user's older 48-tab sheet that qualified on the 23 Nov list and are not on the master, not delivered and not F1 partners, one tab per
sector, with the user's own marking (x, blank on a marked tab, tab not gone through).

`templates.py "<label>=<tracker.xlsx>" ...` stores the user's template trackers in `templates_built.json`. A row whose brand already has
a template is filled green and says so in the last column; a tracker brand that was not built says "No" with the tracker's reason and
is not green. Names are matched exactly; any other pairing goes in `SAME` in `templates.py` after a check by hand.
