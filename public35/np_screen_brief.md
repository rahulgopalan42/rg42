# Brief: commercial-motivation screen for listed companies below the capacity threshold

Each input line is a listed company that meets the entry size test (revenue USD 100M+, or market value USD 500M+)
but whose estimated sponsorship capacity is below USD 3.5M a year:

    SYMBOL | Company name | Country | Sector | revenue, market value

The question for each line: leaving size aside, does THIS company have a real commercial reason to buy a global
Formula 1 partnership (team or series) in 2027-2028? Work only from your own knowledge of the company. No web search.

Give one score per line:

- `5` a brand-led consumer company or an enterprise technology company with clear international ambitions and an
      obvious use for F1: direct rivals already sponsor F1 or other top-tier global sport, or the company itself
      sponsors top-tier sport, or it is pushing into the countries that host races
- `4` strong on at least two of: fast international expansion; a marketing-led culture (heavy brand advertising or
      existing sports sponsorship); high-value B2B hospitality needs (sells to senior enterprise buyers worldwide);
      a real technology tie-in with racing (engineering, data, materials, mobility, energy)
- `3` plausible but not obvious
- `2` weak: domestic, little marketing culture, commodity, contract manufacturer or regulated utility
- `1` very unlikely or restricted
- `?` you do not recognise the company and the name and sector do not settle it

Be strict with `4` and `5`: they are for companies you actually know something about. A typical file has well under
one line in ten at 4 or 5. Do not score up because of the sector alone, and do not invent facts about a company.

Output: one line per input line, same order, every symbol exactly once, in the form `SYMBOL|score`, nothing else.
