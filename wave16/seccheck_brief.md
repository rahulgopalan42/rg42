# Wave 16 sector check brief (knowledge only, no web, no Clay/Apollo/Lusha)

Each company needs ONE primary sector so it sits in exactly one sector tab of the final Formula 1 prospect
workbook. The current sector was derived from the LinkedIn industry label, which is often generic
("Manufacturing", "Investment Management", "Design Services") and puts companies in the wrong tab.
Use the row data plus what you already know. Do NOT browse, search or call any connector.

## Input
JSON array of rows `[i, name, website, country, industry, current_sector_no, description]`.

## Output
JSON array, one entry per input row, same order: `[i, sec]`
- `i`: copied from the input.
- `sec`: number (1-48) of the company's correct PRIMARY sector: what it mainly sells or does, judged at the
  level of this brand (not its parent's portfolio). Keep `current_sector_no` when it is right.
  Holding companies of a diversified group (SK, LG, Tata Sons) go to 48 unless one business clearly dominates.

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
47 Education & Training; 48 Diversified & Other

Examples: Philip Morris International -> 33; Allwyn (lotteries) -> 5; RH (Restoration Hardware) -> 27;
On (running shoes) -> 30; Western Digital -> 11; Hon Hai / Foxconn -> 11; a law firm -> 46.

## Method
Read the input with a small Python script (print compact lines, 300 rows at a time is fine), decide, then
write the output with ONE Write call per file as compact JSON. Then validate with Python: same length as
input, `i` equals 0..N-1 in order, every `sec` an int 1-48. Fix any file that fails.
