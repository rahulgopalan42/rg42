"""Hand corrections after reading every row: sector (the automatic sector guess works from the description only) and
the group a company belongs to when that group is already on Rahul's lists (shown in its own column, not dropped)."""
SECTOR = {
 'Changsha Jingjia Microelectronics': 'Semiconductors & Electronics', 'Weihai Guangwei Composites': 'Chemicals & Materials',
 'COFCO Biotechnology': 'Food & Beverage', 'Jiugui Liquor': 'Alcoholic Drinks', 'Hebei Hengshui Laobaigan Liquor': 'Alcoholic Drinks',
 'Casamigos': 'Alcoholic Drinks', 'Excelland Robotics (Wuxi)': 'Industrial Machinery & Equipment', 'Tenneco Clean Air India': 'Automotive & Mobility',
 'Direct Drive Tech': 'Industrial Machinery & Equipment', 'Parag Parikh Financial Advisory Services (PPFAS)': 'Investment & Capital Markets',
 'China Hainan Rubber Industry Group': 'Agriculture & Agribusiness', 'Ovctek China (Autek China)': 'Medical Devices & Diagnostics',
 'Better Life Commercial Chain': 'Retail & E-commerce', 'Anhui Xinhua Media': 'Media, Entertainment & Publishing', 'Laza Medical': 'Medical Devices & Diagnostics',
 'Guangdong Aofei Data Technology': 'IT Services & Consulting', 'Taiwan Cogeneration Corporation': 'Utilities & Renewable Energy',
 'Guangdong Provincial Expressway Development': 'Logistics & Transportation', 'Suzhou Kingswood Education Technology': 'Education & Training',
 'Do-Fluoride New Materials': 'Chemicals & Materials', 'Ningbo Ronbay New Energy Technology': 'Chemicals & Materials',
 'Hunan Changyuan Lico': 'Chemicals & Materials', 'Beibu Gulf Port': 'Logistics & Transportation', 'Ningbo Xusheng Group': 'Automotive & Mobility',
 'Eacon Group (Eacon Mining Technology)': 'Industrial Machinery & Equipment', 'Yifeng Pharmacy Chain': 'Healthcare Services',
 'DaShenLin Pharmaceutical Group': 'Healthcare Services', 'Henan Zhongyuan Expressway': 'Logistics & Transportation', 'Sinomine Resource Group': 'Mining & Metals',
 'RoboTechnik Intelligent Technology': 'Industrial Machinery & Equipment', 'Shandong Iron and Steel Company': 'Mining & Metals',
 'Shandong Hi-Speed Road&Bridge Group': 'Construction & Engineering', 'Kidswant Digital Technology (Kidswant)': 'Retail & E-commerce',
 'Zhejiang Daily Digital Culture Group': 'Media, Entertainment & Publishing', 'Farglory Land Development': 'Real Estate',
 'Biem.L.Fdlkk Garment': 'Fashion, Apparel & Footwear', 'Guangzhou Great Power Energy and Technology': 'Semiconductors & Electronics',
 'Jiangsu Expressway Company': 'Logistics & Transportation', 'Fujian Dongbai Group': 'Retail & E-commerce', 'Jizhong Energy Resources': 'Mining & Metals',
 'Taiwan Fertilizer Co.': 'Agriculture & Agribusiness', 'Busy Ming Group (Zhao Yi Ming / Hao Hen Mang)': 'Retail & E-commerce',
 'Fujian Wanchen Food Group': 'Retail & E-commerce', 'Fameglow Holdings (per Face)': 'Healthcare Services',
 'Minmetals New Energy Materials (Hunan) (Changsha Research Institute of Mining and Metallurgy)': 'Chemicals & Materials',
 'Shenzhen Agricultural Power Group': 'Agriculture & Agribusiness', 'Lontium Semiconductor': 'Semiconductors & Electronics',
}
GROUP = {
 'China Resources New Energy': 'China Resources', 'Eastern Air Logistics': 'China Eastern Airlines', 'CGN New Energy Holdings': 'China General Nuclear (CGN)',
 'Sinopec Oilfield Service Corporation': 'Sinopec', 'Bank OCBC NISP': 'OCBC', 'Tenneco Clean Air India': 'Tenneco', 'COFCO Biotechnology': 'COFCO',
 'China Merchants Expressway Network & Technology Holdings': 'China Merchants Group', 'Kind Snacks': 'Mars', 'Kylie Cosmetics': 'Coty',
 'Casamigos': 'Diageo', 'Yuyuan Jewelry & Fashion Group': 'Shanghai Yuyuan Tourist Mart / Fosun', 'Fresh Life Style (Xianshenghuo)': 'New Hope Group',
 'China CSSC Holdings': 'CSSC (China State Shipbuilding)', 'Shandong Hi-Speed Road&Bridge Group': 'Shandong Hi-Speed Group',
 'Jiangsu Expressway Company': 'Jiangsu Communications Holding', 'Yunnan Aluminium': 'Chinalco (Aluminum Corporation of China)',
}
GROUP.update({
 'Inner Mongolia Dian Tou Energy': 'SPIC (State Power Investment Corp)', 'Shanghai Electric Power': 'SPIC (State Power Investment Corp)',
 'Hubei Energy Group': 'China Three Gorges', 'SDIC Capital': 'SDIC', 'Guangshen Railway': 'China State Railway Group',
 'Liaoning Port': 'China Merchants Group (China Merchants Port)', 'China Merchants Expressway': 'China Merchants Group',
 'Shenzhen Agricultural Power Group': 'Shenzhen Investment Holdings', 'Eastern Air Logistics': 'China Eastern Airlines',
})
# same company as one already on the lists under another name -> not new
DROP = {'Zhejiang Daily Digital Culture Group': 'already covered as Zhejiang Daily Media (its former name)',
        'Heilongjiang Agriculture Company': 'already covered as Beidahuang (its brand / parent group)'}
# descriptions that came back too short
ABOUT = {
 'Guizhou BC&TV Information Network': "Guizhou province's cable TV network operator (Guizhou Radio & TV Information Network), providing cable and IPTV television, "
     "broadband internet, smart-home services and government/enterprise ICT and data-centre services across Guizhou; listed in Shanghai.",
 'Befar Group': 'Shandong (Binzhou) chemical producer, Befar / Binhua: chlor-alkali (caustic soda), propylene oxide, chlorinated solvents, '
     'C3/C4 olefin derivatives and wet electronic-grade chemicals for the semiconductor and display industries; sells across China and exports.',
 'Eacon Group (Eacon Mining Technology)': 'Beijing-based autonomous-driving company for mining: retrofits and factory-fits driverless haulage '
     'systems on mining trucks and runs large driverless truck fleets at open-pit coal and metal mines in Inner Mongolia, Xinjiang and abroad; '
     'Hong Kong-listed.',
 'Xizang Zhihui Mining': 'Tibet-based non-ferrous mining company producing lead, zinc, silver and copper concentrates from its mines in the '
     'Tibet Autonomous Region, sold to smelters in China; Hong Kong-listed.',
}
