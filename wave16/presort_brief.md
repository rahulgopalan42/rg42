# Wave 16 pre-sort brief (knowledge only, no web, no Clay/Apollo/Lusha)

You pre-sort Formula 1 sponsorship prospects for SPORTFIVE. Every company passed a Clay database filter of
USD 75M+ annual revenue (a database estimate). Your job is a quick, honest first read of each record using
the row data plus what you already know. Do NOT browse, search or call any connector. Today is 19 Oct 2026.

## Input
A JSON file: array of rows `[i, name, website, country, industry, staff, type, description]`
(`i` is the row number to copy back; description is cut to ~220 characters).

## Output
Write a JSON file (path given in your task): an array with ONE array per input row, same order:

`[i, t, a, s, l, n, scale, parent, sec, note]`

- `i`: copy from input.
- `t`: `"r"` real operating company / brand; `"d"` division, regional arm, local branch, subsidiary page or
  sub-brand of a bigger group; `"j"` junk (not a real company record: spam, placeholder, freelancer, fan page,
  test record, garbled, a person, an event, a product page, a website directory); `"g"` government body,
  public agency, state school/university, public hospital/health trust, charity, association, cooperative,
  religious or political organisation; `"x"` defunct, acquired and absorbed, or bankrupt (only if you know).
- `a` audience overlap with F1 (0-4): F1 fans skew affluent, 18-54, global; plus senior B2B decision-makers.
  4 = premium/affluent consumer brand or brand selling to C-suite buyers globally; 0 = no plausible overlap.
- `s` commercial synergies (0-4): could it use F1 to sell (hospitality for clients, B2B tech/engineering
  showcase, product placement, retail activation, data/technology partner)? 4 = obvious, 0 = none.
- `l` brand alignment (0-4): performance, innovation, technology, precision, luxury, global ambition.
- `n` international relevance (0-4): sells in several F1 race markets (Americas, Europe, Middle East, Asia)?
  4 = global brand in many F1 markets; 1 = one country only; 0 = local/single-site.
- `scale`: `"L"` you know it is large (about USD 1B+ revenue or a major listed group); `"M"` mid
  (about USD 75M-1B); `"S"` you believe it is clearly below USD 75M revenue; `"U"` unknown. Be conservative:
  use `"U"` rather than guess.
- `parent`: controlling parent company if the brand is owned (>50%) by a group you know, else `""`.
  Never put a minority shareholder or a holding of the same name.
- `sec`: `0` if the sector shown in the industry field is fine; otherwise the number of the correct
  primary sector from this list:
  1 Automotive & Mobility; 2 Aerospace, Defence & Space; 3 Airlines & Air Travel; 4 Travel, Hotels & Leisure;
  5 Gambling & Gaming Venues; 6 Sports, Fitness & Events; 7 Video Games & Esports; 8 Software, Internet & AI;
  9 Media, Entertainment & Publishing; 10 Telecommunications; 11 Semiconductors & Electronics;
  12 IT Services & Consulting; 13 Banking & Lending; 14 Insurance; 15 Investment & Capital Markets;
  16 Financial Services & Payments; 17 Oil, Gas & Fuels; 18 Utilities & Renewable Energy; 19 Mining & Metals;
  20 Chemicals & Materials; 21 Industrial Machinery & Equipment; 22 Shipping, Maritime & Shipbuilding;
  23 Logistics & Transportation; 24 Building Products & Materials; 25 Construction & Engineering; 26 Real Estate;
  27 Home & Furniture; 28 Luxury, Jewellery & Watches; 29 Beauty & Personal Care; 30 Fashion, Apparel & Footwear;
  31 Alcoholic Drinks; 32 Food & Beverage; 33 Tobacco & Nicotine; 34 Consumer Products; 35 Retail & E-commerce;
  36 Pharma & Biotech; 37 Medical Devices & Diagnostics; 38 Healthcare Services; 39 Agriculture & Agribusiness;
  40 Packaging & Printing; 41 Environmental & Waste Services; 42 Security Services; 43 Staffing & HR;
  44 Marketing, Advertising & PR; 45 Government, Non-profit & Associations; 46 Professional & Business Services;
  47 Education & Training; 48 Diversified & Other.
- `note`: at most 6 words, only when useful (why junk/division, known F1 deal, sanctioned, etc.), else `""`.

## Rules
- Judge the company, not the industry label. An unknown mid-size B2B firm usually scores 1-2 on most fit items.
- Do not invent facts. If you do not recognise the company, score from the row data and set `scale` to `"U"`.
- Do not give a subsidiary its parent's fame: score the brand itself; name the parent in `parent`.
- If the company already sponsors an F1 team or F1 itself, say so in `note` (e.g. "F1: McLaren partner").
- Keep exactly one output row per input row, same order, valid JSON (double quotes). No prose in the file.

## How to work efficiently
Process one input file at a time: read it, write its output file, move on. Skip any file whose output
already exists. Do not re-read files you have finished. When done, reply in one line: files written and
counts of t values.
