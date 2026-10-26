# Pipeline state - rebuilt 2026-10-21 after container reset (old scratchpad lost entirely)
# CONTEXT: Oct-11 run (1,548 brands, 23 wave packs) fully delivered Oct 12; all packs + master bundle
# + no-contact pack are with the user (sent via SendUserFile). Lost locally: v7_assemble.py (old),
# the 4 Merge Master v7 docx, all template JSONs, all_contacts.json, run11_brands.json. Repo survived
# (f1run/api_runner.py, f1run/out/*.contacts.json x21, queue files). Transcript survived only in
# compacted form (no v7 exemplar text in it).
# OPEN ITEM A (Oct 13): follow-up chain recovery. User cannot connect Outlook (SPORTFIVE bans Claude).
# Delivered "F1 Follow-Up Lookup - which subject went to which list.xlsx"; user never replied with
# row numbers. Follow-up format approved Oct 7 (short, two reasons: audience overlap + credibility,
# one deep reference brand, "to help support your learning, happy to host you at a race", keen to hear).
# OPEN ITEM B (Oct 21, ACTIVE): 14 new brands "Emails for the following": Kobold Metals, Standard
# Lithium, Lilac, EnergyX, Redwood Materials, US Strategic Metals, Alta Resource Technologies, EACON,
# Principal Mineral, Nth Cycle, EARTH AI, Element3, pH7 Technologies, Scout Discoveries Corp.
# Dedup: none previously built. Pack label: "Wave 24 Critical Minerals".
# Toolkit rebuilt in scratchpad: v7_brief.md (agent brief), cm_chunks.json (cm_A/cm_B/cm_C),
# mini_enrich.py (Apollo REST, key in apollo_key.txt - KEY STILL VALID Oct 21, zero dialogs),
# make_masters.py (4 Merge Master v7 docx; fixed wording = reconstruction, see below),
# v7_assemble.py (new; python3.13 has openpyxl+python-docx, python3 = 3.11 does NOT).
# Research: 3 background general-purpose agents -> cm_A_rows.json, cm_B_rows.json, cm_C_rows.json.
# DONE 21 Oct: all 3 chunks in, edits applied (cm_final_edits.py), pack built: "WAVE 24 CRITICAL
# MINERALS - Complete.zip" (1 Merge List B2B, 54 rows, 14 brands all B2B with reference, Emails Ready,
# 4 masters). Apollo balance 1,069 (was 3,818 on 12 Oct; today's run ~61 credits; account shows
# 2,674 EXPORT credits used by someone else in between - flagged to user). Follow-up lookup item still open.
# PROGRESS 21 Oct: cm_A and cm_B rows DONE (new example shape). cm_C pending. CONTACTS DONE for all
# 14 -> cm_contacts.json (Apollo REST, ~58 credits; widened senior/mid search; Earth AI only 2,
# Element3 3, rest 4). User demands: 3-4 senior/mid contacts per brand, human non-AI tone.
# cm_final_edits.py = merge chunks + my line edits -> cm_templates.json. Pack label
# "Wave 24 Critical Minerals". Identity notes: Principal Mineral = strategic materials maker
# (Isola owner, Southlake TX), EACON = HKEX 7687 China HQ (eacon.com), Earth AI = SF HQ,
# Alta domain altatech.io (Apollo), Element3 = element3.io.
# THEN: merge rows -> cm_templates.json; fix domains from agent output -> cm_domains.json;
# python3 mini_enrich.py cm_domains.json cm_contacts.json (spends ~1 credit per matched person,
# cap 4/brand); python3.13 v7_assemble.py "Wave 24 Critical Minerals" cm_templates.json
# cm_contacts.json; SendUserFile the zip + chat summary (one line per brand: angle + flags).
# STANDARD UPDATES 21 Oct (apply to every future build): (1) fit_reason must CONNECT the brand's
# current news to F1 (customers on the grid, engineering parallel, or market entered), never just
# describe the brand - see FIT dict in cm_final_edits.py; (2) target_audience names 3-4 relevant
# grid brands of the buyer's exact type - see TA dict. Fourth zip sent = final.
# REWRITE 21 Oct (user: "sound very human, target audience = who they serve with relevant grid names,
# sharp for non-native CEOs"): all 14 rows hand-rewritten in cm_final_edits.py EDITS (fit_reason,
# target_audience, shared_values, market_reference; market_overlap kept). Longest sentence <= 31
# words, 179-207 words per email, scrub clean. Pack rebuilt and re-sent (third zip = final).
# FORMAT CONFIRMED from user's Outlook screenshot (sent 13 Oct 2026, Carparts.com): Calibri 11,
# 1.5 line spacing, blank line between every paragraph and bullet, designation BOLD in the hook,
# bullet labels BOLD ("Your target audience:", "Market Overlap:", "Shared Values:", "Market
# Reference:", "Formula 1 Audience:" for B2C), SPORTFIVE bold in signature, real Word bullets.
# Live subject line in use: "Exploring Formula 1 Team Partnership Opportunity" (now the Subject
# column default). make_masters.py + v7_assemble.py rebuilt to this; Wave 24 re-sent 21 Oct.
# FIXED WORDING CONFIRMED (user pasted his Motional v7 email, 21 Oct; copied verbatim into
# make_masters.py TEXT, v7_assemble.py OPENER/CLOSE and the top of v7_brief.md): opener
# "...authorized agency managing brands sponsorships for Formula 1 teams working closely with
# McLaren, Haas, Audi & Mercedes to name a few."; hook "...was identified as a potential fit
# <Fit_reason = 'due to ...' clause>"; bullets Your target audience / Market Overlap / Shared Values /
# Market Reference (+ F1 Audience for B2C); close "Open to a short call to see if there is an
# alignment? If interested, we would love to host you at a race to show you how partners are
# generating ROI." B2B target_audience carries NO stats (two sentences: customers you serve + brands
# of that profile on the grid). User also asked to use https://f1salaries.com/sponsors/ as the
# current partner-landscape source (added to brief; agents messaged mid-run).
# Standing rules unchanged: emails only, never phones; cap 4; no waterfall/personal; verified only;
# QC scrub; China/India/Brazil HQ override flag; capacity grades in flags; parked items stay parked.
# AUDIT 25 Oct: master "MASTER REFERENE OCT.xlsx" (Drive 1voLorjVmfB4FAs5Ie_EaXNCJcNyzrSuD, 59 tabs, 12,370 brands)
# vs Drive folder 1PpySg3zefnpksp_C52Y9N7AtNE0wlboG (Wave 1-23 Emails Ready docx, W10 duplicated).
# Scripts audit_extract.py -> audit_match.py -> audit_build.py. Result: 1,322 verified (green, fill B7E1A1),
# A 1,803 / B 5,445 / C 3,266 (x = no template, user's Sept rule) / D 534 (483 TBR undefined, Later, CHECK,
# "check with Alex Waltham", stray s/xx/z/x], 26 uncertain). 38 tabs have no doc in the folder; Waves 1-4
# (256 brands) match no tab, only 3 found in master. Drive upload not done (connector needs inline base64).
# NEW RUN 26 Oct: brand list Drive 17klkBmI1cydBneRiTNyebnqnKmwpuP2j (27 tabs, 1,514 rows, 1,415 unique; RED tabs 1,220).
# Standard = v8_brief.md (hook "identified for the following reasons:" for B2B; order TA, MO, MR, SV, (F1A);
# close "Would you be open to a quick call?"; Calibri 12). Order: Prepare First (214 unique = 14 plain names +
# 204-row funding table) -> red tabs -> non-red (ERP Finance, GRC Risk, Automation, Vertical Saas, Space).
# HOLD pending user: Existing Group Overlays (156/157 marked x), MASTER (75/76 x), Horizontal Saas "Linear" (x).
# Prepare First: chunks pf_00..pf_21 (10 each) -> pf_XX_rows.json; agents 00-10 launched 26 Oct; 11-21 next.
# Then: merge rows -> enrich with mini_enrich.py (domains from agent output) -> v7_assemble.py "Prepare First" ->
# zip (+ Flagged Brands.xlsx for B2B/B2C ambiguity) -> SendUserFile. Apollo balance 1,069 at start.
# USER 26 Oct: Existing Group Overlays -> BUILD the 156 x-marked brands (x = build here; MathWorks unmarked -> skip).
# MASTER -> BUILD the 75 x-marked brands EXCEPT Stegra (no template; "H2 Green" row = Stegra's old name, skip).
# Exclusion list so far: Stegra. User will top up Apollo credits shortly.

