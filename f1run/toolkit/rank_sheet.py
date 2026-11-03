# Merge row OCR (rec2/rows_*.json) with rec/companies.json, categorise into sector tabs, score and rank -> xlsx
import json,glob,re,collections,math,sys
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from rapidfuzz import process,fuzz
SUF=r'\b(inc|corp|corporation|ltd|limited|plc|llc|ag|sa|se|nv|co|company|group|holdings?|technologies|technology|the|labs?|ai)\b'
key=lambda s:re.sub(r'[^a-z0-9]','',re.sub(SUF,'',(s or '').lower()))
comps=json.load(open('rec/companies.json'))
ckeys={}
for c in comps: ckeys.setdefault(key(c['name']),c)
klist=list(ckeys)
# ---------- gather row observations
obs=collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
def clean_name(n):
    n=re.sub(r"\s+\S*[\d][\d,\.]{4,}\S*.*$",'',n)          # trailing funding amount bleed
    n=re.sub(r"\s+['‘’`]?\S{0,4}[$€£¥₹]\S*.*$",'',n)
    n=re.sub(r'\s+(?:I\s+)?(?:Public|Private)\s*\S{0,3}$','',n)
    n=re.sub(r'\bAl\b','AI',n).strip(" '\"`.,;:-_~*|‘’"); return n
for f in glob.glob('rec2/rows_*.json'):
    for fr in json.load(open(f))['frames']:
        for r in fr.get('rows',[]):
            k=key(clean_name(r.get('name','')))
            if len(k)<2: continue
            if k not in ckeys:
                m=process.extractOne(k,klist,scorer=fuzz.ratio,score_cutoff=85 if len(k)>=8 else 90)
                if m: k=m[0]
                else:
                    ws=clean_name(r.get('name','')).split(); hit=None
                    while len(ws)>1 and not hit:
                        ws=ws[:-1]; kk=key(' '.join(ws))
                        if len(kk)>=4 and kk in ckeys: hit=kk
                    if not hit: continue
                    k=hit
            if not r.get('rank') and r.get('desc'):
                m=re.search(r'(\d{1,3}(?:[,\.]\d{3})+|\d{1,6})\s*$',r['desc'])
                if m: r['rank']=m.group(1)
            for fld in ('total','last','date','stage','industries','hq','rank'):
                v=(r.get(fld) or '').strip()
                if v: obs[k][fld][v]+=1
# ---------- parsers
FX={'$':1,'US$':1,'€':1.08,'£':1.27,'CA$':0.73,'A$':0.66,'AU$':0.66,'R$':0.18,'RS':0.18,'MX$':0.055,'CN¥':0.14,'CNY¥':0.14,'¥':0.0067,'JP¥':0.0067,'₹':0.012,'SAR':0.27,'AED':0.27,'CHF':1.13,'SEK':0.095,'NOK':0.092,'HK$':0.13,'S$':0.74,'NT$':0.031,'₩':0.00072,'KRW':0.00072,'THB':0.028,'ZAR':0.055,'TRY':0.03,'PLN':0.25,'DKK':0.145,'ILS':0.27,'NZ$':0.6,'IDR':0.000063,'MYR':0.22,'PHP':0.017,'VND':0.00004,'NGN':0.00065,'EGP':0.02,'KZT':0.002}
def money(s):
    s=s.replace("'",'').replace('‘','').replace(' ','')
    m=re.search(r'([A-Z]{0,4}[$€£¥₹₩]?)\s*([\d,]{5,})',s)
    if not m: return None
    cur=m.group(1) or '$'; amt=float(m.group(2).replace(',',''))
    rate=FX.get(cur, FX.get(cur.replace('S','$')))
    if rate is None: rate=1 if cur in ('','$') else None
    if rate is None: return None
    v=amt*rate
    return v if 1e6<=v<=5e11 else None
def year(s):
    m=re.search(r'(20\d\d|19\d\d)',s); return int(m.group(1)) if m else None
