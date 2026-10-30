# Connector-pool screen (knowledge only, quick; do not run git)
Input `/home/user/rg42/unicorns/pool/screen_in_<n>.json`: rows [name, domain, country, extra] from the Apollo / Clay
"total funding USD 200M+" filters. These databases are noisy: many rows are big corporates, public companies,
universities, media, subsidiaries or wrongly-tagged firms. Rahul wants PRIVATE, independent companies valued at
USD 1B+ with USD 200M+ equity funding raised.
For each row decide: "Y" = you believe it is a private independent company valued >= USD 1B with >= USD 200M raised;
"?" = plausible (venture/growth-backed scale-up that might be valued around or above USD 1B; you are unsure);
"N" = no (public/listed, acquired subsidiary, corporate/family business without venture funding, government,
university, non-profit, media outlet, clearly small, or unknown and unlikely).
Output `/home/user/rg42/unicorns/pool/screen_out_<n>.json`: one row per input row, same order:
[name, domain, country, verdict, reason (<= 10 words)]. Validate row count with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`. Reply in 1 line: counts Y/?/N.
