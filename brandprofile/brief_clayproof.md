# Proving Clay leads (read after brief_newsectors.md and brief_pass2.md)

Your input file lists companies that the Clay database returned as privately held with revenue above about USD 200M. Clay is often wrong:
many are listed, are local units of listed or foreign groups, are smaller than shown, or no longer exist. Each line gives name, domain,
hq, industry and Clay's revenue bracket. NONE of that counts as proof. Your job is to sort every lead into one of three outcomes, quickly.

1. QUALIFIES -> one line in your main output file, in the format of brief_newsectors.md plus "stage" and "theme" ("" unless obvious),
   with "group": "Clay leads". The company must be unlisted and not owned by a listed group or an F1 partner, and one capacity test
   must be proven from a page you fetched (usually published revenue of USD 300M or more: Wikipedia infobox with a year, the company's
   own "about" or annual-review page, a public ranking, filed-accounts summary). Clay's bracket is NOT proof.
2. OUT -> one line in your "out" file: {"name": "...", "reason": "listed (ticker) | owned by <listed or foreign group> | closed |
   revenue below USD 300M (<figure, year, url>) | current F1 partner | not a company"}. Only when a page shows it.
3. STILL A LEAD -> write nothing. It simply stays on the leads tab.

How to work fast: one or two fetches per lead. Try the English or local-language Wikipedia article first (WebFetch on the normal page,
spaced out), then the company's own site (the domain is given). If neither shows ownership and a figure, move on. Do the well-known
and consumer-facing names first. Run on_sheet.py on names before researching in case another researcher has since covered them.
Convert currencies at approximate current rates and say so in capacity_detail. Do not use WebSearch beyond the number your task allows.
