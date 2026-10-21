# Merges the three research chunks into cm_templates.json and applies the hand rewrite of
# 21 Oct: short sentences, plain words, buyer-relevant grid names, human tone. Every name and fact
# below comes from the agents' verified rows and flags; nothing new is introduced here.
import json, os

SCRATCH = os.path.dirname(os.path.abspath(__file__))
rows = []
for fn in ('cm_A_rows.json', 'cm_B_rows.json', 'cm_C_rows.json'):
    p = os.path.join(SCRATCH, fn)
    if os.path.exists(p):
        rows += json.load(open(p))
    else:
        print('MISSING', fn)

EDITS = {
    'Kobold Metals': {
        'brand': "KoBold Metals",
        'fit_reason': "due to breaking ground this spring at Mingomba in Zambia, its first move from exploration "
                      "into building a mine.",
        'target_audience': "You work with mining majors like BHP, and with the governments and automakers that need "
                           "new copper. Buyers of that kind are already in Formula 1: Ford (Red Bull), Toyota Gazoo "
                           "Racing (Haas) and General Motors (Cadillac), and Ma'aden (Aston Martin) is a miner on the grid.",
        'market_overlap': "You explore in Quebec, Finland and Australia, are building Mingomba in Zambia and run the "
                          "company from California. The Formula 1 calendar aligns with the markets you are present in "
                          "and expanding into: Montreal in May, Melbourne in March, and Miami, Austin and Las Vegas at home.",
        'shared_values': "An F1 team takes the data from its car's sensors every lap and turns it into decisions "
                         "within hours. KoBold does the same with geoscience data: deciding where to drill, and now "
                         "where to build.",
        'market_reference': "Ma'aden, the Saudi mining group, became a Principal Partner of Aston Martin in 2025 to "
                            "build its name worldwide and attract talent. Mining is already on the grid. No "
                            "exploration company is, and KoBold would be the first.",
    },
    'EARTH AI': {
        'brand': "Earth AI",
        'target_audience': "You sell drilled, proven projects to mining companies, and you raise money from investors "
                           "who back exploration. Mining companies are already in Formula 1: Ma'aden (Aston Martin) "
                           "and NexGen Energy (Aston Martin).",
        'shared_values': "An F1 team makes a prediction in the simulator, then proves it on track at the next race. "
                         "Earth AI predicts where the minerals are, then proves it with its own drill rigs and, since "
                         "April, its own lab.",
        'market_reference': "Komatsu sells equipment to the same mine operators you sell discoveries to. It has been a "
                            "Principal Partner of Williams since 2024 and extended the deal in September. The mining "
                            "supply chain is on the grid; exploration technology is not there yet.",
    },
    'Scout Discoveries Corp.': {
        'fit_reason': "due to Agnico Eagle taking a strategic stake in the company, alongside Electrum, in the private "
                      "placement closed in September.",
        'target_audience': "You go after gold and copper producers that fund earn-ins on your projects, like Agnico "
                           "Eagle and Centerra Gold. The mining world is already in Formula 1: Ma'aden (Aston Martin) "
                           "and Komatsu (Williams).",
        'shared_values': "An F1 team keeps design, build and race operations under one roof, so nothing waits on a "
                         "supplier. Scout works the same way: targeting, mapping, drilling and now sample preparation, "
                         "all in-house.",
        'market_reference': "NexGen Energy, a Canadian mine developer that is also pre-production, has been a Team "
                            "Partner of Aston Martin since 2024. It uses the team to share know-how on process, "
                            "technology and safety. Your Canadian backers know that name; no US exploration company "
                            "is on the grid yet.",
    },
    'Principal Mineral': {
        'target_audience': "You sell to the electronics makers that build servers, networking gear and aerospace "
                           "systems on your copper foil and laminates. Those buyers are already in Formula 1: HP "
                           "(Ferrari), Dell Technologies (McLaren) and Lenovo (Formula 1).",
        'shared_values': "An F1 team builds much of its own electronics and tests every material before it goes on "
                         "the car. Principal Mineral makes the copper foil, laminates and shielding those electronics "
                         "are built on.",
        'market_reference': "3M, a materials company selling into the same electronics and aerospace supply chains, "
                            "joined the Cadillac team in June as Official Material Science Partner. Greene Tweed, "
                            "another advanced materials maker, is a McLaren partner. Advanced materials are on the "
                            "grid; copper foil and laminates are not yet.",
    },
    'EACON': {
        'fit_reason': "due to its Hong Kong listing in July, backed by Zijin Mining and XCMG, with the proceeds set "
                      "aside for international growth.",
        'target_audience': "You sell to the operators of large open-pit mines, from coal and copper groups in China "
                           "to contractors like Thiess in Western Australia. Mining companies are already in Formula "
                           "1: Ma'aden (Aston Martin) and NexGen Energy (Aston Martin).",
        'shared_values': "An F1 team runs its cars from a control room: software, sensors and live decisions, in "
                         "public view. EACON does the same with fleets of driverless trucks that run around the clock "
                         "in open-pit mines.",
        'market_reference': "Komatsu, your direct rival in autonomous haulage and the maker of the trucks you retrofit "
                            "in Western Australia, has been a Principal Partner of Williams since 2024 and extended in "
                            "September. Your closest overseas competitor is already next to an F1 team. EACON would "
                            "be the first autonomous mining specialist on the grid.",
    },
    'Standard Lithium': {
        'target_audience': "You sell to battery makers and automakers that want a North American source of lithium, "
                           "with LG Energy Solution and Trafigura already signed for offtake. Automakers of that kind "
                           "are in Formula 1: Ford (Red Bull), Toyota Gazoo Racing (Haas) and General Motors (Cadillac).",
        'shared_values': "An F1 team spends years developing a car before it turns a wheel, with its partners watching "
                         "every step. Standard Lithium is doing the same in Arkansas: years of drilling and pilot "
                         "work, in public, toward a final investment decision.",
        'market_reference': "ExxonMobil, your closest rival for Smackover brine lithium in Arkansas, is in Formula 1 "
                            "through Mobil 1 at Red Bull Racing and a second deal with Racing Bulls since 2025. Two "
                            "companies are developing the same brine. One of them already has its name on the grid.",
    },
    'Lilac': {
        'target_audience': "You sell your extraction technology to lithium developers, mining companies and energy "
                           "majors moving into brine projects. Energy majors of that kind are in Formula 1: Aramco "
                           "(Aston Martin), Shell (Ferrari) and bp (Audi).",
        'shared_values': "An F1 team tests every new part on the bench before it goes on the car. Lilac proves its "
                         "technology the same way: pilots in Argentina, Chile, Germany and Indonesia first, then the "
                         "first commercial plant.",
        'market_reference': "Eni backed a rival extraction technology this year, putting money into the Black Giant "
                            "project in Chile. Eni is also a Premium Partner of Alpine. The energy majors choosing "
                            "lithium technology are in Formula 1; no extraction technology company is there yet.",
    },
    'EnergyX': {
        'target_audience': "You sell to automakers, battery makers and the traders that supply them, with Trafigura "
                           "signed this month. Automakers of that kind are in Formula 1: Toyota Gazoo Racing (Haas) "
                           "and Ford (Red Bull).",
        'shared_values': "An F1 team is now a battery engineer as much as an engine builder: the 2026 power units run "
                         "on far more electrical power. EnergyX works at the other end of that chain, producing the "
                         "lithium those batteries need.",
        'market_reference': "General Motors led your Series B and owns the new Cadillac team. Eni invested in Black "
                            "Giant in July and is a Premium Partner of Alpine. Two of your investors are already in "
                            "this sport. Your name is not there yet.",
    },
    'Element3': {
        'target_audience': "You work with oil and gas operators in the Permian Basin and sell lithium carbonate to "
                           "battery makers. Both sides are in Formula 1: Petronas (Mercedes) on the energy side, Ford "
                           "(Red Bull) and General Motors (Cadillac) on the buyer side.",
        'shared_values': "An F1 car recovers the energy it would lose under braking and uses it again on the next "
                         "straight. Element3 does the same with oilfield water: a waste stream turned into "
                         "battery-grade lithium.",
        'market_reference': "Aramco is entering your business. Lithium has been extracted from its Saudi oilfield "
                            "brines, and this month it contracted its first direct lithium extraction plant. Aramco's "
                            "name is across the Aston Martin team. A peer is moving into your market; your seat is "
                            "still open.",
    },
    'US Strategic Metals': {
        'target_audience': "You sell cobalt, nickel and copper to battery makers, alloy producers and advanced "
                           "manufacturers that want a US source. Buyers of that kind are in Formula 1: General Motors "
                           "(Cadillac), Ford (Red Bull) and Komatsu (Williams).",
        'shared_values': "An F1 team makes most of its car in its own factory to control quality and supply. US "
                         "Strategic Metals is building that control for American battery metals: mining, refining and "
                         "recycling on one site in Missouri.",
        'market_reference': "Ma'aden, the Saudi mining and metals company, became a Principal Partner of Aston Martin "
                            "in 2025. It is a peer in the kingdom where you signed your alliance in January. A miner "
                            "is on the grid; no American critical minerals producer is there yet.",
    },
    'Redwood Materials': {
        'fit_reason': "due to its expanded General Motors partnership in June, the first automaker to work with "
                      "Redwood across the full battery lifecycle.",
        'target_audience': "You sell cathode material and copper foil to automakers and battery makers, and energy "
                           "storage to utilities and data centers. Your own customers are in Formula 1: Toyota Gazoo "
                           "Racing (Haas), Ford (Red Bull) and General Motors (Cadillac).",
        'shared_values': "An F1 team runs a hybrid power unit, and from 2026 the battery does far more of the work. "
                         "Redwood works at the other end of a battery's life, recovering the metals in used packs for "
                         "new cells and storage.",
        'market_reference': "Toyota, your cathode and copper foil customer, became Haas's title partner for 2026. "
                            "General Motors, your full battery lifecycle partner, owns the new Cadillac team. Your "
                            "customers are in the sport; the battery materials seat next to them is open.",
    },
    'Nth Cycle': {
        'fit_reason': "due to its binding term sheet with Glencore in September for black mass supply and nickel and "
                      "lithium offtake.",
        'target_audience': "You refine black mass and scrap for recyclers, miners and manufacturers, with Glencore "
                           "signed in September for supply and offtake. The automakers behind that demand are in "
                           "Formula 1: Toyota Gazoo Racing (Haas), Ford (Red Bull) and General Motors (Cadillac).",
        'market_overlap': "Nth Cycle runs its Oyster plant in Fairfield, Ohio, is planning a refinery in the US Southeast "
                          "and is exploring Europe with Glencore. The Formula 1 calendar aligns with the markets you are "
                          "present in and expanding into: Miami, Austin and Las Vegas, plus the European rounds.",
        'shared_values': "An F1 team wins on efficiency: a power unit built to waste as little fuel as possible. Nth "
                         "Cycle brings the same thinking to metals, refining black mass and scrap with electricity "
                         "instead of smelting.",
        'market_reference': "Komatsu, the direct competitor of your investor Caterpillar, has been a Principal Partner "
                            "of Williams since 2024 and renewed in September. Your investor's closest rival has its "
                            "name on an F1 car; the critical minerals refining seat next to it is open.",
    },
    'pH7 Technologies': {
        'fit_reason': "due to its oversubscribed Series B in April, backed by BHP Ventures and Asahi Kasei, to take "
                      "its metals extraction from catalyst recycling into copper mining.",
        'target_audience': "You sell to automakers, catalyst makers and recyclers that trade in platinum, palladium "
                           "and rhodium, and now to copper mines like Gibraltar. Those buyers are in Formula 1: Toyota "
                           "Gazoo Racing (Haas), Ford (Red Bull) and Ma'aden (Aston Martin).",
        'shared_values': "An F1 team works to a public sustainability plan: 100% sustainable fuel from 2026 and net "
                         "zero by 2030. pH7 fits that plan directly: platinum, palladium and rhodium recovered from "
                         "spent catalytic converters, in a closed loop, with no wastewater.",
        'market_reference': "Tenneco, whose Clean Air and Walker businesses make the catalysts and converters that "
                            "become your feedstock, joined the Cadillac team as Official Technical Partner in January. "
                            "The front end of your supply chain is in the sport; the platinum group metals seat next "
                            "to it is open.",
    },
    'Alta Resource Technologies': {
        'target_audience': "You sell separated rare earths to magnet makers and to the motor and electronics "
                           "manufacturers that need a supply outside China. The automakers that depend on those "
                           "magnets are in Formula 1: Toyota Gazoo Racing (Haas), Ford (Red Bull) and General Motors "
                           "(Cadillac).",
        'shared_values': "The motors in an F1 power unit run on high-performance permanent magnets, and from 2026 "
                         "they do more of the work than ever. Alta sits at the start of that supply chain, separating "
                         "rare earths from magnet scrap with engineered proteins instead of chemical refining.",
        'market_reference': "NexGen Energy, a Canadian mine developer, has been a partner of Aston Martin since 2024, "
                            "using the team to share process, technology and safety know-how. A mine developer has "
                            "found a practical use for an F1 partnership. The rare earth seat is open.",
    },
}

