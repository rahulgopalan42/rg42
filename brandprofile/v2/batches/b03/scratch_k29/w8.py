import sys; sys.path.insert(0,"scratch_k29")
from rec import *
Q="https://qaztehna.kz/"
W("main",name="QazTehna",website="qaztehna.kz",aliases=["QazТehna LLP"],hq_city="Kostanay region",hq_country="Kazakhstan",sector="Automotive & Mobility",subsector="bus and commercial vehicle manufacturing",
 desc="Kazakhstan's leading bus maker, assembling Yutong city, tourist and electric buses and special vehicles, with a 68% domestic market share in 2024.",
 products="city, tourist, special and electric buses (Yutong), Howo and Sitrak trucks",model="B2B",customers="city transport operators (Onay), Qarmet fleet",
 ownership_type="privately held group",parent_ultimate="Andrey Lavrentyev, Onay PAY (Vitaly Kan, Olga Nigay, Ilya Kan), Yutong International Trade Pte. Ltd. (per Forbes Kazakhstan)",parent_listed="private",
 minority_investors="Yutong International Trade (subsidiary of listed Yutong Bus)",employees=900,stores_or_sites="40,500 m2 plant; capacity 1,200-1,500 units a year",markets="Kazakhstan",reach="Domestic",route="A",
 fin=kzfin(133.47,17.85),qualifying_metric="revenue",profitability="profitable",profitability_basis="net profit KZT 17.85bn per Forbes Kazakhstan 2025",
 signals=[{"category":"commercial","what":"selected by Qarmet as supplier for bus fleet modernisation","date":"2025-05","status":"confirmed","source":Q},
  {"category":"capital","what":"large investment project incl. first bus body panel stamping workshop in Kazakhstan","date":"2025-06","status":"confirmed","source":Q}],
 fit="10001100",fit_rationale="Domestic bus assembler for municipal buyers; F1 offers little commercial lever beyond corporate image, so fit is weak.",
 access=("yes","no","mid","General director, owners"),outstanding="exports; owner shares",sources=[Q,FS],conf="medium",discovery_source=FS)
K="https://kazazot.kz/en/"
W("main",name="KazAzot",website="kazazot.kz",aliases=["KazAzot JSC"],hq_city="Aktau",hq_country="Kazakhstan",sector="Chemicals & Materials",subsector="ammonia and ammonium nitrate",
 desc="Kazakh producer and exporter of ammonia and ammonium nitrate from its own Mangystau gas field and Aktau plant, selling to 15 countries.",
 products="ammonia, ammonium nitrate fertiliser",model="B2B",customers="agriculture and mining (Kazatomprom, ERG shown as partners)",
 ownership_type="founder-owned",parent_ultimate="Bakharidin Ablazimov (per Forbes Kazakhstan)",parent_listed="private",employees=1230,markets="Kazakhstan, Russia, CIS, Eastern Europe (15 countries)",reach="International",route="B",
 fin=kzfin(66.8,5.96),qualifying_metric="revenue",exception_note="Revenue about USD 140M (KZT 66.8bn) with net profit KZT 5.96bn and exports to 15 countries",
 profitability="profitable",profitability_basis="net profit KZT 5.96bn per Forbes Kazakhstan 2025",signals=[],
 fit="10000101",fit_rationale="Fertiliser exporter with B2B commodity sales; F1 brings little commercial value beyond hospitality for distributors.",
 access=("yes","no","lean","Owner, general director"),outstanding="no 2025-2026 news on site (latest 2024: ammonia-urea complex with Tecnicas Reunidas planned)",sources=[K,FS],conf="medium",discovery_source=FS)
