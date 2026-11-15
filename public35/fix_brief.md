# Brief: rewrite thin profile fields for listed companies (Formula 1 sponsorship database)

Each input line is one listed company (JSON) with its current profile fields and a `fix` list naming the fields that
are too thin. Rewrite ONLY the fields named in `fix`, from your own knowledge of the company. No web search. No
financial figures. Never invent facts: if you do not know the company well, write a careful sentence that stays within
what the name, country, sector and existing fields support.

Field rules
- `desc`: what the company actually does, ONE plain sentence of 10-20 words (count them), specific to this company
  (products, customers, where). No marketing language. No generic filler such as "for customers around the world".
- `markets`: main customer markets, existing international operations and any expansion plans you KNOW of, 8-25 words.
  End with "No verified expansion plans." if you know of none.
- `rationale`: why a Formula 1 partnership could make commercial sense for THIS company, 12-25 words, specific: which
  audience or markets it would reach, B2B hospitality for which customers, what technology or product it would
  showcase, which races matter. If the fit is weak, say plainly why it is weak and what limited use there could be.
  Do not claim the company intends to sponsor anything.

Output: one JSON object per input line, on one line, same order, containing "sym" and only the rewritten fields, e.g.
{"sym": "ABC", "desc": "...", "rationale": "..."}
Valid JSON, double quotes, no line breaks inside values. At the end check: same number of lines and same symbols in the
same order as the input, every line parses, word limits hold. Keep helper scripts in your own new scratch directory
(named in your instructions) and never run a script you did not write. Create no other files in the repository.
Reply with: lines written and anything you were unsure about.
