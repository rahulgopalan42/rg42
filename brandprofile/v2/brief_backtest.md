# Brief: backtest of Formula 1 sponsors that were privately owned when they entered the sport

Today is 27 November 2026. We are testing two sets of prospecting rules against real Formula 1 sponsors. For each sponsor in your
task, record what was **publicly known before the sponsorship was announced**. The sponsorship being tested must not be used as
evidence of capacity or intent. Every fact must come from a page you open in this session; `""` or `null` is fine, an invented or
remembered figure is not. Do not estimate or invent sponsorship fees.

For each sponsor write ONE JSON object on one line to the file named in your task:

    {"sponsor": "", "f1_property": "",            // team, championship or Grand Prix
     "designation": "",                            // e.g. title partner, official partner
     "announced": "YYYY-MM", "announce_source": "url",
     "private_at_entry": "yes|no|unclear",         // were its OWN shares unlisted on the announcement date?
     "ownership_at_entry": "venture-backed|bootstrapped|founder-owned|family-owned|private equity-backed|state-owned|sovereign fund-backed|subsidiary of listed group|subsidiary of private group|partnership|foundation-owned|unclear",
     "parent_at_entry": "", "hq_country": "", "sector": "", "model": "B2B|B2C|Hybrid",
     "pre": [{"metric": "equity_funding|revenue|arr|ebitda|valuation|transaction_value|aum|employees|countries|stores|marketing_spend",
              "value_orig": "", "usd_m": null, "as_of": "YYYY or YYYY-MM", "kind": "reported|estimated|inferred", "source": "url"}],
                                                   // only figures dated BEFORE the announcement (latest available before it)
     "prior_sponsorships": "",                     // paid sports sponsorships it already had before this deal, with year; "" if none found
     "prior_signals": "",                          // dated events in the 24 months before: funding round, expansion, new CMO, rebrand, IPO plan
     "last_round_before": "",                      // for venture-backed: date and size of the last equity round before the deal
     "what_happened_after": "",                    // one line: still a partner, ended early, collapsed, listed later
     "notes": "", "conf": "high|medium|low"}

`usd_m` for money metrics is USD millions at these fixed rates: EUR 1.10, GBP 1.30, CHF 1.15, AUD 0.66, JPY 0.0067, CNY 0.14.
For employees, countries and stores put the count in `usd_m` and leave the currency out.

If a sponsor on your list turns out to have been listed on a stock exchange at the announcement date, still write the line with
`"private_at_entry": "no"` and nothing else filled in. If you cannot date the deal, say so in `notes`.

WebSearch calls are strictly limited to the number in your task; a refusal means stop searching and never work around it. WebFetch
is not limited: Wikipedia, company press pages, team announcement pages and funding histories are usually enough. Use only public pages.
Before you finish, check that every line parses as JSON. In your final report give the count of lines and anything you could not establish.
