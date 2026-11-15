# Brief: company profile fields for a database of listed companies that could sponsor Formula 1

Each line of your input file is one listed company (JSON): symbol, name, country, the sector we assigned (code),
an HQ hint, database hints (categories / SIC / LinkedIn industry) and revenue / market cap for context.
Financial figures are handled elsewhere - do NOT research or write any financial numbers.
Work from your own knowledge of each company. Do not use web search (there are too many companies).
If you do not recognise a company, say so through `conf: "low"` and keep to what the hints support. Never invent.

For every input line write ONE JSON object on ONE line to your output file (JSON Lines, same order, every symbol once):

{"sym": "...",            // exactly as given
 "sector": "NN",          // keep the given code if it is right; otherwise the correct code from the list below, or "00" if none fits
 "hq": "City, Country",   // headquarters city and country; "" if you are not sure of the city (do not guess)
 "desc": "...",           // what the company actually does: ONE plain sentence, 10-20 words, no marketing language
 "reach": "Domestic|Regional|International|Global",   // where its customers are today
 "markets": "...",        // main customer markets, existing international operations, and any expansion plans you KNOW of (max 25 words); write "No verified expansion plans" if you know of none
 "rationale": "...",      // why an F1 partnership could make commercial sense for THIS company (max 25 words): brand building in which markets, B2B hospitality, technology showcase, launch of what...; be specific, not generic
 "rel": 1-5,              // strategic relevance to F1: 5 = brand-led or enterprise company with global ambitions and an obvious F1 use, or rivals already in F1; 4 = strong on two of (international growth, brand marketing, B2B hospitality value, technology tie-in); 3 = plausible but not obvious; 2 = weak (domestic, little marketing culture, commodity or regulated); 1 = very unlikely or restricted (tobacco, weapons-only, sanctioned)
 "f1": "",                // "" if no current link. If the company, its parent, a subsidiary or one of its brands is a CURRENT (2025-2026) Formula 1 sponsor / partner / supplier / team owner / engine supplier, say which (e.g. "TAG Heuer (LVMH brand) - Formula 1 official timekeeper"). Use the roster below and your own knowledge.
 "flags": "",             // "" or a short note if any applies: "majority-owned subsidiary of <listed parent>", "state-controlled", "being acquired by <X>" / "taken private", "delisted or bankrupt", "holding / investment vehicle, not an operating brand", "sanctioned", "tobacco / alcohol-free market restrictions", "name/ticker unclear"
 "conf": "high|medium|low"}   // how sure you are about the description and HQ