def rank(s):
    m=re.search(r'(\d[\d,\.]*)',s.replace('.',',')); 
    try: return int(m.group(1).replace(',','')) if m else None
    except: return None
COUNTRIES=['United States','United Kingdom','United Arab Emirates','China','India','Brazil','Germany','France','Japan','Canada','Australia','Singapore','Switzerland','Netherlands','Sweden','Israel','Spain','Italy','South Korea','Korea','Saudi Arabia','Qatar','Hong Kong','Taiwan','Mexico','Indonesia','Ireland','Norway','Denmark','Finland','Belgium','Austria','Poland','Russia','Turkey','Argentina','Chile','Colombia','Peru','South Africa','Nigeria','Egypt','Kenya','Thailand','Vietnam','Philippines','Malaysia','New Zealand','Portugal','Greece','Czech Republic','Romania','Hungary','Luxembourg','Estonia','Lithuania','Latvia','Ukraine','Kazakhstan','Pakistan','Bangladesh','Sri Lanka','Kuwait','Bahrain','Oman','Jordan','Morocco','Iran','Cayman Islands','Bermuda','Jersey','Guernsey','Cyprus','Malta','Iceland','Slovenia','Croatia','Serbia','Bulgaria','Slovakia','Uruguay','Ecuador','Ghana','Monaco','Liechtenstein','Azerbaijan','Georgia','Armenia','Mongolia','Myanmar','Cambodia','Uzbekistan']
US_STATES='Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington West_Virginia Wisconsin Wyoming District_of_Columbia'.replace('_',' ').split()
US_STATES=[s.replace('_',' ') for s in 'Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington West_Virginia Wisconsin Wyoming District_of_Columbia'.split()]
def country(hq):
    parts=[p.strip(' .') for p in hq.replace('…','').split(',') if p.strip(' .')]
    if not parts: return ''
    last=parts[-1]
    for c in COUNTRIES:
        if len(last)>=3 and (c.lower().startswith(last.lower()) or last.lower().startswith(c.lower()[:max(3,len(last))])): 
            if last.lower().startswith('united'):
                if len(last)>=8: return {'s':'United States','k':'United Kingdom','a':'United Arab Emirates'}.get(last[7:8].lower(),'')
                return ''
            return c
    if len(parts)>=2 and any(parts[1].lower().startswith(s.lower()[:6]) for s in US_STATES): return 'United States'
    return ''
