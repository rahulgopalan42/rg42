import sys; sys.path.insert(0,"scratch_k29")
from rec import *
H="https://helios.kz/"
W("main",name="Helios",website="helios.kz",aliases=["Гелиос","Helios LLP"],hq_city="Almaty",hq_country="Kazakhstan",sector="Oil, Gas & Fuels",subsector="fuel station chain",
 desc="Nationwide Kazakh fuel retail chain with more than 277 filling stations across all major regions and a loyalty bonus card.",products="fuel retail, convenience retail, bonus card",model="B2C",customers="motorists, corporate fuel-card clients",
 ownership_type="family-owned",parent_ultimate="Sarsenov family (per Forbes Kazakhstan)",parent_listed="private",employees=4492,stores_or_sites="more than 277 filling stations",
 markets="Kazakhstan (15+ regions)",reach="Domestic",route="A",fin=kzfin(136.9),qualifying_metric="revenue",
 signals=[{"category":"marketing","what":"open fuel-quality check event in Astana","date":"2026-10","status":"confirmed","source":H},
  {"category":"commercial","what":"station Helios No. 10 in Almaty reopened after reconstruction","date":"2026-06","status":"confirmed","source":H}],
 fit="00011130",fit_rationale="Motorist-facing fuel chain running co-promotions with Pepsi and energy drinks; F1 could power loyalty and fuel-quality marketing domestically, though it has no international footprint.",
 category_conflict="potential: fuel partners (Shell, Aramco, Petronas) at team level",access=("yes","no","lean","Owner family, marketing director"),
 outstanding="check.py POSSIBLE match was Helios Kliniken (unrelated German hospitals)",sources=[H,FS],conf="medium",discovery_source=FS)
O="https://orbis.kz/"
W("main",name="Orbis Auto",website="orbis.kz",aliases=["Orbis Kazakhstan (holding)"],hq_city="Almaty",hq_country="Kazakhstan",sector="Automotive & Mobility",subsector="car dealer group",
 desc="Automotive retail division of the diversified Almaty holding Orbis Kazakhstan, one of Kazakhstan's largest car dealer groups by revenue.",products="car retail and service",model="B2C",customers="car buyers",
 ownership_type="family-owned",parent_immediate="Orbis Kazakhstan",parent_ultimate="Farrukh and Sukhrab Makhmudov (per Forbes Kazakhstan)",parent_listed="private",employees=2747,
 markets="Kazakhstan",reach="Domestic",route="A",fin=kzfin(448.05),qualifying_metric="revenue",
 signals=[{"category":"commercial","what":"agreement signed with Volkswagen China (17 July, year not shown)","date":"","status":"inferred","source":O},
  {"category":"marketing","what":"opened an engineering laboratory at ALT University (27 February, year not shown)","date":"","status":"inferred","source":O}],
 fit="10011221",fit_rationale="Large car retailer with Volkswagen China ties; F1 would suit dealer events and automotive positioning, though it is purely domestic.",
 category_conflict="potential: car brands sold may conflict with team engine partners",access=("yes","no","mid","Owners, Orbis Auto CEO, marketing director"),
 outstanding="brands represented; news dates",sources=[O,FS],conf="medium",discovery_source=FS)
FG="https://forbes.ge/en/georgia-s-100-richest-entrepreneurs/"; M="https://meama.com/en"
W("watch",name="Meama",website="meama.com",aliases=["MEAMA"],hq_city="Tbilisi",hq_country="Georgia",sector="Food & Beverage",subsector="coffee capsules and machines",
 desc="Georgian maker of capsule drinks and multi-format machines with 80+ drinks, selling in Georgia, Germany and Austria and preparing wider launches.",
 products="Multicapsule and espresso capsules, Versatile machine, Meama Collect cafes",model="Hybrid",customers="consumers, offices, hotels, cafes",
 ownership_type="founder-owned",parent_ultimate="Suliko Varsemashvili (85% per Forbes Georgia)",parent_listed="private",markets="Georgia, Germany, Austria",
 expansion_markets="coming soon: Switzerland, France, Spain, Italy, UK, Ireland, US, Poland, Czechia, UAE, Saudi Arabia, Jordan",reach="Regional",
 signals=[{"category":"geographic","what":"site lists Germany and Austria live and 12 more markets coming soon","date":"2026","status":"confirmed","source":M}],
 fit="00011331",fit_rationale="Design-led capsule coffee brand launching across Europe, the Gulf and the US; F1 paddock coffee and consumer campaigns would fit, but no route shown.",
 category_conflict="potential: coffee partners on some teams",access=("yes","no","lean","Founder, CMO"),outstanding="revenue, funding, employees",sources=[M,FG],conf="medium",discovery_source=FG)
U="https://www.ucom.am/en/about-us"
W("watch",name="Ucom",website="ucom.am",aliases=["Orange Armenia (acquired 2015)"],hq_city="Yerevan",hq_country="Armenia",sector="Telecommunications",subsector="converged telecom operator",
 desc="Armenian converged operator offering fixed and mobile internet, 5G, TV and voice, which bought Orange Armenia in 2015.",products="mobile, fixed broadband, TV (Uplay), voice",model="B2C",
 ownership_type="requires verification",parent_listed="requires verification",markets="Armenia (5G in 47 cities)",reach="Domestic",
 sponsorships=[{"rights_holder":"National Olympic Committee of Armenia","sport":"multi-sport","designation":"supporter","announced":"2021","duration":"","value":"","source":U}],
 signals=[{"category":"commercial","what":"launched Uplay TV and media platform; 5G rolled out to 47 cities","date":"2025","status":"confirmed","source":U}],
 fit="00001220",fit_rationale="Domestic Armenian operator with Olympic sponsorship history; small market limits F1 value; no financial route found.",category_conflict="potential: telecom partners on teams",
 access=("unknown","no","lean","CEO, marketing director"),outstanding="owners, revenue, subscribers",sources=[U],conf="low",discovery_source="https://en.wikipedia.org/wiki/List_of_companies_of_Armenia")
D("PASHA Holding, PASHA Bank, Kapital Bank (PASHA group)","check.py POSSIBLE: PASHA Real Estate is Azerbaijan Grand Prix Event Supporter 2026; PASHA Bank reported partly listed on Baku Stock Exchange since June 2026 (per dups_q21_assess); politically exposed ownership; left out")
