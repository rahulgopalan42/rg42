# Refresh of 23 November 2026: addendum (read after brief_newsectors.md, brief_pass2.md and brief_subs.md)

Today is 23 November 2026. The user's list of unlisted companies was last built on 18 November 2026 (2,039 new brands, plus the
brands on the user's own sheet). The user now wants it brought up to date: NEW brands that qualify today, and NEWS about brands the
user already has. Everything in the three earlier briefs applies (who qualifies, the five capacity tests, subsidiaries in scope with a
parent, the output line, "every fact from a page you found in this session", no Apollo). Where they conflict, this file wins.

## What you look for
Your task names a field (a region, a sector or a kind of event). In that field, find what was ANNOUNCED OR REPORTED SINCE 1 NOVEMBER 2026,
with most weight on the last ten days (13-23 November 2026):
- equity rounds of USD 100M or more, and any round that values the company at USD 1B or more;
- companies newly valued at or bought for USD 1B or more; buyouts, carve-outs and spin-offs that create a stand-alone unlisted company;
- companies taken private (delisted) since 1 November 2026: they are unlisted now;
- unlisted companies that signed a top-tier sports sponsorship (the list in brief_newsectors.md, point 3d).
Older companies that qualify and that the lookup below calls "new" are welcome too: nothing that qualifies should be left out.

## Check every company first
    /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I /home/user/rg42/brandprofile/newsec/on_sheet.py "Name one" "Name two" ...
- "new" -> research it. If it qualifies (brief_newsectors.md point 3, on a page you found), write the full line to your MAIN file.
  If it looks right but a test or its ownership could not be shown from a page, write it to your UNCONFIRMED file (brief_pass2.md point 4).
- "ALREADY KNOWN ... on the sheet" or "... in the new-brands workbook" -> the user has it. Do NOT write a full line. If what you found is
  news about it since 1 November 2026 (round closed, listing, IPO filing, bought, merged, closed down, new F1 or other top-tier
  sponsorship, new CEO or marketing chief, new country), write ONE line to your EVENTS file (format below).
- "ALREADY KNOWN ... listed" -> leave it out, unless it was taken private or delisted since 1 November 2026 (then: EVENTS file, event "taken_private").
- "ALREADY KNOWN ... current F1 partner" -> leave it out.
- "POSSIBLY KNOWN" lists similar names: decide whether one is the same company.

## The MAIN file line
The JSON object of brief_newsectors.md, plus "stage" and "theme" (brief_pass2.md point 2), plus "parent", "parent_listed", "parent_stake"
and "parent_f1" (brief_subs.md; all four are "" for an independent company). In "signals", "raise" is the round you found, written as
"what happened (Mon YYYY; url)". Convert currencies at about EUR 1.10, GBP 1.30 and say the original amount in "capacity_detail".
A round of USD 100-149M qualifies only if the page also shows total equity raised of USD 150M or more, or a valuation of USD 1B or more.

## The EVENTS file line (news about a company the user already has, or a listed company gone private)
{"company": "...", "known_as": "what on_sheet.py printed for it", "event": "raised|listed|ipo_filed|acquired|merged|taken_private|f1_partner|sponsorship|closed|leadership|expansion",
 "date": "DD Mon YYYY", "detail": "one factual sentence with the amounts as the page states them", "counterparty": "investor, buyer, exchange, team or property, or \"\"",
 "usd_m": 500, "valuation_usd_m": 5000,        // USD millions, null where the page gives none
 "source_url": "https://..."}

## Searching
Your task states your WebSearch limit: it is strict. WebFetch is not limited: use it on round-up pages that list many deals at once
(weekly "biggest funding rounds" articles, daily funding news pages, regional funding trackers, unicorn lists, league tables) and on
press releases. If WebSearch is refused with a limit message, stop searching and do not work around it in any way (no search-engine,
Google News, Bing News or RSS search pages through WebFetch or curl); carry on with WebFetch on pages whose addresses you know.
Use only public pages and a declared user agent. Never write a figure, a date or an event you did not read on a page in this session.
Write your files in chunks (append). At the end check them: valid JSON on every line, no company twice, desc 10-20 words.
