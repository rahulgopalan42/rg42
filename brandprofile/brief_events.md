# Brief: what has happened since 1 November 2026 to companies on the user's prospect lists

Today is 23 November 2026. The user sells Formula 1 sponsorships and keeps lists of UNLISTED companies that can afford one (about
9,700 companies: their own sheet plus 2,039 new brands added on 18 November). A company leaves the list when it becomes a Formula 1
partner, lists its shares, is absorbed by a buyer or closes; it changes when it is bought (the buyer becomes its parent). Your job is
to find such events in ONE field (named in your task) and report each one as a line. Accuracy matters more than volume: every line
must rest on a page you found in this session.

For every company in an event, run the lookup and copy what it prints into "known_as":
    /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I /home/user/rg42/brandprofile/newsec/on_sheet.py "Name one" "Name two" ...
Report the event whatever the lookup says ("new" companies included): the matching is done afterwards.

Write ONE JSON object per line to your EVENTS file:
{"company": "...", "known_as": "what on_sheet.py printed", "event": "f1_partner|listed|ipo_filed|acquired|merged|taken_private|closed|raised|sponsorship",
 "date": "DD Mon YYYY",                 // the date of the announcement, as the page gives it
 "detail": "one factual sentence: who, what, the amounts and terms as the page states them",
 "counterparty": "the F1 team or series, the exchange, the buyer, or \"\"",
 "owner": "for a brand: the company that owns it, if the page says so, else \"\"",
 "usd_m": null, "valuation_usd_m": null,   // USD millions where the page gives a figure
 "status": "completed|announced|reported", // reported = press report resting on unnamed sources
 "source_url": "https://..."}

Meaning of the events
- f1_partner: a brand announced as a sponsor, partner or supplier of the Formula 1 championship, an F1 team or a Grand Prix, for 2026 or
  2027, in an announcement dated 1 October 2026 or later. Give the team and the start of the deal. Include renewals only if the brand is new
  to that team. Include deals that were announced to END (event "sponsorship", detail saying it ends).
- listed: shares began trading on a stock exchange since 1 November 2026 (IPO, direct listing, SPAC merger completed).
- ipo_filed: a public filing or a company announcement of a planned listing since 1 November 2026.
- acquired / merged: a deal for an unlisted company announced or completed since 1 November 2026, at USD 300M or more or with no price given
  but a well-known target. Say whether the target keeps its own brand.
- taken_private: a listed company whose buyout completed (shares delisted) since 1 November 2026.
- closed: insolvency, bankruptcy filing or shutdown of a company that had raised USD 100M or more.

Searching: your task states your WebSearch limit: it is strict. WebFetch is not limited: use it on list pages (team partner pages, IPO
calendars, deal round-ups, newsroom pages) and press releases. If WebSearch is refused with a limit message, stop searching and do not work
around it in any way (no search-engine, Google News, Bing News or RSS search pages through WebFetch or curl); carry on with WebFetch on pages
whose addresses you know. Use only public pages and a declared user agent. Do not use Apollo. Never write a figure, a date or an event you
did not read on a page in this session. Write the file in chunks (append). At the end check it: valid JSON on every line, no event twice.
