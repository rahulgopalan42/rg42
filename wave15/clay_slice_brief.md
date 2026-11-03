# Clay slice pull brief (Wave 15 top-up, beats the 4,000-row cap)

Earlier pulls stopped at ~3,000-4,000 rows per search. You re-pull your group in small slices so every slice
finishes. Today is 14 October 2026. The user has asked for this.

1. Load tools: ToolSearch "select:mcp__Clay__search-companies,mcp__Clay__load-more-search-results". No Lusha/Apollo.
2. Industries: the list for your group key in /home/user/rg42/wave15/sector_groups.json.
3. Bands (given in your task): B = annual_revenue = "1B-10B"; C1 = annual_revenue in ("200M-500M","500M-1B").
4. For each band, run one search per size bucket:
   select from companies where industry in (<industries>) and annual_revenue <band> and company_size = "<size>"
   sizes: "10,001+", "5,001-10,000", "1,001-5,000", "501-1,000", "201-500", "51-200".
   Page each with load-more-search-results until hasMore is false (no page cap).
   If a slice reaches 190 pages and hasMore is still true, stop it and re-run that slice split further: one search
   per single industry (industry = "<x>") with the same band and size, each paged to the end.
   If Clay rejects an industry value, drop it and retry. If "too many concurrent requests", wait briefly and retry.
5. Append EVERY company to /home/user/rg42/wave15/clay_slice_<group>.tsv (header first if new): name, domain,
   country, locality, type, size, employee_count, annual_revenue, industry, linkedin_url, search
   (search = "<band>|<size>" or "<band>|<size>|<industry>"). Strip tabs, newlines and "|" from values (except the
   search field). Append after each page. No descriptions. Write rows with python3 -I; helper files only in
   /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/slice_<group>/.
6. If you run low on room before finishing, write /home/user/rg42/wave15/clay_slice_<group>.progress.txt listing
   slices done and the slice in progress (with its page count), then stop; you will be continued.
7. Report ONLY: rows per band, slices finished, slices still open. Under 60 words.
8. Save room: when a search result is saved to a file, parse it with python3 -I and print only the row count,
   hasMore and the next taskId. Never print or read full result payloads.
