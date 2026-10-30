# New-brand discovery brief (knowledge only: no web, no connectors; do not run git)

Read `/home/user/rg42/brands200/verify_brief.md` first: Rahul's money rule, the 38-field output row, the scoring
scales and the sector list there all apply. This brief only changes where the rows come from.

## Your task
Your task names ONE sector. From your own knowledge, list brands in that sector that meet the money rule and would
make sense as Formula 1 sponsorship prospects (cheque about USD 2.5M a year):
- FUNDING: private, founder-owned, family, PE-backed or partnership companies that have raised more than USD 200M
  in equity (scale-ups and unicorns, especially with raises in 2024-26), or
- LISTED REVENUE: listed companies with annual revenue or ARR of USD 100M or more (mid-caps outside the headline
  indices are especially welcome: Japan, Korea, India, Southeast Asia, Gulf, Turkey, Latin America, Nordics, Iberia,
  Benelux, Central Europe, Australia, Canada).
Brands of larger groups are allowed when the brand has its own marketing budget; give the parent.

## Not wanted
- Anything in the known-names file named in your task (it lists names already on Rahul's sheets for this sector);
  names there in any spelling, their parents and their subsidiaries are all out. Many more names are filtered by
  machine after you finish, so prefer companies a sponsorship seller would NOT name from memory.
- Current F1 or F1-team sponsors; funds, SPACs, governments, universities, sports clubs, tobacco, sanctioned countries.
- Never pad: a company whose funding or listed revenue you cannot state with some confidence is out.

## Output
`/home/user/rg42/brands200/discover_out/sNN.json` (NN = your sector number, two digits): a JSON array of rows in the
38-field format of verify_brief.md. `key` = "ds:" + the brand name. Every row: sector = your sector number,
qualifies "Y" (only rows you believe qualify), status "P" or "S". Target 40-60 rows; fewer is fine.
Validate with `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`
(38 fields, integer scores in range, sector correct). Write in two pieces and merge if long. Reply in 2 lines.
