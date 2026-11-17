# Brief: unlisted companies reported to be in funding talks (watch list)

Today is 17 November 2026. The user sells Formula 1 sponsorships and keeps a prospect list of unlisted companies that can afford one.
A company gets onto that list when it has raised USD 150M or more in equity in total, or has been valued at USD 1B or more.
Yesterday a company (Model ML) was missing from the list because it had raised only USD 87M; a September press report had said it was
in talks to raise at a valuation above USD 1B, and the round was announced today. The user now wants a WATCH LIST of companies in the
same position: press reports of funding talks that are NOT yet confirmed, where the round, if it happens, would take the company over
one of the two lines. This list is leads only. Accuracy still matters: every line must rest on a report you found in this session.

## Who goes on the list
1. An operating company that is not listed on a stock exchange and is not owned by a listed group.
2. It is not a current Formula 1 partner and does not own one (roster at the end of /home/user/rg42/brandprofile/brief_check.md, paragraph
   starting "Current Formula 1 roster").
3. Since 1 May 2026 a named outlet has reported that it is in talks to raise equity, is seeking or weighing a round, has received term
   sheets, or is arranging a share sale that values it, and the report rests on unnamed sources or is otherwise not confirmed by the company.
4. If the reported round happened, the company would pass a line: a valuation of USD 1B or more, OR total equity raised (what it has
   raised so far plus the reported round) of USD 150M or more.
Leave out: rumours with no outlet you can name and link; debt-only financings; listed companies; pure investment funds.

## Check each candidate against what the user already has
    /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I /home/user/rg42/brandprofile/newsec/on_sheet.py "Name one" "Name two" ...
"new" = not on the user's lists: these are the main target. "ALREADY KNOWN ... on the sheet / in the new-brands workbook" = the user already
has the company; still record it, in the SECOND file (short form), because talks of a new round are a buying signal. "listed" or "F1 partner" = leave out.
"POSSIBLY KNOWN" lists similar names: decide whether one is the same company.

## Check what has happened since the report
For every candidate, look for a later announcement. Set "status" to one of:
- "unconfirmed": no announcement of the round found (say when you last saw it reported);
- "since confirmed": the round was announced. Give amount, valuation, date and the page in status_detail and status_url;
- "denied or fell through": the company denied it, or a later report says the talks ended.

## Output
MAIN file (companies that came back "new"), one JSON object per line:
{"name": "...", "hq": "City, Country", "sector": "one of the 48 sector names in brief_check.md (line starting \"- `sector` must be one of\")",
 "theme": "best fit or \"\": Quantum computing | Nuclear & fusion energy | Prediction markets, betting & iGaming | Digital assets, stablecoins & crypto | Defence technology | Space & satellites | Robotics, humanoids & autonomous driving | AI infrastructure: data centres & GPU cloud | AI chips & semiconductors | AI models, agents & applications | Cybersecurity | EVs, charging & new mobility | Energy storage, renewables & grid | Consumer health, GLP-1, wearables & longevity | Neobanks, payments & trading apps",
 "desc": "what it does, one plain sentence of 10-20 words",
 "reach": "Global|International|Regional|Domestic", "markets": "where it sells or operates, 6-20 words",
 "talks": "what is reported, in one sentence: size of round, valuation, investors named, as the outlet put it",
 "talks_usd_m": 250, "talks_valuation_usd_m": 1500,          // numbers in USD millions, null where the report gives none
 "talks_date": "Sep 2026", "talks_outlet": "Bloomberg", "talks_url": "https://...",
 "raised_so_far": "USD 87M in total (seed USD 12M, Series A USD 75M, Nov 2025), per <outlet>", "raised_usd_m": 87, "raised_url": "https://...",   // "" / null if not found
 "would_pass": "valuation|total raised|both",
 "status": "unconfirmed|since confirmed|denied or fell through", "status_detail": "...", "status_url": "https://... or \"\"",
 "rationale": "why an F1 partnership could make sense for THIS company, 10-22 words",
 "rel": 3,                // 1-5 relevance to F1, 5 = brand-led with international ambitions and rivals already in F1
 "conf": "high|medium|low"}   // how sure you are the report says what you wrote
SECOND file (companies the user already has), one short JSON object per line:
{"name": "...", "known_as": "what on_sheet.py printed", "talks": "...", "talks_usd_m": null, "talks_valuation_usd_m": null, "talks_date": "...", "talks_outlet": "...", "talks_url": "...", "status": "...", "status_detail": "...", "status_url": ""}

## Rules
- Report only what the outlet said. Do not write a figure you did not see in a search result or on a page. Convert currencies at approximate
  current rates and say so.
- Paywalled originals (Bloomberg, The Information, FT) are fine to cite through a page that reports them by name; give the page you read.
- WebSearch calls are strictly limited (your task gives the number). If a call is refused with a limit message, stop searching and do not
  work around it in any way; finish with what you have. WebFetch is not limited. Use only public pages. Do not use Apollo or Clay.
- Write both files in chunks (append) as you go. At the end check them: valid JSON on every line, no company twice, desc 10-20 words.
