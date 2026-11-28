import sys; sys.path.insert(0,"scratch_k29")
from rec import *
C="https://www.caepco.kz/en/"
W("main",name="Central-Asian Electric Power Corporation",website="caepco.kz",aliases=["CAEPCO","Pavlodarenergo","Sevkazenergo","Akmola Electricity Distribution Company"],hq_city="Astana",hq_country="Kazakhstan",
 sector="Utilities & Renewable Energy",subsector="power and heat generation and distribution",desc="Kazakhstan's largest private power generator by installed capacity, supplying electricity and heat to over 2 million consumers in the north.",
 products="electricity and heat generation, power distribution grids, renewable generation (TSATEK Green Energy)",model="Hybrid",customers="more than 2 million consumers",
 ownership_type="founder-owned",parent_ultimate="Alexander Klebanov (47.1%), Sergey Kan (47.1%) per Forbes Kazakhstan",parent_listed="private",employees=9008,
 stores_or_sites="1,306 MW electric capacity; 48,200 km of power lines; CHP plants in Pavlodar and Petropavlovsk",markets="North Kazakhstan, Akmola and Pavlodar regions",reach="Domestic",route="A",
 fin=kzfin(291.72,17.42),qualifying_metric="revenue",profitability="profitable",profitability_basis="net profit KZT 17.42bn per Forbes Kazakhstan 2025",
 signals=[{"category":"commercial","what":"subsidiary Sevkazenergo REK investing over KZT 2.9bn in grid modernisation (undated item on site)","date":"2026","status":"inferred","source":C}],
 fit="10000100",fit_rationale="Regional utility in northern Kazakhstan with no international customers; F1 offers little beyond corporate image, so fit is weak despite size.",
 access=("unknown","no","mid","Chairman, corporate communications director"),outstanding="news items undated",sources=[C,FS],conf="medium",discovery_source=FS)
T="https://www.ttc.kz/en/"
W("main",name="Transtelecom",website="ttc.kz",aliases=["Transtelecom JSC","TTC"],hq_city="Astana",hq_country="Kazakhstan",sector="Telecommunications",subsector="fibre backbone, IT and system integration",
 desc="Kazakh telecom and IT integrator, spun off from the national railway, running a 15,000 km fibre backbone and data centres and railway automation.",
 products="fibre transit, data centres, SAP services, cybersecurity, railway automation, home internet",model="B2B",customers="KTZ, Kazatomprom, Kazpost, state pension fund",
 ownership_type="privately held group",parent_ultimate="Galimzhan Yessenov and Dmitry Pokupatelev (75% together via Unit Telecom); KTZ (25%)",parent_listed="private",minority_investors="Kazakhstan Temir Zholy (25%)",
 employees=2764,markets="Kazakhstan; international data transit",reach="Domestic",route="A",fin=kzfin(88.84,18.35),qualifying_metric="revenue",profitability="profitable",profitability_basis="net profit KZT 18.35bn per Forbes Kazakhstan 2025",
 signals=[{"category":"commercial","what":"will provide infrastructure for AWS Outposts in Kazakhstan","date":"2026-10","status":"confirmed","source":T},
  {"category":"commercial","what":"presented Starlink-based digital infrastructure for passenger trains","date":"2026-10","status":"confirmed","source":T},
  {"category":"capital","what":"planned early partial bond buyback","date":"2026-11","status":"confirmed","source":T}],
 fit="20100101",fit_rationale="B2B telecom and IT integrator with AWS and railway projects; limited F1 relevance beyond enterprise hospitality, domestic only.",category_conflict="potential: telecom and cloud partners on teams",
 access=("unknown","no","mid","CEO, commercial director"),sources=[T,FS],conf="medium",discovery_source=FS)
A="https://www.atasu.kz/en/"
W("main",name="Atasu Group",website="atasu.kz",aliases=[],hq_city="Almaty",hq_country="Kazakhstan",sector="Logistics & Transportation",subsector="China-Europe rail and multimodal freight",
 desc="Kazakh freight forwarder and logistics group running rail, container, road and air freight between China, Kazakhstan and Europe with own terminals.",
 products="rail and container freight, multimodal and road transport, customs, terminals at Dostyk, Zhetysu and Burundai",model="B2B",customers="partners shown include Maersk, Rhenus, Shandong Port",
 ownership_type="founder-owned",parent_ultimate="Marat Zhuman (founder)",parent_listed="private",employees=2500,stores_or_sites="own railcars, containers and trucks; terminals at Dostyk, Zhetysu, Burundai",
 markets="China, Kazakhstan, Central Asia, Europe, Russia",reach="International",route="A",fin=kzfin(67.78,7.5),qualifying_metric="revenue",profitability="profitable",profitability_basis="net profit KZT 7.5bn per Forbes Kazakhstan 2025",
 signals=[],fit="22001101",fit_rationale="Eurasian rail freight specialist connecting China and Europe; F1 freight is handled by DHL, so only B2B hospitality value, modest brand need.",
 category_conflict="potential: DHL (F1 global logistics partner)",access=("yes","no","lean","Founder, commercial director"),outstanding="news items undated on site",sources=[A,FS],conf="medium",discovery_source=FS)
S="https://www.sulpak.kz/"
W("main",name="Sulpak",website="sulpak.kz",aliases=["Arena S"],hq_city="Almaty",hq_country="Kazakhstan",sector="Retail & E-commerce",subsector="consumer electronics retail",
 desc="Kazakh consumer electronics and appliance retail chain operated by Arena S, a member of the European Euronics buying group.",products="electronics, appliances, online store, corporate and wholesale sales",model="B2C",customers="retail consumers, corporate and government buyers",
 ownership_type="founder-owned",parent_immediate="Arena S LLP",parent_ultimate="Almas Sultangaziyev and Igor Yakovlev per Forbes Kazakhstan",parent_listed="private",employees=3700,
 markets="Kazakhstan",reach="Domestic",route="A",fin=kzfin(331.7),qualifying_metric="revenue",
 signals=[{"category":"commercial","what":"joined Euronics International (date not shown)","date":"","status":"inferred","source":S}],
 fit="00001120",fit_rationale="Domestic electronics retailer able to run consumer promotions with brands such as Samsung or LG; no international reach.",
 compliance="one shareholder named by Forbes as a Russian citizen (Igor Yakovlev); company is Kazakh",access=("yes","no","lean","Owner, marketing director"),
 signals_checked="no",outstanding="news page not found; store count",sources=[S,FS],conf="medium",discovery_source=FS)