NOTES = {   # extra flags from the contact run, shown as NOTE lines in Emails Ready
    'EARTH AI': "Contacts: Apollo holds 25 people at Earth AI but only three with verified work emails: founder and "
                "CEO Roman Teslyuk, the COO and business operations.",
    'Alta Resource Technologies': "Contacts: only two commercial people exist in Apollo (business development director, "
                                  "president); the other two are senior R&D leaders at a small company.",
    'Scout Discoveries Corp.': "Contacts: a four-person Apollo footprint; the third and fourth contacts are exploration "
                               "and operations leads, not marketing.",
    'EACON': "Contacts: VP Strategy and Partnerships and the founder are the senior pair; the other two are a product "
             "strategy manager and a marketing associate (Apollo has seven usable people).",
    'Element3': "Contacts: three verified; no marketing or commercial titles exist at the company in Apollo.",
}

# The reason clause must connect what the brand is doing to Formula 1 (customers on the grid,
# an engineering parallel, or a market it is entering), not just describe the brand.
FIT = {
    'Kobold Metals': "due to its step from exploration into mine building at Mingomba in Zambia, which brings it "
                     "to the same table as the automakers and mining groups already partnering in Formula 1.",
    'EARTH AI': "due to the way it predicts a deposit and then proves it with its own rigs and lab, the same "
                "predict-and-prove discipline an F1 team runs every race weekend.",
    'Scout Discoveries Corp.': "due to the producers now backing it, Agnico Eagle among them, the same kind of mining "
                               "companies that Aston Martin already counts as partners.",
    'Principal Mineral': "due to its acquisition of Isola in June, which makes it a materials supplier to the "
                         "electronics industry at the moment that industry's biggest names, HP, Dell and Lenovo, "
                         "are investing in Formula 1.",
    'EACON': "due to its Hong Kong listing in July, which funds its push into international mining markets where "
             "its biggest rival, Komatsu, already partners with an F1 team.",
    'Standard Lithium': "due to its Franklin project assessment this month, which brings a North American lithium "
                        "source closer for the automakers, Ford, Toyota and General Motors among them, that already "
                        "sit in Formula 1.",
    'Lilac': "due to its DOE award in August for a first commercial plant on the Great Salt Lake, moving its "
             "technology from pilots to production at the moment energy majors like Aramco, an Aston Martin "
             "title partner, are choosing their lithium extraction technology.",
    'EnergyX': "due to its Trafigura supply agreement this month and the fact that two of its own investors, "
               "General Motors and Eni, are already in Formula 1.",
    'Element3': "due to the plant it opened in Midland in February, turning oilfield water into battery-grade "
                "lithium, the same recover-and-reuse logic an F1 car applies to the energy it would otherwise lose.",
    'US Strategic Metals': "due to the refinery it is building near Fredericktown, Missouri, at the moment the "
                           "automakers building US battery supply chains, General Motors and Ford among them, are "
                           "investing in Formula 1.",
    'Redwood Materials': "due to its expanded General Motors partnership in June, the first automaker to work with "
                         "Redwood across the full battery lifecycle, and GM now owning a Formula 1 team.",
    'Nth Cycle': "due to its Glencore term sheet in September, which moves its refining from one Ohio plant toward "
                 "a full US supply chain at the moment the automakers in Formula 1, Toyota, Ford and General "
                 "Motors, are building theirs.",
    'pH7 Technologies': "due to its move from catalyst recycling into copper mining, which puts it alongside the "
                        "automakers and mining groups, Toyota, Ford and Ma'aden among them, that already partner "
                        "in Formula 1.",
    'Alta Resource Technologies': "due to its Korea Zinc joint venture to produce rare earth oxides in the US from "
                                  "2027, a supply chain that ends in the motors and magnets every F1 power unit "
                                  "depends on.",
}

