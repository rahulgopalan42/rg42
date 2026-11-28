import sys; sys.path.insert(0,"scratch_k29")
from rec import *
R="https://en.wikipedia.org/wiki/Azerbaijan_Railways"
W("main",name="Azerbaijan Railways",website="ady.az",aliases=["ADY","ADY Express","ADY Container"],hq_city="Baku",hq_country="Azerbaijan",sector="Logistics & Transportation",subsector="national railway and Middle Corridor freight",
 desc="State-owned national railway of Azerbaijan, a key link of the Middle Corridor and Baku-Tbilisi-Kars line carrying China-Europe freight.",
 products="rail freight and passenger services, container logistics (ADY Container), forwarding (ADY Express)",model="Hybrid",customers="freight forwarders and shippers on China-Turkey-EU routes",
 ownership_type="state-owned",parent_immediate="AZCON Holding",parent_ultimate="Republic of Azerbaijan",parent_listed="state",employees=17000,stores_or_sites="2,918 km network, 176 stations",
 markets="Azerbaijan; transit corridors to Georgia, Turkey, Central Asia and China",reach="International",route="C",
 fin=[{"metric":"operating_budget","value_orig":"operating income AZN 323.4M","usd_m":None,"period":"FY2024","published":"","kind":"reported","source":R}],qualifying_metric="alternative indicators",
 alt_indicators=[{"indicator":"employees","evidence":"more than 17,000","source":R},{"indicator":"network of evident scale","evidence":"2,918 km of track, 176 stations, Middle Corridor and BTK operations","source":R}],
 signals=[{"category":"geographic","what":"rail line through Nakhchivan to Turkey under construction","date":"","status":"inferred","source":R}],
 fit="20101201",fit_rationale="Middle Corridor rail operator courting international shippers; Baku Grand Prix hospitality could serve logistics and government partners, though F1 freight itself is air and sea.",
 category_conflict="potential: DHL (F1 logistics partner)",f1_markets="Azerbaijan (Baku Grand Prix), Turkey (corridor)",access=("no","no","complex","Chairman, commercial director"),
 compliance="Azerbaijan Grand Prix deal not found on the Wikipedia page; circuit partners page not available",outstanding="revenue; any Baku Grand Prix deal",signals_checked="no",sources=[R],conf="medium",discovery_source="https://en.wikipedia.org/wiki/List_of_companies_of_Azerbaijan")
