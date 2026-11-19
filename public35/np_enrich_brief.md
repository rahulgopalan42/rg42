# Addendum to enrich_brief.md (new parameters, 19 Nov 2026) - this file wins where the two differ

Read enrich_brief.md first: it defines the job (one JSON object per company, from your own knowledge, no web search,
never invent) and the fields sym, sector, hq, desc, reach, markets, rationale, rel, f1, flags, conf. Then apply these changes.

1. Sector codes. `00` is no longer used. New codes exist besides 01-46:
   `47` Tobacco & nicotine; `48` Packaging, paper & forest products; `49` Agriculture, agribusiness & food commodities;
   `50` Other operating company (fits none of 01-49); `FF` not an operating company (fund, trust, SPAC, shell, pure
   investment vehicle); `DD` a second share class or duplicate line of a company already listed under another name.
   Keep the given code if it is right; otherwise give the right one.

2. F1 links are now FLAGGED, not excluded. Keep filling `f1` exactly as before (which current F1 partner, team owner or
   engine supplier the company is, or belongs to the same group as). An F1 link does not lower `rel`.

3. FOUR new fields on every line:
 "sports": "...",   // sports sponsorships of this company or its brands that you KNOW of, current or recent (2023-2026),
                    // outside or inside F1: the property and the year where you know it, e.g. "Shirt sponsor of Club X
                    // since 2024; official partner of the NBA". "" if you know of none. Never guess.
 "signals": "...",  // buying signals you KNOW of from 2025-2026, each with the month or year where you know it: new
                    // funding round, IPO or share sale; new CEO or marketing chief; rebrand; entry into new countries;
                    // a marked rise in advertising; a new sponsorship; a major product launch. "" if you know of none.
                    // Do not infer signals from the company's size or sector. These are shown as "desk research, to verify".
 "b2b": 1-5,        // team fit and business-to-business value: 5 = a technology, engineering, data or industrial company
                    // whose products an F1 team could use or showcase, or whose customers are senior enterprise buyers;
                    // 3 = some B2B hospitality value; 1 = none
 "act": 1-5         // activation potential with fans: 5 = a consumer brand sold in many of the countries that host races;
                    // 3 = a consumer brand in a few markets, or a business brand with a public profile; 1 = no consumer or brand angle

4. Lengths: `desc` one plain sentence of 10-20 words; `rationale` at most 25 words and specific to the company;
   `markets` at most 25 words.

5. Many of these companies are smaller than in the earlier pass (some have low revenue, are loss-making or have thin
   data). Do not mark a company down for that: `rel` is about strategic fit and commercial motivation, not size.
   If you do not recognise a company, set "conf": "low", keep to what the name and hints support, leave `hq` city,
   `sports` and `signals` empty, and do not invent.

Output: JSON Lines, same order as the input, every symbol exactly once, valid JSON on every line.