# Target audience: who they sell to, then three or four grid brands of exactly that type.
TA = {
    'Kobold Metals': "You work with mining majors like BHP, and with the governments and automakers that need new "
                     "copper. Buyers of that kind are already in Formula 1: Ford (Red Bull), Toyota Gazoo Racing "
                     "(Haas) and General Motors (Cadillac), and Ma'aden (Aston Martin) is a miner on the grid.",
    'EARTH AI': "You sell drilled, proven projects to mining companies, and you raise money from investors who back "
                "exploration. The mining world is already in Formula 1: Ma'aden (Aston Martin), NexGen Energy "
                "(Aston Martin) and Komatsu (Williams).",
    'Scout Discoveries Corp.': "You go after gold and copper producers that fund earn-ins on your projects, like Agnico "
                               "Eagle and Centerra Gold. The mining world is already in Formula 1: Ma'aden (Aston "
                               "Martin), NexGen Energy (Aston Martin) and Komatsu (Williams).",
    'Principal Mineral': "You sell to the electronics makers that build servers, networking gear and aerospace "
                         "systems on your copper foil and laminates. Those buyers are already in Formula 1: HP "
                         "(Ferrari), Dell Technologies (McLaren), Lenovo (Formula 1) and Oracle (Red Bull).",
    'EACON': "You sell to the operators of large open-pit mines, from coal and copper groups in China to contractors "
             "like Thiess in Western Australia. The mining world is already in Formula 1: Ma'aden (Aston Martin), "
             "NexGen Energy (Aston Martin) and Komatsu (Williams).",
    'Standard Lithium': "You sell to battery makers and automakers that want a North American source of lithium, "
                        "with LG Energy Solution and Trafigura already signed for offtake. Automakers of that kind "
                        "are in Formula 1: Ford (Red Bull), Toyota Gazoo Racing (Haas), General Motors (Cadillac) "
                        "and Honda (Aston Martin).",
    'Lilac': "You sell your extraction technology to lithium developers, mining companies and energy majors moving "
             "into brine projects. Energy majors of that kind are in Formula 1: Aramco (Aston Martin), Shell "
             "(Ferrari), bp (Audi) and Petronas (Mercedes).",
    'EnergyX': "You sell to automakers, battery makers and the traders that supply them, with Trafigura signed this "
               "month. Automakers of that kind are in Formula 1: Toyota Gazoo Racing (Haas), Ford (Red Bull) and "
               "Honda (Aston Martin).",
    'Element3': "You work with oil and gas operators in the Permian Basin and sell lithium carbonate to battery "
                "makers. Both sides are in Formula 1: Petronas (Mercedes) on the energy side, Ford (Red Bull), "
                "General Motors (Cadillac) and Toyota Gazoo Racing (Haas) on the buyer side.",
    'US Strategic Metals': "You sell cobalt, nickel and copper to battery makers, alloy producers and advanced "
                           "manufacturers that want a US source. Buyers of that kind are in Formula 1: General "
                           "Motors (Cadillac), Ford (Red Bull), Toyota Gazoo Racing (Haas) and Komatsu (Williams).",
    'Redwood Materials': "You sell cathode material and copper foil to automakers and battery makers, and energy "
                         "storage to utilities and data centers. Your own customers are in Formula 1: Toyota Gazoo "
                         "Racing (Haas), Ford (Red Bull), General Motors (Cadillac) and Audi, which runs its own team.",
    'Nth Cycle': "You refine black mass and scrap for recyclers, miners and manufacturers, with Glencore signed in "
                 "September for supply and offtake. The automakers behind that demand are in Formula 1: Toyota "
                 "Gazoo Racing (Haas), Ford (Red Bull), General Motors (Cadillac) and Honda (Aston Martin).",
    'pH7 Technologies': "You sell to automakers, catalyst makers and recyclers that trade in platinum, palladium and "
                        "rhodium, and now to copper mines like Gibraltar. Those buyers are in Formula 1: Toyota Gazoo "
                        "Racing (Haas), Ford (Red Bull), Honda (Aston Martin) and Ma'aden (Aston Martin).",
    'Alta Resource Technologies': "You sell separated rare earths to magnet makers and to the motor and electronics "
                                  "manufacturers that need a supply outside China. The automakers that depend on "
                                  "those magnets are in Formula 1: Toyota Gazoo Racing (Haas), Ford (Red Bull), "
                                  "General Motors (Cadillac) and Honda (Aston Martin).",
}

