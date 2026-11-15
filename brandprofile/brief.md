# Brief: accurate company profiles for a Formula 1 sponsorship prospect workbook

The user (an F1 sponsorship seller) gave us a sheet of brands taken from Crunchbase searches. For every brand we must
fill the same profile fields we use for listed companies. The user has asked for the result to be HIGHLY ACCURATE.
A blank or "not confirmed" answer is acceptable. A wrong or invented answer is not.

Each line of your input file is one brand (JSON):
- `id`, `brand` (as written in the sheet; long names may be cut short by "..." or carry reading errors)
- `tab` (the sector tab it sits on; assigned automatically, so it is sometimes wrong), `subsector` (Crunchbase industries, often cut short)
- `country`, `loc` (Crunchbase headquarters location, often cut short), `funding` (total funding as shown by Crunchbase), `last` (date of last funding round)
- `about` (a description written earlier by a researcher; `about_conf` says how sure they were), `cb_desc` (start of the Crunchbase description)
- `flags` (earlier notes, for example "listed (IPO status: public)" or "last funding 2012: check it is still independent and operating")
- `user_added: true` means the user typed this brand in without any data: profile it from what you know.

How to work
- Sources, in order of trust: (1) the Crunchbase facts in the line; (2) what you know for certain about THIS company; (3) the `about` text.
- Do not use web search. Do not write any financial figure (revenue, valuation, funding, headcount).
- First make sure you have the right company: name + country + city + industry must fit together. Several companies share a name.
- If you do not recognise the company, write only what the line supports, set `conf` to "low" and `basis` to "inferred". Never invent
  products, customers, countries, owners, tickers or deals.
- Correct the `about` text where you know it is wrong or out of date (for example the company has since been acquired).

For every input line write ONE JSON object on ONE line (JSON Lines, same order, every id exactly once):

{"id": "...",              // exactly as given
 "name": "...",            // the company's proper name. Complete a name that was cut short or misread ONLY if you are sure which company it is; otherwise copy `brand`
 "hq": "City, Country",    // from `loc` and `country`: fix spelling and cut-off text, use the usual English names (e.g. "Riyadh, Saudi Arabia"). Change the city only if you are certain Crunchbase is wrong. "" for the city part if unknown: then write just the country
 "desc": "...",            // what the company does: ONE plain factual sentence of 10-20 words (products or services, customers). No marketing words, no padding
 "sector": "...",          // the correct sector from the list below. Keep `tab` if it fits; change it only when the tab is clearly wrong (e.g. a power utility on the Semiconductors tab)
 "industry": "...",        // the specific line of business in 2-6 words, e.g. "electric vehicle maker", "clinical-stage oncology biotech", "cloud data warehouse software"
 "reach": "Domestic|Regional|International|Global",
 "basis": "stated|known|inferred",
 "markets": "...",         // main customer markets, existing international operations, and expansion plans you KNOW of. 8-25 words. If you know of no international activity or plans, say so ("Customers in India only; no verified expansion plans.")
 "rationale": "...",       // why an F1 partnership could make commercial sense for THIS company, 12-25 words, specific (which markets, B2B hospitality, technology showcase, product launch...). If it makes little sense, say so plainly ("Pre-revenue drug developer with no brand to market; weak F1 fit.")
 "rel": 1-5,               // strategic relevance to F1, see below
 "status": "private|listed|subsidiary|state-owned|non-commercial|defunct|unknown",
 "ticker": "",             // only if listed and you are sure: "LCID (Nasdaq)", "7203 (Tokyo)", "STLAM (Milan), STLA (NYSE)". Otherwise ""
 "parent": "",             // owner or acquirer if the company is majority-owned by another company or a state: "StoneX Group", "Public Investment Fund (Saudi Arabia)". Otherwise ""
 "stage": "commercial|pre-revenue|project|fund|non-commercial",
 "changed": "",            // any corporate change you know of, with year: "Acquired by StoneX in 2020", "Renamed Nscale in 2024", "Filed for bankruptcy in 2023", "Merged into X". Otherwise ""
 "f1": "",                 // "" if no current link. If the company, its parent, a subsidiary or one of its brands is a CURRENT (2025-2026) Formula 1 sponsor / partner / supplier / team owner / engine supplier, say which
 "conf": "high|medium|low"}  // how sure you are that the whole profile describes the right company correctly

