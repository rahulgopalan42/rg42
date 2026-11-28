import sys; sys.path.insert(0,"scratch_k29")
from rec import *
for n,w in [("KAZ Minerals","ALREADY DELIVERED - b01"),("Eurasian Resources Group (ERG) and its subsidiaries Kazchrome, SSGPO, Aluminium of Kazakhstan, Kazakhstan Electrolysis Plant, Eurasian Energy Corporation, Shubarkol Komir","ALREADY DELIVERED - b01 as Eurasian Resources Group; subsidiaries left out as part of the delivered group"),
("Azerbaijan Airlines (AZAL)","ALREADY DELIVERED - b01"),("Azersun Holding","ALREADY DELIVERED - b01"),("SOCAR","ALREADY DELIVERED - b01"),("UzAuto Motors","F1 PARTNER - current F1 partner"),
("Uzbekistan Airways","IN MASTER - All New Brands"),("Kazakhstan Temir Zholy","ALREADY DELIVERED - b01"),("Ori Nabiji","ALREADY DELIVERED - b02"),("Omega Group (Georgia)","IN MASTER as Omega (likely different company; left out to be safe)"),
("Manaseer Group","IN MASTER - Capacity To Confirm"),("Nuqul Group","IN MASTER - Capacity To Confirm"),("Middle East Airlines","IN MASTER - Capacity To Confirm"),("SABIS","ALREADY DELIVERED - b02 as SABIS School Network"),
("Dar Al-Handasah","IN MASTER as Sidara"),("Khatib & Alami","IN MASTER - Clay Leads"),("Azadea","IN MASTER"),("Patchi","IN MASTER"),("INDEVCO","IN MASTER"),
("Israel Aerospace Industries","IN MASTER"),("Rafael Advanced Defense Systems","IN MASTER"),("Tnuva","IN MASTER"),("Rapyd","IN MASTER"),("Gong","IN MASTER"),("Papaya Global","IN MASTER"),("Snyk","IN MASTER"),
("Cato Networks","F1 PARTNER - Alpine"),("Armis","IN MASTER"),("Fireblocks","IN MASTER"),("Dream Security","IN MASTER"),("Cyera","IN MASTER"),("eToro","F1 PARTNER - Alpine"),("Moon Active","ALREADY DELIVERED - b02"),
("Iscar","ALREADY DELIVERED - b01"),("Electra Group","IN MASTER as Electra"),("Super-Pharm","IN MASTER"),("Keter Group","IN MASTER"),("Mobileye","IN MASTER"),("Matrix","F1 PARTNER - Alpine")]:
    D(n,w)
W("main",name="Kazakhmys",website="kazakhmys.kz",aliases=["Kazakhmys Corporation","Қазақмыс"],hq_city="Zhezkazgan / Ulytau region",hq_country="Kazakhstan",
 sector="Mining & Metals",subsector="copper mining and smelting",desc="Vertically integrated Kazakh copper miner and smelter, the country's largest copper producer, with mines, concentrators, Balkhash smelter, coal and power assets.",
 products="copper cathode and concentrate, precious metals, coal, power",model="B2B",customers="commodity traders and industrial buyers (Mercuria cooperation 2026)",
 ownership_type="founder-owned",parent_immediate="",parent_ultimate="Vladimir Kim (70%), Eduard Ogay (30%)",parent_listed="private",
 employees=31277,stores_or_sites="Zhezkazgan, Balkhash smelter, Karaganda and Ulytau regions, Nurkazgan, Borly coal",markets="Kazakhstan production; copper sold on international commodity markets",
 reach="International",route="A",fin=kzfin(1433,63.6),qualifying_metric="revenue",profitability="profitable",profitability_basis="net profit KZT 63.6bn per Forbes Kazakhstan 2025",
 signals=[{"category":"commercial","what":"expanded strategic cooperation with Mercuria; Mercuria regional office opened in Astana","date":"2026-05","status":"confirmed","source":"https://www.kazakhmys.kz/en/news"},
          {"category":"capital","what":"investment in developing Zhomart and Zhylandy mines","date":"2026-02","status":"confirmed","source":"https://www.kazakhmys.kz/en/news"}],
 fit="20021112",fit_rationale="Kazakhstan's largest copper producer selling into global metals markets; F1 hospitality could serve trader and offtake relationships, and copper ties to EV and electrification narratives, but consumer value is low.",
 category_conflict="none found",f1_markets="none in Kazakhstan; customers in Europe, China, Middle East",access=("yes","no","complex","CEO, director of corporate communications"),
 outstanding="current CEO and marketing structure; export customer list; sponsorship history",sources=["https://www.kazakhmys.kz/en","https://www.kazakhmys.kz/en/news",FS],
 conf="medium",discovery_source=FS)
