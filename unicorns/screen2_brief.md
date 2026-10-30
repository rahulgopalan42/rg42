# Quick screen of Apollo / Clay "total funding USD 200M+" names (knowledge only, fast; do not run git)
These databases are noisy: their funding filter catches public companies, big corporates, subsidiaries, funds, banks,
debt-funded lenders, tiny firms with wrong data, and junk records. Rahul wants PRIVATE, INDEPENDENT companies that have
raised USD 200M+ in EQUITY (any valuation, including undisclosed).
Input `/home/user/rg42/unicorns/pool2/screen_in/<chunk>.json`: rows [name, domain, source].
For each row give a verdict:
- "Y": you believe it is a private, independent, operating company with USD 200M+ equity raised (venture, growth or
  PE growth equity);
- "?": plausible venture/growth-backed company, but you are unsure about the amount or its status;
- "N": public/listed, acquired or a subsidiary of another group, a fund/investor/bank, government, university,
  non-profit, media outlet, family/founder-owned without outside equity of USD 200M+, clearly small, defunct, or unknown
  and unlikely.
Output `/home/user/rg42/unicorns/pool2/screen_out/<chunk>.json`: one row per input row, same order:
[name, domain, verdict, hq_country, sector_1_to_48, reason (<= 10 words)]. Sector numbers are in
/home/user/rg42/unicorns/brief.md. Validate the row count with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`. Reply in 1 line: counts Y/?/N.
