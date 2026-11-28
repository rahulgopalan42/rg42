import sys; sys.path.insert(0,"scratch_k29")
from rec import *
IA="https://en.wikipedia.org/wiki/Iraqi_Airways"
W("main",name="Iraqi Airways",website="ia.com.iq",aliases=[],hq_city="Baghdad",hq_country="Iraq",sector="Airlines & Air Travel",subsector="state flag carrier",
 desc="State-owned flag carrier of Iraq flying 40 aircraft from Baghdad, Basra and Erbil to about 50 destinations, with Boeing 737 MAX and 787 orders.",
 products="scheduled passenger and Hajj flights",model="B2C",customers="travellers to and from Iraq, diaspora, pilgrims",ownership_type="state-owned",parent_ultimate="Government of Iraq",parent_listed="state",
 stores_or_sites="40 aircraft in service, 18 on order (10 737 MAX 10, 7 787-8)",markets="Iraq; Middle East, Europe (Malmo), South Asia",reach="International",route="C",
 fin=[{"metric":"debt_funding","value_orig":"USD 2bn Citibank loan for aircraft","usd_m":2000,"period":"2015","published":"","kind":"reported","source":IA}],qualifying_metric="alternative indicators",
 alt_indicators=[{"indicator":"fleet of evident scale","evidence":"40 aircraft in service incl. 787 and 777, 18 on order","source":IA},{"indicator":"operations in 3+ countries","evidence":"about 50 destinations across the Middle East, Europe and Asia","source":IA}],
 signals=[],fit="00011211",fit_rationale="Growing state carrier rebuilding international routes with new Boeings; F1 could support a brand reset in Gulf and European markets, but airline is a crowded category and governance is state-run.",
 category_conflict="potential: Qatar Airways (F1 global partner), Emirates, Etihad, Saudia",compliance="Wikipedia categorises it among airlines banned in the EU; state airline",
 f1_markets="Bahrain, Qatar, Saudi Arabia (route network)",access=("no","no","complex","Director General, commercial director"),signals_checked="no",
 outstanding="revenue; EU ban status; any 2025-2026 events",sources=[IA],conf="low",discovery_source="https://en.wikipedia.org/wiki/List_of_companies_of_Iraq")
WT="https://en.wikipedia.org/wiki/Wissotzky_Tea"
W("watch",name="Wissotzky Tea",website="wissotzky-tea.com",aliases=["Wissotzky Group"],hq_city="Tel Aviv",hq_country="Israel",sector="Food & Beverage",subsector="tea",
 desc="Family-owned Israeli tea maker holding about 76% of the Israeli market, with London and US offices and distribution in Europe, Asia and North America.",
 products="tea (incl. Signature Collection), olive oil (Zeta), Elsa's Story",model="B2C",ownership_type="family-owned",parent_ultimate="Seidler family (Shalom Seidler heads the company)",parent_listed="private",
 employees=400,markets="Israel, UK, US, Canada, Australia, Japan, South Korea, Europe",reach="International",
 fit="00011221",fit_rationale="Dominant Israeli tea brand pushing into US mass market; consumer campaigns possible but revenue not found and scale is modest.",
 access=("yes","no","lean","CEO (family), marketing director"),signals_checked="no",outstanding="revenue; company site did not resolve",sources=[WT],conf="low",discovery_source=WT)