## 26 Oct 2026 - New list run, tab "Prepare First" (v8 standard)
- 214 brands researched in 22 chunks (pf_00..pf_21) by background agents against v8_brief.md.
- QC: pf_qc.py; edit passes pf_edits.py (chunks 00-10) and pf_edits_B.py (11-21 + email_name display fixes).
- 10 not built (listed on "Not built" sheet of the Flagged Brands xlsx): Loop Earplugs, Exein (already on grid);
  Aescape, Sleep Number, Ab&B Biotech, Reve (insolvency / Ch.11 / suspended / product shut);
  Oasis Security, MaintainX, Celestial AI, Observe (acquired, approach the acquirer).
- Apollo: batch A 103 brands = 409 credits (377 emails, 7 wrong-company contacts dropped by pf_contact_fix.py);
  batch B 98 brands running. Balance before run 1,069.
- Assemble: python3.13 v7_assemble.py "Prepare First" pf_final_rows.json pf_contacts_all.json
  (rows carry optional skip / email_name keys; assembler patched for both).
- Next tabs in order: Asset Management, Fintech, Trading & Crypto, AI Agents, Cyber + IT, AI Cloud & Data, SAAS,
  Machine Tools, Horizontal Saas, Chip Makers, AI DATA, Health & Wellness, Cloud and Data Centers, Consumer Goods,
  Mining, Semiconductors, Software, Existing Group Overlays (x-marked only), MASTER (x-marked minus Stegra),
  Automotive and Mobility, Software Internet & AI; then non-red ERP Finance, GRC Risk, Automation, Vertical Saas, Space.

- Cyber + IT: delivered (42 built, Synopsys skipped: on grid via Ansys). Rows in f1run/runs/cyber_it_rows.json. Contacts from wave3_contacts.json.