# ---------- sectors (ordered; first match on the industries string wins, with first-listed industry weighted)
SECT=[('Crypto, Web3 & Trading',r'crypto|blockchain|bitcoin|ethereum|web3|nft|decentrali|digital asset|stock exchange|trading platform'),
 ('AI & Machine Learning',r'artific|ai infrastructure|agentic|machine learning|generative|\bai\b|deep learning|natural language|computer vision|predictive analytics|intelligent systems'),
 ('Cybersecurity & IT',r'cyber|security|network security|identity management|fraud detection|privacy|it management|information technology|it infrastructure'),
 ('Fintech & Payments',r'fintech|payment|lending|credit|debt|emerging finan|advice|accounting|tax|business development|bdc|credit card|mobile payments|personal finance|financial services|wealth management|insurtech|neobank|banking|bank\b|insurance|asset management|venture capital|private equity|hedge fund|finance|financial'),
 ('Cloud, Data Centers & Telecom',r'cloud|data center|data centre|communications inf|telecom|wireless|internet service|broadband|5g|satellite communication|network infrastructure|hosting|mobile network'),
 ('Semiconductors & Hardware',r'semiconductor|communication hard|chip|electronics|hardware|computer|optical|photonics|quantum|embedded|sensor|electrical'),
 ('Space, Aerospace & Defense',r'aerospace|space|satellite|defense|defence|military|drone|aviation|national security|government'),
 ('Energy & Utilities',r'energy|enerey|environmental|carbon capture|carton capture|waste|recycling|water|charging infra|oil and gas|oil & gas|renewable|solar|wind|power|utilities|electric vehicle charging|nuclear|battery|clean ?tech|fuel|hydrogen|natural gas|electrical distribution'),
 ('Mining, Metals & Chemicals',r'mining|metal|mineral|chemical|steel|gold|copper|lithium|materials|building material|plastics'),
 ('Health, Biotech & Pharma',r'health|biotech|pharma|alternative medic|dietary|bioinformatic|medical|hospital|therapeutic|biopharma|life science|diagnostics|clinical|genetic|drug|wellness|dental|neuroscience|oncology'),
 ('Automotive, Mobility & Logistics',r'automotive|electric vehicle|autonomous vehicle|mobility|transportation|logistics|shipping|freight|delivery|supply chain|ride sharing|airline|railroad|public transportation|trucking|marine'),
 ('Industrial, Manufacturing & Robotics',r'industrial|manufactu|robotics|business process|printing|automation|machinery|3d printing|construction|engineering|packaging'),
 ('Real Estate & Construction',r'real estate|building mat|building maint|property|commercial real estate|construction|architecture|home building|reit|smart building'),
 ('Consumer, Retail & Food',r'consumer|agricultur|agtech|farming|retail|e-commerce|ecommerce|fashion|apparel|food|beverage|restaurant|grocery|beauty|cosmetic|luxury|sports|fitness|pet|furniture|home|wine|spirits|marketplace'),
 ('Media, Entertainment & Gaming',r'media|entertainment|gaming|video game|music|film|content|advertising|marketing|publishing|news|social media|esports|streaming|digital media|broadcasting'),
 ('Travel & Hospitality',r'travel|hospitality|hotel|tourism|leisure'),
 ('Professional & Business Services',r'consulting|human reso|staffing|recruit|employee benefit|customer service|facilities|outsourc|legal|professional services'),
 ('Software & SaaS',r'augmented reality|application perf|information|software|saas|enterprise|developer|analytics|crm|productivity|apps|information services|internet|database|it services|collaboration|b2b|platform|edtech|education|legal|human resources|recruiting')]
def sector(ind):
    s=re.sub(r'\bal\b','ai',ind.lower()).replace('artifc','artific')
    first=s.split(',')[0]
    for name,pat in SECT:
        if re.search(pat,first): return name
    for name,pat in SECT:
        if re.search(pat,s): return name
    return 'Other / Unclassified'
PREMIUM={'United States','United Kingdom','United Arab Emirates','Saudi Arabia','Qatar','Germany','France','Switzerland','Netherlands','Japan','Singapore','Australia','Canada','Italy','Spain','Monaco','Sweden','Ireland','Belgium','Austria','Hong Kong','South Korea','Luxembourg','Norway','Denmark','Finland','Israel','Bahrain','Kuwait'}
OVERRIDE={'China','India','Brazil'}; BLOCK={'Russia','Iran','Belarus','North Korea','Syria','Cuba','Venezuela','Myanmar'}
SECT_FIT={'AI & Machine Learning':12,'Crypto, Web3 & Trading':12,'Fintech & Payments':10,'Cybersecurity & IT':10,'Cloud, Data Centers & Telecom':10,'Software & SaaS':9,'Semiconductors & Hardware':9,
 'Energy & Utilities':8,'Consumer, Retail & Food':9,'Travel & Hospitality':9,'Automotive, Mobility & Logistics':8,'Space, Aerospace & Defense':6,'Industrial, Manufacturing & Robotics':7,
 'Media, Entertainment & Gaming':8,'Professional & Business Services':7,'Real Estate & Construction':7,'Mining, Metals & Chemicals':6,'Health, Biotech & Pharma':3,'Other / Unclassified':4}
