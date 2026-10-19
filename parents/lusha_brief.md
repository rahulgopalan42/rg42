# Lusha pull brief: companies with total funding >= USD 100M

The user has explicitly approved, in this session, up to 60 Lusha credits for this pull (1 credit per 25
results; a page of 50 costs 2 credits). Your task names the pages you own. Do NOT call any other Lusha
tool that costs credits (no enrich, no reveal, no signals, no lookalikes) and do NOT fetch pages outside
your range. If a call returns an error about credits or rate limits, stop and report.

## Call
Tool: `mcp__Lusha__prospecting_company_search` (load it with ToolSearch `select:mcp__Lusha__prospecting_company_search` first).
Arguments for every call:
`funding = {"ranges": [{"coverage": "total_funds", "min": 100000000}]}`, `page_size = 50`, `page = <N>` (0-based),
`reason_for_invocation = "User-approved batch pull of funded companies for Formula 1 sponsorship prospecting"`,
and pass back the `conversation_id` from the previous Lusha response.
Skip a page whose output file already exists.

## Output
For each page write `/home/user/rg42/parents/lusha/page_NNN.json` (NNN = 3-digit page number) with the Write
tool: a compact JSON array, one array per company, fields in this order:

`[lusha_id, name, domain, country, industry, size_or_employees, revenue_range, total_funding, last_round, is_ipo, linkedin]`

Use the field names Lusha returns (print one raw result first to see them); use "" / null where a value is
missing. Do not invent values.

Then validate each file (valid JSON, 11 fields per row, row count = results returned) with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.
Keep helper scripts in the scratchpad folder named in your task. Do not run git.
Reply in 2 lines: pages written with row counts, credits used, and the total result count Lusha reports.
