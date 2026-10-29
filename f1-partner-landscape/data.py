"""F1 partner landscape, October 2026: one record per team-partner relationship.

row:    1 = title / principal / premium, 2 = official / team partner, 3 = supplier / regional / licensee
sector: FS = financial services, PS = professional services, LS = life sciences & health, O = other
new:    month the partnership was announced, if announced in 2026
"""
import json

SRC = {
    "f1": "RTR Sports, F1 sponsors and partners (last updated 6 Oct 2026, checked against the official F1 roster)",
    "mercedes": "mercedesamgf1.com/partners (official, read 29 Oct 2026)",
    "redbull": "redbullracing.com/int-en/partners (official, read 29 Oct 2026)",
    "ferrari": "f1salaries.com/sponsors/ferrari (last updated 30 Sep 2026); ferrari.com partner page unavailable",
    "mclaren": "f1salaries.com/sponsors/mclaren (last updated 30 Sep 2026) + AbbVie (Sportcal, 20 Oct 2026)",
    "astonmartin": "astonmartinf1.com/en-GB/partners (official, read 29 Oct 2026); tiers from f1salaries (30 Sep 2026)",
    "alpine": "alpinef1.com/partners (official, read 29 Oct 2026)",
    "williams": "williamsf1.com/partners (official, read 29 Oct 2026)",
    "haas": "haasf1team.com/partners (official, read 29 Oct 2026)",
    "vcarb": "visacashapprb.com/int-en/partners (official, read 29 Oct 2026)",
    "audi": "audif1.com/en/partners (official, read 29 Oct 2026)",
    "cadillac": "f1salaries.com/sponsors/cadillac (last updated 30 Sep 2026) and RTR Sports (5 Aug 2026) + Frontieras (23 Oct 2026); official page blocked",
}

