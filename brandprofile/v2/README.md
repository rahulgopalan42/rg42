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

## Research

- `brief_discovery.md` is the brief for discovery agents; one sector cluster per agent, four files per agent in `batches/<batch>/`
  (`<key>.jsonl` qualified, `watch_<key>.jsonl`, `dups_<key>.jsonl`, `notes_<key>.txt`).
- `brief_backtest.md` and `backtest.py` cover the backtest on privately owned F1 sponsors (`backtest/`).

## Scoring and the workbook

- `score.py` holds every rule: Routes A, B, C, financial confidence, investment tier bands by company type, and the
  35/30/25/10 score. `RUBRIC` there is the plain-words version printed on the workbook's Methodology tab.
- `build.py check` prints the counts; `build.py xlsx <file>` writes the workbook through `write.py`.
  Main tabs keep the master's 45 columns (`format.json`) with three added after Outreach Priority.

## Not available

PitchBook, Orbis, D&B Hoovers and Sales Navigator are not accessible. Apollo is not to be used. Check the Crunchbase allowance
before relying on it. Never invent a figure, an owner, a signal or a source.