# delivered index + exclusions
TAB=lambda f:f.split('/')[-1].replace('_rows.json','').replace('_',' ').title()
done={}
for f in glob.glob('/home/user/rg42/f1run/runs/*_rows.json'):
    try: rows=json.load(open(f))
    except Exception: continue
    if not isinstance(rows,list): continue
    for r in rows:
        if isinstance(r,dict) and r.get('brand'):
            for n in (r['brand'],r.get('email_name')):
                if len(key(n))>=3: done.setdefault(key(n),('Declined' if r.get('skip') else 'Templated')+' ('+TAB(f)+')')
grid={key(n):t for n,t in json.load(open('rec2/grid.json')).items() if len(key(n))>=2}
ex=json.load(open('/home/user/rg42/f1run/runs/exclusions.json')); ex=ex if isinstance(ex,list) else ex.get('names',[])
exk={key(x) for x in ex}
out=[]
for k,c in ckeys.items():
    o=obs.get(k,{})
    top=lambda fld:(o[fld].most_common(1)[0][0] if fld in o and o[fld] else '')
    ind=top('industries'); hq=top('hq').strip("‘'`’ "); tot=None
    for v,_ in (o.get('total') or collections.Counter()).most_common(3):
        tot=money(v)
        if tot: break
    rk=None
    for v,_ in (o.get('rank') or collections.Counter()).most_common(3):
        rk=rank(v)
        if rk: break
    yr=None
    for v,_ in (o.get('date') or collections.Counter()).most_common(3):
        yr=year(v)
        if yr: break
    stg=top('stage'); ctry=country(hq) if hq else ''
    hasdata=bool(ind or hq or tot or rk)
    sec=(sector(ind) if ind else 'Other / Unclassified') if hasdata else 'No data read'
    # score
    sc=0
    if tot: sc+=min(30,max(0,(math.log10(tot)-7.7)*23))   # $50M=0, ~$1bn=30
    if rk: sc+=max(0,min(25,25-(math.log10(rk)-1)*6))      # CB rank 10->25, 1k->13, 100k->1
    if yr: sc+={2026:15,2025:12,2024:8,2023:5}.get(yr,2 if yr>=2020 else 0)
    if ctry in PREMIUM: sc+=15
    elif ctry in OVERRIDE: sc+=3
    elif ctry: sc+=8
    sc+=SECT_FIT.get(sec,4)
    if 'public' in stg.lower() or 'ipo' in stg.lower(): sc+=3
    conf='High' if c['frames']>=5 else 'Medium' if c['frames']>=3 else 'Low'
    if conf=='Low': sc-=5
    status=done.get(k,'')
    fw=key(c['name'].split()[0]) if c['name'].split() else ''
    if k in grid: status=f'Already an F1 partner ({grid[k]})'
    elif len(fw)>=5 and fw in grid and len(c['name'].split())<=3: status=f'Likely F1 partner, check ({grid[fw]})'
    if k in exk: status='Excluded (your remove list)'
    if ctry in BLOCK: status=status or 'Declined: sanctioned/restricted country'
    flag='China/India/Brazil HQ override' if ctry in OVERRIDE else ''
    out.append(dict(hasdata=hasdata,name=c['name'],sector=sec,industries=ind,hq=hq.replace('…',''),country=ctry,total=tot,rank=rk,year=yr,stage=stg,score=round(sc,1),conf=conf,status=status,flag=flag,frames=c['frames']))
