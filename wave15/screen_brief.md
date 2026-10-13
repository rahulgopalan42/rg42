# Wave 15 screening brief (stage 1 of 2) - v4 rules

You screen ~60 F1 sponsorship prospect candidates pulled from Clay/Apollo for SPORTFIVE. Database data is noisy:
revenue bands are often wrong, many rows are subsidiaries, regional arms, defunct firms, placeholders or spam.
Your job: decide for EVERY brand whether it survives to full verification, and record the key facts.
Today is 13 October 2026.

Input: JSON array at the path in your task (fields: id, company, website, country, database_industry,
db_revenue_band, db_staff, raised_100m_plus, owner_hint, sector_guess).
Output: write a JSON array to the output path in your task, one object per input row, in the same order:
{"id","company","keep","reason","real_name","parent","status","scale_route","scale_evidence","staff_est",
 "f1_tie","sector","fit","verdict_guess","note"}

Field rules
- id, company: copy exactly from input.
- keep: true / false.
- reason: if keep=false, short reason (e.g. "subsidiary of Siemens", "defunct 2008", "placeholder record",
  "government body", "below scale", "F1 tie: Williams partner", "sanctioned").
- real_name: the brand's proper name if the input name is garbled/local-language, else "".
- parent: controlling parent company if any (>50%), else "".
- status: "operating" / "defunct" / "acquired by X" / "distress" / "unknown".
- scale_route: one of "valuation 1B+", "raised 100M+ (36m)", "revenue 500M+", "revenue 150-500M", "below", "unknown".
- scale_evidence: one short dated figure, e.g. "market cap ~USD 4.2B (Oct 2026)", "revenue ~USD 700M FY2025 (est)".
- staff_est: rough headcount, e.g. "~2,000".
- f1_tie: "none found" / "YES: <detail>" / "parent: <detail>" / "minority holder: <detail>" / "lapsed: <detail>".
- sector: the correct tab from the list below (two-digit code + name, or an X tab name).
- fit: 0-4 (one point each: sells in 3+ F1 markets; affluent 25-54 or senior B2B buyers; story maps to
  performance / technology / precision / global ambition; category not crowded on the F1 grid - banking, airline,
  logistics, oil, tyres, watches, crypto, cyber, beer, spirits, automotive, cloud score 0 here).
- verdict_guess: "Yes" / "Stretch" / "Low-value" / "No".
- note: anything the full verifier should know (<= 20 words).

Decision rules (v4)
KEEP only if ALL hold:
1. Real, operating company (not placeholder, freelancer, fan page, spam, test record, school, charity, hospital
   trust, government body, central bank, development bank, state agency).
2. Independent brand: NOT a subsidiary / regional arm / division of a larger group. If it is, keep=false with
   reason "subsidiary of <parent>" - the parent is what matters, and you name it in `parent`.
   Exception: a separately branded, separately marketed consumer brand inside a group (e.g. a luxury maison) may be
   kept with a note.
3. Scale passes on ANY of: worth USD 1B+ (market cap / transacted valuation / EV); raised USD 100M+ equity with a
   priced round in the last 36 months; revenue USD 500M+; revenue USD 150-500M (then verdict at most Stretch).
   Family / private / co-op firms with revenue >= USD 150M pass on revenue.
4. 51+ staff.
5. Not in distress (insolvency, wind-down, going-concern doubt) and not defunct / absorbed.
6. No F1 tie: FAIL ONLY WHEN A TIE IS FOUND - current F1 team partner/sponsor/supplier, F1 global or regional
   partner, Grand Prix / promoter partner, F1 Academy partner, driver personal sponsor - directly or via a
   controlling parent. Minority-holder or lapsed ties: keep, flag in f1_tie, cap verdict at Stretch.
   Teams/owners/PU makers and their groups (GM/Cadillac, Ford, Honda, Toyota, Audi/VW, Mercedes, Ferrari, Renault,
   Aston Martin, McLaren, Red Bull, Williams/Dorilton, Haas, Sauber) are ties.
7. Not sanctioned and not HQ in Russia / Belarus / Iran; US 1260H / Entity List / UFLPA names = No.

Verdict guess: Yes = passes + fit >= 2 + credible marketing motive; Stretch = passes with one reservation
(USD 150-500M revenue route, no published valuation, minority/lapsed tie, fit exactly 2 with weak angle);
Low-value = passes but fit 0-1 or purely domestic/B2B with no brand ambition; No = any rule fails.

Search budget
Use your own knowledge first - most well-known firms need no search. Use WebSearch only when genuinely unsure
(obscure name, possible subsidiary, possible F1 tie, scale unclear): about 15-25 searches for the whole batch.
For every keep=true brand with fit >= 2, do one quick F1-tie check (search "<brand> Formula 1" or "<brand> F1
partner") unless you are certain. Mark guesses "(est)". Do not fabricate figures: use "unknown" instead.

Sector tabs
01 Banking & Insurance, 02 Energy & Industrial, 03 Luxury & Beauty, 04 Food & Beverage, 05 Supercomputing,
06 UCaaS & CPaaS, 07 Marketing & Sales, 08 Devtools & Integration, 09 Fintech, 10 ERP & Finance Procurement,
11 Storage Hardware, 12 Trading & Crypto, 13 AI Agents, 14 Cyber + IT, 15 Observability, 16 Travel & Hospitality,
17 AI Cloud & Data, 18 Services & Other, 19 Gulf Sovereign & Tourism, 20 Staffing & Talent,
21 Materials & Mech Parts, 22 SaaS, 23 Machine Tools, 24 Logistics, 25 IT Services & Consulting,
26 Horizontal SaaS, 27 Chip Makers, 28 AI Data Services, 29 Tech Media & Gaming, 30 Commercial Vehicles,
31 GRC & Risk SW, 32 Defense & Industrial AI, 33 Automation & Robotics, 34 DC Power & Cooling,
35 Semiconductor Equipment, 36 IoT & Connectivity, 37 EDA, 38 Edge & CDN, 39 Construction & Field Svc,
40 Test & Measurement, 41 OT & Physical Security, 42 Health & Wellness, 43 Mobility & Automotive,
44 Grid & Transformers, 45 Electronic Parts, 46 Tools & Industrial Supply, 47 Vertical SaaS, 48 Telecom & Space,
49 Home & Living, 50 Law Firms & Legal AI, 51 Industrial Gases, 52 Photonics & Optical, 53 Consumer & Lifestyle,
54 TIC, 55 Packaging & Food Machinery, 56 Robotics AI.
Outside the 56 use: X Pharma & Biotech, X Medtech, X Retail & E-commerce, X Real Estate, X Utilities & Power,
X Mining & Metals, X Asset Mgmt & PE, X Aviation & Aerospace, X Education, X Gambling & Lotteries,
X Sports Clubs & Leagues, X Maritime & Shipbuilding, X Rail & Transit, X Consumer Electronics, X Agriculture,
X Waste & Recycling, X Live Events & Ticketing, X Pet Care, X Other.

Write the output file with python3 -I (json.dump, ensure_ascii=False) or the Write tool. Write ALL rows before
stopping. Do not touch any other file. Report only: kept N / dropped N, top 3 drop reasons. Under 40 words.
