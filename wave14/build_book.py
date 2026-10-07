import json,glob,re,unicodedata,os,datetime
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
W=os.path.dirname(os.path.abspath(__file__))+'/'; OUT=os.path.abspath(W+'../reports/F1-Wave14-V3-Broad-2026-10.xlsx')
STOP={'inc','corp','corporation','co','ltd','llc','plc','sa','ag','nv','se','spa','group','holdings','holding','company','limited','technologies','technology','intl','international','ab','gmbh','kk','oyj','asa','bhd','tbk','pcl','pt','sdn','ltda','srl','bv','oy','as','kgaa','sas','the','sab','de','cv','jsc','pjsc','psc','qsc','pao','ao','ooo','berhad','public'}
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
    s=re.sub(r'\(.*?\)','',s); s=re.sub(r'[^a-z0-9 ]',' ',s)
    return ' '.join(w for w in s.split() if w not in STOP)
HARD=re.compile(r'f1|formula|grand prix|sponsor|partner|market cap|valuation|headcount|employees|sanction|entity list|1260h|uflpa|acquired|defunct|merged|distress|wind-down|going concern|restructur|cost-cutting|duplicate|subsidiary|listed; out of|below usd|under usd|equity|priced round|24-month|24 month',re.I)
NEWMAP={'NEW: Gaming & Gambling':'NEW: Gambling & Lotteries','NEW: Consumer Subscription & Genealogy':'53 Consumer & Lifestyle','NEW: Utilities':'NEW: Utilities & Power','NEW: Electric & Gas Utilities':'NEW: Utilities & Power','NEW: Pharma & Medical Devices':'NEW: Pharma & Biotech','NEW: Education & Childcare':'NEW: Education & EdTech','NEW: Edtech':'NEW: Education & EdTech','NEW: Security & Electrical Distribution':'X13 Industrial & MRO Distribution','NEW: Construction & Engineering Contractors':'NEW: Construction & Engineering'}
MANUAL_RECLASS={
 'vipps mobilepay':('Stretch','Owned by a consortium of Nordic banks with no published valuation; passes on the member-owned market-leader exception (Norway/Denmark/Finland payments leader, ~USD 200M revenue), capped at Stretch with flag no published valuation. No F1 tie found.'),
 'bright food':('Low-value','Passes v3 gates (Shanghai state-owned, revenue ~USD 17.7B, 44k staff, no F1 tie). Controlling parent of Tnuva (verified separately), kept as its own row: state entity with China-centred brands and no F1 marketing motive, fit 2 at best.'),
 "christie's":('No','F1 tie via controlling parent: Artemis (Pinault family) wholly owns Christie\'s and controls Kering (59% of votes), whose Gucci brand is Alpine title partner from 2027 (announced May 2026). Same treatment as Hema under Alibaba and OTE under Deutsche Telekom: a company controlled by a tied group is excluded under v3 rule 4.'),
 'hd hyundai':('Stretch','Passes v3 gates (market cap ~USD 10.8B, no F1 tie; Hyundai Motor Group states it has no F1 project). Holding-company parent of HD Hyundai Heavy, which is already on this wave as Yes: kept as a separate row with a common-owner flag rather than a duplicate, capped at Stretch.'),
 'revelyst':('Stretch','Passes v3 gates: transacted EV USD 1.125B (SVP acquisition, Jan 2025), ~USD 1.3B revenue, 1k-5k staff, no distress. The Bell trademark (Bell Sports, a Revelyst brand) is licensed to the independent Racing Force Group, whose Bell Racing Helmets unit is a Ferrari technical partner; Revelyst itself has no F1 deal, so the licence is treated as a flag (cap Stretch) rather than a controlled-brand tie. Watch for channel conflict with Bell Racing.'),
 'nordic knots':('No','Fails filter 1 (valuation below USD 1B): the 27 Mar 2026 round is reported by secondary press at USD 2.2B post-money, but investor Creades\' own release says SEK 105.4M bought about 5%, implying roughly SEK 2.1B (about USD 0.22B). The primary source is taken over what looks like a SEK-to-USD conversion error; VC-backed, so no unpublished-valuation exemption. Headcount 20-100, also unconfirmed.'),
 'glossier':('Stretch','Passes v3 gates on the letter: last transacted valuation USD 1.8B (Series E, Aug 2021), 51+ staff, no F1 tie found and not on F1 Academy partner lists. Capped at Stretch with flags: valuation stale (no priced round since 2021), an Apr 2025 raise attempt reportedly at under USD 1B did not price, and Jun 2026 financing was a USD 45M debt facility, so current value and capacity are in doubt. Confirm before outreach.'),
 'immunai':('Low-value','Passes v3 gates on the letter: last transacted valuation just over USD 1B (Oct 2021), 51+ staff, no F1 tie found. Stale valuation flag (no round since 2021). B2B AI-biotech with no consumer marketing motive, fit 1.'),
 'upside foods':('Low-value','Passes v3 gates on the letter: USD 1.0B post-money (Series C, Apr 2022) meets the floor exactly, 51+ staff, no F1 tie found. Flags: stale valuation (no priced round since 2022), layoff rounds in 2024-25 with sizes mostly undisclosed, product still pre-commercial at scale. Treated like other 2021-22 unicorns with no refresh (Glossier, Immunai): kept with flags rather than rejected. Low-value: no marketing function evidenced and fit at most 2.'),
 'hhla (hamburger hafen und logistik)':('No','F1 tie via joint control: MSC, an F1 global partner, holds 49.9% of HHLA alongside the City of Hamburg (50.1%) and the two are described as jointly managing the company. Same treatment as Froneri (Nestle/PAI) and Borouge under v3 rule 4. Valuation (EUR 1.62B market cap), headcount (7,396) and capacity otherwise pass.'),
}  # norm(company) -> (verdict, reason)
base=json.load(open(W+'verified_base.json')); deferred=json.load(open(W+'deferred.json'))
for _r in base['verified']:
    if _r.get('pool')=='F': _r['sector_tab']=re.sub(r'^F\s+','',str(_r.get('sector_tab','')))
    _r['verdict']={'low-value':'Low-value','yes':'Yes','stretch':'Stretch'}.get(str(_r.get('verdict','')).strip().lower(),_r.get('verdict'))
