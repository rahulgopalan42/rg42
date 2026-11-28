# Brief (batch 3, 28 November 2026): how every batch 3 researcher works

Today is 28 November 2026. Work from `/home/user/rg42/brandprofile`.
Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.
Your task line names a KEY (for example `t14_cables`) and a MODE. Find your KEY in `v2/batches/b03/tasks.md` for the scope, sources and
your WebSearch limit. Then read the brief for your MODE and follow it, reading "batch 2" as "batch 3":

| MODE | Brief | Your files (all in `v2/batches/b03/` unless stated) |
|---|---|---|
| sector, country, subsidiaries | `v2/brief_b02.md` (+ `v2/brief_discovery.md`) | MAIN `<KEY>.jsonl`, WATCH `watch_<KEY>.jsonl`, DUPS `dups_<KEY>.jsonl`, DISC `disc_<KEY>.jsonl`, NOTES `notes_<KEY>.txt` |
| queue | `v2/brief_queue.md` (+ `v2/brief_discovery.md`) | INPUT `in_qNN.jsonl` (NN = the number in your KEY), MAIN `<KEY>.jsonl`, WATCH `watch_<KEY>.jsonl`, DUPS `dups_<KEY>.jsonl`, NOTES `notes_<KEY>.txt` |
| clay | `v2/brief_clay.md` | OUT `v2/discovery/clay/<KEY>.jsonl`, NOTES `v2/discovery/clay/notes_<KEY>.txt` |

## What is different in batch 3 (these override the older briefs)

1. The user found a qualifying company that every earlier run missed: AFL (fibre-optic cable, Duncan, South Carolina), a wholly owned
   subsidiary of Tokyo-listed Fujikura. Subsidiaries of listed groups are fully eligible when they trade under their own name or brand,
   have their own website and management, and their own shares do not trade. Name the parent in `parent_immediate`, `parent_ultimate`,
   `parent_listed`. Still leave out the national sales or legal entity of a multinational ("Siemens España"), a plant, a division with
   no separate identity, and holding or finance vehicles.
2. Go past the famous names: suppliers, component makers, distributors, contractors, B2B service firms, regional champions, state-owned
   companies and family groups count as much as consumer brands. Cover every subsector and region in your task, not the first few.
3. `check.py` now also answers ALREADY DELIVERED for names sent to the user in batches 1 and 2: leave those out like IN MASTER.
4. Effort (sector, country and subsidiaries modes): about one third on discovery, two thirds on research. Do not stop after 15 to 20
   companies. Keep researching NEW candidates, largest and most Formula 1-relevant first, until you have written at least 45 MAIN or
   WATCH records or you have no NEW candidate left. Queue mode: work through every line of your INPUT.
5. Every name you read off a list goes in DISC even if you never research it (a later run will): include `figure`, `metric`, `usd_m`
   and `source` exactly as the page gives them. For a subsidiary add `"parent": "<group>"` to the DISC line.
6. Never write a fact from memory. Financial figures, owners, sponsorships and signals need a page you opened in this session.
   `""` or `null` is fine. No Apollo. Public pages only, with your normal declared user agent. If a site refuses, move on.
7. WebSearch: at most the number in your task, in total. If a search is refused, stop searching for good. WebFetch is not limited.
8. Write only your own files. Do not run git. Do not edit scripts, briefs or other researchers' files. Append to your files as you go
   so nothing is lost if you are stopped. At the end check that every line of your files parses as JSON.
9. Final report: under 100 words: counts (MAIN, WATCH, DISC, DUPS) and the main gaps. The detail belongs in NOTES.

## Added on 28 Nov after the user's review of batch 2 (read this too)

10. In batch 2 only 63 of 1,581 companies reached High or Medium priority, mostly because three things were never looked at:
    buying signals (77% of records had none recorded), profitability (88% "unknown") and who runs marketing. For EVERY company
    you write to MAIN, spend one extra fetch on its newsroom / press / news page (or the "History" and recent-events part of its
    Wikipedia article) and record what that page shows:
    - `signals`: dated events since December 2024 with the page URL (funding, acquisition, new owner, IPO plans, new country, plant
      or office, new CMO or senior marketing hire, rebrand, big campaign, new sponsorship, major customer win, product launch);
    - `sponsorships`: any sports or event sponsorship it pays for, with the rights holder and the page;
    - `profitability` ("profitable" / "loss-making") with `profitability_basis`, only when a page states profit, EBITDA or a loss;
    - `access`: `owner_led`, `structure`, and `marketing_head_identified` = "yes" when a page names a CMO / head of marketing / brand
      (put the job title in `roles`, never a personal contact detail);
    - `customer_overlap`: Formula 1 teams, partners or suppliers named as its customers or partners on a page you opened.
    Then add `"signals_checked": "yes"` to the record. If you could not open such a page, write `"signals_checked": "no"`.
    Rate `fit` on what the company is and sells, not on how much press it has: a large, well-capitalised company with real business
    reasons to be in Formula 1 must not be rated low only because little is published about it. Do not inflate either.
11. Value chain: in every subsector look beyond the brand owners to their manufacturers, technology providers, suppliers,
    distributors and importers, infrastructure providers and service businesses.
12. Regions that earlier batches under-covered: Japan, China, South Korea, India, South-East Asia, the Middle East, Turkey, Africa and
    Latin America. If your scope includes them, give them real time and use local-language sources and country-specific directories.
