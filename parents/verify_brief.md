# Web-verification brief: top-ranked NEW parent companies (public information only; no paid credits)

Each input row is a parent company in our new-prospect ranking whose figures came from research memory. Verify
them from public sources so the ranking is accurate. Today is 19 Oct 2026.

## Input
`/home/user/rg42/parents/verify_in/chunk_NN.json`: rows
`[key, name, domain, claimed_val_bn, claimed_basis, claimed_funding_m, claimed_f1_link, type]`.

## Method (per company, at most 3 tool calls)
1. WebSearch `"<name>" market cap` for listed companies, or `"<name>" valuation funding` for private ones; read snippets.
2. If needed, WebFetch one page (company site, stockanalysis.com, companiesmarketcap.com, crunchbase, a news article).
3. WebSearch `"<name>" Formula 1 sponsor OR partner 2026` ONLY if claimed_f1_link is non-empty or the company is
   consumer-facing and large (>= USD 10B).

## Output
`/home/user/rg42/parents/verify_out/chunk_NN.json`: one row per input row, same order, 12 fields:
`[key, verdict, val_bn, val_basis, val_date, funding_m, revenue_m, f1_status, parent_ok, source, note, conf]`
- verdict: "OK" figures confirmed within ~25%; "CORRECTED" you found a different figure (give it); "UNVERIFIED" no
  usable source found; "NOT_A_PROSPECT" (defunct, acquired and absorbed, fund vehicle, sanctioned, tobacco).
- val_bn (USD billions, 1 decimal) / funding_m / revenue_m (USD millions): the verified figures, null if none.
- val_basis "market cap" / "last funding round" / "reported valuation"; val_date "YYYY-MM" of the figure.
- f1_status: "" no current F1 / F1-team deal found; "current: <deal>" ; "former: <deal>"; "unknown".
- parent_ok: "Y" it is the ultimate parent; "N: <actual parent>" if it is owned by another group.
- source: the domain(s) used (e.g. "stockanalysis.com; reuters.com").
- note <= 20 words. conf "H" (official or major financial source), "M", "L".
Never invent a figure. Validate with the venv Python (row count, 12 fields, numeric types). Helper scripts in the
scratchpad folder named in your task. Do not run git. Reply in 2 lines: rows written, counts by verdict.
