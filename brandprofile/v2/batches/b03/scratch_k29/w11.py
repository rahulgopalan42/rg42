import sys; sys.path.insert(0,"scratch_k29")
from rec import *
B="https://bayansulu.kz/"
W("main",name="Bayan Sulu",website="bayansulu.kz",aliases=["Баян Сулу JSC"],hq_city="Kostanay",hq_country="Kazakhstan",sector="Food & Beverage",subsector="confectionery manufacturing",
 desc="Kazakhstan's largest confectionery maker, producing over 85,000 tonnes a year of wafers, chocolate, caramel and biscuits, and building a Confectionery Capital complex.",
 products="wafers, chocolate, candies, caramel, marshmallow, biscuits (300+ products)",model="B2C",customers="retail consumers via grocery chains",
 ownership_type="privately held group",parent_immediate="KazFoodProducts LLP (85.06%)",parent_ultimate="Yerlan Baimuratov (ultimate control per Forbes Kazakhstan)",parent_listed="private",
 minority_investors="Timur Sadykov (5%), SPK Tobol (5%)",employees=1390,stores_or_sites="Kostanay factory; Confectionery Capital complex opened Aug 2026",markets="Kazakhstan",reach="Domestic",route="B",
 fin=kzfin(47.3,3.5),qualifying_metric="revenue",exception_note="Revenue about USD 99M (KZT 47.3bn) with net profit KZT 3.5bn, new production complex opened 2026 and football sponsorship",
 profitability="profitable",profitability_basis="net profit KZT 3.5bn per Forbes Kazakhstan 2025",
 sponsorships=[{"rights_holder":"Kazakhstan football (headline only)","sport":"football","designation":"supporter","announced":"2025-09","duration":"","value":"","source":B}],
 signals=[{"category":"marketing","what":"announced support for Kazakhstan football","date":"2025-09","status":"confirmed","source":B},
  {"category":"geographic","what":"opened Confectionery Capital production complex in Kostanay region","date":"2026-08","status":"confirmed","source":B}],
 fit="00001130",fit_rationale="Leading Kazakh sweets brand already backing football; F1 could drive consumer promotions and packaging campaigns domestically, but it lacks international reach.",
 category_conflict="potential: confectionery partners on some teams",access=("yes","no","mid","Chairman, marketing director"),outstanding="exports; brand names",sources=[B,FS],conf="medium",discovery_source=FS)
