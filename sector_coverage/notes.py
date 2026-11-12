"""Verdict and note per sector, written after reading the counts and the missing names (report.py without arguments).
Verdict rule: share of the sector's well-known names that are on a researched prospect list -
65% or more = Created; 55-64% = Created - top up; under 55% = Thin - start generating."""
C, T, G = 'Created', 'Created - top up', 'Thin - start generating'
NOTES = {
 '01': (C, 'Well covered: every well-known insurer is on a list. No new sourcing needed. To grow it, research the largest of the 4,913 insurers that sit in '
           'database lists. Thinnest parts: Gulf and Takaful insurers (13 researched, 77 more unresearched) and insurtech (30).'),
 '02': (C, 'Online travel agencies (66 researched) and cruise lines (30) are covered. START GENERATING luggage brands: only 4 researched (Samsonite, Rimowa, Away...); '
           'missing e.g. July, Horizn Studios, Carl Friedrik, Mokobara; Tumi is only in a database list. Add cruise challengers: Four Seasons Yachts, Cruise Saudi, '
           'Resorts World Cruises.'),
 '03': (C, 'The big groups are there (Haleon, Kenvue, Opella, Perrigo, Reckitt). Most "missing" names are product brands of groups already listed (Voltaren, Advil, '
           'Tylenol, Nurofen, Vicks). Top up mid-size houses: Sato Pharmaceutical, Karo Pharma, Doppelherz, and supplement brands (Vital Proteins).'),
 '04': (T, '183 researched: online betting 54, lotteries 46, casino resorts 60; the big operators are there (Flutter, Entain, DraftKings, bet365, Stake, Allwyn). '
           '844 more, mostly lotteries and casinos, sit unresearched in database lists. Generate: Brazilian and African betting brands (Betnacional, Pixbet, Betika, '
           'BetKing), state lotteries (Sazka, Norsk Tipping) and mid-size European operators (BetVictor, 10bet, NetBet).'),
 '05': (C, 'The major brands are there (Xiaomi, Dyson, Hisense, TCL, Whirlpool, Groupe SEB). Most "missing" names are sub-brands of listed parents (Rowenta, Krups, '
           'Moulinex belong to Groupe SEB). Top up: gaming and creator hardware (Elgato, Ayaneo, Hasselblad) and Indian wearable brands (Boult; Noise is only in a '
           'database list).'),
 '06': (G, 'START GENERATING. 240 researched, but only half of the well-known chains. 111 well-known chains are only in a database list or the recordings and were '
           'never researched (Denny\'s, IHOP, Applebee\'s, Olive Garden, Jimmy John\'s, Wagamama, Tim Hortons), and 1,705 chains in total sit unresearched. '
           'Missing altogether: Asian tea and coffee chains (ChaPanda, Tastien, Mega MGC Coffee, Paik\'s Coffee, Seesaw Coffee) and Gulf chains (Herfy, Operation Falafel).'),
 '07': (G, 'START GENERATING. 171 researched (delivery 80, ride-hailing 36, car rental 27) and another 107 only in the recordings list. The global names are there '
           '(Uber, Bolt, Grab, Careem, Hertz, Sixt, Avis Budget). Missing: car rental and subscription (ekar, Udrive, Selfdrive, Invygo in the Gulf; Times Car, Orix Auto, '
           'Toyota Rent a Car in Japan), regional ride-hailing (Jeeny, Kaiian, Bykea, BiTaksi) and African mobility (Gokada, SafeBoda). Many are small: check affordability.'),
 '08': (T, '223 researched operators and 191 more only in the recordings list. eSIM and mobile resellers are thin: 31 researched (Airalo and Holafly are there). '
           'Generate eSIM and low-cost mobile brands: Saily, Ubigi, BNESIM, Red Bull Mobile, Tello, ho. Mobile, Kena Mobile, Very Mobile.'),
 '09': (C, 'Well covered (477 researched, all the main labs). Needs a quarterly refresh more than new sourcing. Missing: AI creative tools (Krea, Ideogram, Udio, Tavus, '
           'Hedra, Lovart) and a few assistants (Lindy, Read AI).'),
 '10': (C, 'Well covered (567 researched). Missing only smaller GPU clouds (Hyperstack, Civo, Evroc, Genesis Cloud, Hyperbolic) and a few data-centre operators '
           '(Ark Data Centres, Novva).'),
 '11': (G, 'START GENERATING. Of 98 researched brands only 3 are prediction markets (Kalshi and Polymarket are there) and 30 are stablecoin or tokenisation companies; '
           'the rest are exchanges and crypto infrastructure. Missing: prediction markets (PredictIt, Novig, ForecastEx, Railbird, Opinion Labs) and stablecoin payment '
           'companies (Brale, Coinflow, BlindPay, DolarApp, Monerium, AllUnity, Qivalis). Most are early-stage: check funding first.'),
 '12': (G, 'START GENERATING. 351 researched, but mostly wearables and sleep (111) and telehealth (47); weight-loss has 29 and longevity / diagnostics 30. Missing: '
           'weight-loss telehealth (Zealthy, Mochi Health, Ivim Health, Medvi), longevity and blood testing (Superpower, Biograph, Lifeforce, Thriva, Medichecks), '
           'hormone and women\'s health (Evernow, Elektra Health, Hone Health) and Gulf digital health (Altibbi, Vezeeta, Bioniq).'),
 '13': (T, '983 researched (527 China, 119 South Korea) and 6,441 more consumer companies in database lists. The headline names are there (BYD, Xiaomi, Pop Mart, Shein, '
           'Mixue, Chagee, Luckin). Generate: Chinese and Korean beauty (Judydoll, Flower Knows, Colorkey; COSRX, Beauty of Joseon, Anua, Tirtir), fashion (Urban Revivo, '
           'Songmont, Matin Kim) and food chains (ChaPanda, Tastien, Tai Er). Some "missing" names are sub-brands of listed parents (Denza, Yangwang; Sulwhasoo).'),
 '14': (T, '119 researched, including the leaders (Waymo, Zoox, Pony.ai, WeRide), and 70 more only in the recordings list (Cruise, Aeva, TuSimple). Research the '
           'recordings-only names first. Missing names are mostly small suppliers; add Chinese robotaxi operators (Ruqi / Chenqi Technology, Banma).'),
 '15': (G, 'Small sector: 44 researched, including every main maker (Joby, Archer, Beta, Eve, EHang, Vertical Aerospace, Wisk, Supernal, SkyDrive). Lilium and Volocopter '
           'are only in the recordings list (both went through insolvency: check status). START GENERATING the second tier if you want depth: electric-aircraft makers '
           '(Eviation, magniX, Ampaire), GAC Govy, vertiport operators (Ferrovial Vertiports, Urban-Air Port). Most are pre-revenue.'),
 '16': (T, '154 researched, including the main makers (Figure, Unitree, Apptronik, Agility Robotics). Missing names are mostly small labs. Top up: Chinese makers '
           '(Dexmal, Lumos Robotics, Vita Dynamics), Korea and Japan (WIRobotics, RLWRLD, Tokyo Robotics) and Europe (Enchanted Tools, Pollen Robotics, PAL Robotics).'),
 '17': (G, 'START GENERATING. 85 researched, including the main operators (SpaceX / Starlink, AST SpaceMobile, Lynk, Skylo, Globalstar, Iridium, Viasat, Eutelsat, SES). '
           'Satellite-to-phone itself is only a handful of companies. Missing: regional operators (Es\'hailSat, KT SAT, China Satcom, Hisdesat), satellite IoT (Myriota, '
           'Astrocast, Lacuna Space) and maritime / in-flight connectivity providers (Tototheo, IEC Telecom, Tampnet). Amazon\'s Kuiper is named only under Amazon.'),
}
