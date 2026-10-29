#!/usr/bin/env python3
"""Assign a sector and an F1 sponsorship category to every company in the Clay list.

Sector comes from the company's Clay (LinkedIn) industry, with company-level
overrides where the industry tag is misleading (e.g. AI labs tagged "Research
Services", Ferrero tagged "Manufacturing"). The F1 category uses the sector
groups from the 2026 F1 sponsorship spend data in the SPORTFIVE playbook.

Usage: categorize_sectors.py <input.csv> <output_base>
Writes <output_base>.csv and <output_base>.xlsx.
"""
import csv
import sys
from collections import Counter, defaultdict

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

TECH = "Technology"
TELECOM = "Telecommunications"
MEDIA = "Media, Entertainment & Sports"
FIN = "Financial Services"
ENERGY = "Energy, Utilities & Environment"
AUTO = "Automotive & Mobility"
TRAVEL = "Travel & Hospitality"
TRANSPORT = "Transport & Logistics"
REAL_ESTATE = "Real Estate & Construction"
INDUSTRIAL = "Industrial & Manufacturing"
AERO = "Aerospace & Defense"
CONSUMER = "Consumer Goods & Retail"
FOOD = "Food, Beverage & Agriculture"
HEALTH = "Healthcare & Life Sciences"
BUSINESS = "Business Services"
EDUCATION = "Education"
GAMBLING = "Gambling & Betting"
OTHER = "Diversified & Other"

