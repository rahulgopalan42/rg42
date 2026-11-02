"""Primary sector (one of the same 48 sectors used on the earlier lists) from a company's Crunchbase industries, name
and short description, plus an F1-fit score per sector.

Crunchbase lists a company's industries alphabetically, so the first one is not the main one. Every visible
industry votes for a sector with a weight (specific industries such as Biotechnology outweigh generic ones such as
Software or Health Care); the name and description add smaller votes. The highest total wins; ties go to the
sector listed first below."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'parents'))
from sectors_v3 import NAMES, OTHER

# (sector, weight, industry regex) - matched against each Crunchbase industry (lower case, may be cut short by "...")
IND = [
    ('Tobacco & Nicotine', 4, r'tobacco|e-cigarette|vaping|cannabis|marijuana|nicotine'),
    ('Automotive & Mobility', 3, r'automotive|electric vehicle|autonomous vehicle|ride sharing|car sharing|ridesharing|motorcycle|micro.?mobility|last mile transportation|electric vehicle charging|^ev'),
    ('Aerospace, Defence & Space', 3, r'aerospace|space travel|^space|satellite(?! communication)|drone|defen[cs]e|military|national security|aviation'),
    ('Airlines & Air Travel', 3, r'^air transportation|airline'),
    ('Travel, Hotels & Leisure', 2.5, r'travel|hospitality|hotel|tourism|vacation rental|leisure|cruise|theme park|resorts?$|amusement'),
    ('Gambling & Gaming Venues', 3, r'gambling|casino|betting|lottery|fantasy sports'),
    ('Sports, Fitness & Events', 3, r'^sports|fitness|^gym|outdoors|cycling|golf|events?$|event management|ticketing|stadium|esports?$(?!)'),
    ('Video Games & Esports', 3, r'gaming|video games?|^games|esport|console games|mmo games|pc games|mobile games|online games|game development'),
    ('Semiconductors & Electronics', 3, r'semiconductor|consumer electronics|electronics|^electronic|^hardware|computer hardware|^computer|chip|photonics|optical communication|^sensor|wearables|quantum computing|embedded systems|laser|^display|led lighting|lighting'),
    ('Telecommunications', 2.5, r'telecommunication|^telecom|wireless|broadband|internet service provider|^isp|satellite communication|^5g|mobile network|unified communications|^voip|fiber|cable'),
    ('Financial Services & Payments', 2.5, r'fintech|payments?$|payment|mobile payments|transaction processing|remittance|billing|point of sale|cryptocurrency|bitcoin|ethereum|web3|^nft|decentralized finance|^defi|personal finance|prepaid card|financial services|^finance$'),
    ('Banking & Lending', 2.5, r'banking|^bank|lending|^credit|neo.?bank|micro lending|peer to peer|mortgage|consumer lending|debt'),
    ('Insurance', 3, r'insurance|insurtech|reinsurance'),
    ('Investment & Capital Markets', 2.5, r'asset management|wealth management|venture capital|private equity|hedge fund|stock exchange|trading platform|impact investing|financial exchange|^investment|brokerage|capital markets|^trading'),
    ('Software, Internet & AI', 2, r'artificial intelligence|^ai\b|generative ai|machine learning|software|saas|^apps|mobile apps|^internet|cloud computing|cloud data|cloud infrastructure|developer|enterprise software|analytics|big data|database|cyber ?security|network security|^security$|identity management|collaboration|^crm|information services|search engine|social media|social network|messaging|consumer software|blockchain|^mobile$|^web|internet of things|^iot|computer vision|natural language|robotic process|productivity tools|predictive analytics|data management|data integration|^platforms?$|^open source|^marketplace'),
    ('IT Services & Consulting', 1.5, r'information technology|it services|it management|data center|outsourcing|web hosting|managed services|business information systems|^cloud management'),
    ('Media, Entertainment & Publishing', 2, r'media|entertainment|publishing|^music|^video|film|tv|television|broadcasting|^news|content|podcast|streaming|animation|digital entertainment|audio|radio|photography|^art$|^arts'),
    ('Oil, Gas & Fuels', 3, r'oil and gas|^oil|fossil fuel|petroleum|^fuel|natural gas|^gas$|^coal'),
    ('Oil, Gas & Fuels', 1.3, r'^natural resource'),
    ('Utilities & Renewable Energy', 2.5, r'renewable|clean ?energy|^solar|wind energy|^wind|energy storage|^battery|batteries|power grid|electrical distribution|^utilities|cleantech|nuclear|hydrogen|biofuel|biomass|geothermal|energy efficiency|^energy$|^power|electric utility|smart grid|^water$'),
    ('Mining & Metals', 3, r'mining|mineral|^metals?$|^gold|precious metals|^steel|lithium|^copper|metal'),
    ('Chemicals & Materials', 2.5, r'chemical|advanced materials|^materials|plastics|^paper|nanotechnology|biomaterials|^composites|^glass|^rubber'),
    ('Industrial Machinery & Equipment', 1.5, r'industrial|manufacturing|robotics|machinery|3d printing|additive manufacturing|mechanical engineering|^tools|electrical engineering|^electrical|^automation|^machine'),
    ('Shipping, Maritime & Shipbuilding', 3, r'marine|maritime|boating|^ports|shipbuilding|^ships'),
    ('Logistics & Transportation', 2.5, r'logistics|supply chain|^delivery|freight|transportation|trucking|^shipping|courier|warehousing|railroad|public transportation|fleet management|parcel|^moving'),
    ('Building Products & Materials', 2.5, r'building material|construction material|cement|green building'),
    ('Construction & Engineering', 2.5, r'^construction|civil engineering|architecture|^engineering|infrastructure'),
    ('Real Estate', 2.5, r'real estate|property management|commercial real estate|^rental property|proptech|coworking|^property|^reit|home renovation|^rental$|residential'),
    ('Home & Furniture', 2.5, r'furniture|home decor|home improvement|home services|interior design|smart home|household appliances|^home$|^kitchen|^mattress'),
    ('Luxury, Jewellery & Watches', 3, r'luxury|jewelry|jewellery|^watch'),
    ('Beauty & Personal Care', 3, r'beauty|cosmetic|skin care|hair care|fragrance|personal care|^spa$|wellness products'),
    ('Fashion, Apparel & Footwear', 3, r'fashion|apparel|clothing|footwear|^shoes|lingerie|eyewear|textile'),
    ('Alcoholic Drinks', 3, r'wine|spirits|brewing|^beer|winery|distiller|alcohol'),
    ('Food & Beverage', 2.5, r'food|beverage|restaurant|grocery|coffee|^tea$|snack|meal kit|catering|nutrition|bakery|dairy|confectionery|^drinks|bottled water|quick service'),
    ('Consumer Products', 2, r'consumer goods|consumer products|household|^pet|^toys|^baby|children|^consumer$|^lifestyle|personal health|sporting goods'),
    ('Retail & E-commerce', 2, r'e-commerce|ecommerce|^retail|marketplace|online portals|^shopping|wholesale|flash sale|retail technology|subscription service|department store|^convenience'),
    ('Pharma & Biotech', 3, r'biotechnology|pharmaceutical|life science|drug discovery|therapeutics|biopharma|genetics|genomics|oncology|clinical trials|vaccine|precision medicine|neuroscience|bioinformatics|^biology|^cell|gene therapy|^biotech|drug delivery|rare disease'),
    ('Medical Devices & Diagnostics', 3, r'medical device|diagnostics|medical imaging|^dental|health diagnostics|^surgical|^orthopedic|^cardiology|^ophthalmology|^radiology|^biometrics'),
    ('Healthcare Services', 1.8, r'health care|healthcare|hospital|^medical|home health|elder care|mental health|telehealth|wellness|^clinic|nursing|^pharmacy|veterinary|^health$|health insurance|emergency medicine|^fertility'),
    ('Agriculture & Agribusiness', 3, r'agriculture|agtech|farming|aquaculture|forestry|livestock|^agri|crop|^seed'),
    ('Packaging & Printing', 3, r'packaging|^printing|^labels'),
    ('Environmental & Waste Services', 2.5, r'recycling|waste management|environmental|water purification|water treatment|carbon capture|sustainability|^pollution|^waste'),
    ('Security Services', 2, r'law enforcement|public safety|homeland security|video surveillance|physical security|^security services'),
    ('Staffing & HR', 2.5, r'human resources|recruiting|staffing|employment|^hr|payroll|employee benefits|^career'),
    ('Marketing, Advertising & PR', 2, r'advertising|marketing|ad network|public relations|brand marketing|affiliate|coupons|loyalty program|market research|^seo|lead generation|^ad tech|adtech'),
    ('Government, Non-profit & Associations', 3, r'government|non profit|non-profit|charity|^public sector|^association'),
    ('Professional & Business Services', 2, r'consulting|^legal|^law|professional services|accounting|management consulting|business development|customer service|call center|^facility|facilities|^b2b$|translation|^service industry'),
    ('Education & Training', 3, r'education|edtech|e-learning|higher education|^training|tutoring|language learning|skill assessment|^schools?$|^stem education|^universit'),
]
_IND = [(s, w, re.compile(p, re.I)) for s, w, p in IND]
GENERIC = {'software': 1.0, 'information technology': 0.6, 'internet': 0.7, 'apps': 1.0, 'mobile': 0.6, 'health care': 1.0, 'medical': 1.0,
           'energy': 1.2, 'manufacturing': 0.8, 'financial services': 1.4, 'finance': 1.2, 'industrial': 0.8, 'hardware': 1.2, 'consumer': 1.0,
           'enterprise software': 1.4, 'saas': 1.4, 'analytics': 1.0, 'big data': 1.0, 'transportation': 1.6, 'retail': 1.6, 'e-commerce': 2.2,
           'artificial intelligence (ai)': 2.6, 'artificial intelligence': 2.6, 'machine learning': 1.6, 'generative ai': 2.6, 'cyber security': 2.2,
           'service industry': 1.0, 'b2b': 0.8, 'electronics': 2.0, 'marketplace': 1.4, 'mobile apps': 1.2, 'platforms': 0.8}

# name / description cues: (sector, weight, regex)
NAME = [('Banking & Lending', 3, r'\bbank\b|\bbanco\b'), ('Insurance', 3, r'insurance|assurance|\bre\b'), ('Airlines & Air Travel', 3, r'airlines?|airways'),
        ('Automotive & Mobility', 2, r'motors?\b|automotive|\bauto\b'), ('Pharma & Biotech', 2, r'pharma|therapeutics|biosciences?|\bbio\b|biotech|biologics'),
        ('Utilities & Renewable Energy', 1.5, r'solar|\bwind\b|renewable|\bpower\b'), ('Oil, Gas & Fuels', 2, r'\boil\b|petroleum|\bgas\b|petro'),
        ('Mining & Metals', 1.5, r'mining|\bgold\b|minerals?|metals?\b|lithium'), ('Telecommunications', 1.5, r'telecom|communications|wireless|\bmobile\b'),
        ('Travel, Hotels & Leisure', 2, r'hotels?|resorts?'), ('Food & Beverage', 2, r'\bfoods?\b|beverages?|coffee|restaurants?'),
        ('Real Estate', 2, r'realty|properties|\breit\b|real estate'), ('Investment & Capital Markets', 1, r'\bcapital\b|investments?\b|asset management'),
        ('Video Games & Esports', 2, r'\bgames\b|gaming'), ('Logistics & Transportation', 2, r'logistics|freight|express\b'),
        ('Healthcare Services', 1.5, r'hospital|\bhealth\b|medical|clinic'), ('Semiconductors & Electronics', 3, r'semiconductor|microelectronics')]
DESC = [('Banking & Lending', 1.5, r'\bbank\b|lender|loans?\b'), ('Insurance', 1.5, r'insurance|insurer'), ('Airlines & Air Travel', 2, r'airline'),
        ('Automotive & Mobility', 1.5, r'electric vehicle|\bev\b|automaker|car maker|vehicles?'), ('Pharma & Biotech', 1.5, r'biopharm|biotech|therapeut|clinical.stage|drug|medicines'),
        ('Oil, Gas & Fuels', 1.5, r'oil and gas|exploration and production|petroleum|natural gas'), ('Utilities & Renewable Energy', 1.2, r'solar|wind|renewable|power plant|electricity|energy storage'),
        ('Semiconductors & Electronics', 1.5, r'semiconductor|\bchips?\b|electronics'), ('Video Games & Esports', 1.5, r'\bgames?\b|gaming'),
        ('Retail & E-commerce', 1.2, r'e-commerce|online retailer|online marketplace|retailer'), ('Food & Beverage', 1.2, r'restaurant|\bfood\b|beverage'),
        ('Real Estate', 1.2, r'real estate|\breit\b|propert'), ('Telecommunications', 1.2, r'telecom|wireless|broadband|fiber'),
        ('Mining & Metals', 1.5, r'\bmining\b|\bgold\b|copper|lithium|\bores?\b'), ('Healthcare Services', 1.0, r'hospital|health care provider|clinic|patients'),
        ('Medical Devices & Diagnostics', 1.2, r'medical device|diagnostic'), ('Logistics & Transportation', 1.2, r'logistics|delivery|freight|shipping'),
        ('Financial Services & Payments', 1.2, r'payment|fintech|crypto'), ('Software, Internet & AI', 0.5, r'software|platform|\bsaas\b|\bai\b|artificial intelligence'),
        ('Education & Training', 1.2, r'education|learning|students'), ('Travel, Hotels & Leisure', 1.2, r'travel|hotel|booking'),
        ('Fashion, Apparel & Footwear', 1.2, r'fashion|apparel|clothing|footwear'), ('Beauty & Personal Care', 1.2, r'beauty|cosmetic|skincare|skin care')]
_NAME = [(s, w, re.compile(p, re.I)) for s, w, p in NAME]; _DESC = [(s, w, re.compile(p, re.I)) for s, w, p in DESC]
ORDER = {s: i for i, s in enumerate(NAMES)}

def industries(txt):
    """visible Crunchbase industries; a token cut short by '...' is kept without the dots"""
    out = []
    for p in str(txt or '').split(','):
        p = re.sub(r'[.…]+$', '', p.strip()).strip()
        if len(p) >= 3: out.append(p)
    return out

def sector_of(ind_txt, name='', desc=''):
    votes = {}
    for tok in industries(ind_txt):
        tl = tok.lower()
        for s, w, rx in _IND:
            if rx.search(tl):
                votes[s] = votes.get(s, 0) + GENERIC.get(tl, w); break
    for s, w, rx in _NAME:
        if rx.search(str(name or '')): votes[s] = votes.get(s, 0) + w
    for s, w, rx in _DESC:
        if rx.search(str(desc or '')): votes[s] = votes.get(s, 0) + w
    if not votes: return OTHER
    return max(votes, key=lambda s: (votes[s], -ORDER.get(s, 99)))

# F1 sponsorship fit by sector (0-10): which categories already buy F1 (tech, fintech/crypto, autos, luxury, drinks,
# energy, logistics, telecoms, travel...) and which rarely do (pharma, mining, B2B industrials, government)
FIT = {'Automotive & Mobility': 10, 'Luxury, Jewellery & Watches': 10, 'Software, Internet & AI': 9, 'Financial Services & Payments': 9,
       'Semiconductors & Electronics': 9, 'Airlines & Air Travel': 9, 'Telecommunications': 8, 'IT Services & Consulting': 8,
       'Fashion, Apparel & Footwear': 8, 'Alcoholic Drinks': 8, 'Food & Beverage': 8, 'Beauty & Personal Care': 8, 'Video Games & Esports': 8,
       'Travel, Hotels & Leisure': 8, 'Oil, Gas & Fuels': 7, 'Logistics & Transportation': 8, 'Retail & E-commerce': 8, 'Shipping, Maritime & Shipbuilding': 7,
       'Utilities & Renewable Energy': 7, 'Aerospace, Defence & Space': 7, 'Media, Entertainment & Publishing': 7, 'Sports, Fitness & Events': 7,
       'Investment & Capital Markets': 7, 'Banking & Lending': 7, 'Insurance': 7, 'Consumer Products': 7, 'Gambling & Gaming Venues': 5,
       'Chemicals & Materials': 6, 'Industrial Machinery & Equipment': 6, 'Marketing, Advertising & PR': 6, 'Professional & Business Services': 6,
       'Home & Furniture': 5, 'Real Estate': 5, 'Construction & Engineering': 5, 'Building Products & Materials': 5, 'Security Services': 5,
       'Staffing & HR': 5, 'Education & Training': 5, 'Mining & Metals': 4, 'Healthcare Services': 4, 'Medical Devices & Diagnostics': 4,
       'Packaging & Printing': 4, 'Environmental & Waste Services': 4, 'Pharma & Biotech': 3, 'Agriculture & Agribusiness': 3,
       'Government, Non-profit & Associations': 1, 'Tobacco & Nicotine': 0, OTHER: 4}
assert set(FIT) == set(NAMES), set(NAMES) ^ set(FIT)
CONSUMER = re.compile(r'consumer|mobile app|^apps|e-commerce|gaming|video game|fintech|payments|crypto|travel|beverage|fashion|beauty|automotive|electric vehicle|'
                      r'artificial intelligence|generative ai|social|dating|music|streaming|food delivery|ride sharing|sports|fitness|neo.?bank|personal finance|'
                      r'wearables|consumer electronics|luxury|hospitality|delivery|marketplace', re.I)

if __name__ == '__main__':
    for ind, nm, d in [('Biotechnology, Health Care, ...', 'Tengion', 'Tengion is a clinical-stage biotechnology company'),
                       ('Banking, Credit Cards, Fi...', 'Cardtronics', 'operator of ATM'), ('Apps, Information Servic...', 'Prysm Systems', ''),
                       ('Energy, Natural Resource...', 'Saguaro Resources', 'exploration, acquisition'), ('Advertising, Coupons, Di...', 'Quotient Technology', ''),
                       ('E-Commerce, Fashion, Re...', 'Privalia', 'e-commerce website that trades fashion'), ('Artificial Intelligence (AI), Machine Learning', 'Mistral AI', ''),
                       ('Health Care, Hospital, Me...', 'Mediclinic International', ''), ('Internet, Real Estate, Ren...', 'Iwjw', 'online platform'),
                       ('Consumer Software, Ed...', 'iTutorGroup', 'individualized and personalized learning')]:
        print(nm, '->', sector_of(ind, nm, d))
