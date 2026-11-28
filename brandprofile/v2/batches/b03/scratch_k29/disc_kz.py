import json,sys
SRC="https://forbes.kz/ranking/75-krupneyshih-chastnyh-kompaniy-kazahstana-2025-ac7ea1"
R=0.0021
rows="""KAZ Minerals|1810|Mining & Metals|copper mining|ALREADY DELIVERED|left out|ALREADY DELIVERED b01
Kazakhmys|1433|Mining & Metals|copper mining and smelting|NEW|not researched|
Astana Motors|1179.79|Automotive & Mobility|car dealer and distributor|NEW|not researched|
Qarmet|752.70|Mining & Metals|steel|NEW|not researched|
Kazchrome|1002.52|Mining & Metals|ferroalloys|NEW|left out|ERG subsidiary; ERG already delivered b01
BI Group|979.04|Construction & Engineering|construction and development|NEW|not researched|
Magnum Cash&Carry|453.13|Retail & E-commerce|grocery retail|NEW|not researched|
SSGPO|416.9|Mining & Metals|iron ore|NEW|left out|ERG subsidiary; ERG already delivered b01
Orbis Auto|448.05|Automotive & Mobility|car dealer|NEW|not researched|
Kazakhstan Utility Systems|328.6|Utilities & Renewable Energy|power and utilities|NEW|not researched|
Aluminium of Kazakhstan|317.63|Mining & Metals|alumina|NEW|left out|ERG subsidiary; ERG already delivered b01
Integra Construction KZ|418.8|Construction & Engineering|construction|NEW|not researched|
Central-Asian Electric Power Corporation|291.72|Utilities & Renewable Energy|power generation and distribution|NEW|not researched|
Bazis|316.80|Construction & Engineering|residential construction|NEW|not researched|
Sulpak|331.7|Retail & E-commerce|electronics retail|NEW|not researched|
Qazaq Stroy|347.01|Construction & Engineering|construction|NEW|not researched|
SCAT Airlines|311.1|Airlines & Air Travel|airline|NEW|not researched|
Kazakhstan Electrolysis Plant|288.56|Mining & Metals|aluminium smelting|NEW|left out|ERG subsidiary; ERG already delivered b01
Railways Systems KZ|262.6|Industrial Machinery & Equipment|rail equipment|NEW|not researched|
Prima Distribution|231.8|Consumer Products|FMCG distribution|NEW|not researched|
Mechta Market|261.1|Retail & E-commerce|electronics retail|NEW|not researched|
KazPetroDrilling|209.2|Oil, Gas & Fuels|drilling services|NEW|not researched|
Technodom Operator|232.19|Retail & E-commerce|electronics retail|NEW|not researched|
PetroRetail|220.7|Oil, Gas & Fuels|fuel retail|NEW|not researched|
Alageum Electric|198.47|Industrial Machinery & Equipment|electrical equipment|NEW|not researched|
RG Brands|196|Food & Beverage|beverages and snacks|NEW|not researched|
Caspiy Neft|167.57|Oil, Gas & Fuels|oil production|NEW|not researched|
Eurasian Energy Corporation|150.69|Utilities & Renewable Energy|power generation|NEW|left out|ERG subsidiary; ERG already delivered b01
Helios|136.9|Oil, Gas & Fuels|fuel retail|POSSIBLE|not researched|check.py POSSIBLE matched Helios Kliniken (different company)
Aitas KZ|129.74|Agriculture & Agribusiness|meat and agribusiness|NEW|not researched|
Shubarkol Komir|146.68|Mining & Metals|coal|NEW|left out|ERG subsidiary; ERG already delivered b01
Kazphosphate|120.8|Chemicals & Materials|phosphate fertilisers|NEW|not researched|
Imstalcon|113.67|Construction & Engineering|industrial construction|NEW|not researched|
Vender|163.99|Retail & E-commerce|wholesale trade|NEW|not researched|
Transtelecom|88.84|Telecommunications|telecom operator|NEW|not researched|
QazTehna|133.47|Automotive & Mobility|bus manufacturing|NEW|not researched|
Almatyinzhstroy|107.5|Construction & Engineering|construction|NEW|not researched|
Kazpetrol Group|85.46|Oil, Gas & Fuels|oil and gas|NEW|not researched|
Atasu Group|67.78|Logistics & Transportation|freight logistics|NEW|not researched|
Olzha Agro|39.65|Agriculture & Agribusiness|farming|NEW|not researched|
Trest Sredazenergomontazh|53.6|Construction & Engineering|energy construction|NEW|not researched|
Neftestroyservice LTD|45.6|Oil, Gas & Fuels|oilfield services|NEW|not researched|
Mercury Properties|80.2|Real Estate|property development|NEW|not researched|
Eikos|68.08|Retail & E-commerce|trade|NEW|not researched|
Eastcomtrans|87.1|Logistics & Transportation|rail freight|NEW|not researched|
Gulser Computers|87.5|Retail & E-commerce|electronics retail|NEW|not researched|
Orbis Oilfield Services|57.27|Oil, Gas & Fuels|oilfield services|NEW|not researched|
Mega shopping centres (Mega Center)|60.68|Real Estate|shopping centres|NEW|not researched|
Karazhyra|73.39|Mining & Metals|coal|NEW|not researched|
KazAzot|66.8|Chemicals & Materials|fertilisers|NEW|not researched|
KazakhBitum|89.5|Building Products & Materials|bitumen|NEW|not researched|
South Oil|60.4|Oil, Gas & Fuels|oil production|NEW|not researched|
Evrika|72.8|Retail & E-commerce|electronics retail|NEW|not researched|
Galanz Bottlers|64.55|Food & Beverage|beverages|NEW|not researched|
Alel Agro|55.98|Agriculture & Agribusiness|poultry|NEW|not researched|
Kainar-AKB|61.79|Automotive & Mobility|batteries|NEW|not researched|
Buzachi Neft|58.8|Oil, Gas & Fuels|oil production|NEW|not researched|
Kostanay Minerals|38.78|Mining & Metals|chrysotile mining|NEW|not researched|
Atameken-Agro|39.85|Agriculture & Agribusiness|grain farming|NEW|not researched|
Zhambyl GRES|63.3|Utilities & Renewable Energy|power plant|NEW|left out|single power plant
ST Networks|68.89|Semiconductors & Electronics|IT distribution|NEW|not researched|
Aqniet Group|57.37|Pharma & Biotech|pharma distribution|NEW|not researched|
AlemAgro|66.1|Agriculture & Agribusiness|agrochemicals distribution|NEW|not researched|
Kazakhmys Coal|53.8|Mining & Metals|coal|NEW|left out|Kazakhmys subsidiary
Bayan Sulu|47.3|Food & Beverage|confectionery|NEW|not researched|
AgromashHolding KZ|57.47|Industrial Machinery & Equipment|agricultural machinery|NEW|not researched|
Standard Cement|45.93|Building Products & Materials|cement|NEW|not researched|
Otau-Stroy|49.76|Construction & Engineering|construction|NEW|not researched|
AVC Production|55.8|Construction & Engineering|construction|NEW|not researched|
AltynEx Company|36.35|Mining & Metals|gold mining|NEW|not researched|
Kazakh Institute of Oil and Gas|33.06|Professional & Business Services|engineering design|NEW|not researched|
Meliorator|48.98|Construction & Engineering|construction|NEW|not researched|
Shin-Line|45.4|Food & Beverage|food production|NEW|not researched|
Bapy Mining|37.19|Mining & Metals|mining|NEW|not researched|"""
out=open(sys.argv[1],"a")
for l in rows.splitlines():
    n,rev,sec,sub,chk,st,why=l.split("|")
    v=float(rev)
    out.write(json.dumps({"name":n,"website":"","hq_country":"Kazakhstan","sector":sec,"subsector":sub,"figure":f"KZT {rev} bn revenue (Forbes Kazakhstan 75 largest private companies 2025)","metric":"revenue","usd_m":round(v*1000*R),"source":SRC,"check":chk,"stage":st,"why":why},ensure_ascii=False)+"\n")