INDUSTRY_SECTOR = {
    TECH: [
        "Software Development", "Technology, Information and Internet", "IT Services and IT Consulting",
        "Computer and Network Security", "Semiconductor Manufacturing", "Information Technology and Services",
        "Computer Hardware Manufacturing", "Computers and Electronics Manufacturing", "Artificial Intelligence",
        "Data Infrastructure and Analytics", "Robotics Engineering", "Blockchain Services", "Information Services",
        "Computer Networking Products", "Data Security Software Products", "Robot Manufacturing", "Semiconductors",
        "Desktop Computing Software Products", "IT System Custom Software Development", "Computer Hardware",
        "Climate Data and Analytics", "Research Services", "Public Safety", "Fundraising",
    ],
    TELECOM: ["Telecommunications", "Wireless Services"],
    MEDIA: [
        "Entertainment Providers", "Spectator Sports", "Computer Games", "Musicians",
        "Broadcast Media Production and Distribution", "Internet Publishing", "Media Production",
        "Technology, Information and Media", "Advertising Services", "Entertainment", "Online Audio and Video Media",
        "Book and Periodical Publishing", "Animation and Post-production", "Marketing Services", "Events Services",
        "Radio and Television Broadcasting", "Online Media", "Internet News", "Cable and Satellite Programming",
        "Social Networking Platforms",
    ],
    FIN: [
        "Financial Services", "Insurance", "Banking", "Investment Management",
        "Venture Capital and Private Equity Principals", "Investment Banking", "Capital Markets", "Funds and Trusts",
        "Insurance Agencies and Brokerages", "Loan Brokers", "Community Services",
    ],
    ENERGY: [
        "Oil and Gas", "Renewable Energy Power Generation", "Utilities", "Environmental Services",
        "Renewable Energy Semiconductor Manufacturing", "Electric Power Generation", "Services for Renewable Energy",
        "Energy Technology", "Solar Electric Power Generation", "Renewable Energy Equipment Manufacturing",
        "Renewables & Environment", "Electric Power Transmission, Control, and Distribution",
        "Climate Technology Product Manufacturing", "Nuclear Electric Power Generation",
        "Geothermal Electric Power Generation", "Water, Waste, Steam, and Air Conditioning Services",
        "Retail Gasoline", "Oil, Gas, and Mining", "Natural Gas Distribution", "Waste Treatment and Disposal",
        "Air, Water, and Waste Program Management",
    ],
    AUTO: [
        "Motor Vehicle Manufacturing", "Automotive", "Motor Vehicle Parts Manufacturing", "Retail Motor Vehicles",
        "Alternative Fuel Vehicle Manufacturing",
    ],
    TRAVEL: [
        "Airlines and Aviation", "Hospitality", "Travel Arrangements", "Leisure, Travel & Tourism",
        "Recreational Facilities", "Golf Courses and Country Clubs",
    ],
    TRANSPORT: [
        "Transportation, Logistics, Supply Chain and Storage", "Maritime Transportation", "Truck Transportation",
        "Warehousing and Storage", "Freight and Package Transportation", "Maritime", "Rail Transportation",
        "Transportation/Trucking/Railroad", "Ground Passenger Transportation", "Urban Transit Services",
    ],
    REAL_ESTATE: [
        "Real Estate", "Construction", "Wholesale Building Materials", "Leasing Non-residential Real Estate",
        "Civil Engineering", "Commercial Real Estate", "Architecture and Planning", "Leasing Residential Real Estate",
        "Interior Design", "Landscaping Services", "Surveying and Mapping Services", "Government Administration",
    ],
    INDUSTRIAL: [
        "Manufacturing", "Chemical Manufacturing", "Mining", "Appliances, Electrical, and Electronics Manufacturing",
        "Packaging and Containers Manufacturing", "Machinery Manufacturing", "Paper and Forest Product Manufacturing",
        "Plastics Manufacturing", "Primary Metal Manufacturing", "Industrial Machinery Manufacturing",
        "Automation Machinery Manufacturing", "Glass, Ceramics and Concrete Manufacturing",
        "Engines and Power Transmission Equipment Manufacturing", "Shipbuilding",
        "Chemical Raw Materials Manufacturing", "Electrical Equipment Manufacturing", "Paper and Forest Products",
        "Agriculture, Construction, Mining Machinery Manufacturing", "Glass Product Manufacturing",
        "Industrial Automation", "Commercial and Industrial Machinery Maintenance", "Equipment Rental Services",
        "Wholesale",
    ],
    AERO: [
        "Defense and Space Manufacturing", "Aviation and Aerospace Component Manufacturing",
        "Space Research and Technology", "Defense & Space", "Aviation & Aerospace",
    ],
    CONSUMER: [
        "Retail", "Consumer Services", "Wellness and Fitness Services", "Retail Apparel and Fashion",
        "Internet Marketplace Platforms", "Retail Luxury Goods and Jewelry", "Personal Care Product Manufacturing",
        "Consumer Electronics", "Health, Wellness and Fitness", "Sporting Goods Manufacturing", "Consumer Goods",
        "Retail Groceries", "Consumer Goods Rental", "Retail Office Equipment", "Luxury Goods and Jewelry",
        "Retail Health and Personal Care Products", "Retail Appliances, Electrical, and Electronic Equipment",
        "Online and Mail Order Retail", "Textile Manufacturing",
    ],
    FOOD: [
        "Food and Beverage Manufacturing", "Food and Beverage Services", "Food & Beverages", "Restaurants",
        "Farming", "Food Production", "Agricultural Chemical Manufacturing", "Dairy Product Manufacturing",
        "Fisheries", "Forestry and Logging", "Food and Beverage Retail", "International Trade and Development",
    ],
    HEALTH: [
        "Biotechnology Research", "Hospitals and Health Care", "Pharmaceutical Manufacturing",
        "Medical Equipment Manufacturing", "Biotechnology", "Medical Practices", "Mental Health Care",
        "Medical Devices", "Health and Human Services", "Veterinary Services", "Alternative Medicine",
        "Home Health Care Services", "Public Health", "Dentists", "Medical and Diagnostic Laboratories",
    ],
    BUSINESS: [
        "Business Consulting and Services", "Human Resources Services", "Professional Services", "Market Research",
        "Security and Investigations", "Facilities Services", "Outsourcing and Offshoring Consulting",
        "Translation and Localization", "Engineering Services", "Design Services", "Accounting",
        "Staffing and Recruiting", "Public Relations and Communications Services", "Law Practice", "Legal Services",
        "Strategic Management Services", "Research",
    ],
    EDUCATION: [
        "E-Learning Providers", "Education Administration Programs", "Professional Training and Coaching",
        "Higher Education", "E-Learning",
    ],
    GAMBLING: ["Gambling Facilities and Casinos"],
    OTHER: ["Holding Companies", "Individual and Family Services"],
}

