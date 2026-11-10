"""Hand triage of the NEW Crunchbase organisations (pool.json, excluded == ''): keep operating companies / brands at
the bar (valuation >= USD 1B or funding >= USD 150M); drop joint ventures, project companies, funds/REITs/BDCs,
public bodies, development banks, sports clubs/leagues, non-profits, subsidiaries of groups already covered,
acquired/defunct companies and obvious data errors. Writes new600/cb_keep.json and cb_dropped.json."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
KEEP = '''LendInvest|Zenith Energy|Sidewalk Infrastructure Partners|Gold Tree Studios|Forum Markets|Competitive Power Ventures|S&U|
Xinhua Semiconductor|Kallpa Generación|Anhui YOFC Advanced Semiconductor|Power Capital Renewable Energy|Ferovinum|CHIP Reverse Mortgage|
Sky Harbour|Hangzhou Changchuan Technology|ZeroStack|South Wind Exploration & Production|Navios South American Logistics|
Hengtong Submarine Power Cable|IRulya Therapeutics|InstaVolt|Tonix Pharmaceuticals Holding Corp.|
Shanghai Wai Gaoqiao Free Trade Zone Development|Aicox Soluciones|Conavi Medical (formerly Titan Medical)|Tejon Treating and Carbon Solutions|
Trinity Biotech|Sify Infinit Spaces|Guangdong Aofei Data Technology|Österreichische Glasfaser-Infrastrukturgesellschaft|Adagene|
First Avenue Real Estate Development|Starlab Space|T-Therapeutics|Aline Accounting Partners|AA-I Technologies|Chongqing Ant Consumer Finance|
Oman International Development & Investment|Ajlan Sons for Commercial and Real Estate Investment|Xinlian Power|Shenzhou Automotive Technology|
AI Financial|Equatys|Willow Wealth|Easpring Finland New Materials Oy|
Terminus Technologies|Shanghai Canxing Cultural and Broadcast Company|Tuduoduo|Huaqin Communication Technology|Sagar Defence Engineering|
Sadia Halal|Cove Kaz Capital Group|Vale Indonesia|Maropost|Shuyishao Xiancao|Shaanxi Xifeng Liquor|HMNC Brain Health|Omega Geração|
Archosaur Games (Zulong Entertainment)|Parag Parikh Financial Advisory Services|LONGi Hydrogen Energy|Yuyuan Jewelry & Fashion Group|Qdama|
Antekin Biotech|Kiwimoore|eRoad Software|Aipuqiang|Letu|NOME|Scivita Medical Technology|Xinwanxing Composites|
Tongchuang Purun Electromechanical High-Tech|Jinyuansheng|Aijia Home Furnishing Products|Zhejiang Tianneng New Material|Oasis Market|
Aaru|Axelar Network|Mavria|io.net|Supermonkey|SmartMi International Limited|Lianshang Literature|Wifi Skeleton Key|Jiankang 160|
Traversal|Yizhu Technology|Lingchuan Technology|Sungrow New Energy|
Connected Kerb|Laza Medical|Curevo|ATEX Resources|Grande Asset Hotels and Property|Corvia Medical|Sunday Lake Gold|AvAir|Duos Technologies|
Ampliform|Sono Motors|UniX AI|National Commodity & Derivatives Exchange|Vaeridion|Yuanbao Insurance Research Institute|Tutor Intelligence|
Revera Energy|Rostrum Pacific'''
keep = {k.strip() for k in KEEP.replace('\n', '').split('|') if k.strip()}
pool = [c for c in json.load(open(os.path.join(H, 'pool.json'))) if not c['excluded']]
names = {c['name'] for c in pool}; missing = keep - names
assert not missing, missing
k = [c for c in pool if c['name'] in keep]; d = [c for c in pool if c['name'] not in keep]
json.dump(k, open(os.path.join(H, 'cb_keep.json'), 'w'), indent=0, ensure_ascii=False)
json.dump([c['name'] for c in d], open(os.path.join(H, 'cb_dropped.json'), 'w'), indent=0, ensure_ascii=False)
print('kept', len(k), 'dropped', len(d))
