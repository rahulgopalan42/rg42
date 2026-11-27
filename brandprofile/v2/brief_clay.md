# Brief (batch 2): Clay discovery stream

Today is 27 November 2026. Work from `/home/user/rg42/brandprofile`.
Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

Goal: pull candidate non-public companies of real scale out of Clay's company search for the industries in your task and save them
as compact rows. Another step checks and researches them; you extract.

Tools: load with ToolSearch `select:mcp__Clay__search-companies,mcp__Clay__load-more-search-results`. If they are not available to
you, stop and report that at once. Do NOT call add-company-data-points, run_subroutine or any enrichment tool (they cost credits).
Do not render widgets.

Query form (one query per industry and revenue group):
`select from companies where industry = "<industry>" and company_type in ("Privately Held", "Partnership", "Self Owned") and annual_revenue in (<brackets>)`
Revenue brackets, in this order: first ("1B-10B", "10B-100B", "100B-1T"), then ("500M-1B"), then ("200M-500M") where your task says so.
`industry` is an enum: if a value is rejected, read the error or the tool description for the valid names and use the closest ones.
You may add a second pass with `locations.any(region = ...)` or country filters if a query has far more results than you can page.
Page with load-more-search-results (pass the latest taskId) until `hasMore` is false or you reach the page cap in your task.

After EVERY page, append its rows to your OUT file with a short Python heredoc, then move on (do not hold rows for later):

    {"name": "", "domain": "", "country": "", "locality": "", "industry": "", "size": "", "employee_count": 0, "annual_revenue": "",
     "funding_range": "", "type": "", "desc": "<first 200 characters of the description, plus any sentence that names an owner or parent:
     'subsidiary of', 'part of', 'owned by', 'a ... company', NYSE/NASDAQ tickers>", "linkedin": "", "query": "<industry | brackets>"}

Skip nothing: listed subsidiaries, odd rows and duplicates are filtered later. Copy values exactly; do not add facts from memory.

When extraction is done, run the duplicate check over all rows and write the result into each row:

    <python> -I v2/disc_check.py <your OUT file>

NOTES file (plain text): each query, the number of pages read, the rows saved, whether `hasMore` was still true when you stopped
(= unfinished, say so), industries not reached, and the counts by check status printed by disc_check.py.
Final report: under 120 words.
