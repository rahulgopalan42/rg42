# APOLLO CONTACT METHOD (F1 Oct-11 run)
# Account: Apollo paid plan, team credits shared. Spend approved by the account owner for the
# runbook's work-order files only, HARD CAP 4 revealed contacts per brand.

TOOLS (load via ToolSearch "select:mcp__Apollo_io__apollo_mixed_people_api_search,mcp__Apollo_io__apollo_people_bulk_match"):
1. apollo_mixed_people_api_search - FREE. Always search first:
   - q_organization_domains_list: [the brand's domain from the work-order file] (if domain empty: one WebSearch to find it first)
   - person_titles: ["marketing","chief marketing officer","vp marketing","head of marketing","brand","partnerships","business development","chief revenue officer","chief executive officer"]
   - contact_email_status: ["verified","likely to engage"]
   - per_page: 25
   If zero results: ONE retry without contact_email_status filter; still zero -> brand stays at 0, move on.
2. apollo_people_bulk_match - 1 credit per matched person, max 10 per call.
   - Pass ONLY the `id` values returned by the search (never names).
   - Pick up to 4 people per brand by role priority: (1) most senior MARKETING (CMO > VP > head > director > manager),
     (2) partnerships/business development, (3) CRO/sales leader, (4) CEO/CCO only as last fill.
   - reveal_phone_number: NEVER true. run_waterfall_email: NEVER true. run_waterfall_phone: NEVER true.
     reveal_personal_emails: NEVER true. Work emails come with the standard match.
   - Batch several brands' picks into one call (up to 10 ids) to save calls.
   - KEEP only results with a usable verified work email; a person returned without one does NOT
     count toward the brand's 4 and their row is dropped.
   - If a response includes an mcp_credits block, note estimated/spent/balance in your chat updates.

ROLES in output rows: decision_maker (top marketing pick), vp_marketing, cro, field_marketing, spare.
OUTPUT shape: {"rows":[{"brand","people":[{"name","title","role","email"}]}]}, people [] if none.
HARD RULES: emails only, no phones ever; dedup people by name within a brand; never exceed 4 per brand.