by_brand = {r['brand']: r for r in rows}
for brand, fields in EDITS.items():
    if brand in by_brand:
        by_brand[brand].update(fields)
    else:
        print('edit target missing:', brand)
for brand, reason in FIT.items():          # applied after EDITS so these win
    if brand in by_brand:
        by_brand[brand]['fit_reason'] = reason
    else:
        print('fit target missing:', brand)
for brand, text in TA.items():
    if brand in by_brand:
        by_brand[brand]['target_audience'] = text
    else:
        print('audience target missing:', brand)
for brand, note in NOTES.items():
    if brand in by_brand:
        by_brand[brand].setdefault('flags', []).append(note)

json.dump(rows, open(os.path.join(SCRATCH, 'cm_templates.json'), 'w'), indent=1)
print('cm_templates.json:', len(rows), 'brands;', sum(1 for r in rows if r.get('market_reference')), 'with reference;',
      sum(1 for r in rows if r.get('variant') == 'B2C'), 'B2C')
for r in rows:
    words = sum(len((r.get(f) or '').split()) for f in ('fit_reason', 'target_audience', 'market_overlap', 'shared_values', 'market_reference', 'f1_audience'))
    print(f'  {r["brand"]:28s} {r["variant"]:4s} {words:>3} words  {r["designation"]}')