# (partner, row, sector, published tier, new-in-2026 month or None)
T = {
"f1": [
    ("Aramco",1,"O","Global Partner",None),("AWS",1,"O","Global Partner",None),("DHL",1,"O","Global Partner",None),
    ("Heineken",1,"O","Global Partner",None),("Lenovo",1,"O","Global Partner",None),("LVMH",1,"O","Global Partner",None),
    ("MSC Cruises",1,"O","Global Partner",None),("Pirelli",1,"O","Global Partner",None),("Qatar Airways",1,"O","Global Partner",None),
    ("Salesforce",1,"O","Global Partner",None),
    ("Allwyn",2,"O","Official Partner",None),("American Express",2,"FS","Official Partner",None),("Barilla",2,"O","Official Partner",None),
    ("Crypto.com",2,"FS","Official Partner",None),("Globant",2,"O","Official Partner",None),
    ("Las Vegas Convention & Visitors Authority",2,"O","Official Partner",None),("LIQUI MOLY",2,"O","Official Partner",None),
    ("Louis Vuitton",2,"O","Official Partner",None),("Marsh",2,"FS","Official Partner","Apr"),("Moët Hennessy",2,"O","Official Partner",None),
    ("Nestlé (KitKat)",2,"O","Official Partner",None),("Paramount+",2,"O","Official Partner",None),("PepsiCo",2,"O","Official Partner",None),
    ("PwC",2,"PS","Official Partner",None),("Santander",2,"FS","Official Partner",None),("Standard Chartered",2,"FS","Official Partner","Jan"),
    ("TAG Heuer",2,"O","Official Partner",None),
    ("Arcos Dorados (McDonald's)",3,"O","Regional Partner",None),("T-Mobile",3,"O","Regional Partner",None),
    ("Aggreko",3,"O","Official Provider",None),("Fever",3,"O","Official Provider",None),("Flexjet",3,"O","Official Provider",None),
    ("PUMA",3,"O","Official Provider",None),("Tata Communications",3,"O","Official Provider",None),
    ("Betway",3,"O","Official Betting Operator",None),("FanDuel",3,"O","Official Betting Operator",None),
],
"mercedes": [
    ("PETRONAS",1,"O","Title Partner",None),("CrowdStrike",1,"O","Principal Partner",None),("INEOS",1,"O","Principal Partner",None),
    ("Microsoft",1,"O","Principal Partner","Jan"),
    ("adidas",2,"O","Team Partner",None),("Snapdragon",2,"O","Team Partner",None),("TeamViewer",2,"O","Team Partner",None),
    ("Solera",2,"O","Team Partner",None),("Hewlett Packard Enterprise",2,"O","Team Partner",None),("UBS",2,"FS","Team Partner",None),
    ("Stripe",2,"FS","Team Partner","Oct"),("Meta AI",2,"O","Team Partner",None),("Nu",2,"FS","Team Partner",None),
    ("WhatsApp",2,"O","Team Partner",None),("Vercel",2,"O","Team Partner",None),("SAP",2,"O","Team Partner",None),
    ("G42",2,"O","Team Partner",None),("Signify",2,"O","Team Partner",None),("Marriott Bonvoy",2,"O","Team Partner",None),
    ("AMD",2,"O","Team Partner",None),("Einhell",2,"O","Team Partner",None),("IWC Schaffhausen",2,"O","Team Partner",None),
    ("Akkodis",2,"PS","Team Partner",None),("Sherwin-Williams",2,"O","Team Partner",None),("Nasdaq",2,"FS","Team Partner",None),
    ("PepsiCo",2,"O","Team Partner",None),
    ("Endless",3,"O","Team Supplier",None),("Pirelli",3,"O","Team Supplier",None),("Mous",3,"O","Team Supplier",None),
    ("BetterUp",3,"PS","Regional Partner",None),
],
"redbull": [
    ("Oracle",1,"O","Title Partner",None),("Visa",1,"FS","Partner",None),
    ("TAG Heuer",2,"O","Partner",None),("Rokt",2,"O","Partner",None),("Mobil 1",2,"O","Partner",None),("Ford Racing",2,"O","Partner",None),
    ("Carlyle",2,"FS","Partner",None),("DAMAC Properties",2,"O","Partner","Feb"),("AT&T",2,"O","Partner",None),("Gate",2,"FS","Partner",None),
    ("Hard Rock",2,"O","Partner",None),("AvaTrade",2,"FS","Partner",None),("YETI",2,"O","Partner",None),("1Password",2,"O","Partner",None),
    ("Indeed",2,"PS","Partner",None),("Siemens",2,"O","Partner",None),("Heineken",2,"O","Partner",None),("Castore",2,"O","Partner",None),
    ("Armor All",2,"O","Partner",None),("Hexagon",2,"O","Partner",None),("New Era",2,"O","Partner",None),("Maui Jim",2,"O","Partner",None),
    ("Pepe Jeans",2,"O","Partner",None),("Rauch",2,"O","Partner",None),("DMG MORI",2,"O","Partner",None),
    ("Athletic Propulsion Labs",2,"O","Partner",None),("Synopsys",2,"O","Partner",None),("CLEAR",2,"O","Partner",None),
    ("Philips Professional Displays",2,"O","Partner",None),("mophie",2,"O","Partner",None),("Neat",2,"O","Partner",None),
    ("Pirelli",3,"O","Partner",None),("Sparco",3,"O","Partner",None),("PWR",3,"O","Partner",None),
],
"ferrari": [
    ("HP",1,"O","Title Partner",None),("Shell",1,"O","Premium Partner",None),("UniCredit",1,"FS","Premium Partner",None),
    ("PUMA",1,"O","Premium Partner",None),("IBM",1,"O","Premium Partner",None),("CEVA Logistics",1,"O","Premium Partner",None),
    ("Ambipar",2,"PS","Partner",None),("Aon",2,"FS","Partner",None),("BingX",2,"FS","Partner",None),("Bitdefender",2,"O","Partner",None),
    ("Chivas",2,"O","Partner",None),("DXC Technology",2,"O","Team Partner",None),("Ecopol",2,"O","Official Partner",None),
    ("Espacio",2,"O","Official Partner",None),("Genesys",2,"O","Partner",None),("IVECO",2,"O","Partner",None),
    ("ManpowerGroup",2,"PS","Partner",None),("Marina Bay Sands",2,"O","Partner",None),("Mumm",2,"O","Partner",None),
    ("Peroni",2,"O","Partner",None),("Ray-Ban",2,"O","Partner",None),("Richard Mille",2,"O","Partner",None),
    ("S.Pellegrino",2,"O","Partner",None),("SkinCeuticals",2,"O","Partner",None),("Technogym",2,"O","Partner",None),
    ("Vantage",2,"FS","Official Partner",None),("VistaJet",2,"O","Partner",None),("WHOOP",2,"O","Team Partner",None),
    ("ZCG",2,"FS","Partner",None),("ZYN",2,"O","Partner",None),
    ("BBS",3,"O","Technical Supplier",None),("Bell",3,"O","Technical Supplier",None),("Brembo",3,"O","Technical Supplier",None),
    ("Garrett",3,"O","Technical Supplier",None),("NGK",3,"O","Technical Supplier",None),("Öhlins",3,"O","Technical Supplier",None),
    ("OMR",3,"O","Technical Supplier",None),("Pirelli",3,"O","Technical Supplier",None),("Riedel",3,"O","Technical Supplier",None),
    ("Sabelt",3,"O","Technical Supplier",None),("SKF",3,"O","Technical Supplier",None),
],
"mclaren": [
    ("Mastercard",1,"FS","Official Naming Partner",None),("British American Tobacco",1,"O","Principal Partner",None),
    ("OKX",1,"FS","Official Primary Partner",None),("Google",1,"O","Official Primary Partner",None),
    ("DP World",2,"O","Partner",None),("Dell Technologies",2,"O","Official Innovation Partner",None),("FxPro",2,"FS","Partner",None),
    ("Etihad",2,"O","Official Partner","Feb"),("Airwallex",2,"FS","Partner",None),("AkzoNobel (Sikkens)",2,"O","Partner",None),
    ("Allwyn",2,"O","Partner",None),("Alpinestars",2,"O","Partner",None),("Alteryx",2,"O","Partner",None),
    ("Arrow Electronics",2,"O","Partner",None),("Ashurst",2,"PS","Partner",None),("Cisco",2,"O","Partner",None),
    ("CNBC",2,"O","Partner",None),("Deloitte",2,"PS","Partner",None),("Dropbox",2,"O","Partner",None),("Ecolab",2,"O","Partner",None),
    ("Freshworks",2,"O","Partner",None),("Global",2,"O","Partner","May"),("Goldman Sachs",2,"FS","Partner",None),
    ("Greene Tweed",2,"O","Partner",None),("Groq",2,"O","Partner",None),("Hedera",2,"FS","Partner","Jan"),("Hilton",2,"O","Partner",None),
    ("Intel",2,"O","Partner",None),("Iron Mountain",2,"O","Partner",None),("Jack Daniel's",2,"O","Partner",None),
    ("KAUST",2,"O","Partner",None),("LEGO",2,"O","Partner",None),("Liquid I.V.",2,"O","Partner",None),("Medallia",2,"O","Partner",None),
    ("Monster Energy",2,"O","Partner",None),("Motul",2,"O","Partner",None),("Okta",2,"O","Partner",None),
    ("Optimum Nutrition",2,"O","Partner",None),("PUMA",2,"O","Team Kit and Apparel Partner","Jan"),("Reiss",2,"O","Partner",None),
    ("Richard Mille",2,"O","Partner",None),("Rubrik",2,"O","Partner","Jan"),("Schneider Electric",2,"O","Partner","Jan"),
    ("SharkNinja",2,"O","Official Partner","Sep"),("Smartsheet",2,"O","Partner",None),("Stanley Black & Decker",2,"O","Partner",None),
    ("T-Mobile",2,"O","Partner",None),("TUMI",2,"O","Partner",None),("Udemy",2,"PS","Partner",None),("Workday",2,"PS","Partner",None),
    ("AbbVie",2,"LS","Official Pharmaceutical Partner","Oct"),
    ("Pirelli",3,"O","Technical Supplier",None),
],
"astonmartin": [
    ("Aramco",1,"O","Title Partner",None),("Maaden",1,"O","Principal Partner",None),
    ("Honda",2,"O","Technical Partner",None),("Cognizant",2,"O","Global AI Services Partner",None),
    ("CoreWeave",2,"O","Official AI Cloud Computing Partner",None),("Cohere",2,"O","Official Generative AI Partner",None),
    ("Arm",2,"O","Partner",None),("Atlas Air",2,"O","Partner",None),("BOSS",2,"O","Partner",None),("Breitling",2,"O","Partner",None),
    ("Celsius",2,"O","Partner",None),("Cognition",2,"O","Partner",None),("Coinbase",2,"FS","Partner",None),
    ("CoinPayments",2,"FS","Partner",None),("Eight Sleep",2,"O","Partner",None),("ELEMIS",2,"O","Partner",None),
    ("Financial Times",2,"O","Partner",None),("Glenfiddich",2,"O","Partner",None),("JCB",2,"O","Partner",None),
    ("Krown Produce",2,"O","Partner",None),("Morrison Foerster",2,"PS","Partner",None),("NetApp",2,"O","Partner",None),
    ("NexGen",2,"O","Partner",None),("Oakley",2,"O","Partner",None),("Pepperstone",2,"FS","Partner",None),("Public",2,"FS","Partner",None),
    ("PUMA",2,"O","Partner",None),("Regent Seven Seas Cruises",2,"O","Partner",None),("ServiceNow",2,"O","Partner",None),
    ("TikTok",2,"O","Partner",None),("UKG",2,"PS","Partner",None),("Valvoline",2,"O","Partner",None),("Velocity Black",2,"O","Partner",None),
    ("Xerox",2,"O","Partner",None),("Zscaler",2,"O","Partner",None),("BK8 News",2,"O","Partner",None),("BOXBOX",2,"O","Partner",None),
    ("AQUAME",3,"O","Official Supplier",None),("Pirelli",3,"O","Partner",None),
],
"alpine": [
    ("BWT",1,"O","Title Partner",None),("Eni",1,"O","Premium Partner",None),("MSC Cruises",1,"O","Premium Partner",None),
    ("H. Moser & Cie.",1,"O","Premium Partner",None),("Adobe",1,"O","Premium Partner","Oct"),("R5 Turbo 3E",1,"O","Premium Partner",None),
    ("AtkinsRéalis",2,"PS","Team Partner",None),("Arctic Wolf",2,"O","Team Partner",None),("Apex Ultra",2,"O","Team Partner",None),
    ("Avature",2,"PS","Team Partner",None),("Businessolver",2,"PS","Team Partner",None),("Castore",2,"O","Team Partner",None),
    ("Cato Networks",2,"O","Team Partner",None),("eToro",2,"FS","Team Partner","Jan"),("Eurodatacar",2,"O","Team Partner",None),
    ("IndraMind",2,"O","Team Partner",None),("Mercado Libre",2,"O","Team Partner",None),
    ("Mobilize Financial Services",2,"FS","Team Partner",None),("MODO",2,"O","Team Partner",None),("New Era",2,"O","Team Partner",None),
    ("OAKBERRY",2,"O","Team Partner",None),("Qatar Airways",2,"O","Team Partner",None),("SEALSQ",2,"O","Team Partner",None),
    ("Shamir",2,"O","Team Partner",None),("Skip",2,"O","Team Partner",None),("Valvoline",2,"O","Team Partner",None),
    ("The Venetian Resort",2,"O","Team Partner",None),("viagogo",2,"O","Team Partner",None),("Boeing",2,"O","Team Partner",None),
    ("3D Systems",3,"O","Team Supplier",None),("Alpinestars",3,"O","Team Supplier",None),("Beforeyouspeak",3,"O","Team Supplier",None),
    ("Built For Athletes",3,"O","Team Supplier",None),("JAAQ",3,"LS","Team Supplier",None),("Delphi",3,"O","Team Supplier",None),
    ("D3O",3,"O","Team Supplier",None),("HMN24",3,"O","Team Supplier",None),("Matrix",3,"O","Team Supplier",None),
    ("LUMI",3,"O","Team Supplier",None),("M-Experiment",3,"O","Team Supplier",None),("MISSION",3,"O","Team Supplier",None),
    ("Pirelli",3,"O","Team Supplier",None),("Roland DG",3,"O","Team Supplier",None),("Trak Racer",3,"O","Team Supplier",None),
    ("United Machining",3,"O","Team Supplier",None),("Endstate",3,"O","Team Licensee",None),("The James Brand",3,"O","Team Licensee",None),
    ("Perfect Moment",3,"O","Team Licensee",None),
],
"williams": [
    ("Atlassian",1,"O","Title Partner",None),("Barclays",1,"FS","Not labelled",None),("Komatsu",1,"O","Not labelled",None),
    ("Claude",2,"O","Not labelled",None),("Kraken",2,"FS","Not labelled",None),("BNY",2,"FS","Not labelled",None),
    ("Gulf",2,"O","Not labelled",None),("Betway",2,"O","Not labelled",None),("NMC",2,"O","Not labelled",None),
    ("VAST Data",2,"O","Not labelled",None),("Stephens",2,"FS","Not labelled",None),("Wilkinson Sword",2,"O","Not labelled",None),
    ("Estrella Galicia",2,"O","Not labelled",None),("Duracell",2,"O","Not labelled",None),("Jackpot City",2,"O","Not labelled",None),
    ("Airia",2,"O","Not labelled",None),("Brillio",2,"O","Not labelled",None),("Keeper Security",2,"O","Not labelled",None),
    ("Nuveen",2,"FS","Not labelled",None),("Zoox",2,"O","Not labelled",None),("New Era",2,"O","Not labelled",None),
    ("Girard-Perregaux",2,"O","Not labelled",None),("Spinal Injuries Association",2,"O","Not labelled",None),("M&S",2,"O","Not labelled",None),
    ("Pirelli",3,"O","Not labelled",None),("Sparco",3,"O","Not labelled",None),
],
"haas": [
    ("Toyota Gazoo Racing",1,"O","Title Partner",None),
    ("IC Markets",2,"FS","Not labelled",None),("Haas Automation",2,"O","Not labelled",None),("Play'n GO",2,"O","Not labelled",None),
    ("Castore",2,"O","Not labelled","Jan"),("CommScope",2,"O","Not labelled",None),("D.Energy",2,"O","Not labelled",None),
    ("Emburse",2,"FS","Not labelled",None),("Exein",2,"O","Not labelled",None),("Fix Network",2,"O","Not labelled",None),
    ("HaasTooling.com",2,"O","Not labelled",None),("Infobip",2,"O","Not labelled",None),("MGM Rewards",2,"O","Not labelled",None),
    ("Mphasis",2,"O","Not labelled",None),("NeverMile",2,"O","Not labelled",None),("New Era",2,"O","Not labelled",None),
    ("Orion180",2,"FS","Not labelled",None),("RUCKUS Networks",2,"O","Not labelled","Jan"),("Singha",2,"O","Not labelled",None),
    ("Taittinger",2,"O","Not labelled",None),("TravisMathew",2,"O","Not labelled",None),("UChicago Medicine",2,"LS","Not labelled",None),
    ("Vellamo Water",2,"O","Not labelled",None),("Zoomex",2,"FS","Not labelled",None),
    ("Pirelli",3,"O","Not labelled",None),("Alpinestars",3,"O","Not labelled",None),("Schuberth",3,"O","Not labelled",None),
],
"vcarb": [
    ("Visa",1,"FS","Team Partner (featured)",None),("Cash App",1,"FS","Team Partner (featured)",None),
    ("TUDOR",2,"O","Team Partner",None),("HUGO",2,"O","Team Partner",None),("Ford Racing",2,"O","Team Partner",None),
    ("Nouryon",2,"O","Team Partner",None),("Mobil 1",2,"O","Team Partner",None),("Salesforce",2,"O","Team Partner",None),
    ("ThreatLocker",2,"O","Team Partner",None),("Introl",2,"O","Team Partner",None),("Confluent",2,"O","Team Partner",None),
    ("NEFT Vodka",2,"O","Team Partner",None),("XMTrading",2,"FS","Team Partner",None),("Airtasker",2,"O","Team Partner",None),
    ("Octave",2,"O","Team Partner",None),("Dynatrace",2,"O","Team Partner",None),("Student.com",2,"O","Team Partner",None),
    ("Randstad",2,"PS","Team Partner",None),("Siemens",2,"O","Team Partner",None),("HUGO Eyewear",2,"O","Team Partner",None),
    ("Riedel",2,"O","Team Partner",None),("RebelDot",2,"O","Team Partner",None),("Roboze",2,"O","Team Partner",None),
    ("Hahnair",2,"O","Team Partner",None),("Floyd",2,"O","Team Partner",None),("Barilla",2,"O","Team Partner",None),
    ("Pirelli",3,"O","Team Partner",None),
],
"audi": [
    ("Revolut",1,"FS","Title Sponsor",None),("Visit Qatar",1,"O","Principal Partner",None),("bp",1,"O","Principal Partner",None),
    ("Castrol",1,"O","Principal Partner",None),
    ("adidas",2,"O","Official Partner",None),("Aleph",2,"O","Official Partner","Jan"),("Nexo",2,"FS","Official Partner","Jan"),
    ("NinjaOne",2,"O","Official Partner",None),("Gillette (P&G)",2,"O","Official Partner",None),("Hyatt",2,"O","Official Partner",None),
    ("Perk",2,"O","Official Partner",None),("ic! berlin",2,"O","Official Partner",None),("Libertex",2,"FS","Official Partner","Mar"),
    ("ElevenLabs",2,"O","Official Partner","Jan"),("Camozzi",2,"O","Official Partner",None),("Piquadro",2,"O","Official Partner",None),
    ("Extreme Networks",2,"O","Official Partner",None),
    ("Paulaner",3,"O","Official Supplier",None),("Mammoet",3,"O","Official Supplier",None),("Öhlins",3,"O","Official Supplier",None),
    ("Pirelli",3,"O","Official Supplier",None),("Specialized",3,"O","Official Supplier",None),("Bell Helmets",3,"O","Official Supplier",None),
    ("JigSpace",3,"O","Official Supplier",None),("Glasurit",3,"O","Not labelled",None),("Sabelt",3,"O","Not labelled",None),
],
"cadillac": [
    ("TWG AI",1,"O","Primary Partner","Feb"),
    ("Claro (América Móvil)",2,"O","Official Telecommunications Partner","Jan"),("Tommy Hilfiger",2,"O","Official Apparel Partner",None),
    ("Tenneco",2,"O","Official Technical Partner","Jan"),("Core Scientific",2,"O","Official Data Center Partner","Mar"),
    ("IFS",2,"O","Official Technology Partner","Jan"),("3M",2,"O","Official Material Science Partner","Jun"),
    ("Jim Beam",2,"O","Official Spirits Partner",None),("Frontieras",2,"O","Official Energy Transformation Partner","Oct"),
    ("Alpinestars",3,"O","Technical Racewear Supplier",None),("Pirelli",3,"O","Official Tire Supplier",None),
],
}

