"""Primary sector for every brand from its LinkedIn industry (company-specific, from the Clay CSV).
First matching rule wins; research or pre-sort corrections override it later in the build."""
import re

SECTORS = [
    ('Automotive & Mobility', r'motor vehicle|automotive|alternative fuel vehicle|vehicle repair|retail motor vehicles|wholesale motor vehicles'),
    ('Aerospace, Defence & Space', r'aviation and aerospace component|aviation & aerospace|defense|space research|armed forces|flight training|military'),
    ('Airlines & Air Travel', r'airlines'),
    ('Travel, Hotels & Leisure', r'hospitality|hotels|accommodation|bed-and-breakfast|leisure, travel|travel arrangements|sightseeing|skiing|amusement|golf courses|recreational facilities|zoos|museums|historical sites'),
    ('Gambling & Gaming Venues', r'gambling|casinos|racetracks'),
    ('Sports, Fitness & Events', r'sports|sporting goods|wellness and fitness|health, wellness and fitness|events services|performing arts'),
    ('Video Games & Esports', r'computer games|mobile gaming'),
    ('Software, Internet & AI', r'software|technology, information|internet marketplace|social networking|artificial intelligence|data infrastructure|business intelligence|blockchain|information services|computer networking|computer and network security|climate data|mobile computing'),
    ('Media, Entertainment & Publishing', r'media|broadcast|movies|music|entertainment|publishing|newspaper|internet news|blogs|animation|radio and television|cable and satellite|online audio|artists|theater|dance|fine art|photography|writing'),
    ('Telecommunications', r'telecommunication|wireless services|satellite telecom'),
    ('Semiconductors & Electronics', r'semiconductor|computers and electronics|computer hardware|electronic and precision|appliances, electrical|audio and video equipment|communications equipment|magnetic and optical|consumer electronics|electric lighting|household appliance|smart meter'),
    ('IT Services & Consulting', r'it services|it system|information technology and services|outsourcing'),
    ('Banking & Lending', r'banking|savings institutions|credit intermediation|loan brokers|collection agencies'),
    ('Insurance', r'insurance|claims adjusting'),
    ('Investment & Capital Markets', r'investment|capital markets|securities and commodity|venture capital|funds and trusts|pension funds|trusts and estates|holding companies'),
    ('Financial Services & Payments', r'financial services'),
    ('Oil, Gas & Fuels', r'oil|natural gas|petroleum|pipeline transportation|retail gasoline|coal mining|fossil fuel'),
    ('Utilities & Renewable Energy', r'utilit|power generation|electric power|renewable|energy technology|fuel cell|geothermal|hydroelectric|nuclear|solar|wind electric|steam and air|water supply|services for renewable|climate technology'),
    ('Mining & Metals', r'mining|metal ore|primary metal|wholesale metals'),
    ('Chemicals & Materials', r'chemical|plastics|rubber|paint, coating|glass|ceramics|clay and refractory|abrasives|lime and gypsum|artificial rubber|nanotechnology|paper and forest|wood product'),
    ('Industrial Machinery & Equipment', r'machinery|industrial automation|automation machinery|robot|engines and power|hvac|boilers|measuring and control|metalworking|metal valve|fabricated metal|metal treatments|turned products|spring and wire|cutlery|electrical equipment|railroad equipment|transportation equipment|commercial and industrial|equipment rental|mechanical or industrial|^manufacturing$'),
    ('Shipping, Maritime & Shipbuilding', r'maritime|shipbuilding'),
    ('Logistics & Transportation', r'logistics|transportation|truck|freight|warehous|rail|postal|ground passenger|bus services|urban transit|taxi|shuttles'),
    ('Building Products & Materials', r'building materials|construction hardware|architectural and structural|wholesale building|retail building|wholesale hardware'),
    ('Construction & Engineering', r'construction|civil engineering|engineering services|contractors|architecture|surveying|utility system construction|accessible architecture'),
    ('Real Estate', r'real estate|leasing|subdivision of land'),
    ('Home & Furniture', r'furniture|mattress|interior design|household services|home furnishings'),
    ('Luxury, Jewellery & Watches', r'luxury|jewelry'),
    ('Beauty & Personal Care', r'cosmetic|personal care|soap and cleaning|retail health and personal'),
    ('Fashion, Apparel & Footwear', r'apparel|fashion|footwear|textile|leather|handbag'),
    ('Alcoholic Drinks', r'breweries|distilleries|wineries|wine and spirits|alcoholic'),
    ('Food & Beverage', r'food|beverage|dairy|baked goods|meat products|seafood|sugar and confectionery|fruit and vegetable|restaurants|caterers|bars, taverns|retail groceries'),
    ('Tobacco & Nicotine', r'tobacco'),
    ('Consumer Products', r'^consumer goods$'),
    ('Retail & E-commerce', r'retail|online and mail order|consumer goods|wholesale|import and export|consumer services|parts distribution'),
    ('Pharma & Biotech', r'pharmaceutical|biotechnology|drugs and sundries'),
    ('Medical Devices & Diagnostics', r'medical devices|medical equipment|diagnostic laboratories'),
    ('Healthcare Services', r'hospital|health care|medical practices|physicians|dentists|nursing|mental health|outpatient|ambulance|alternative medicine|optometrists|therapists|home health|public health|veterinar|pet services'),
    ('Agriculture & Agribusiness', r'farming|ranching|agricultur|fisheries|horticulture|forestry|animal feed'),
    ('Packaging & Printing', r'packaging|printing services|business supplies'),
    ('Environmental & Waste Services', r'environmental|waste|recyclable|conservation|regenerative'),
    ('Security Services', r'security|investigations|fire protection|public safety'),
    ('Staffing & HR', r'staffing|human resources|temporary help|executive search'),
    ('Marketing, Advertising & PR', r'advertising|marketing|public relations|market research|design services|graphic design|^design$'),
    ('Government, Non-profit & Associations', r'government|non-profit|civic|philanthrop|fundraising|religious|political|public policy|industry associations|professional organizations|international affairs|international trade|think tanks|legislative|justice|law enforcement|community|housing|economic programs|public assistance|transportation programs|program management|public works|emergency and relief|individual and family|services for the elderly|vocational rehabilitation|health and human services|environmental quality'),
    ('Professional & Business Services', r'law|legal|accounting|consulting|professional services|strategic management|translation|research services|^research$|operations consulting|administrative|office administration|executive offices|business content|telephone call|facilities services|janitorial|landscaping|laundry|repair and maintenance|death care|funeral|child day care|personal and laundry|consumer goods rental'),
    ('Education & Training', r'education|e-learning|schools|training|higher education|libraries'),
]
_RX = [(s, re.compile(p, re.I)) for s, p in SECTORS]
OTHER = 'Diversified & Other'
NAMES = [s for s, _ in SECTORS] + [OTHER]

def sector_of_industry(ind):
    ind = str(ind or '')
    for s, rx in _RX:
        if rx.search(ind): return s
    return OTHER