# Company-level corrections where the Clay industry tag points to the wrong sector.
COMPANY_SECTOR = {
    # Research / information services
    "NMS Group": HEALTH, "Science 37": HEALTH, "Nerviano Medical Sciences - Part of NMS Group": HEALTH,
    "Sun World International": FOOD, "Atheneum": BUSINESS, "GLG": BUSINESS, "Beyond Music": MEDIA,
    # Holding companies
    "Hippocrates Holding S.p.A. | B Corp": HEALTH, "Limak Group of Companies": REAL_ESTATE,
    "RÖNESANS HOLDİNG": REAL_ESTATE,
    # Consumer services
    "FINN": AUTO, "Starship Technologies": TECH, "Tango": MEDIA, "Clutter, by Iron Mountain": TRANSPORT,
    "FLO EV Charging": AUTO, "Pollen": TRAVEL, "Veho": TRANSPORT, "Zippy Shell Incorporated": TRANSPORT,
    # Health services
    "ATI Physical Therapy": HEALTH, "Sharecare": HEALTH, "Elemy": HEALTH, "PharmEasy": HEALTH,
    "The Smilist": HEALTH, "US Oral Surgery Management": HEALTH, "Elevage Medical Technologies": HEALTH,
    "Evidation": HEALTH, "Resonetics": HEALTH,
    # Professional services
    "Exodigo": TECH, "Holtec International": ENERGY,
    # Tech / media tags
    "Authentic Brands Group": CONSUMER, "Kpler": TECH, "Accelerated Brands": CONSUMER, "Movile": TECH,
    "Figma": TECH, "Monotype": TECH, "Material Bank®": TECH,
    "Mercado Libre": CONSUMER, "Verivox GmbH": TECH, "Droom": AUTO, "Farcaster": TECH, "Skyscanner": TRAVEL,
    # Gambling operators tagged as entertainment or hospitality
    "Lottomatica SpA": GAMBLING, "KingMakers": GAMBLING, "Enjoy S.A.": GAMBLING, "Crown Resorts": GAMBLING,
    "Rivers Casino & The Landing Hotel Pittsburgh": GAMBLING,
    "Lingokids": EDUCATION,
    # Hospitality software and others tagged as hospitality
    "Buyers Edge Platform": TECH, "Canary Technologies": TECH, "Cloudbeds": TECH, "Lighthouse": TECH,
    "Deliverect": TECH, "Industrious": REAL_ESTATE, "LIVEKINDLY": FOOD,
    # Aircraft lessors tagged as airlines
    "Aero Capital Solutions": FIN, "Aviation Capital Group (ACG)": FIN, "AviLease": FIN, "Avolon": FIN,
    "Dubai Aerospace Enterprise": FIN, "Macquarie AirFinance": FIN, "SKY Leasing": FIN,
    "SMBC Aviation Capital": FIN, "TrueNoord": FIN, "Aquila Air Capital": FIN,
    "Splend": AUTO,
    # Retail
    "Enilive": ENERGY, "NWP Property": REAL_ESTATE,
    # Marketplaces
    "Rebel Foods": FOOD, "Accel Club": TECH, "Getaround": AUTO, "Voice": TECH,
    # Facilities / environmental services
    "Budderfly": ENERGY, "EVPassport": AUTO, "Bureau Veritas": BUSINESS, "SOCOTEC": BUSINESS,
    "ALTRAD": INDUSTRIAL, "Powerdot": AUTO, "VEMO": AUTO,
    # Consumer goods tags
    "Dangote Industries Limited": OTHER, "Montana Renewables, LLC": ENERGY,
    # Wholesale
    "Ankorstore": CONSUMER, "Assaí Atacadista": CONSUMER, "Mercon Coffee Group": FOOD, "Naturex": FOOD,
    "SucroCan Sourcing LLC": FOOD,
    # Electrical / electronics
    "Dreame Technology": CONSUMER, "Pioneer Corporation": CONSUMER, "ABB E-mobility": AUTO,
    "Morrow Batteries": ENERGY, "LEADRIVE": AUTO, "AaltoSemi Inc.": TECH,
    "Shanghai Fullhan Microelectronics Co., Ltd.": TECH,
    # "Manufacturing" covers very different businesses
    "American Bath Group": CONSUMER, "Beko Corporate": CONSUMER, "Beko Global": CONSUMER,
    "Butternut Box | B Corp": CONSUMER, "Divergent": AUTO, "Ferrero": FOOD, "Form Energy": ENERGY,
    "Froneri": FOOD, "Future Group India": CONSUMER, "Group14 Technologies": ENERGY, "Jostens": CONSUMER,
    "Juul Labs": CONSUMER, "Lyten": ENERGY, "Michelin": AUTO, "Natron Energy": ENERGY, "Positec": CONSUMER,
    "Roquette": FOOD, "SGP BioEnergy": ENERGY, "SK On": AUTO, "Tata Electronics": TECH, "Brandless": CONSUMER,
    "Drylock Technologies": CONSUMER, "EVelution Energy": ENERGY, "factory14": CONSUMER, "Hayat": CONSUMER,
    "HexClad Cookware": CONSUMER, "MAV Beauty": CONSUMER, "McBride": CONSUMER, "Merama": CONSUMER,
    "MTD Products": CONSUMER, "SuperMaxWorld": CONSUMER, "WaterWipes": CONSUMER,
    "Zero Motorcycles Inc.": AUTO,
}