TEAMS = [  # key, display name, group
    ("f1", "Formula 1", "Central Organisation"),
    ("mercedes", "Mercedes-AMG Petronas", "Podium Teams"), ("redbull", "Oracle Red Bull Racing", "Podium Teams"),
    ("ferrari", "Scuderia Ferrari HP", "Podium Teams"), ("mclaren", "McLaren Mastercard", "Podium Teams"),
    ("alpine", "BWT Alpine", "Challenger Teams"), ("astonmartin", "Aston Martin Aramco", "Challenger Teams"),
    ("cadillac", "Cadillac", "Challenger Teams"), ("audi", "Audi Revolut", "Challenger Teams"),
    ("haas", "TGR Haas", "Challenger Teams"), ("vcarb", "Visa Cash App Racing Bulls", "Challenger Teams"),
    ("williams", "Atlassian Williams", "Challenger Teams"),
]

out = {"teams": [], "sources": SRC}
for key, name, group in TEAMS:
    rows = T[key]
    names = [r[0] for r in rows]
    assert len(names) == len(set(names)), (key, [n for n in names if names.count(n) > 1])
    out["teams"].append({
        "key": key, "name": name, "group": group,
        "partners": [{"name": n, "row": r, "sector": s, "tier": t, "new": nw} for n, r, s, t, nw in rows],
    })

if __name__ == "__main__":
    import sys
    json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    for t in out["teams"]:
        p = t["partners"]
        foc = [x for x in p if x["sector"] != "O"]
        print(f'{t["name"]:28} total {len(p):3}  rows {[sum(1 for x in p if x["row"]==r) for r in (1,2,3)]}  '
              f'FS {sum(x["sector"]=="FS" for x in p)} PS {sum(x["sector"]=="PS" for x in p)} LS {sum(x["sector"]=="LS" for x in p)}  '
              f'focus {len(foc)/len(p):.0%}  new {sum(1 for x in p if x["new"])}')
    teams = [t for t in out["teams"] if t["key"] != "f1"]
    allp = [x["name"] for t in teams for x in t["partners"]]
    from collections import Counter
    c = Counter(allp)
    print("team partnerships", len(allp), "unique brands", len(c), "multi-team brands", sum(1 for v in c.values() if v > 1))
    print([(k, v) for k, v in c.most_common(15)])
