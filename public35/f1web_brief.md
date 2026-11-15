# Brief: web check - is this listed company a current Formula 1 sponsor?

Each input line is a listed company (JSON: sym, name, country, sector) that our roster says is NOT a current Formula 1
partner. Check that with the web. For each company run ONE WebSearch (a second one only if the first is unclear), e.g.
`"<company>" Formula 1 partner OR sponsor 2026 team` - also think of its best-known brands.

Classify from what the search results actually say:
- "current": the company, its parent, a subsidiary or one of its brands is a sponsor, partner or supplier of the Formula 1
  championship, an F1 team or a Grand Prix in the 2025 or 2026 season. Say which property and since when.
- "past": a sponsorship existed but ended before 2025 (say which, and when it ended if known).
- "related": not a sponsorship of F1 itself but close: broadcaster / media-rights holder, licensing or merchandise
  collaboration, F1 Academy or driver-personal sponsor, F2/F3, race promoter. Say what.
- "none": the results show no Formula 1 sponsorship.
- "unclear": conflicting or thin results.
- "not_checked": you could not search (tool unavailable or out of budget).

Rules: use only what the search results show - do not answer from memory alone, do not invent URLs. `source_url` must be
a URL that appeared in your search results and supports the status ("" for none / not_checked if nothing relevant came
back). Keep `detail` under 30 words. If WebSearch stops working, mark the remaining companies "not_checked" and finish.

Output: one JSON object per input line, same order:
{"sym": "...", "status": "current|past|related|none|unclear|not_checked", "detail": "...", "source_url": "..."}
Append to the output file as you go (every 5-10 companies) so progress is saved. Keep helper files in your own scratch
directory (named in your instructions). Create no other files in the repository.
Reply with: counts per status, and the list of "current" and "unclear" companies.