Field rules
- `reach` = where the company's customers and operations are TODAY:
  Domestic = essentially one country. Regional = several countries in one region (Europe; Gulf / Middle East; South-East Asia; Latin America;
  US + Canada). International = customers or operations in two or more world regions, but not a worldwide footprint.
  Global = sells or operates across North America, Europe and Asia-Pacific (usually more) at real scale.
  A company with no customers yet (clinical-stage biotech, mine under development, product not launched) takes the reach of its operations,
  normally Domestic, and `markets` must say it is pre-revenue. Selling software on the internet does not by itself make a company Global.
- `basis`: "stated" = the line itself says where it sells or operates. "known" = you know it as a fact about this company.
  "inferred" = you are judging from the type of business and its location. When in doubt between two reach values and the basis is
  "inferred", choose the narrower one.
- `rel`: 5 = brand-led or enterprise company with international ambitions and an obvious F1 use, or direct rivals already sponsor F1.
  4 = strong on two of: international growth, brand marketing, B2B hospitality value, technology tie-in. 3 = plausible but not obvious.
  2 = weak: domestic, little marketing culture, commodity, regulated utility, early-stage or pre-revenue.
  1 = very unlikely or restricted: tobacco, weapons-only, sanctioned, defunct, a fund or project vehicle, government body, charity.
- `status`: "listed" = its own shares trade on a stock exchange today. "subsidiary" = majority-owned by another company (including companies
  that were acquired and still trade under the brand). "state-owned" = government-controlled and not listed. "non-commercial" = government
  body, university, research institute, charity, association. "defunct" = closed, liquidated, or the brand no longer exists.
  "unknown" = you cannot tell. "private" = everything else (independent, founder-, family-, PE- or VC-owned).
- `stage`: "commercial" = sells products or services. "pre-revenue" = still developing its product (most clinical-stage biotechs, explorers).
  "project" = a single asset or project-finance vehicle (one wind farm, pipeline, mine, tower, property scheme, data-centre campus).
  "fund" = investment fund, holding or SPAC with no operating brand. "non-commercial" = public body or non-profit.
- `sector` must be one of: Automotive & Mobility; Aerospace, Defence & Space; Airlines & Air Travel; Travel, Hotels & Leisure; Gambling & Gaming Venues; Sports, Fitness & Events; Video Games & Esports; Software, Internet & AI; Media, Entertainment & Publishing; Telecommunications; Semiconductors & Electronics; IT Services & Consulting; Banking & Lending; Insurance; Investment & Capital Markets; Financial Services & Payments; Oil, Gas & Fuels; Utilities & Renewable Energy; Mining & Metals; Chemicals & Materials; Industrial Machinery & Equipment; Shipping, Maritime & Shipbuilding; Logistics & Transportation; Building Products & Materials; Construction & Engineering; Real Estate; Home & Furniture; Luxury, Jewellery & Watches; Beauty & Personal Care; Fashion, Apparel & Footwear; Alcoholic Drinks; Food & Beverage; Tobacco & Nicotine; Consumer Products; Retail & E-commerce; Pharma & Biotech; Medical Devices & Diagnostics; Healthcare Services; Agriculture & Agribusiness; Packaging & Printing; Environmental & Waste Services; Security Services; Staffing & HR; Marketing, Advertising & PR; Government, Non-profit & Associations; Professional & Business Services; Education & Training; Diversified & Other.
- `f1`: use the roster below and your own knowledge. Being a rival of a sponsor is NOT a link. A licence, franchise or supplier relation is a
  link only if you say so explicitly ("bottler for PepsiCo").

