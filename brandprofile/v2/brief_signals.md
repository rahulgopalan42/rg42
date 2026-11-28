# Brief (batch 3): buying signals, profitability and decision-makers for companies already on the list

Today is 28 November 2026. Work from `/home/user/rg42/brandprofile`.
Python: `/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`.

Why: the user sells Formula 1 sponsorships. In the last batch only 63 of 1,581 qualified companies reached High or Medium priority,
because nobody had looked at their recent news: 77% had no buying signal recorded, 88% had "unknown" profitability and almost none
had a marketing lead identified. Your INPUT file lists strong companies (financially capable, good Formula 1 fit) whose record lacks
this. Find the evidence, or establish honestly that there is none. Never invent or assume: every item needs a page you opened.

INPUT `v2/batches/b03/in_sNN.jsonl` (NN from your KEY): `name`, `website`, `hq_country`, `sector`, `desc`. Work through every line.
OUTPUT `v2/batches/b03/sig_sNN.jsonl`: ONE JSON line per company, written as you go, in exactly this shape:

    {"name": "<exactly as in the input>", "signals_checked": "yes|no",
     "signals": [{"category": "capital|geographic|marketing|commercial|strategic", "what": "", "date": "YYYY-MM", "status": "confirmed", "source": "url"}],
     "sponsorships": [{"rights_holder": "", "sport": "", "designation": "", "announced": "", "duration": "", "value": "", "source": "url"}],
     "profitability": "profitable|loss-making|", "profitability_basis": "",
     "access": {"owner_led": "yes|no|unknown", "marketing_head_identified": "yes|no", "structure": "lean|mid|complex", "roles": "job titles only"},
     "marketing_autonomy": "yes|no|", "customer_overlap": "", "fit": {"ecosystem": 0, "technical": 0},
     "expansion_markets": "", "distress": "", "f1_deal": "", "sources": ["url"]}

For each company (about three page fetches):
1. Open its newsroom / press / news page (try `/news`, `/press`, `/newsroom`, `/media`, `/en/news`, `/about/news`, then the
   home page) and its Wikipedia article (local-language version if richer).
2. `signals`: events dated December 2024 or later that the page states: capital (funding round, growth or private equity
   investment, IPO preparation, acquisition, change of owner); geographic (new country, office, plant, distribution); marketing
   (new CMO or senior marketing hire, rebrand, major campaign, brand ambassador, new sponsorship, more marketing spend);
   commercial (major customer win, product launch, new division, distribution deal); strategic (a direct competitor entered Formula 1
   or raised its sports spend, stated global brand ambition, leadership interest in motorsport). One event = one signal. Give the
   month (YYYY-MM) and the URL. Older events do not count.
3. `sponsorships`: sports teams, events, stadium naming, athletes or motorsport that the company pays for, with the page.
4. `profitability`: only when a page states a profit, EBITDA or a loss for a recent year (put the figure and year in the basis).
5. `access`: `owner_led` = a founder, owner family or named CEO visibly runs it; `structure` = lean (one brand, one management
   team), mid, or complex (many divisions or layers); `marketing_head_identified` = "yes" when a page names a CMO, head of
   marketing, brand or partnerships (job title in `roles`; never a personal contact detail). `marketing_autonomy` for subsidiaries.
6. `customer_overlap` and `fit.ecosystem` (0-3): only if a page names Formula 1 teams, partners or suppliers as its customers or
   partners. `fit.technical` (0-3): only if a page shows its product is used in motorsport or by a racing team. Otherwise leave 0.
7. `f1_deal`: if any page shows the company (or this brand) currently holds a Formula 1 championship, team or Grand Prix
   partnership, write what and the URL. Such a company must come off the list.
8. `signals_checked`: "yes" when you read at least one news, press or Wikipedia page for the company, even if you found nothing
   (then `signals` is `[]`: that is a real, useful answer). "no" when no page would open.

WebSearch: 0. WebFetch only, public pages, your normal declared user agent; if a site refuses, try Wikipedia, then move on.
Write only your OUTPUT file. Do not run git. Check at the end that every line parses as JSON and that every input company has a line.
Final report: under 80 words (companies done, how many with at least one signal, how many with none, any F1 deals found).