inputs={}
for f in sorted(glob.glob(W+'queue/*_input.json')):
    for r in json.load(open(f)): inputs[norm(r['company'])]=r
verified={norm(r['company']):dict(r) for r in base['verified']}
rejects=list(base['rejects'])
def dom(x):
    d=str(x or '').lower().replace('www.','').strip().split('/')[0]; return re.sub(r'\s*\(.*$','',d).strip()
base_domains={dom(r.get('domain')) for r in base['verified'] if dom(r.get('domain')) and '.' in dom(r.get('domain'))}
newrecs={}
for f in sorted(glob.glob(W+'results/*_verified.json')):
    try: arr=json.load(open(f))
    except Exception as e: print('bad json',f,e); continue
    for r in arr:
        if isinstance(r,dict) and r.get('company'): newrecs.setdefault(norm(r['company']),r)
for k,r in newrecs.items():
    if k in verified: continue
    v=str(r.get('verdict','')).strip().title().replace('Low Value','Low-value'); reason=str(r.get('verdict_reason',''))
    # a re-verification of a name already kept in this wave (same domain, or marked duplicate) is dropped silently, not added to rejects
    d=dom(r.get('domain'))
    if (d and '.' in d and d in base_domains) or (v=='No' and 'duplicate' in reason.lower()):
        verified[k]={'_rejected':True,'company':r['company'],'_dup':True}; continue
    v={'low-value':'Low-value','yes':'Yes','stretch':'Stretch','no':'No'}.get(str(v).strip().lower(),v)
    if k in MANUAL_RECLASS: v,reason=MANUAL_RECLASS[k]
    if v=='No' and not HARD.search(reason): v='Low-value'
    flags=' '.join(map(str,r.get('flags') or [])).lower()
    if v=='Yes' and 'no published valuation' in flags: v='Stretch'
    inp=inputs.get(k,{}); pool=inp.get('pool') or r.get('pool') or 'G'
    tab=r.get('sector_tab') or inp.get('sector_tab') or 'NEW: Unassigned'; tab=NEWMAP.get(tab,tab)
    rec={'company':r['company'],'sector_tab':tab,'pool':pool,'domain':r.get('domain'),'hq':r.get('hq'),'ownership':r.get('ownership'),'sells':r.get('sells'),'headcount_band':r.get('headcount_band'),'revenue':r.get('revenue'),'valuation':r.get('valuation'),'latest_raise':r.get('latest_raise'),'fit_score':r.get('fit_score'),'up_and_coming':'yes' if r.get('up_and_coming') in (True,'true','yes','True') else 'no','verdict':v,'verdict_reason':reason,'best_angle':r.get('best_angle'),'flags':'; '.join(map(str,r.get('flags') or [])) if isinstance(r.get('flags'),list) else r.get('flags'),'fit_detail':r.get('fit_detail')}
    if v=='No': rejects.append({'company':r['company'],'sector_tab':tab,'pool':pool,'reason':reason}); verified[k]={'_rejected':True,'company':r['company']}
    else: verified[k]=rec
