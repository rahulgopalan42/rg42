# Brief: check a delivery list against current Formula 1 Grand Prix, team and championship partners

Today is 27 November 2026. Work from `/home/user/rg42/brandprofile`. Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

`v2/batches/b01/delivered_names.tsv` holds about 1,360 non-listed companies (name, country, sector, list, website) that are about to be
sent to a Formula 1 sponsorship seller as NEW prospects. Any brand that already holds a current (2026 season) Formula 1 deal with
the championship, a team, or a Grand Prix promoter must be taken out. The existing register covers team and championship partners
well but is thin on Grand Prix-level partners: ADNOC (Official Founding Partner of the Abu Dhabi Grand Prix) slipped through.

## What to do
1. For each 2026 Grand Prix, open the promoter's or circuit's official partners/sponsors page (WebFetch) and collect every partner
   named there with its designation. Start with the Gulf and Asian races, where state-owned companies on the list are most likely
   to appear: Abu Dhabi (abudhabigp.com/en/partners, yasmarinacircuit.com), Saudi Arabia, Bahrain, Qatar, Azerbaijan, Singapore,
   China, Japan; then Australia, Miami, Las Vegas, Austin, Canada, Mexico, Brazil, Monaco, Spain (Barcelona and Madrid), Austria,
   Britain, Belgium, Hungary, Netherlands, Italy (Monza; Imola if on the calendar).
2. Write every partner you read to `v2/f1_gp_partners_2026.json` as a JSON list of
   `[partner name, partner website or "", "Grand Prix name: designation", source url]`.
3. Compare the partners with the delivery list (normalise names in Python, then judge by eye: same company, parent or brand).
   Also flag any name on the delivery list that you positively know from a page you open to be a current F1 team or championship partner.
4. Write one JSON line per match to `v2/batches/b01/f1_gp_check.jsonl`:
   `{"name": "<exactly as in delivered_names.tsv>", "f1_property": "", "designation": "", "status": "current 2026|ended|unclear", "source": "url", "note": ""}`
5. Finish with a short report: races whose page you read, races you could not read, matches found.

## Rules
- Facts only from pages you open in this session. No invented partners. If a page is not reachable, say so; do not guess.
- WebSearch: at most 12 calls in total; a refusal means stop searching. WebFetch is not limited. Public pages only. Do not use Apollo.
- Do not edit any other file. Be quick: aim to finish within about 12 minutes; cover the Gulf and Asian races first.
