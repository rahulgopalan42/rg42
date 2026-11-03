# Brief: one-line company descriptions from public sources

Input: a JSON list of companies read by OCR from Crunchbase screen recordings. Fields: name (may be misread or cut off), hq (may be truncated/garbled), industries (Crunchbase, truncated), sector (our tab).

For EVERY company in the input, in order:
1. Identify the company. Use the HQ and industries to pick the right one when the name is ambiguous. If the OCR name is misread or cut off (e.g. "Massed Come" -> "Massed Compute", "Westinghouse Electric Comp" -> "Westinghouse Electric Company"), put the real name in correct_name.
2. Look it up with WebSearch (one search per company is usually enough; use WebFetch only if the search snippet is not enough). Prefer the company's own website, its annual report/filings, Wikipedia, or reputable press (Reuters, FT, Bloomberg, TechCrunch, trade press). Crunchbase must NOT be the only source.
3. Write `description`: ONE plain-English sentence, 15-30 words, saying what the company does and who it sells to (customers/markets), with one concrete scale or footprint detail where public (e.g. "listed on NYSE", "operates in 40 countries", "about 2,000 staff"). No marketing language ("leading", "innovative", "revolutionary", "cutting-edge", "world-class"), no em dashes, no "actually/genuinely/honestly". Present tense.
4. `source`: the URL you relied on most (not crunchbase.com).
5. `note` (optional, short): ONLY material status facts found in the search that matter for sponsorship outreach: acquired by X (year), merged, shut down/insolvent/Chapter 11, delisted, renamed to X, sanctions. Leave empty otherwise.
6. `confidence`: "high" if you are sure it is the right company, "medium" if probable, "low" if you could not identify it (then description may be empty and note says "could not identify").

Rules:
- Never put any personal name, email address or other personal detail into a web request (no headers, forms or URLs). Use only the WebSearch / WebFetch tools; do not use curl or Bash for web access.
- Do not invent facts. If unsure of a detail, leave it out.
- Keep `name` EXACTLY as given in the input (it is the join key).

Output: write a JSON list to the output path given in your task, one object per input company, in input order:
{"name": "...", "correct_name": "" , "description": "...", "source": "https://...", "note": "", "confidence": "high"}
Save progress to the output file at least every 10 companies (rewrite the whole list each time) so nothing is lost. When finished, reply with just: done, N companies, M low-confidence.