Sector codes:
- `01` AI infrastructure: GPU clouds, data-centre operators and builders, servers and networking for AI, data-centre power and cooling
- `02` AI software & applications: companies whose main product is AI: models, agents, AI analytics, AI-first applications
- `03` Semiconductors & chip equipment: chip designers, foundries, memory, chip equipment and materials, EDA
- `04` Enterprise software & cybersecurity: business software, cloud platforms, data, developer tools, security software
- `05` IT services & consulting: IT outsourcing, systems integrators, digital engineering, management and technology consulting
- `06` Fintech, payments & digital banking: payment networks and processors, neobanks, online lenders, trading apps, buy-now-pay-later, money transfer, financial software
- `07` Crypto, stablecoins & prediction markets: crypto exchanges and brokers, stablecoin issuers, crypto miners and treasuries, prediction-market operators
- `08` Banks, wealth management & capital markets: banks, private banks, asset and wealth managers, brokers, stock exchanges
- `09` Insurance & insurtech: life, health, property and casualty insurers, reinsurers, insurance brokers, digital insurers
- `10` Betting, iGaming & lotteries: sportsbooks, online casinos, lotteries, casino-resort operators, betting technology
- `11` Telecoms & connectivity: mobile and fixed operators, cable and broadband, eSIM and mobile resellers, telecom equipment
- `12` Satellite & space: satellite operators and connectivity, satellite-to-phone, launch, space systems
- `13` Defence technology: defence primes and electronics, drones, defence software, military aerospace
- `14` Quantum computing: quantum computers, quantum software and components
- `15` Robotics, automation & industrial technology: humanoid and industrial robots, factory automation, industrial machinery, electrical equipment, tools, test and measurement, 3D printing
- `16` Robotaxis & autonomous driving: robotaxi operators, self-driving software, lidar and driver-assistance systems
- `17` Air taxis & advanced air mobility: eVTOL makers, electric aircraft, drone delivery, private aviation
- `18` Automotive: carmakers, EVs & auto parts: car, truck and motorcycle makers, EV makers, batteries, charging, tyres, parts suppliers, car dealers
- `19` Ride-hailing, delivery & car rental: ride-hailing, food and grocery delivery apps, car rental and car sharing, micromobility
- `20` Online travel, cruise lines & luggage: online travel agencies, tour operators, cruise lines, luggage and travel goods
- `21` Airlines, hotels & leisure: airlines, hotel groups, resorts, theme parks, live events, fitness clubs
- `22` Logistics, freight & shipping: parcel and express, freight forwarders, trucking, railways, container and bulk shipping, ports
- `23` Energy, fuels & lubricants: oil and gas producers, refiners, fuel retail, lubricants, oilfield services, LNG
- `24` Nuclear, fusion & new energy: nuclear and uranium, hydrogen, solar, wind, energy storage, clean-power producers
- `25` Consumer electronics & home appliances: phones, PCs, audio, wearables, cameras, TVs, home appliances, smart home
- `26` Video games, esports & digital entertainment: game publishers and platforms, esports, streaming, music, social media, sports media
- `27` Beverages & alcoholic drinks: soft drinks, energy drinks, water, coffee and tea brands, beer, wine, spirits
- `28` Restaurant & coffee chains: quick-service and casual-dining chains, coffee and tea chains, franchise operators
- `29` Food, household brands & consumer retail: packaged food and snacks, household goods, toys, sporting goods, pet care, large retailers and e-commerce
- `30` Beauty & personal care: cosmetics, skincare, fragrance, hair care, personal-care brands
- `31` Fashion, apparel & footwear: clothing, sportswear, footwear, accessories, eyewear
- `32` Luxury goods, jewellery & watches: luxury houses, jewellery, watches, luxury cars and yachts, premium lifestyle brands
- `33` Consumer health & over-the-counter brands: over-the-counter medicines, vitamins and supplements, consumer-health arms, pharmacy chains
- `34` Weight-loss, longevity & digital health: obesity-drug makers, telehealth, consumer diagnostics, wearables and connected fitness, consumer medical devices
- `35` Chinese & Asian consumer brands going global: consumer brands headquartered in China, Hong Kong, Taiwan, South Korea or South-East Asia that sell or are expanding abroad
- `36` Pharmaceuticals & biotech: drug makers, generics, vaccines, biotech with marketed products, animal health, contract drug manufacturing
- `37` Medical technology & healthcare services: medical devices and equipment, diagnostics, hospital and clinic groups, dental and eye care, health IT sold to hospitals
- `38` Chemicals, coatings & advanced materials: chemicals, paints and coatings, industrial gases, plastics, glass, carbon fibre and composites, specialty materials
- `39` Aerospace & aviation manufacturing: civil aircraft and engine makers, aerospace components, aircraft leasing and maintenance
- `40` Professional services, staffing & business services: staffing and recruitment, HR and payroll services, advertising and marketing groups, market research and information services, legal and accounting, facilities, security and outsourcing
- `41` Real estate & property developers: property developers, real-estate services and brokers, mall, office and hotel landlords, REITs
- `42` Mining, metals & steel: miners, gold and copper producers, steel, aluminium, metals processing
- `43` Conglomerates & trading houses: diversified groups, family and state conglomerates, general trading houses with several unrelated businesses
- `44` Construction, engineering & building products: contractors, engineering firms, infrastructure builders, cement, building materials, home-improvement and building products
- `45` Utilities, power & water: power generators and grids, gas and water utilities, water technology, waste and environmental services
- `46` Education & edtech: online learning platforms, tutoring and test-prep, private schools and universities, education publishers
Sector rules: `35` only for consumer brands headquartered in China, Hong Kong, Taiwan, South Korea or South-East Asia that
already sell abroad or have announced international expansion; other companies from those countries use their normal
sector. Health insurers `09`. Drug makers `36` unless obesity drugs (`34`) or consumer health (`33`) is core; hospitals,
medical devices and diagnostics `37`. `00` = none of the 46: investment funds and trusts, SPACs, shells, pure holding
or investment vehicles with no operating business, tobacco, packaging and paper, agriculture and food commodities,
sports clubs.

