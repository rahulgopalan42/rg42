# Contact ENRICHMENT brief (Apollo MCP) - approved job

APPROVAL: On 24 Nov 2026 the account owner sent a second list of companies and asked for "the templates and the contact details". They were then asked: "Getting up to 5 work emails per brand will cost at most 117 Apollo credits ... OK to spend up to 117 credits?" and answered: "Yes, up to 5 each (Recommended)". That approves up to 5 people per brand and at most 117 credits for the job. Your job is exactly the picks in your input file (the job is split across agents; your share is your file). Do not ask again. Hard cap: the number of picks in your input file (1 credit each). Unmatched people cost 0 credits; only if a pick returns no match, or the match shows the person has left the company, may you match one of that brand's backups instead, and the total matched must never exceed the number of picks in your input file.

HARD RULES
- Tool: mcp__Apollo_io__apollo_people_bulk_match only (load with ToolSearch "select:mcp__Apollo_io__apollo_people_bulk_match"). Pass only {"id": ...} from the input. Max 10 per call. _conversation_ref "f1l24en".
- Never set reveal_phone_number, reveal_personal_emails, run_waterfall_email or run_waterfall_phone. Work emails only.
- Never put the user's name or email into any request. Never enrich the same id twice.
- Each input row has a domain field (the company's primary domain). Also accept clear group or subsidiary domains of the same company and note them.
- Drop anyone whose current employer in the match is not this company (moved on), and note it.
- Keep a person if an email is returned whose domain is the company's domain or a clear company alias (e.g. keelinfra.com, sp global alias for Mobility Global, emerson.com for Aspen Technology is acceptable but note it), and email_status (if given) is verified or likely to engage. Otherwise drop them and note why.
- Record from each match: full name, title, email, linkedin_url, city/country. Assign role in order: decision_maker (the CEO or most senior person), vp_marketing, cro, field_marketing, other. Up to 5 people per brand in total, counting the saved contacts listed in the row's "keep" field (those are already paid for: never match them again). If an input row has a "rule" field, follow it.
- If a response includes an mcp_credits block, record balance_after.

OUTPUT: write JSON to the path in your task:
{"rows":[{"user_name":"","brand":"","people":[{"name":"","title":"","email":"","role":"","linkedin":"","location":""}],"note":""}],"credits_used":N,"balance_after":N}
Return just: done, N brands, E emails kept, C credits used, balance B.