F1_SPEND = [  # 2026 team + series sponsorship spend, $M (playbook stat bank, GlobalData 2026)
    ("Tech, media & telecom", 569.4 + 137.1),
    ("Financial services", 442.4 + 87.5),
    ("Clothing & accessories", 194.1 + 107.5),
    ("Energy & utilities", 214.7 + 55),
    ("Beverages", 170.9 + 85),
    ("Automotive", 165.1 + 67.5),
    ("Consumer goods", 180.3 + 11),
    ("Travel & tourism", 60.5 + 88.4),
    ("Industrial", 63.5 + 6.25),
    ("Logistics", 22.3 + 40),
    ("Gambling", 20.5 + 15),
    ("Construction & real estate", 32.5),
]
NOT_IN_F1 = "Not in F1 spend data"

SECTOR_F1 = {
    TECH: "Tech, media & telecom", TELECOM: "Tech, media & telecom", MEDIA: "Tech, media & telecom",
    FIN: "Financial services", ENERGY: "Energy & utilities", AUTO: "Automotive", TRAVEL: "Travel & tourism",
    TRANSPORT: "Logistics", REAL_ESTATE: "Construction & real estate", INDUSTRIAL: "Industrial",
    AERO: "Industrial", CONSUMER: "Consumer goods", FOOD: "Consumer goods", GAMBLING: "Gambling",
    HEALTH: NOT_IN_F1, BUSINESS: NOT_IN_F1, EDUCATION: NOT_IN_F1, OTHER: NOT_IN_F1,
}
CLOTHING_INDUSTRIES = {
    "Retail Apparel and Fashion", "Retail Luxury Goods and Jewelry", "Luxury Goods and Jewelry",
    "Textile Manufacturing", "Sporting Goods Manufacturing",
}
CLOTHING_COMPANIES = {
    "Aéropostale", "Gymshark", "Koton", "Kurt Geiger", "Reiss", "Takko Fashion", "Arezzo&Co", "Rue Gilt Groupe",
    "SPORT 2000", "Quince", "Authentic Brands Group",
}
NOT_CLOTHING = {"Rad Power Bikes"}
BEVERAGE_COMPANIES = {"Hindustan Coca-Cola Beverages", "Refresco", "Califia Farms"}
AGRICULTURE_INDUSTRIES = {
    "Farming", "Agricultural Chemical Manufacturing", "Fisheries", "Forestry and Logging",
    "International Trade and Development",
}

INDUSTRY_TO_SECTOR = {ind: sector for sector, inds in INDUSTRY_SECTOR.items() for ind in inds}
SECTOR_ORDER = [TECH, FIN, ENERGY, CONSUMER, MEDIA, HEALTH, AUTO, TRAVEL, FOOD, TELECOM, REAL_ESTATE,
                INDUSTRIAL, TRANSPORT, AERO, BUSINESS, EDUCATION, GAMBLING, OTHER]
FUNDING_ORDER = {"$250M+": 0, "$100M - $250M": 1}


def classify(r):
    name, industry = r["name"].strip(), r["industry"]
    sector = COMPANY_SECTOR.get(name) or INDUSTRY_TO_SECTOR.get(industry) or OTHER
    f1 = SECTOR_F1[sector]
    if sector == CONSUMER and name not in NOT_CLOTHING and (
            industry in CLOTHING_INDUSTRIES or name in CLOTHING_COMPANIES):
        f1 = "Clothing & accessories"
    elif name in BEVERAGE_COMPANIES:
        f1 = "Beverages"
    elif sector == FOOD and industry in AGRICULTURE_INDUSTRIES and name not in COMPANY_SECTOR:
        f1 = NOT_IN_F1
    return sector, f1


