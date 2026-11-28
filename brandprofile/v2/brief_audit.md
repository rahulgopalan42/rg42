# Brief (batch 3): completeness cross-check against rankings nobody has used

Today is 28 November 2026. Work from `/home/user/rg42/brandprofile`.
Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.
Read `v2/brief_b03.md` and `v2/brief_discovery.md` (eligibility, routes, the JSON record).

The user wants proof of coverage, not a claim. Your task line in `v2/batches/b03/tasks.md` names independent rankings or
directories. For each one:
1. Make sure nobody used it: `grep -ril "<its name or domain>" v2/batches/*/notes_*.txt`. If it was used, pick the closest
   unused alternative and say so in NOTES.
2. Open it and extract EVERY company it lists, with the figure it gives.
3. Run `<python> -I v2/found.py "Name | site" ...` (50 names per call). It answers IN MASTER, ALREADY DELIVERED, F1 PARTNER,
   LISTED?, KNOWN (batch 3 has it: researched, left out, on the register, or a database lead) or NOT FOUND ANYWHERE.
4. Decide, for each NOT FOUND ANYWHERE name, whether it would qualify: its own shares do not trade and it meets a route
   (revenue USD 150M+, funding USD 100M+, valuation USD 1B+, AUM USD 5B+, or two indicators of scale). Use the source's own figure.
5. Write every NOT FOUND ANYWHERE name to DISC `disc_<KEY>.jsonl` (the DISC line format in `brief_b02.md`, with figure and source),
   and research the largest and most Formula 1-relevant of them to MAIN `<KEY>.jsonl` (full record, including point 10 of
   `brief_b03.md`), WATCH or DUPS as usual.
6. NOTES `notes_<KEY>.txt` must hold one line per source in exactly this form, so the miss rates can be added up:
   `SOURCE | <name and url> | listed on it: N | unlisted and qualifying: N | already known: N | not found anywhere: N | miss rate: N%`
   (miss rate = not found anywhere / unlisted and qualifying), followed by the names not found.
Be strict and honest: a low miss rate is as useful as a high one. Do not count a listed company or a company below the
thresholds as a miss. WebSearch: the number in your task. Write only your own files. Do not run git. No invented facts.
Final report: under 100 words: each source with its miss rate.
