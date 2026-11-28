import sys; sys.path.insert(0,"scratch_k29")
from rec import *
FA="https://forbes.kz/articles/75-krupneyshih-chastnyh-kompaniy-kazahstana-2025-0c8cc0"
NO="company newsroom not opened (sites blocked or unreachable in this session); signals taken from the Forbes Kazakhstan 2025 profile"
def K(name,site,aliases,city,sector,sub,desc,products,model,owner,otype,emp,markets,reach,rev,ni,fitc,rat,sig=None,route="A",exc="",prof=None,extra=None,conflict="none found",acc=("yes","no","mid","Owner, CEO, marketing director"),out="",kind="main",period="FY2024",estimated=False):
    f=kzfin(rev,ni,period)
    if estimated: f[0]["kind"]="estimated"
    p,pb=("unknown","")
    if ni is not None:
        p=("profitable" if ni>0 else "loss-making"); pb=f"net {'profit' if ni>0 else 'loss'} KZT {abs(ni)}bn per Forbes Kazakhstan 2025"
    kw=dict(name=name,website=site,aliases=aliases,hq_city=city,hq_country="Kazakhstan",sector=sector,subsector=sub,desc=desc,products=products,model=model,
      ownership_type=otype,parent_ultimate=owner,parent_listed="private",employees=emp,markets=markets,reach=reach,route=route,fin=f,qualifying_metric="revenue",exception_note=exc,
      profitability=p,profitability_basis=pb,signals=sig or [],fit=fitc,fit_rationale=rat,category_conflict=conflict,access=acc,signals_checked="no",
      outstanding=(NO+("; "+out if out else "")),sources=[FA,FS],conf="medium",discovery_source=FS)
    if extra: kw.update(extra)
    W(kind,**kw)
s=lambda c,w,d: {"category":c,"what":w,"date":d,"status":"confirmed","source":FA}
K("RG Brands","",[],"Almaty","Food & Beverage","juices, soft drinks, water, dairy, tea","Kazakh food and drinks group with plants in Almaty, Almaty region and Kostanay making juices, soft drinks, water, milk and tea.",
  "juices, soft drinks, bottled water, milk, packaged tea","B2C","Kairat Mazhibayev via RG Brands Holding Limited (Dubai entity)","founder-owned",3520,"Kazakhstan","Domestic",196,21.1,"00001120",
  "Leading Kazakh FMCG drinks maker; F1 could support on-pack and retail promotions, but it has no international market.",out="brand list and licences not verified")
K("Technodom","technodom.kz",["Technodom Operator"],"Almaty","Retail & E-commerce","consumer electronics retail","Kazakh electronics and appliance retailer since 2002 with 63 stores and 66 pickup points in 28 cities.",
  "electronics, appliances, online sales","B2C","Eduard Kim via TD Retail B.V.","founder-owned",3933,"Kazakhstan (28 cities)","Domestic",232.19,0.387,"00001120",
  "Large domestic electronics retailer with brand co-marketing (Samsung, LG promotions on its site); F1 consumer promotions possible, domestic only.",out="whether any shares are listed not confirmed")
K("Mechta","mechta.kz",["Mechta Market"],"Astana","Retail & E-commerce","consumer electronics retail","Astana-based electronics and appliance chain with 87 stores in 51 cities and over 20,000 products, plus B2B and wholesale units.",
  "electronics, appliances, B2B and wholesale","B2C","Erem Arutyunyan, Yuri Gotzelig, Rima Usoltseva and two LLPs","founder-owned",2822,"Kazakhstan (51 cities)","Domestic",261.1,6.32,"00001120",
  "Nationwide electronics chain able to run consumer promotions; no international reach, so F1 value is mainly domestic activation.")
K("Railways Systems KZ","",["RSKZ"],"Ekibastuz","Industrial Machinery & Equipment","rail equipment and wagons","Kazakh rail machinery group with eight plants in Ekibastuz and Petropavlovsk making track components, wheelsets and passenger and freight wagons.",
  "track components, wheelsets, passenger and freight wagons, forgings, steel (plant under construction)","B2B","Sergey Pavlinger","founder-owned",3107,"Kazakhstan","Domestic",262.6,None,"10100101",
  "Rail engineering group building a 1 Mt steel plant; F1 has limited relevance beyond engineering credentials and B2B hospitality.",
  sig=[s("capital","began building a steel plant in Ekibastuz (planned 1 million tonnes a year)","2024-12"),s("commercial","launched forging-and-tyre complex","2025-04")])
K("Prima Distribution","",[],"Almaty","Consumer Products","FMCG distribution","Kazakh distributor of food and household chemicals with branches in 34 cities reaching 38,000+ outlets, with a hub in Vilnius.",
  "distribution of food and household products (55,000+ SKUs), logistics","B2B","Alexander Garber, Roman Tikhomirov, Elina Pugach","founder-owned",4927,"Kazakhstan; logistics hub in Vilnius (Lithuania)","Regional",231.8,None,"11001110",
  "FMCG distributor whose principals include global brands; F1 hospitality could serve supplier relationships, limited own-brand need.",estimated=True,out="revenue is a Forbes estimate")
