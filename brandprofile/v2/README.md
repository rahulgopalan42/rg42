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