rows=[v for v in verified.values() if not v.get('_rejected')]
# domain dedup
seen={}; out=[]
for r in rows:
    d=str(r.get('domain') or '').lower().replace('www.','').strip().split('/')[0]; d=re.sub(r'\s*\(.*$','',d)
    if d and '.' in d:
        if d in seen: continue
        seen[d]=1
    out.append(r)
rows=out
def fit(r):
    try: return int(float(r.get('fit_score') or 0))
    except: return 0
def prio(r): return {'Yes':60+fit(r)*8,'Stretch':40+fit(r)*6}.get(r['verdict'],20+fit(r)*4)
remaining=[inputs[k] for k in inputs if k not in verified]
json.dump(remaining,open(W+'remaining_active.json','w'),indent=1)
# ---- workbook
wb=Workbook(); rm=wb.active; rm.title='00 READ ME'
F='Arial'; BODY=Font(name=F,size=10); BOLD=Font(name=F,size=10,bold=True); TITLE=Font(name=F,size=12,bold=True)
HDR_FONT=Font(name=F,size=10,bold=True,color='FFFFFF'); HDR_FILL=PatternFill('solid',fgColor='1F3864'); WRAP=Alignment(wrap_text=True,vertical='top')
FILL={'Yes':PatternFill('solid',fgColor='CFE8FD'),'Stretch':PatternFill('solid',fgColor='FFF2CC'),'Low-value':PatternFill('solid',fgColor='F8CBAD')}
COLS=['also_on_tabs','rank','priority_score','company','sector_tab','source_pool','domain','hq','ownership','what_it_sells','headcount_band','revenue (dated, sourced)','valuation (dated, sourced)','latest_raise','fit_score','up_and_coming','verdict','verdict_reason','best_angle','flags','fit_detail']
KEYS=['company','sector_tab','pool','domain','hq','ownership','sells','headcount_band','revenue','valuation','latest_raise','fit_score','up_and_coming','verdict','verdict_reason','best_angle','flags','fit_detail']
WID=[30,6,8,30,26,8,22,22,30,40,14,36,36,30,6,9,10,60,40,40,40]
RED_FILL=PatternFill('solid',fgColor='FF0000'); RED_HDR=Font(name=F,size=10,bold=True,color='FFFFFF'); RED_NAME=Font(name=F,size=10,bold=True,color='C00000')
AMB_FILL=PatternFill('solid',fgColor='FFC000'); AMB_FONT=Font(name=F,size=10,bold=True,color='000000')
PRIORITY_KEYS=set(); UC_KEYS=set(); FR_KEYS=set()
def write_tab(ws,title,sub,rs,self_tab=None):
    ws['A1']=title; ws['A1'].font=TITLE; ws['A2']=sub; ws['A2'].font=BODY
    for j,h in enumerate(COLS,1): c=ws.cell(row=3,column=j,value=h); c.font=HDR_FONT; c.fill=HDR_FILL
    rs=sorted(rs,key=lambda r:(-prio(r),str(r['company'])))
    for i,r in enumerate(rs,1):
        k=norm(r['company']); labs=[]
        if k in PRIORITY_KEYS and self_tab!='01': labs.append('01 PRIORITY')
        if k in UC_KEYS and self_tab!='02': labs.append('02 UP-AND-COMING')
        if k in FR_KEYS and self_tab!='03': labs.append('03 FUNDED $100M+')
        on_prio='01 PRIORITY' in labs
        vals=[('; '.join(labs) if labs else ''),i,prio(r)]+[r.get(kk) for kk in KEYS]
        if r.get('pool')=='F': vals[4]='F '+str(r.get('sector_tab'))
        for j,v in enumerate(vals,1):
            c=ws.cell(row=i+3,column=j,value=v if not isinstance(v,(list,dict)) else json.dumps(v)); c.font=BODY; c.alignment=WRAP
            if r['verdict'] in FILL: c.fill=FILL[r['verdict']]
            if j==1 and on_prio: c.fill=RED_FILL; c.font=RED_HDR
            elif j==1 and labs: c.fill=AMB_FILL; c.font=AMB_FONT
            if j==4 and on_prio: c.font=RED_NAME
    for j,w in enumerate(WID,1): ws.column_dimensions[ws.cell(row=3,column=j).column_letter].width=w
    ws.freeze_panes='A4'