Current Formula 1 roster (championship, team and Grand Prix partners, 2025-26). A company on this list, or the parent /
subsidiary / brand owner of one, must get a non-empty `f1`:
1Password; 3D Systems; 3M; adidas; Aggreko; Airia; Airtasker; Airwallex; Akkodis; Aleph; Allwyn; Alpinestars; ALT Sports Data; Alteryx; Ambipar; AMD; American Express; América Móvil (Claro); Anthropic (Claude); Aon; Apex Ultra; Aquame; Aramco; Arcos Dorados (McDonald's); Arctic Monkeys; Arm; Armor All; Arrow Electronics; Ashurst; AT&T; Athletic Propulsion Labs; AtkinsRéalis; Atlas Air; Atlassian; Audi; AvaTrade; Avature; AWS; Barclays; Barilla; BBS; Before You Speak Coffee; Bell Helmets; Bell Racing; BetterUp; Betway; BingX; Bitdefender; BK8; BlockDAG; BNY; Boeing; BOSS; BOXBOX; BP; Breitling; Brembo; Brillio; British American Tobacco; Built For Athletes; Businessolver; BWT; Camozzi; Carlyle; Cash App; Castore; Castrol; Cato Networks; Cefla; Celsius; CEVA Logistics; Champagne Taittinger; Chivas Regal; Circle; Cisco (Webex); Claro; Clear; CNBC; Cognition; Cognizant; Cohere; Coinbase; CoinPayments; CommScope; Confluent; Core Scientific; CoreWeave; CrowdStrike; Crypto.com; D.Energy; DAMAC Properties; Dell Technologies; Deloitte; Delphi; DeWalt (Stanley Black & Decker); DHL; DMG MORI; DP World; Dropbox; Duracell; DXC Technology; Dynatrace; Ecolab; Ecopol; Edward Jones; Eight Sleep; Einhell; ELEMIS; ElevenLabs; Emburse; Endless; EndState; Eni; Espacio; Esso Synergy; Estrella Galicia 0,0; Etihad; Etihad Airways; eToro; Eurodatacar; Exein; Extreme Networks; Fanatec; FanDuel; Ferrari (power unit supplier); Fever; Financial Times; Fix Network; Flexjet; Floyd; Ford; Ford Racing; Freshworks; Frontieras North America; FxPro; G.H. Mumm; G42; Garrett Motion; Gate.io; General Motors; Genesys; Gillette; Girard-Perregaux; Glasurit; Glenfiddich; Globant; Goldman Sachs; Google; Greene Tweed; Groq; Gulf Air; Gulf Oil International; H. Moser & Cie; Haas Automation; Haas Tooling; Hahnair; Hard Rock International; Hedera; Heineken; Hewlett Packard Enterprise; Hexagon; Hilton; HMN24; Honda; HP; HUGO; HUGO Eyewear; IBM; IC Markets; ic! berlin; IFS; Indeed; IndraMind; INEOS; Infobip; Introl; Iron Mountain; Iveco; IWC Schaffhausen; Jaaq; Jack Daniel's; Jackpot City; JCB; JigSpace; Jim Beam; KAUST; Keeper Security; Komatsu; Kraken; Krown Produce; Las Vegas Convention and Visitors Authority; LEGO; Lenovo; Libertex; Liqui Moly; Louis Vuitton; Lumi; LVMH; M-Experiment; Maaden; Mammoet; ManpowerGroup; Marks & Spencer; Marriott Bonvoy; Marsh; Mastercard; Matrix; Mattel; Maui Jim; Medallia; Memento Exclusives; Mercedes-AMG High Performance Powertrains; Mercedes-Benz (power unit supplier); Meta AI; MGM Resorts; Microsoft; MISSION; Mobil 1; Mobilize Financial Services; Modo Casino; Monster Energy; mophie; Morrison Foerster; Motul; Mous; Moët & Chandon; Moët Hennessy; Mphasis; MSC Cruises; Nasdaq; Neat; NEFT Vodka; Nestlé (KitKat); NetApp; NeverMile; New Era; NexGen; Nexo; NGK Spark Plugs; NinjaOne; NMC²; Nouryon; Nu; Nuveen; OAKBERRY; Oakley; Octave; Okta; OKX; OMR; ONEflight; Optimum Nutrition; Oracle; Orion180; Paramount+; Paulaner; Pepe Jeans; Pepperstone; PepsiCo; Perfect Moment; Perk; Peroni Nastro Azzurro; Petronas; Philips Professional Displays; Piquadro; Pirelli; Play'n GO; Playseat; PUBG Mobile; Public; Puma; Pure Electric; PwC; PWR; Qatar Airways; R5 Turbo 3E; Randstad; Rauch; Ray-Ban; RebelDot; Red Bull; Red Bull Ford Powertrains; Regent Seven Seas Cruises; Reiss; Revolut; Richard Mille; Riedel Communications; Roboze; Rokt; Roland; Rubrik; Ruckus Networks; S.Pellegrino; Sabelt; Salesforce; Santander; SAP; Schneider Electric; Schuberth; SEALSQ; Secretlab; ServiceNow; Shamir; Shell; Sherwin-Williams; Siemens; Signify; Sikkens (AkzoNobel); Singapore Airlines; Singha Corporation; SKF; SkinCeuticals; Smartsheet; Snapdragon (Qualcomm); Solera; Sparco; Specialized; Spinal Injuries Association; Splunk; Standard Chartered; STC; Stephens; Stripe; Student.com; Synopsys (Ansys); T-Mobile; TAG Heuer; Tata Communications; TeamViewer; Technogym; Tenneco; The James Brand; The Venetian Resort; ThreatLocker; TikTok; Tommy Hilfiger; Toyota Gazoo Racing; Trak Racer; TravisMathew; TUDOR; TUMI; TWG AI; TWG Motorsports; UBS; UChicago Medicine; Udemy; UKG; UniCredit; United Machining; Valvoline; Vantage; VAST Data; Vellamo; Velocity Black; Vercel; viagogo; Visa; Visit Qatar; VistaJet; WhatsApp; WHOOP; Wilkinson Sword; Workday; World of Hyatt; Xerox; XMTrading; YETI; Yugo; ZCG; Zoomex; Zoox; Zscaler; ZYN; Öhlins
Added Nov 2026 (new deals and partner pages re-read): Intel; Adobe; SharkNinja; Unilever (Clear haircare, Liquid I.V.); Logitech; Wynn Resorts; Caesars Entertainment; Bradesco;
Mercado Libre; Stratasys; AbbVie; Rakuten (Ferrari, from 2027); Daimler Truck (Mercedes-Benz Trucks); Arctic Wolf; D3O; Roland DG; Tenex AI; Revolut (Audi title sponsor); BWT.
Also: team owners and engine suppliers (Ferrari, Mercedes-Benz, Renault/Alpine, Audi/Volkswagen group, Honda, Ford,
General Motors/Cadillac, Toyota, Aston Martin, Liberty Media).

Write every company's fields for that company. If you reuse a standard sentence for similar companies, every word of it must be true for
each one (a medical-device maker is not a "drug developer"; a company with sales is not "pre-revenue"). Count the words of each `desc`
before you finish: 10 to 20, no fewer, no more.

Output rules: valid JSON on each line, double quotes, no trailing commas, no line breaks inside a value, no text outside the JSON lines.
Write the output file in chunks of about 30 companies (append each chunk), then check: same number of lines as the input, same ids in the
same order, every line parses as JSON, `desc` is 10-20 words, `reach`/`basis`/`status`/`stage`/`conf` use only the allowed values.
Keep any helper script in your own scratch directory (named in your instructions). Never run or edit a script you did not write, and create
no other files in the repository: other agents share this machine.
Reply with one short line: lines written; how many conf low; how many basis inferred; how many status defunct or subsidiary; how many non-empty f1.
