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
- Send files with the file card in the conversation. Do not put files in the user's Google Drive: I did so once on 28 Nov 2026 without
  asking and the user said they do not want that.
- Never invent figures, owners, signals or sources. Say what was and was not completed.