def main(src, out_base):
    rows = list(csv.DictReader(open(src, newline="")))
    unmapped = sorted({r["industry"] for r in rows
                       if r["name"].strip() not in COMPANY_SECTOR and r["industry"] not in INDUSTRY_TO_SECTOR})
    if unmapped:
        sys.exit(f"Industries with no sector mapping: {unmapped}")
    for r in rows:
        r["sector"], r["f1_category"] = classify(r)
    # Largest sectors first
    sector_counts = Counter(r["sector"] for r in rows)
    SECTOR_ORDER.sort(key=lambda s: -sector_counts[s])
    rows.sort(key=lambda r: (SECTOR_ORDER.index(r["sector"]), FUNDING_ORDER.get(r["funding_range"], 9),
                             r["name"].lower()))

    fields = ["entityId", "name", "sector", "f1_category", "industry", "funding_range", "domain", "linkedin_url",
              "type", "country", "locality", "size", "employee_count", "annual_revenue"]
    with open(out_base + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    headers = ["Company", "Sector", "F1 sponsorship category", "Clay industry", "Total funding (Clay range)",
               "Website", "LinkedIn", "Company type", "Country", "City", "Size", "Employees", "Annual revenue"]
    widths = [34, 30, 26, 34, 18, 26, 44, 15, 18, 22, 13, 11, 15]

    def row_values(r):
        emp = r["employee_count"]
        return [r["name"], r["sector"], r["f1_category"], r["industry"], r["funding_range"], r["domain"],
                r["linkedin_url"], r["type"], r["country"], r["locality"], r["size"],
                int(emp) if emp.isdigit() else emp, r["annual_revenue"]]

    def company_sheet(ws, sheet_rows):
        ws.append(headers)
        for c in ws[1]:
            c.font = Font(bold=True)
        for r in sheet_rows:
            ws.append(row_values(r))
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = ws.dimensions
        for i, width in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = width

    wb = Workbook()
    summary = wb.active
    summary.title = "Summary"
    by_sector = defaultdict(Counter)
    for r in rows:
        by_sector[r["sector"]][r["funding_range"]] += 1
    summary.append(["Sector", "Companies", "$250M+", "$100M - $250M", "F1 sponsorship category"])
    for c in summary[1]:
        c.font = Font(bold=True)
    for s in SECTOR_ORDER:
        if by_sector[s]:
            summary.append([s, sum(by_sector[s].values()), by_sector[s]["$250M+"], by_sector[s]["$100M - $250M"],
                            SECTOR_F1[s]])
    total = Counter(r["funding_range"] for r in rows)
    summary.append(["Total", len(rows), total["$250M+"], total["$100M - $250M"], ""])
    summary[summary.max_row][0].font = Font(bold=True)

    summary.append([])
    summary.append(["F1 sponsorship category", "Companies in list", "2026 F1 sponsorship spend ($M, team + series)"])
    for c in summary[summary.max_row]:
        c.font = Font(bold=True)
    f1_counts = Counter(r["f1_category"] for r in rows)
    for cat, spend in F1_SPEND:
        summary.append([cat, f1_counts[cat], round(spend, 1)])
    summary.append([NOT_IN_F1, f1_counts[NOT_IN_F1], ""])
    summary.append([])
    summary.append(["Notes"])
    summary[summary.max_row][0].font = Font(bold=True)
    for note in [
        "Source: Clay company search, companies tagged Privately Held or Self Owned with total funding of $100M+.",
        "Clay stores funding as ranges only. \"$250M+\" means $250M and above, with no upper limit.",
        "Sector is based on each company's Clay (LinkedIn) industry, corrected company by company where that tag was misleading.",
        "F1 spend figures are from the SPORTFIVE playbook stat bank (GlobalData 2026).",
    ]:
        summary.append([note])
    for i, width in enumerate([34, 18, 18, 18, 26], start=1):
        summary.column_dimensions[get_column_letter(i)].width = width

    company_sheet(wb.create_sheet("All companies"), rows)
    for s in SECTOR_ORDER:
        sheet_rows = [r for r in rows if r["sector"] == s]
        if sheet_rows:
            company_sheet(wb.create_sheet(s), sheet_rows)
    wb.save(out_base + ".xlsx")

    print("rows:", len(rows))
    for s in SECTOR_ORDER:
        print(f"  {s}: {sum(by_sector[s].values())} ({by_sector[s]['$250M+']} at $250M+)")
    print("F1 categories:", dict(f1_counts))
    unused = sorted(set(COMPANY_SECTOR) - {r["name"].strip() for r in rows})
    if unused:
        print("override names not found:", unused)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