K("PetroRetail (Qazaq Oil)","",["Qazaq Oil","formerly KMG-Retail"],"Astana","Oil, Gas & Fuels","fuel station chain","Successor to KMG-Retail operating over 370 owned and partner filling stations under the Qazaq Oil brand, with depots and roadside hotels.",
  "fuel retail, oil depots, Keruen Inn roadside hotels","B2C","Timur Kulibayev and Raushan Sagdiyeva (via Joint Technologies), Daniyar Abulgazin and Baurzhan Toibazarov (via Prime Case), Dauyl Domatov (via Qazoil Company)","privately held group",4560,
  "Kazakhstan","Domestic",220.7,None,"00011130","Qazaq Oil is a national fuel brand for motorists; F1 could support fuel and loyalty marketing, though domestic only.",
  sig=[s("commercial","opened first roadside hotel Keruen Inn, four more planned","2025-09")],estimated=True,conflict="potential: fuel partners at team level",
  extra={"compliance":"shareholders include Timur Kulibayev, son-in-law of Kazakhstan's former president (politically exposed person): check"},out="revenue is a Forbes estimate")
K("Galanz Bottlers","",[],"Almaty","Food & Beverage","soft drinks and water","Kazakh soft drinks producer founded in 1998 with three sites, making Maxi tea, Garden, Happy, Lime Time and Sevens water.",
  "iced tea, juices, soft drinks, bottled water","B2C","Tursengali Alaguzov (majority)","founder-owned",1010,"Kazakhstan","Domestic",64.55,17.3,"00001120",
  "Profitable drinks brand owner building a second Almaty plant; F1 could fuel on-pack promotions domestically.",route="B",exc="Revenue about USD 136M with net profit KZT 17.3bn (27% net margin) and a second plant under construction",
  sig=[s("geographic","second Almaty plant under construction","2025")])
K("Aitas KZ","",["Aitas"],"Astana","Agriculture & Agribusiness","poultry and meat processing","Kazakh agro-holding with poultry plants in Makinsk and Ust-Kamenogorsk, a breeding plant and meat distribution, building new plants.",
  "poultry meat, meat processing, breeding","B2C","Serik Tolukpayev","founder-owned",4424,"Kazakhstan","Domestic",129.74,21.92,"00001020",
  "Domestic meat producer expanding plants; F1 offers little relevant audience.",sig=[s("geographic","announced a 50,000 t/year meat plant in Shymkent and Almaty poultry plant under construction","2025")])
K("Integra Construction KZ","",[],"Almaty","Construction & Engineering","railway and infrastructure construction","Major Kazakh railway builder also active in roads, gas processing and power, including 836 km of second tracks Dostyk-Moiynty.",
  "railway construction, roads, gas processing and power plant construction","B2B","Shakhmurat Mutalip (founder)","founder-owned",2842,"Kazakhstan","Domestic",418.8,35.43,"10000101",
  "Infrastructure contractor for state rail projects; F1 has little commercial role for it.",out="company site is a hosting placeholder")
K("Qazaq Stroy","",[],"Almaty","Construction & Engineering","construction group","Kazakh construction group founded in 2003 with over 4.8 million m2 built across 55 projects and design and management arms.",
  "general contracting, design, development management","B2B","Nurlan Artykbayev (founder)","founder-owned",1957,"Kazakhstan","Domestic",347.01,50.79,"10000101",
  "Profitable domestic contractor; F1 hospitality could serve clients but brand need is low.")
K("Bazis","bazis.kz",["BAZIS-A"],"Almaty","Construction & Engineering","construction and development","Kazakh construction group founded in 1991 working in Kazakhstan, Uzbekistan and Russia, delivering about 400,000 m2 a year.",
  "residential and industrial construction, dams, power plants","Hybrid","Pavel Belovich","founder-owned",3769,"Kazakhstan, Uzbekistan, Russia","Regional",316.80,None,"10000101",
  "Contractor and developer with regional work; low F1 relevance.",estimated=True,extra={"compliance":"operations in Russia: check sanctions exposure"},out="revenue is a Forbes estimate")
K("Kainar-AKB","",[],"Taldykorgan","Automotive & Mobility","automotive batteries","Kazakh battery maker in Taldykorgan producing over 3 million units a year in 50+ types, exporting to Russia, Kyrgyzstan and Azerbaijan.",
  "starter and industrial batteries","B2B","Yerbol and Amina Azhmagambetov","family-owned",1254,"Kazakhstan, Russia, Kyrgyzstan, Azerbaijan","Regional",61.79,1.61,"10111121",
  "Automotive battery maker with exports and a new industrial line; F1 suits its automotive product story, though scale is modest.",route="B",
  exc="Revenue about USD 130M (+16% in 2024) with profit up 34% and a KZT 10bn third production line",sig=[s("capital","announced third industrial battery line (KZT 10bn investment)","2025-10")])