Current Formula 1 roster (championship, team and Grand Prix partners, 2025-26). A company on this list, or the parent /
subsidiary / brand owner of one, must get a non-empty `f1`:
1Password; 3D Systems; 3M; adidas; Aggreko; Airia; Airtasker; Airwallex; Akkodis; Aleph; Allwyn; Alpinestars; ALT Sports Data; Alteryx; Ambipar; AMD; American Express; América Móvil (Claro); Anthropic (Claude); Aon; Apex Ultra; Aquame; Aramco; Arcos Dorados (McDonald's); Arctic Monkeys; Arm; Armor All; Arrow Electronics; Ashurst; AT&T; Athletic Propulsion Labs; AtkinsRéalis; Atlas Air; Atlassian; Audi; AvaTrade; Avature; AWS; Barclays; Barilla; BBS; Before You Speak Coffee; Bell Helmets; Bell Racing; BetterUp; Betway; BingX; Bitdefender; BK8; BlockDAG; BNY; Boeing; BOSS; BOXBOX; BP; Breitling; Brembo; Brillio; British American Tobacco; Built For Athletes; Businessolver; BWT; Camozzi; Carlyle; Cash App; Castore; Castrol; Cato Networks; Cefla; Celsius; CEVA Logistics; Champagne Taittinger; Chivas Regal; Circle; Cisco (Webex); Claro; Clear; CNBC; Cognition; Cognizant; Cohere; Coinbase; CoinPayments; CommScope; Confluent; Core Scientific; CoreWeave; CrowdStrike; Crypto.com; D.Energy; DAMAC Properties; Dell Technologies; Deloitte; Delphi; DeWalt (Stanley Black & Decker); DHL; DMG MORI; DP World; Dropbox; Duracell; DXC Technology; Dynatrace; Ecolab; Ecopol; Edward Jones; Eight Sleep; Einhell; ELEMIS; ElevenLabs; Emburse; Endless; EndState; Eni; Espacio; Esso Synergy; Estrella Galicia 0,0; Etihad; Etihad Airways; eToro; Eurodatacar; Exein; Extreme Networks; Fanatec; FanDuel; Ferrari (power unit supplier); Fever; Financial Times; Fix Network; Flexjet; Floyd; Ford; Ford Racing; Freshworks; Frontieras North America; FxPro; G.H. Mumm; G42; Garrett Motion; Gate.io; General Motors; Genesys; Gillette; Girard-Perregaux; Glasurit; Glenfiddich; Globant; Goldman Sachs; Google; Greene Tweed; Groq; Gulf Air; Gulf Oil International; H. Moser & Cie; Haas Automation; Haas Tooling; Hahnair; Hard Rock International; Hedera; Heineken; Hewlett Packard Enterprise; Hexagon; Hilton; HMN24; Honda; HP; HUGO; HUGO Eyewear; IBM; IC Markets; ic! berlin; IFS; Indeed; IndraMind; INEOS; Infobip; Introl; Iron Mountain; Iveco; IWC Schaffhausen; Jaaq; Jack Daniel's; Jackpot City; JCB; JigSpace; Jim Beam; KAUST; Keeper Security; Komatsu; Kraken; Krown Produce; Las Vegas Convention and Visitors Authority; LEGO; Lenovo; Libertex; Liqui Moly; Louis Vuitton; Lumi; LVMH; M-Experiment; Maaden; Mammoet; ManpowerGroup; Marks & Spencer; Marriott Bonvoy; Marsh; Mastercard; Matrix; Mattel; Maui Jim; Medallia; Memento Exclusives; Mercedes-AMG High Performance Powertrains; Mercedes-Benz (power unit supplier); Meta AI; MGM Resorts; Microsoft; MISSION; Mobil 1; Mobilize Financial Services; Modo Casino; Monster Energy; mophie; Morrison Foerster; Motul; Mous; Moët & Chandon; Moët Hennessy; Mphasis; MSC Cruises; Nasdaq; Neat; NEFT Vodka; Nestlé (KitKat); NetApp; NeverMile; New Era; NexGen; Nexo; NGK Spark Plugs; NinjaOne; NMC²; Nouryon; Nu; Nuveen; OAKBERRY; Oakley; Octave; Okta; OKX; OMR; ONEflight; Optimum Nutrition; Oracle; Orion180; Paramount+; Paulaner; Pepe Jeans; Pepperstone; PepsiCo; Perfect Moment; Perk; Peroni Nastro Azzurro; Petronas; Philips Professional Displays; Piquadro; Pirelli; Play'n GO; Playseat; PUBG Mobile; Public; Puma; Pure Electric; PwC; PWR; Qatar Airways; R5 Turbo 3E; Randstad; Rauch; Ray-Ban; RebelDot; Red Bull; Red Bull Ford Powertrains; Regent Seven Seas Cruises; Reiss; Revolut; Richard Mille; Riedel Communications; Roboze; Rokt; Roland; Rubrik; Ruckus Networks; S.Pellegrino; Sabelt; Salesforce; Santander; SAP; Schneider Electric; Schuberth; SEALSQ; Secretlab; ServiceNow; Shamir; Shell; Sherwin-Williams; Siemens; Signify; Sikkens (AkzoNobel); Singapore Airlines; Singha Corporation; SKF; SkinCeuticals; Smartsheet; Snapdragon (Qualcomm); Solera; Sparco; Specialized; Spinal Injuries Association; Splunk; Standard Chartered; STC; Stephens; Stripe; Student.com; Synopsys (Ansys); T-Mobile; TAG Heuer; Tata Communications; TeamViewer; Technogym; Tenneco; The James Brand; The Venetian Resort; ThreatLocker; TikTok; Tommy Hilfiger; Toyota Gazoo Racing; Trak Racer; TravisMathew; TUDOR; TUMI; TWG AI; TWG Motorsports; UBS; UChicago Medicine; Udemy; UKG; UniCredit; United Machining; Valvoline; Vantage; VAST Data; Vellamo; Velocity Black; Vercel; viagogo; Visa; Visit Qatar; VistaJet; WhatsApp; WHOOP; Wilkinson Sword; Workday; World of Hyatt; Xerox; XMTrading; YETI; Yugo; ZCG; Zoomex; Zoox; Zscaler; ZYN; Öhlins
Added Nov 2026 (new deals and partner pages re-read): Intel; Adobe; SharkNinja; Unilever (Clear haircare, Liquid I.V.); Logitech; Wynn Resorts; Caesars Entertainment; Bradesco;
Mercado Libre; Stratasys; AbbVie; Rakuten (Ferrari, from 2027); Daimler Truck (Mercedes-Benz Trucks); Arctic Wolf; D3O; Roland DG; Tenex AI; Revolut (Audi title sponsor); BWT.
Also: team owners and engine suppliers (Ferrari, Mercedes-Benz, Renault/Alpine, Audi/Volkswagen group, Honda, Ford,
General Motors/Cadillac, Toyota, Aston Martin, Liberty Media).

Output rules: valid JSON on each line, double quotes, no trailing commas, no line breaks inside a value. Write the file
in chunks of about 25 companies (append), then at the end check: same number of lines as the input, same symbols in the
same order, every line parses as JSON. Create no other files in the repository (use your scratchpad for temp files).
Reply with: lines written, how many `conf: low`, how many sector changes, how many non-empty `f1`.
