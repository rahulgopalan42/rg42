# Verification brief: top-ranked NEW parent companies (offline, from gathered public evidence; no web tools, no credits)

Each input row is a parent company in our new-prospect ranking whose figures came from research memory. A script has
fetched its homepage summary and Wikipedia summary (`/home/user/rg42/parents/peek/verify_NN.json`, same order as
the input, keys: name, domain, title, description, og, h1, text, lang, wiki_title, wiki_desc, wiki_extract).
Use that evidence plus your knowledge to confirm identity, parent status, figures and F1 status. Today is 19 Oct 2026.
Do NOT use WebSearch/WebFetch/Clay/Apollo/Lusha.

## Input
`/home/user/rg42/parents/verify_in/chunk_NN.json`: rows
`[key, name, domain, claimed_val_bn, claimed_basis, claimed_funding_m, claimed_f1_link, type]`.

## Output
`/home/user/rg42/parents/verify_out/chunk_NN.json`: one row per input row, same order, 12 fields:
`[key, verdict, val_bn, val_basis, val_date, funding_m, revenue_m, f1_status, parent_ok, source, note, conf]`
- verdict: "OK" the company is what we think and the claimed figure is plausible (within ~25% of what you know or the
  evidence states); "CORRECTED" you are confident of a different figure (give it); "UNVERIFIED" neither evidence nor
  memory can confirm; "NOT_A_PROSPECT" (defunct, acquired and absorbed, fund vehicle, sports property / circuit /
  team, public body, sanctioned, tobacco).
- val_bn (USD billions, 1 decimal) / funding_m / revenue_m (USD millions): best supported figures, null if none.
- val_basis "market cap" / "last funding round" / "reported valuation"; val_date "YYYY-MM".
- f1_status: "" no current F1 or F1-team deal known; "current: <deal>"; "former: <deal>"; "unknown".
- parent_ok: "Y" ultimate parent; "N: <actual parent>" if owned/controlled by another group.
- source: "homepage" / "wikipedia" / "memory" (combine with ";").
- note <= 20 words. conf "H" only when Wikipedia/homepage evidence and memory agree; else "M" or "L".
Never invent a figure. Validate with the venv Python (row count, 12 fields, numeric types). Helper scripts in the
scratchpad folder named in your task. Do not run git. Reply in 2 lines: rows written, counts by verdict.
