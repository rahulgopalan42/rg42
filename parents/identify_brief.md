# Identification brief: unrecognised funded companies (offline, from gathered public evidence; no web tools, no credits)

Each input row is a company that Apollo lists with total funding >= USD 100M (or Lusha, same filter), that is NOT in
any of SPORTFIVE's existing prospect databases, and that our research model could not identify from memory. A script
has already fetched public evidence for every row: its homepage (title, meta description, h1, first text) and the
Wikipedia summary when one exists. Identify and score each company from that evidence plus your own knowledge.
Today is 19 Oct 2026. Do NOT use WebSearch/WebFetch/Clay/Apollo/Lusha (web budgets are exhausted).

## Input
- `/home/user/rg42/parents/score_in/chunk_NN.json`: rows
  `[name, domain, hq_country_hint, exchange_hint, revenue_hint, industry_hint, naics_hint, children, connector_funding_flag]`
- `/home/user/rg42/parents/peek/score_NN.json`: same order, one object per row with keys name, domain, title,
  description, og, h1, text, lang, wiki_title, wiki_desc, wiki_extract (keys missing when nothing was fetched).
  The wiki match is by name and can be a different entity: trust it only if it plainly describes this company.

## Output
`/home/user/rg42/parents/score_out/chunk_NN.json`: EXACTLY one row per input row, same order, the 25 fields of
`score_brief.md` (read it for field definitions, sectors and the a/s/l/n scoring):
`[in_name, status, parent_name, hq_country, domain, type, ticker, val_bn, val_basis, val_date, funding_m, sector, brand, approach, why, a, s, l, n, fin, f1, subs, conf, qualifies, note]`
- status "P" operating company and its own ultimate parent; "S" subsidiary (name the parent); "X" not a prospect
  (fund / investment or real-estate vehicle / SPV / public body / non-profit / university / hospital system /
  defunct / absorbed / tobacco / sanctioned); "U" evidence too thin to say what it is.
- val_bn / funding_m only when the evidence or your knowledge states a figure (never invent; null otherwise).
- qualifies "Y" if a figure >= the thresholds (valuation USD 1B, funding USD 100M, revenue USD 100M) is known;
  "?" otherwise (the Apollo filter alone is weak evidence); "N" if the evidence shows a tiny company.
- `note` <= 20 words: what the company does + evidence used ("homepage", "wikipedia", "memory").
- conf "M" when the homepage/Wikipedia evidence identifies the company; "L" when identified from memory only.
Validate with /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I
(row count and order, 25 fields, numeric ranges, status/qualifies codes). Helper scripts go in the scratchpad folder
named in your task. Do not run git. Reply in 2 lines: rows written, counts by status.
