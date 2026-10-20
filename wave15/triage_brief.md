# Wave 15 quick triage (knowledge only, no web search)

Database rows below are F1 sponsorship candidates. Many are junk: personal pages, tiny shops, blogs, spam, job
pages, political parties, clubs, schools, charities, local branches, mislabeled "10,001+ staff / USD 1B+" records.
Your job is ONLY to remove obvious junk so the expensive checker does not waste time. Do NOT use WebSearch/WebFetch.

For each input row decide:
- "junk": you are confident it is NOT a real operating company that could plausibly have USD 150M+ revenue or USD 100M+
  funding (personal/blog/spam/placeholder name, tiny local business, non-profit/government/school/political body,
  obvious mismatch between name and domain, a page about a person).
- "keep": a real company that might plausibly reach that scale, OR you are not sure. When in doubt, keep.

Input: JSON arrays at the paths in your task (fields id, company, website, country, database_industry, ...).
Output: for each input file in_NNNN.json write /home/user/rg42/wave15/screen/triage_NNNN.json: a JSON array, one object
per input row, same order: {"id": <copy>, "t": "junk" or "keep", "r": "<=6 words reason if junk, else ''"}.
Write with python3 -I (json.dump, ensure_ascii=False). Helper files only in
/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/triage_<first batch>/.
Skip any batch whose triage file already exists. Report only: junk N / keep N per your whole range. Under 30 words.