K("Kazphosphate","kazphosphate.kz",["Kazfosfat"],"Taraz","Chemicals & Materials","phosphate mining and fertilisers","Kazakh phosphate miner and fertiliser producer with plants in Taraz, Shymkent and Stepnogorsk; exports are 68.7% of revenue.",
  "phosphate rock, fertilisers, phosphorus products","B2B","KP Fertilizers (50%), Kazakhmys Resources (40%), Nurlanov family (10%)","privately held group",3828,"Kazakhstan; exports 68.7% of revenue","International",120.8,-33.2,"10000101",
  "Export-led fertiliser producer; F1 offers B2B hospitality only.",extra={"distress":"net loss KZT 33.2bn in 2024; revenue down 5.9%"})
K("Eastcomtrans","",["Istkomtrans","ECT"],"Almaty","Logistics & Transportation","rail wagon operator and terminals","Kazakh rolling-stock operator with 11,000+ wagons, transshipment at Aktau port and Dostyk and branches in Russia, China and Uzbekistan.",
  "wagon leasing and operation, terminals, logistics hub","B2B","Marat Sarsenov, Steinhardt Holding N.V.","founder-owned",193,"Kazakhstan, Russia, China, Uzbekistan","International",87.1,None,"11001101",
  "Rail logistics operator opening in China; F1 offers B2B hospitality value only.",estimated=True,sig=[s("geographic","opened ECT China office in Qingdao","2025")],extra={"compliance":"branches in Russia: check sanctions exposure"},out="revenue is a Forbes estimate")
K("KazPetroDrilling","kpd.kz",[],"Aktau","Oil, Gas & Fuels","oilfield drilling and well services","Kazakh oilfield services firm offering drilling, workovers, well abandonment and fracking in Mangystau and West Kazakhstan.",
  "drilling, workover, fracking, well abandonment","B2B","Gaidar Adamsopiev (85%), Balzhanov family (15%)","founder-owned",3768,"Kazakhstan","Domestic",209.2,3.6,"10000101","Domestic oilfield services; little reason for F1.")
K("Caspiy Neft","",["Kaspiy Neft","Caspian Oil"],"Atyrau","Oil, Gas & Fuels","oil production","Kazakh oil producer on the Airankol field in Atyrau region with 30.9 million barrels of proven reserves and 830,000 t output in 2024.",
  "crude oil","B2B","Timur Kulibayev via Joint Resources","founder-owned",282,"Kazakhstan","Domestic",167.57,33.55,"10000001","Upstream oil producer without a consumer brand; minimal F1 fit.",
  extra={"compliance":"owner Timur Kulibayev is a politically exposed person: check"})
K("Kazakhstan Utility Systems","",["KKS","Kazakhstanskie Kommunalnye Sistemy"],"Almaty","Utilities & Renewable Energy","heat and power","Kazakh heat and power group running CHPs in Karaganda and Ust-Kamenogorsk, utilities in four regions and the Zhuzimdyk wind farm.",
  "electricity, heat, wind power","B2C","Magda Idrisova and Zharmukhamed Appaz (wife and son of Dinmukhamet Idrisov)","family-owned",8788,"Kazakhstan","Domestic",328.6,38.9,"00000101","Regional utility; F1 adds little.")
K("Imstalcon","",[],"Almaty","Construction & Engineering","construction and steel structures","Kazakh construction and steel-structures firm founded in 1995 with six plants and work in over half of the country's major cities.",
  "construction, steel structures","B2B","Mikhail Konovalov via AvtoTekhCentr-Asia (95%)","founder-owned",4000,"Kazakhstan","Domestic",113.67,3.74,"10000101","Domestic contractor; low F1 relevance.",route="B",
  exc="Revenue about USD 239M? no: KZT 113.67bn is about USD 239M",out="")
K("Mercury Properties","",[],"Almaty","Real Estate","commercial real estate","Kazakh commercial real estate holding with 50+ malls, business centres, hotels and warehouses in six cities and over 1 million m2.",
  "malls, offices, hotels, warehouses","B2B","Timur and Dinara Kulibayev","family-owned",1731,"Kazakhstan","Domestic",80.2,None,"10011010","Mall and hotel owner could host F1 fan activations, domestic only.",
  extra={"compliance":"beneficiaries Timur and Dinara Kulibayev are politically exposed persons: check"})
K("AgromashHolding KZ","",[],"Kostanay","Industrial Machinery & Equipment","agricultural machinery","Kazakh farm machinery maker assembling combines and tractors under Essil, Lovol, Kirovets and Deutz-Fahr, with an Amazone agreement.",
  "combines, tractors, farm equipment","B2B","Andrei Lavrentyev (55.05%), Alexander Lavrentyev (25%), others","family-owned",636,"Kazakhstan","Domestic",57.47,4.6,"10000101",
  "Farm machinery assembler; F1 relevance limited.",route="B",exc="Revenue about USD 121M, roughly doubled year on year, profitable (KZT 4.6bn)",sig=[s("commercial","agreement with Amazone; planned localisation centre for 3,000 tractors and 1,000 combines a year","2024-09")])
