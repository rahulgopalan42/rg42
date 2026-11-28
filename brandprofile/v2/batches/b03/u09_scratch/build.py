import re,html,json,glob
C=[]
def add(name,web,hq,desc,parent,src,sector=''):
    C.append(dict(name=html.unescape(name).replace('\\u0026','&').strip(),website=web.strip().rstrip('/').replace('https://','').replace('http://','').replace('www.','') if web else '',hq=hq,desc=desc.replace('\\u0026','&'),parent=parent,source=src,sector_hint=sector))
# Vista
s=open('vista.html',encoding='utf-8',errors='ignore').read()
for m in re.finditer(r'data-status="(\w+)".*?data-slug="([^"]+)"\s+data-search="([^"]+)"',s,re.S):
    if m.group(1)!='current': continue
    t=html.unescape(html.unescape(m.group(3)))
    # name = before description; find via slug words
    words=m.group(2).replace('-',' ')
    loc=re.search(r'\.\s+([^.]+?)\s+current\s',t)
    hq=loc.group(1) if loc else ''
    desc=t[:loc.start()+1] if loc else t
    add(m.group(2).replace('-',' ').title(),'',hq,desc,'Vista Equity Partners','https://www.vistaequitypartners.com/companies/')
# Silver Lake
s=open('silverlake.html',encoding='utf-8',errors='ignore').read()
for m in re.finditer(r"data-groups='([^']*)'.*?href=\"(/portfolio/[^\"]+)\">\s*(.*?)\s*</a>\s*</h3>\s*<p[^>]*>(.*?)</p>",s,re.S):
    if 'current' in m.group(1): add(m.group(3),'','',html.unescape(m.group(4)),'Silver Lake','https://www.silverlake.com/portfolio/',html.unescape(m.group(4)))
# Hg
s=open('hg.html',encoding='utf-8',errors='ignore').read().replace('\\"','"')
seen={}
for m in re.finditer(r'"__typename":"Company".{0,600}?"slug":"([^"]+)","title":"([^"]+)","shortDescription":"([^"]*)","stage":\["(\w+)"\]',s,re.S):
    seen[m.group(2).strip()]=(m.group(4),m.group(3))
for k,v in seen.items():
    if v[0]=='Current': add(k,'','',v[1],'Hg','https://hgcapital.com/portfolio')
# Triton
L=open('tri_all.txt').read().split('\n'); ss=set()
for i,l in enumerate(L):
    if l=='Current' and L[i-1] in ('TMM','TSM','TSC','TIF') and L[i-5] not in ss:
        ss.add(L[i-5]); add(L[i-5],'',L[i-2],L[i-4],'Triton Partners','https://www.triton-partners.com/portfolio',L[i-4])
# LGP
L=open('lgp.txt').read().split('\n')
for i,l in enumerate(L):
    if l=='Status: Current':
        j=i-1
        while j>0 and not L[j].startswith('Sector:'): j-=1
        k=j-1
        while k>0 and not (('.' in L[k]) and (' ' not in L[k]) and len(L[k])<40): k-=1
        add(L[k-2],L[k].split('/')[0],L[k-1],L[k+1],'Leonard Green & Partners','https://www.leonardgreen.com/portfolio/',L[j].replace('Sector: ',''))
# Genstar
L=open('gen_all.txt').read().split('\n'); ss=set()
for i,l in enumerate(L):
    if l=='Status:' and L[i+1].replace(' ','').startswith('Current'):
        name=L[i-3]
        if name=='Driving Efficiency Forward': name='OTC Industrial Technologies'
        if name in ss: continue
        ss.add(name); add(name,L[i-1],'',L[i-2],'Genstar Capital','https://www.gencap.com/companies/',L[i+3] if L[i+2]=='Sector:' else '')
# EQT
s=open('eqt3.html',encoding='utf-8',errors='ignore').read().replace('\\"','"')
for funds,title in re.findall(r'"snowflakeFunds":\[(.*?)\],"snowflakeOverrideFunds".*?"title":"([^"]+)"',s,re.S):
    m=re.search(r'"market":"([^"]*)","sector":"([^"]*)"',funds); f=re.search(r'"fundName":"([^"]*)"',funds)
    add(title,'',m.group(1) if m else '',(m.group(2) if m else '')+' ('+(f.group(1) if f else '')+')','EQT','https://eqtgroup.com/about/current-portfolio')
# Ardian
for line in open('ardian_list.txt'):
    p=[x.strip() for x in line.split(' | ')]
    if len(p)<7: continue
    web=p[5] if '?' not in p[5] else ''
    add(p[0],web.split('/')[2] if web.startswith('http') else web,p[2],p[6],'Ardian ('+p[1]+')','https://www.ardian.com/expertise/our-portfolio',p[4])
# Nordic case studies
for n in ['ActiveViam','ADVANZ PHARMA','ArisGlobal','Autocirc','Cary Group','Cint','corpuls','Duco','iLOQ','Itiviti','Macrobond','Max Matthiessen','NOBA Bank Group','Nordnet','Regnology','Sortera','Sunrise Medical','Surgical Information Systems','The Binding Site','Vivecti Group']:
    add(n,'','','case study (status not stated on list)','Nordic Capital','https://www.nordiccapital.com/portfolio-cases/')
for n in ['Urbaser','Peranel','De Wave Group','Heat Controller','Motors & Armatures','Unical Aviation','Infratech','Trime','Pelican Products','Peli BioThermal','EDP','Soulshine Farms']:
    add(n,'','','named on homepage','Platinum Equity','https://www.platinumequity.com/')
for n in ['ROSEN Group','International Schools Partnership','SureWerx','AMMEGA','Rawlings Sporting Goods','SEG','Emeria']:
    add(n,'','','named on PE page (case study / news)','Partners Group','https://www.partnersgroup.com/en/our-investments/private-equity')
with open('cands.jsonl','w') as f:
    for c in C: f.write(json.dumps(c)+'\n')
print(len(C))
