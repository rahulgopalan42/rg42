# Apollo funded pull brief (Wave 15)

The user has explicitly approved up to 400 Apollo credits for this pull (1 credit per page). Do not ask again; do not exceed your assigned pages.

1. Load the tool: ToolSearch "select:mcp__Apollo_io__apollo_mixed_companies_search".
2. For each page in your assigned range, call it with EXACTLY these arguments (only `page` changes):
   _conversation_ref: "f1w15sweep01"
   _rationale: "User-approved funding-based company pull across all sectors for an F1 prospect coverage check."
   total_funding_range: {"min": 100000000}
   organization_num_employees_ranges: ["51,200","201,500","501,1000","1001,5000","5001,10000","10001,1000000"]
   per_page: 100
   page: <n>
3. The result is too large and gets saved to a file; the error message gives the path. Parse that file with python3 -I (json.loads of the whole file) and append every entry of `organizations` (and `accounts` if any) to your output TSV.
4. Output TSV (create with header first): fields name, primary_domain, founded_year, organization_revenue_printed, publicly_traded_exchange, owned_by_organization, linkedin_url, naics_codes, sic_codes, page. Lists/dicts as JSON strings; strip tabs and newlines. Append after every page.
5. If a page errors, retry once, then skip it and note it.
6. Report ONLY: pages fetched, rows written, pages skipped. Under 60 words.
