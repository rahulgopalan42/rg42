# Addendum to classify_brief.md (new parameters, 19 Nov 2026) - this file wins where the two differ

The user now wants ALL sectors searched, so `00` is no longer used. Read classify_brief.md first for the 46 sector
codes, the rules between them and the output format. Then apply these changes.

New codes (use them only when none of 01-46 fits the company's main business):
- `47` Tobacco & nicotine: cigarettes, cigars, vaping, nicotine pouches, tobacco leaf.
- `48` Packaging, paper & forest products: packaging makers, pulp and paper, labels, containers, timber.
- `49` Agriculture, agribusiness & food commodities: farming, plantations, grain and sugar processors, animal feed,
       fertiliser and seeds, fishing and aquaculture, commodity food processors with no consumer brand.
- `50` Other operating company: a real operating business that fits none of 01-49 (for example a sports club,
       a funeral-services chain, a postal operator).

Codes for names that must be taken out:
- `FF` Not an operating company: investment fund, trust, closed-end fund, business development company, ETF,
       SPAC or blank-cheque company, shell, pure holding or investment vehicle with no operating business,
       royalty trust. (A REIT that owns and runs property is `41`, not `FF`. A bank or asset manager is `08`.)
- `DD` A second share class, depositary receipt or duplicate line of a company (for example "Class B", "ADR",
       "Preferred"), when the name makes that clear.

Other points
- Do NOT write `00`. Tobacco, packaging and agriculture now have their own codes (47, 48, 49).
- `??` is still right when you do not recognise the company and neither its name nor the hints make the business
  clear. Do not guess. A name such as "... Pharmaceutical", "... Bank", "... Electronics", "... Paper",
  "... Sugar" or "... Cement" is enough to classify.
- Many of these companies are small listed companies from China, Japan, India, South Korea and Taiwan. Use the
  company name, the exchange and the revenue / market value hints.
- Do not use web search or web fetch: this is a classification from the name, the hints and your own knowledge.

Output: plain text, one line per input line, same order: `SYMBOL|code`. Every input symbol exactly once, nothing else.
