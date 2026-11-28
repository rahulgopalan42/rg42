import sys; sys.path.insert(0,"scratch_k29")
from rec import *
M="https://en.wikipedia.org/wiki/Mekorot"
W("main",name="Mekorot",website="mekorot.co.il",aliases=["Mekorot Water Company","Israel National Water Company"],hq_city="Tel Aviv",hq_country="Israel",sector="Utilities & Renewable Energy",subsector="national water company",
 desc="State-owned Israeli national water company supplying bulk water and desalination, with water-management contracts and MOUs in Bahrain, Jordan, Azerbaijan, Morocco and beyond.",
 products="bulk water supply, desalination, water infrastructure and consulting abroad",model="B2B",customers="Israeli municipalities and utilities; foreign governments",
 ownership_type="state-owned",parent_ultimate="State of Israel",parent_listed="state",marketing_autonomy="unknown",markets="Israel; projects or agreements in Bahrain, Jordan, Azerbaijan, Morocco, Singapore, France, Argentina, Chile, Italy",
 reach="International",route="A",fin=[{"metric":"operating_budget","value_orig":"invests NIS 1.5-2bn a year; raised over NIS 5bn in bonds since 2019","usd_m":None,"period":"2019-2025","published":"","kind":"reported","source":M}],
 qualifying_metric="documented state backing with commercial mandate (state-owned national water company issuing bonds, investing NIS 1.5-2bn a year)",
 signals=[{"category":"strategic","what":"CEO Amit Lang to leave in December 2025","date":"2025-10","status":"confirmed","source":M}],
 fit="10001100",fit_rationale="State water utility with Gulf and Azerbaijan contracts; F1 could support government-to-government relations in Bahrain or Baku, but commercial marketing need is small.",
 compliance="politically sensitive: Gaza water supply shutdowns reported during the war",access=("no","no","complex","CEO, international business division head"),
 signals_checked="yes",outstanding="revenue figure; company site not opened",sources=[M],conf="medium",discovery_source=M)
Z="https://zcmc.am/en"
W("watch",name="Zangezur Copper Molybdenum Combine",website="zcmc.am",aliases=["ZCMC"],hq_city="Kajaran",hq_country="Armenia",sector="Mining & Metals",subsector="copper and molybdenum mining",
 desc="Armenia's largest copper producer and a top-10 global molybdenum producer, operating the Kajaran deposit with over 4,800 staff.",products="copper and molybdenum concentrates",model="B2B",
 ownership_type="requires verification",parent_listed="requires verification",employees=4800,markets="Armenia production; concentrates sold internationally",reach="International",
 alt_indicators=[{"indicator":"employees","evidence":"over 4,800 employees","source":Z},{"indicator":"industry ranking","evidence":"among top 10 molybdenum producers, 2.2% of global output; first among Armenian taxpayers H1 2026","source":Z}],
 signals=[{"category":"commercial","what":"new digitalisation projects announced","date":"2026-10","status":"confirmed","source":Z}],
 fit="10000101",fit_rationale="Large concentrate producer with Route C indicators, but ownership was not shown on the page I opened, so it stays on watch.",
 access=("unknown","no","mid","General director"),outstanding="ownership (state stake) must be verified before it can move to MAIN; revenue",sources=[Z],conf="medium",discovery_source="https://en.wikipedia.org/wiki/List_of_companies_of_Armenia")
