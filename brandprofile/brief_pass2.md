# Second pass: addendum (read after brief_newsectors.md)

The first pass produced a workbook of 722 new unlisted companies. The user wants nothing missed, so this second pass closes the gaps.
Everything in brief_newsectors.md applies (who qualifies, the five capacity tests, the output line, "every fact from a page you fetched"),
with these additions.

1. Check EVERY candidate before researching it:
       /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I /home/user/rg42/brandprofile/newsec/on_sheet.py "Name one" "Name two" ...
   "ALREADY KNOWN" = leave it out (it is on the user's sheet, already in the new workbook, listed, or an F1 partner).
   "POSSIBLY KNOWN" = it lists similar names; leave the candidate out if one of them is the same company. "new" = research it.
2. Add two fields to every line: "stage": "commercial" or "pre-revenue"; "theme": "" unless your task names one.
3. Working with few searches: WebSearch calls are strictly limited (your task gives the number). WebFetch is not limited. Fetch list pages
   (rankings, league tables, portfolio pages, Wikipedia lists) and company pages (Wikipedia article, the company's own "about", newsroom or
   annual-review page). The Wikipedia API is rate-limited from this machine: use WebFetch on normal article pages and space the calls out.
   If a WebSearch call is refused with a limit message, stop searching and do not work around it in any way (no search-engine pages through
   WebFetch or curl); carry on with WebFetch on pages whose addresses you know.
4. Nothing found may be lost. If a company looks like it qualifies but you could not prove a capacity test or its unlisted status from a page,
   do NOT put it in the main output. Write it to your "unconfirmed" file instead, one JSON object per line:
   {"name": "...", "hq": "City, Country or ''", "group": "...", "sector": "one of the 48 sector names", "what_is_known": "one sentence, from pages you read",
    "missing": "what could not be shown (e.g. 'no page states revenue or funding', 'owner not shown')", "pages_tried": "one or two urls"}
5. Leave out companies owned by an F1 partner (the roster includes Carlyle, so Carlyle-owned companies are out), sanctioned companies, and
   family holdings whose main operating business is itself listed.
6. Use only public pages and a declared user agent. Do not use Apollo. Do not write any figure you did not read on a page.
