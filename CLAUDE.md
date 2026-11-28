# Project notes

## Non-public company prospecting (Formula 1 sponsorship)

The governing methodology for every non-public company prospecting exercise is
`brandprofile/v2/GOVERNING-METHODOLOGY-NON-PUBLIC.md` (the user's master prompt of 27 Nov 2026, stored verbatim).
Read it before any such work. The working rules built from it are in `brandprofile/v2/README.md`.

Standing points from it:
- Deliver only brands that are absent from the user's master spreadsheet (`PRIVATE NEW- 27_11.xlsx` on their Drive). The user
  clarified on 27 Nov 2026 that ONLY that master counts as a duplicate: the older 48-tab sheet and earlier waves do not exclude.
  Check each name with `brandprofile/v2/check.py` before it goes on a list, and record every delivered name in `v2/delivered/`.
- From batch 2 (user's second instruction of 27 Nov 2026): run Clay, Crunchbase and independent web research as three streams into
  one discovery register; deduplicate against the master and every batch already delivered; record which stream found each company;
  give a coverage summary by stream; research one sector in depth at a time; do not loosen the financial parameters to add names.
  The continuation checkpoint is `brandprofile/v2/CHECKPOINT.md`.
- Financial qualification is OR-based (Routes A, B, C). Missing financial data is not negative evidence.
- Keep the existing spreadsheet format. Rank within each sector and across sectors by the 35/30/25/10 score.
- Deliver new brands as a workbook with one tab per sector in the format of the public-company master
  (`reports/F1-PUBLIC-COMPANIES-MASTER-2026-11-15.xlsx`: 22 columns from Company Name and Headquarters to Priority Score, Geographic
  Reach as its own column, rows by score): `brandprofile/v2/public_format.py <batch> <xlsx>`. The user asked for this on 28 Nov 2026
  after finding the 61-tab batch 2 workbook too complex to open and rejecting a one-sheet version. Keep the full workbook in
  `reports/` as supporting material; do not lead with it.
- Third instruction, 28 Nov 2026 (`brandprofile/v2/INSTRUCTION-COVERAGE-AND-PRIORITISATION.md`, verbatim): go beyond the sector list and
  along each value chain; close the gaps in Japan, China, Korea, India, South-East Asia, the Middle East, Turkey, Africa and Latin
  America with local-language sources; page database searches as far as they go; do not call a batch complete because the researchers
  finished: cross-check against rankings nobody used (`v2/brief_audit.md`, `v2/found.py`) until several of them show few misses.
- The user's go-ahead of 28 Nov 2026: use every resource and research agent; the December Crunchbase allowance may be used (it resets
  on 1 Dec 00:00 UTC); the 5,636 older-sheet brands that are not on the master are re-scored and included (`v2/older.py`); the user
  does not want to be asked again to run another round, so schedule the continuation yourself and report.
- Priority scores: missing information is not negative evidence. Since 28 Nov the rubric scores an unknown at the midpoint, and
  buying intent nobody researched takes the average found among researched companies, never zero; High still needs a confirmed, dated
  signal. Researchers read each company's news page (`v2/brief_b03.md` point 10, `v2/brief_signals.md`). Never raise a score without evidence.
- The lead deliverable is one workbook for every new brand: `brandprofile/v2/consolidated.py <xlsx>` (public-company format, a ranked
  tab per sector, the cross-sector ranking, Verification Required, plus Qualification Status, Where It Came From, the user's marking
  and Template Already Built at the right; template rows green).
- Limits met on 28 Nov: 20 subagents at once (hard); the machine has 4 CPUs, so the Workflow tool runs only 2 agents at a time: use
  background agents and the launch list in `brandprofile/v2/batches/b03/launch_log.md`.
- Send files with the file card in the conversation. Do not put files in the user's Google Drive: I did so once on 28 Nov 2026 without
  asking and the user said they do not want that.
- Never invent figures, owners, signals or sources. Say what was and was not completed.
