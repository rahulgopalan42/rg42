import sys; sys.path.insert(0,"scratch_k29")
from rec import *
SW="https://en.wikipedia.org/wiki/Silk_Way_West_Airlines"
W("main",name="Silk Way West Airlines",website="silkwaywest.com",aliases=["Silk Way Group","Silk Way Airlines","SW Technics"],hq_city="Baku",hq_country="Azerbaijan",sector="Logistics & Transportation",subsector="air cargo airline",
 desc="Baku-based all-cargo airline of the Silk Way Group flying Boeing 747 and 777 freighters to about 45 destinations across Europe, Asia and the Americas.",
 products="scheduled and charter air freight, outsize and special cargo",model="B2B",customers="freight forwarders, logistics integrators, shippers",
 ownership_type="subsidiary of private group",parent_immediate="Silk Way Group",parent_ultimate="Silk Way Group (beneficial owners not stated on page)",parent_listed="private",
 stores_or_sites="13 freighters in service (747-400F, 747-8F, 777F), 9 on order (A350F, 777-8F, 777F)",markets="Europe, CIS, Middle East, Central and East Asia, North and South America",reach="Global",route="A",
 fin=[{"metric":"revenue","value_orig":"about USD 1.14bn","usd_m":1140,"period":"FY2023","published":"","kind":"reported","source":SW},
  {"metric":"net_income","value_orig":"about USD 48M","usd_m":48,"period":"FY2023","published":"","kind":"reported","source":SW}],qualifying_metric="revenue",
 profitability="profitable",profitability_basis="net income about USD 48M in 2023 (Wikipedia)",
 signals=[{"category":"capital","what":"exercised purchase option for two Airbus A350F freighters","date":"2025-11","status":"confirmed","source":SW}],
 fit="22213211",fit_rationale="Global 747/777 freighter operator from the home of the Baku Grand Prix; F1 moves race freight by air, so hospitality and logistics credibility with forwarders are directly relevant.",
 customer_overlap="",category_conflict="potential: DHL is F1's global logistics partner",f1_markets="Azerbaijan, plus Europe, Asia and Americas on its network",
 compliance="Azerbaijan Grand Prix deal: none found on the page; beneficial ownership should be checked (Azerbaijani private group)",
 access=("unknown","no","mid","President of Silk Way Group, commercial director"),signals_checked="no",outstanding="company site 404; beneficial owners; Baku GP partner list",sources=[SW],conf="medium",discovery_source="https://en.wikipedia.org/wiki/List_of_companies_of_Azerbaijan")
