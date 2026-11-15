# Brief: put each listed company into one of 46 sectors (F1 sponsorship prospect database)

Your input file has one company per line:  `SYMBOL | Name | Country | categories | SIC industry | LinkedIn industry`
(the last three are hints from databases and can be empty or wrong; for some files the fourth field holds revenue,
market value and the exchange instead of categories). Use your own knowledge of the company first; the company name
itself usually says what it does.

Give each company exactly ONE code: the sector that matches its MAIN business today, or `00` if none fits.

Sectors:
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

Rules
- `35` is only for consumer brands (food, drinks, restaurants, beauty, fashion, toys, consumer electronics, EVs sold
  to consumers, games, e-commerce) headquartered in China, Hong Kong, Taiwan, South Korea or South-East Asia THAT ALREADY
  SELL ABROAD under their own brand or have announced international expansion. A consumer brand from those countries
  that is domestic-only goes to its product sector (25-34, 46). An Asian bank, chip maker, telecom or industrial
  company goes to its normal sector, not 35. Japan and India use the normal sectors.
- Carmakers of any country go to `18` (not 35) unless the company is mainly a consumer EV brand from the 35 region.
- Health insurers go to `09`. Drug makers go to `36` unless obesity / weight-loss drugs (`34`) or consumer health (`33`)
  is a core business. Hospitals, clinics, medical devices, diagnostics: `37`.
- Chemicals, coatings, glass, plastics, specialty materials `38`; mining, metals, steel `42`; cement, building
  materials, contractors, engineering firms `44`; power, gas, water, waste and environmental utilities `45`;
  property developers, landlords and REITs `41`; staffing, advertising groups, information and business services `40`;
  civil aerospace `39` (military aerospace stays `13`); education `46`.
- Conglomerates and trading houses: use the sector of the largest consumer-facing or best-known business; if no
  single business dominates, `43`.
- `00` is now only for: investment funds and trusts, SPACs, shells, pure holding or investment vehicles with no
  operating business, tobacco, packaging and paper, agriculture and food commodities, sports clubs.
- If you do not recognise the company and neither its name nor the hints make the business clear, give `??` (do not
  guess). A name such as "... Pharmaceutical", "... Bank", "... Electronics" or "... Cement" is enough to classify.

Output: write a plain text file (path given in your task) with one line per input line, in the same order:
`SYMBOL|code`   e.g.  `AAPL|25`
Nothing else in the file. Every input symbol must appear exactly once. Do not use web search; this is a
classification from knowledge and the hints. When done, reply with: lines written, and how many `??`.
