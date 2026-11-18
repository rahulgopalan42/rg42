# Subsidiaries pass: addendum (read after brief_newsectors.md and brief_pass2.md)

Today is 18 November 2026. The user has changed one rule: SUBSIDIARIES ARE NOW IN SCOPE, and every line must name the parent company.
Earlier passes left out any company owned by a listed group, and kept only the parent of an unlisted group. This pass finds those companies.
Everything in brief_newsectors.md and brief_pass2.md applies, with the changes below. Where they conflict, this file wins.

Who qualifies in this pass
1. A SUBSIDIARY: an operating company, or a brand business run as its own company, that is majority-owned (more than 50%) by another
   company, the parent. The parent may be a listed company, an unlisted group, a family conglomerate, a co-operative or a state group.
   It must trade under its own name, with its own website and management. A product line, a division with no identity of its own, or a
   country branch of the parent ("X France") does not count.
2. The subsidiary itself is not listed on a stock exchange. (A subsidiary with its own share listing is out.)
3. It is not itself a current Formula 1 partner. Check EVERY candidate with on_sheet.py (brief_pass2.md, point 1):
   "ALREADY KNOWN" = leave it out. "POSSIBLY KNOWN" = leave it out if one of the names shown is the same company. "new" = research it.
   A company whose PARENT or sister brand is an F1 partner is now ALLOWED: record it and say so in "parent_f1" (see below).
4. It can pay ON ITS OWN FIGURES. At least one of these is stated on a page you fetched, for the subsidiary, not for the parent group:
   a. it has raised USD 150M or more in equity from outside investors;
   b. its own published revenue is USD 300M or more, for 2023 or later (its own accounts or press release, or the parent's annual report
      where a segment or brand line is that subsidiary and nothing else);
   c. it was bought for, or valued at, USD 1B or more since November 2023 (the price the parent paid counts);
   d. its own brand currently pays for a top-tier sports sponsorship (the list in brief_newsectors.md, point 3d);
   e. it is owned by a state investment fund that is building the brand internationally.
   Never use the parent's group revenue, market value or sponsorships as the subsidiary's proof.
5. Still out: investment funds, closed or fully absorbed companies (brand retired), sanctioned companies.

The output line: the same JSON object as brief_newsectors.md, plus "stage" and "theme" (brief_pass2.md, point 2), plus FOUR new fields:
 "parent": "...",          // the parent company's usual name (the ultimate parent if there is a chain; put the chain in "ownership")
 "parent_listed": "...",   // "listed (NYSE: CRM)" with the exchange and ticker if you saw them, "listed", or "not listed"
 "parent_stake": "...",    // "100%", "majority", "about 80%" as stated on a page, or "" if the page only says "subsidiary"
 "parent_f1": "..."        // run on_sheet.py on the PARENT's name. If it prints "current F1 partner" or "owner of a current F1 partner",
                           // copy what it printed here. Otherwise "".
"ownership" should read "subsidiary of <parent>" (add the chain or the other shareholders if a page states them).
The rationale must be about the subsidiary's own brand, 12-25 words.

Nothing found may be lost: a company that looks right but whose own capacity proof, or whose ownership, you could not show from a page
goes in your "unconfirmed" file (format in brief_pass2.md, point 4), with "parent" added.

Searching: your task states your WebSearch limit. WebFetch is not limited. If WebSearch is refused with a limit message, stop searching.
Do NOT work around the limit in any way: no search-engine pages and no news-feed or RSS search pages (Google News, Bing News and the like)
through WebFetch or curl. Use WebFetch on list pages and company pages whose addresses you know or find on pages you read (Wikipedia
lists of acquisitions and subsidiaries, annual-report pages, newsroom pages, sponsor lists). Space out Wikipedia calls.
Use only public pages and a declared user agent. Do not use Apollo. Do not write any figure you did not read on a page.
Write in chunks (append). At the end check the file: valid JSON on every line, no company twice, every line has a parent.
