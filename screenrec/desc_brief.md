# Company descriptions for the F1 prospect workbook (knowledge only: no web search, do not run git)

SPORTFIVE sells Formula 1 sponsorship. Rahul has a ranked list of ~19,000 companies read from Crunchbase. He wants,
for every company, a description detailed enough that he does NOT need to open LinkedIn or the website to understand
what the company does and whether it could be an F1 sponsor.

## Input
`/home/user/rg42/screenrec/desc/in_NNN.json`: a JSON array of rows
`[id, brand, hq_country, hq_location, crunchbase_industries, crunchbase_short_description, total_funding_as_shown, last_funding_date, listed]`.
The Crunchbase fields were read from screen recordings, so they are cut short ("...") and may contain small OCR typos.
`listed` = true means the row came from a search for listed (public) companies.

## Output
`/home/user/rg42/screenrec/desc/out_NNN.json` (same NNN): a JSON array, one row per input row, SAME ORDER:
`[id, about, conf]`
- `id`: copied exactly from the input.
- `about`: 60-110 words of plain English, written for a sponsorship seller. Cover, in this order where known:
  1. What the company is and does: its main products / services / brands (name them), in concrete terms.
  2. Who its customers are (consumers, enterprises, governments; which industries) and how it makes money.
  3. Where it operates (HQ city and key markets) and scale markers you are confident of (employees, revenue,
     customers, users, stores, fleet, production capacity, notable funding or valuation, year founded).
  4. Ownership / status if relevant: listed (exchange + ticker), acquired (by whom, when), merged, defunct,
     state-owned, subsidiary of X, PE-owned.
  5. One short line on consumer / brand visibility (e.g. "consumer brand sold in 40 countries", "B2B, little
     public brand awareness") - this is what matters for sponsorship.
  No marketing fluff, no repeating the company name in every sentence, no bullet points, no line breaks.
- `conf`: "H" you clearly know this company; "M" you know it partly (sector, main product) and the rest comes from
  the input; "L" you do not recognise it - then write ONLY what the input supports (expand the Crunchbase line and
  industries into clear sentences, say where it is based) and end with "(Limited public information - check before
  outreach.)". NEVER invent products, figures, customers, owners or dates. Same-named companies exist: use the HQ,
  industries and description to make sure you describe the right one; if unsure which one it is, use "L".
- If you know the company was acquired, went public, merged, renamed or closed, say so with the year.

## How to work
- Process the rows in order and write the output in pieces (e.g. 50 rows at a time: build the array in a Python
  script or append to a JSON file), so nothing is lost if you run long.
- When done, validate with `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`:
  same number of rows as the input, ids in the same order, every `about` 40-140 words, `conf` in H/M/L.
- Reply in ONE line: rows written and the count of H / M / L.
