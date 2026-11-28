import sys; sys.path.insert(0,"scratch_k29")
from rec import *
UW="https://en.wikipedia.org/wiki/Uzum"; US="https://uzum.com/en"
W("main",name="Uzum",website="uzum.com",aliases=["Uzum Market","Uzum Bank","Uzum Nasiya","Uzum Tezkor"],hq_city="Tashkent",hq_country="Uzbekistan",
 sector="Retail & E-commerce",subsector="e-commerce and fintech ecosystem",desc="Uzbekistan's first tech unicorn, combining the Uzum Market marketplace, a digital bank, BNPL, food delivery and car-sales platforms.",
 products="online marketplace, digital bank and cards, BNPL instalments, express delivery, SME platform, car marketplace",model="Hybrid",customers="20 million monthly users; 18,000+ sellers",
 ownership_type="venture-backed",parent_immediate="holding registered in Abu Dhabi Global Market",parent_ultimate="founders Djasur Djumaev, Nikolay Seleznev, Roman Lavrentyev and investors",parent_listed="private",
 minority_investors="FinSight Ventures, Xanara, Tencent, VR Capital, Omani sovereign entities",employees=14000,markets="Uzbekistan",expansion_markets="IPO planned 2027 (LSE, Nasdaq, Abu Dhabi, Hong Kong considered)",reach="Domestic",route="A",
 fin=[{"metric":"valuation","value_orig":"USD 2.3bn pre-money","usd_m":2300,"period":"2026-03","published":"2026-03","kind":"reported","source":UW},
  {"metric":"equity_funding","value_orig":"USD 52M Series A equity (2024) + ~USD 70M (2025) + >USD 130M strategic incl. structured capital (2026)","usd_m":252,"period":"2024-2026","published":"2026","kind":"reported","source":UW},
  {"metric":"revenue","value_orig":"USD 691M","usd_m":691,"period":"FY2025","published":"","kind":"reported","source":UW},
  {"metric":"net_income","value_orig":"USD 176M","usd_m":176,"period":"FY2025","published":"","kind":"reported","source":UW}],
 qualifying_metric="valuation",profitability="profitable",profitability_basis="net income USD 176M in 2025 (Wikipedia)",
 signals=[{"category":"capital","what":"~USD 70M equity round led by Tencent and VR Capital at ~USD 1.5bn","date":"2025-08","status":"confirmed","source":UW},
  {"category":"capital","what":"London Stock Exchange added to candidate venues for planned 2027 IPO","date":"2025-10","status":"confirmed","source":UW},
  {"category":"capital","what":"USD 130M+ strategic investment led by Omani sovereign entities at USD 2.3bn pre-money","date":"2026-03","status":"confirmed","source":UW}],
 fit="21012231",fit_rationale="Profitable unicorn preparing a 2027 international IPO with Gulf sovereign investors; F1 could build its investor-facing brand and bank/card consumer marketing, though operations are Uzbekistan-only.",
 category_conflict="potential: fintech and payments partners on several teams",f1_markets="Abu Dhabi, Qatar, Saudi Arabia (investor geography)",access=("yes","no","mid","CEO (founder), CMO, Chief Strategy Officer"),
 outstanding="press page not opened; marketing head",sources=[US,UW],conf="high",discovery_source=US)
NW="https://en.wikipedia.org/wiki/Navoi_Mining_and_Metallurgical_Company"; NS="https://www.ngmk.uz/en/"
W("main",name="Navoi Mining and Metallurgical Company",website="ngmk.uz",aliases=["NMMC","NGMK","Navoiy MMC"],hq_city="Navoi",hq_country="Uzbekistan",
 sector="Mining & Metals",subsector="gold mining",desc="State-owned Uzbek gold miner operating the Muruntau mine, describing itself as one of the world's four largest gold producers.",
 products="gold, silver, mining machinery (Navoi Machine-Building Plant)",model="B2B",customers="",ownership_type="state-owned",parent_immediate="Ministry of Economy and Finance of Uzbekistan (98%)",
 parent_ultimate="Republic of Uzbekistan",parent_listed="state",minority_investors="State Assets Management Agency (2%)",employees=50000,stores_or_sites="12 deposits, 7 processing plants",
 markets="Uzbekistan production; gold sold internationally",reach="International",route="A",
 fin=[{"metric":"revenue","value_orig":"USD 10.8bn","usd_m":10800,"period":"FY2025","published":"","kind":"reported","source":NS},
  {"metric":"net_income","value_orig":"USD 2,137M","usd_m":2137,"period":"FY2024","published":"2025","kind":"reported","source":NW}],qualifying_metric="revenue",
 profitability="profitable",profitability_basis="64.2% EBITDA margin 2025 (company site); net income USD 2.1bn 2024",
 signals=[{"category":"capital","what":"S&P upgraded NMMC to BB+ stable","date":"2026-11","status":"confirmed","source":NS},
  {"category":"strategic","what":"took part in meeting on developing the Tashkent International Financial Centre; UK delegation visit","date":"2026-11","status":"confirmed","source":NS}],
 distress="fatal workplace accident (tyre explosion, two workers killed) Sep 2026",fit="20001201",
 fit_rationale="One of the world's largest gold producers with international ratings and long-mooted IPO; F1 could build investor and sovereign-brand visibility, but it sells a commodity with little marketing need.",
 category_conflict="none found",access=("no","no","complex","Chairman of the Board, investor relations director"),outstanding="IPO timing; any sports sponsorship",sources=[NS,NW],conf="high",discovery_source="https://www.spot.uz/ru/2025/01/14/top-taxpayers/")
