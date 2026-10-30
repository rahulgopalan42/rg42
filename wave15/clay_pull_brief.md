# Clay pull brief (Wave 15 coverage sweep)

You are pulling a complete company list from Clay for one sector group, for an F1 sponsorship prospecting coverage check. Today is 13 October 2026.

1. Load tools: ToolSearch with query "select:mcp__Clay__search-companies,mcp__Clay__load-more-search-results". Do NOT use Lusha or Apollo.
2. Read your group's industry list from /home/user/rg42/wave15/sector_groups.json (key given in your task).
3. Run TWO searches, each paged to the end:
   A. select from companies where industry in (<your industries>) and annual_revenue in ("10B-100B", "100B-1T")
   B. select from companies where industry in (<your industries>) and annual_revenue = "1B-10B"
   If Clay rejects an industry value as invalid, drop that value and retry; note which you dropped.
4. For each search, call load-more-search-results with its taskId until hasMore is false, or until 150 pages for search B / 60 pages for search A. If a call errors, retry once, then continue.
5. For EVERY company returned, append one line to /home/user/rg42/wave15/clay_<group>.tsv (create with a header row first) with tab-separated fields: name, domain, country, locality, type, size, employee_count, annual_revenue, industry, linkedin_url, search (A or B). Strip tabs, newlines and "|" from values. Append after each page so nothing is lost. No descriptions.
6. Report back ONLY: rows written per search, pages per search, whether hasMore was still true at the end of each, any industry values dropped, any errors. Under 80 words.
