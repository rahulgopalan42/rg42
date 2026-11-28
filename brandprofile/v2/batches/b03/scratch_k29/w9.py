import sys; sys.path.insert(0,"scratch_k29")
from rec import *
G="https://www.qazaqgaz.kz/en"
W("main",name="QazaqGaz",website="qazaqgaz.kz",aliases=["National Company QazaqGaz","formerly KazTransGas"],hq_city="Astana",hq_country="Kazakhstan",sector="Oil, Gas & Fuels",subsector="national gas transmission, distribution and processing",
 desc="Kazakhstan's national gas company, running main pipelines, distribution networks, storage and new gas processing plants and representing the state in gas markets.",
 products="gas transmission, distribution, storage, processing (Karachaganak and Kashagan plants under construction), gas trading",model="B2B",customers="2.6 million consumers; domestic and foreign gas buyers",
 ownership_type="state-owned",parent_ultimate="Republic of Kazakhstan (national company representing state interests, per its site; holding entity not shown on page)",parent_listed="state",
 markets="Kazakhstan and foreign gas markets",reach="International",route="C",
 fin=[{"metric":"debt_funding","value_orig":"USD 700M guaranteed bonds prospectus","usd_m":700,"period":"2026","published":"2026","kind":"reported","source":G}],qualifying_metric="alternative indicators",
 alt_indicators=[{"indicator":"infrastructure of evident scale","evidence":"77,000 km distribution networks, 56 compressor stations, 3 underground storage sites, 2.6 million consumers","source":G},
  {"indicator":"major contracts","evidence":"EPC contracts for new gas processing plants at Karachaganak and Kashagan (Nov 2026)","source":G},
  {"indicator":"credit ratings","evidence":"Moody's Baa2, Fitch and S&P BB+","source":G}],
 signals=[{"category":"commercial","what":"EPCC contract signed for new gas processing plant at Kashagan","date":"2026-11","status":"confirmed","source":G},
  {"category":"commercial","what":"EPC contract signed for new gas processing plant at Karachaganak","date":"2026-11","status":"confirmed","source":G},
  {"category":"capital","what":"USD 700M guaranteed bond prospectus","date":"2026","status":"confirmed","source":G}],
 fit="20001101",fit_rationale="National gas champion contracting large EPC projects with international partners; F1 hospitality could serve partner and investor relations, but it has no consumer brand need.",
 category_conflict="potential: energy partners (Aramco, Shell, Petronas) in F1",access=("no","no","complex","Chairman of the Management Board, communications director"),
 outstanding="revenue and holding structure",sources=[G],conf="medium",discovery_source=G)
