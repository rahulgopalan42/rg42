# Web-identification brief: unrecognised funded companies (public information only; no Clay/Apollo/Lusha credits)

Each input row is a company that Apollo lists with total funding >= USD 100M (or Lusha, same filter) and that is
NOT in any of SPORTFIVE's existing prospect databases, but our research model could not identify it from memory.
Identify it from public web information and score it for Formula 1 sponsorship. Today is 19 Oct 2026.

## Input
`/home/user/rg42/parents/score_in/chunk_NN.json`: rows
`[name, domain, hq_country_hint, exchange_hint, revenue_hint, industry_hint, naics_hint, children, connector_funding_flag]`.

## Method (per company, keep it cheap)
1. One WebSearch: `"<name>" <domain>` (or `"<name>" company funding` if no domain). Read the snippets.
2. Only if the snippets do not tell you what the company does, WebFetch `https://<domain>` once.
3. Do not spend more than two tool calls on one company. If still unclear, status "U".
Never invent a figure: valuation / funding only if a snippet or page states it (give the source in `note`).

## Output
`/home/user/rg42/parents/score_out/chunk_NN.json`: EXACTLY one row per input row, same order, the 25 fields of
`score_brief.md` (read it for field definitions and sectors):
`[in_name, status, parent_name, hq_country, domain, type, ticker, val_bn, val_basis, val_date, funding_m, sector, brand, approach, why, a, s, l, n, fin, f1, subs, conf, qualifies, note]`
- status "P" operating company that is its own ultimate parent; "S" subsidiary (give the parent); "X" not a prospect
  (fund / investment vehicle / SPV / public body / non-profit / university / defunct / acquired-and-absorbed /
  tobacco / sanctioned); "U" still unidentifiable.
- qualifies "Y" only if a source states valuation >= USD 1B, funding >= USD 100M or revenue >= USD 100M; else "?".
- `note` <= 20 words: what the company does + source domain (e.g. "AI drug discovery; crunchbase.com").
- conf: "M" if identified from a credible source, "L" if thin evidence.

Validate with /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I
(row count and order, 25 fields, numeric ranges, status/qualifies codes). Helper scripts go in the scratchpad folder
named in your task. Do not run git. Reply in 2 lines: rows written, counts by status.