def tabname(r):
    t=str(r['sector_tab']) if r.get('pool')!='F' else 'F '+str(r['sector_tab'])
    t=re.sub(r'[:\[\]\*\?/\\]','',t).replace('  ',' ').strip()
    return t[:31]
bytab={}
for r in rows: bytab.setdefault(tabname(r),[]).append(r)
ny=sum(r['verdict']=='Yes' for r in rows); ns=sum(r['verdict']=='Stretch' for r in rows); nl=sum(r['verdict']=='Low-value' for r in rows); nu=sum(str(r.get('up_and_coming')).lower()=='yes' for r in rows)
ws=wb.create_sheet('01 PRIORITY (all Yes)')
py=[r for r in rows if r['verdict']=='Yes']
nF=sum(1 for r in py if r.get('pool')=='F')
PRIORITY_KEYS.update(norm(r['company']) for r in py)
UC_KEYS.update(norm(r['company']) for r in rows if str(r.get('up_and_coming')).lower()=='yes')
FR_KEYS.update(norm(r['company']) for r in rows if r.get('pool')=='F')
write_tab(ws,f'PRIORITY LIST: EVERY YES VERDICT, ALL SECTORS — {len(py)} names ({len(py)-nF} at USD 1B+ valuation, {nF} on the USD 100M+ funded track), ranked best first','Highest-conviction prospects only: passed every v3 hard filter (51+ staff, no distress, no F1 tie direct or via controlling parent, not sanctioned) with fit 3+ and no capping flag. USD 1B+ names and USD 100M+ funded names (source_pool F, sector_tab prefixed F) sit side by side; sort or filter on source_pool to separate them. Sorted by priority_score. The same rows also sit on their sector tabs. Stretch and red rows are NOT on this tab.',py,self_tab='01')
ws=wb.create_sheet('02 UP-AND-COMING (all)'); uc=[r for r in rows if str(r.get('up_and_coming')).lower()=='yes']
write_tab(ws,f'UP-AND-COMING BRANDS, ALL SECTORS — {len(uc)} names: crossed $1B within 24 months, growing >40%/yr, 2025-26 IPO, visible challenger, or announced new-market entry','Consolidated view of every up_and_coming=yes brand across all tabs, ranked best first. The same rows also sit on their sector tabs.',uc,self_tab='02')
ws=wb.create_sheet('03 FUNDED $100M+ (all)'); fr=[r for r in rows if r.get('pool')=='F']
write_tab(ws,f'TRACK F: FUNDED USD 100M+ BUT BELOW USD 1B VALUATION — {len(fr)} names','Separate track: private companies with >= USD 100M cumulative funding and a priced round in the last 24 months, valuation below USD 1B or unknown. Same verdicts and red marking as the main list. Never mixed into the USD 1B tabs; the same rows also sit on their F-prefixed sector tabs.',fr,self_tab='03')
main_tabs=sorted(t for t in bytab if not t.startswith('F ')); f_tabs=sorted(t for t in bytab if t.startswith('F '))
for t in main_tabs+f_tabs:
    ws=wb.create_sheet(t); write_tab(ws,f'{t} — Wave 14 (v3) — {len(bytab[t])} names','Fresh names only (nothing here is in the master, the expansion book or an earlier batch). Ranked best first; red rows = Low-value.',bytab[t])