_act=sorted([x['score'] for x in out if not x['status'] and x['hasdata']],reverse=True)
_cut=lambda q:_act[min(len(_act)-1,int(len(_act)*q))] if _act else 0
T1,T2,T3=_cut(0.10),_cut(0.30),_cut(0.60)
def tier(s): return 'Top' if s>=T1 else 'High' if s>=T2 else 'Medium' if s>=T3 else 'Low'
wb=openpyxl.Workbook(); rd=wb.active; rd.title='Read me'
bys=collections.defaultdict(list)
for x in out: bys[x['sector']].append(x)
order=sorted(bys,key=lambda s:(s=='No data read',s=='Other / Unclassified',-len(bys[s])))
summ=wb.create_sheet('Summary'); summ.append(['Sector tab','Brands','Top','High','Medium','Low','Already templated / excluded'])
hdr=['Rank','Brand','Priority','Score','HQ location','HQ country','Total funding (USD est.)','Last funding year','CB rank','Industries (Crunchbase)','Stage','Status','Flag','Read confidence']
for s in order:
    L=sorted(bys[s],key=lambda x:(bool(x['status']),-x['score'])) if s!='No data read' else sorted(bys[s],key=lambda x:-x['frames'])
    ws=wb.create_sheet(s[:31].replace('/','-').replace(',',''))
    ws.append(hdr); n=0
    for x in L:
        nd=(s=='No data read'); n+=1 if not x['status'] and not nd else 0
        ws.append([n if not x['status'] and not nd else '',x['name'],(tier(x['score']) if not nd else 'Unscored') if not x['status'] else '—',x['score'],x['hq'],x['country'],round(x['total']) if x['total'] else None,x['year'],x['rank'],x['industries'],x['stage'],x['status'],x['flag'],x['conf']])
    for i,wd in enumerate([6,34,9,7,34,16,20,10,9,40,14,34,26,10]): ws.column_dimensions[openpyxl.utils.get_column_letter(i+1)].width=wd
    for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F3864')
    for row in ws.iter_rows(min_row=2,min_col=7,max_col=7):
        for c in row: c.number_format='#,##0'
    ws.freeze_panes='C2'; ws.auto_filter.ref=ws.dimensions
    act=[x for x in L if not x['status']]
    summ.append([s,len(L)]+([sum(1 for x in act if tier(x['score'])==t) for t in ('Top','High','Medium','Low')] if s!='No data read' else ['unscored','','',''])+[len(L)-len(act)])
for i,wd in enumerate([38,9,7,7,9,7,26]): summ.column_dimensions[openpyxl.utils.get_column_letter(i+1)].width=wd
for c in summ[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F3864')
cov=sum(1 for x in out if x['industries']); 
for line in ['Brands from your 10 Crunchbase screen recordings, sorted into sector tabs and ranked for outreach (Rank 1 = contact first).',
 'Sector = from the Crunchbase Industries column shown in the recording (first-listed industry wins).',
 'Score (0-100) = total funding (capacity, up to 30) + Crunchbase rank (prominence, up to 25) + last funding year (recent cash and intent, up to 15) + HQ market (US/UK/Europe/Gulf/Japan/Singapore/Australia/Canada 15; China/India/Brazil 3 under the override rule; others 8) + sector fit for F1 B2B sponsorship (3-12), +3 if public, -5 if the name was read in only 2 frames.',
 f'Priority tiers are relative across all brands: Top = top 10% of scores ({T1:.0f}+), High = next 20% ({T2:.0f}+), Medium = next 30% ({T3:.0f}+), Low = the rest. Brands already templated, declined or on your remove list are listed at the bottom of each tab without a rank.',
 f'Coverage: {len(out)} brands; industries read for {cov}. Brands whose rows were on screen too briefly for the 3-second sampling (or whose names were misread) are in the "No data read" tab, unranked and sorted by how often they appeared. "Other / Unclassified" holds brands with data but no clear sector.',
 'Brands already partnered with an F1 team (from the team sponsor lists on f1salaries.com, 2 Nov 2026) are marked "Already an F1 partner" and not ranked.',
 'Values are read by OCR from the recordings: HQ text and industries are cut off where Crunchbase truncated them on screen; funding in other currencies is converted to USD at rough rates. Check a brand before acting on it.']:
    rd.append([line])
rd.column_dimensions['A'].width=150
wb.save('Screen Recording Brands - Sector Tabs Ranked.xlsx')
print('brands',len(out),'with data',cov); print({s:len(bys[s]) for s in order})
