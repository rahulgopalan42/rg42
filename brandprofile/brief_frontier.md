# Addendum for technology themes (read after brief_newsectors.md)

Your group is a technology THEME rather than an ownership type. Everything in brief_newsectors.md applies, with these differences.

1. Most companies here qualify on test (a): equity raised of USD 150M or more IN TOTAL, with no limit on how long ago the last round was.
   Test (c) (valued at or bought for USD 1B or more since November 2023) is the next most common. Prove whichever you use from a page.
2. Pre-revenue companies stay in. Add the field "stage": "commercial" or "pre-revenue" to every line.
3. Add the field "theme": the theme named in your task (use the sub-theme where your task lists several, e.g. "Quantum computing").
4. The user's sheet already holds about 18,850 brands. Only companies that are NOT on it are wanted. Before you research a candidate, check it:
       /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I /home/user/rg42/brandprofile/newsec/on_sheet.py "Name one" "Name two" ...
   (as many names per call as you like). "ALREADY KNOWN" = leave it out. "POSSIBLY KNOWN" = it lists similar names; leave the candidate out if one
   of them is the same company. "new" = research it. Expect most well-known names to be on the sheet already: nominate widely (60-150 candidates,
   all regions: United States, Canada, UK, Europe, Israel, Gulf, India, China, Japan, Korea, South-East Asia, Australia, Latin America, Africa)
   so that enough new ones remain.
5. How to work with few searches: nominate candidates from what you know and from list pages you fetch (Wikipedia lists and categories, the
   Wikipedia "List of unicorn startup companies", industry league tables, investor portfolio pages, news round-ups). Then confirm each "new"
   candidate from a page you fetch: its Wikipedia article, its own newsroom, or a news article. You can read several Wikipedia articles in one
   call with: https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&exintro=0&exlimit=20&redirects=1&format=json&titles=A|B|C
   A fact you only remember does not count: if no fetched page states the funding total, valuation or revenue, leave the company out.
   Totals may be built from rounds stated on fetched pages; say so in capacity_detail (e.g. "Series B USD 100M (2023) + Series C USD 200M (2025)").
6. Leave out companies that are listed (including by SPAC or on any exchange), bought by a listed group, or closed.