ws=wb.create_sheet('98 PENDING'); ws['A1']=f'Queued for verification: {len(remaining)} active | {len(deferred)} deferred (index-miner listed mid-caps, run paused on 6 Oct 2026 to protect the weekly usage limit; ~85% of this pool has come back Low-value)'; ws['A1'].font=TITLE
for j,h in enumerate(['company','sector_tab','pool','status'],1): c=ws.cell(row=3,column=j,value=h); c.font=HDR_FONT; c.fill=HDR_FILL
i=4
for r in remaining:
    for j,v in enumerate([r['company'],r['sector_tab'],r.get('pool'),'active'],1): ws.cell(row=i,column=j,value=v).font=BODY
    i+=1
for r in deferred:
    for j,v in enumerate([r['company'],r['sector_tab'],r.get('pool'),'deferred (index-miner)'],1): ws.cell(row=i,column=j,value=v).font=BODY
    i+=1
for col,w in zip('ABCD',(32,30,8,24)): ws.column_dimensions[col].width=w
ws=wb.create_sheet('99 REJECTS'); ws['A1']=f'Failed a v3 hard filter — {len(rejects)} names'; ws['A1'].font=TITLE
for j,h in enumerate(['company','sector_tab','pool','reason'],1): c=ws.cell(row=3,column=j,value=h); c.font=HDR_FONT; c.fill=HDR_FILL
for i,r in enumerate(rejects,4):
    for j,v in enumerate([r['company'],r['sector_tab'],r.get('pool'),r['reason']],1): c=ws.cell(row=i,column=j,value=v); c.font=BODY; c.alignment=WRAP
for col,w in zip('ABCD',(32,30,8,100)): ws.column_dimensions[col].width=w
status=('COMPLETE (index-miner pool of %d listed mid-caps deferred to a later run)'%len(deferred)) if not remaining else 'IN PROGRESS'
lines=json.load(open(W+'readme_lines.json'))[:6]
lines[0]=f'F1 WAVE 14 — BROAD DISCOVERY UNDER v3 PARAMETERS ({datetime.date.today():%d %b %Y})'
lines+=[f'Status: {status} — verified {len(rows)+len(rejects)} | kept {len(rows)} ({ny} Yes / {ns} Stretch / {nl} Low-value) | rejected {len(rejects)} | pending {len(remaining)} active + {len(deferred)} deferred | up-and-coming {nu}','','TAB INDEX','tab | names | Yes | Stretch | Low-value']
for t in main_tabs+f_tabs:
    rs=bytab[t]; lines.append(f"{t} | {len(rs)} | {sum(r['verdict']=='Yes' for r in rs)} | {sum(r['verdict']=='Stretch' for r in rs)} | {sum(r['verdict']=='Low-value' for r in rs)}")
for i,l in enumerate(lines,1):
    c=rm.cell(row=i,column=1,value=l); c.font=BOLD if i==1 or l=='TAB INDEX' else BODY; c.alignment=WRAP
rm.column_dimensions['A'].width=140
wb.save(OUT)
print(f'verified {len(rows)+len(rejects)} keep {len(rows)} (Y{ny} S{ns} L{nl}) rejects {len(rejects)} remaining {len(remaining)} active + {len(deferred)} deferred tabs {len(bytab)} -> {OUT}')
