# Apollo pull brief: companies with total funding >= USD 100M

The user has explicitly approved, in this session, a batch of up to 250 Apollo company-search pages
(1 credit each) for this pull. Your task names the pages you own. Do NOT call any other Apollo tool
(no enrich, no people search, no lookup) and do NOT fetch pages outside your range.

## Call
Tool: `mcp__Apollo_io__apollo_mixed_companies_search` (load it with ToolSearch `select:mcp__Apollo_io__apollo_mixed_companies_search` first).
Arguments for every call: `total_funding_range = {"min": 100000000}`, `per_page = 100`, `page = <N>`,
`_conversation_ref = "f1parents2026"`, `_rationale = "User-approved batch pull of funded companies for F1 prospecting"`.
Skip a page whose output file already exists.

## Output
For each page write `/home/user/rg42/parents/apollo/page_NNN.json` (NNN = 3-digit page number) with the Write
tool: a compact JSON array, one array per organization in the `organizations` list (and per `accounts` entry
if any), fields in this order:

`[id, name, primary_domain, linkedin_url, founded_year, publicly_traded_exchange, owner_name, owner_website, revenue_printed, sic0, naics0]`

- `id`: Apollo organization id (`id` for organizations, `organization_id` for accounts).
- `primary_domain`: `primary_domain` (or `domain` for accounts); "" if missing.
- `publicly_traded_exchange`: "" if missing.
- `owner_name` / `owner_website`: from `owned_by_organization.name` / `.website_url`, "" if none.
- `revenue_printed`: `organization_revenue_printed` or "".
- `sic0` / `naics0`: first SIC / NAICS code or "".
Use "" for any missing string and null for a missing founded_year. Keep names exactly as Apollo gives them.

Then validate each file with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`:
valid JSON, every row has 11 fields, row count equals the number of organizations returned.
Keep helper scripts in the scratchpad folder named in your task. Do not run git.
Reply in 2 lines: pages written with row counts, and the `total_entries` reported by Apollo.
