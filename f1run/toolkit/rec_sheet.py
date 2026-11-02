# Builds "Screen Recordings - Company List.xlsx" from rec/companies.json, matched against delivered tabs
import json,glob,re,openpyxl
from openpyxl.styles import Font,PatternFill
SUF=r'\b(inc|corp|corporation|ltd|limited|plc|llc|ag|sa|se|nv|co|company|group|holdings?|technologies|technology|the|labs?|ai)\b'
key=lambda s:re.sub(r'[^a-z0-9]','',re.sub(SUF,'',(s or '').lower()))
TAB=lambda f:f.split('/')[-1].replace('_rows.json','').replace('_',' ').title()
idx={}
for f in glob.glob('/home/user/rg42/f1run/runs/*_rows.json'):
    try: rows=json.load(open(f))
    except Exception: continue
    if not isinstance(rows,list): continue
    for r in rows:
        if not isinstance(r,dict) or 'brand' not in r: continue
        st=('Declined/skipped' if r.get('skip') else 'Template built')+' ('+TAB(f)+')'
        for n in (r['brand'],r.get('email_name')):
            k=key(n)
            if len(k)>=3: idx.setdefault(k,st)
d=json.load(open('rec/companies.json'))
vmap={'v1':'1','v2':'2','v3':'3','vS4':'S4','v5':'5','v6':'6','vS7':'S7','v8':'8','clip_1-02PM':'clip 1:02 PM','clip_1-21PM':'clip 1:21 PM'}
wb=openpyxl.Workbook(); ws=wb.active; ws.title='All companies'
ws.append(['Company (as read from the recording)','Confidence','Frames seen','Recording(s)','Already templated?'])
new=wb.create_sheet('Not yet templated'); new.append(['Company','Confidence','Frames seen','Recording(s)'])
n_new=n_done=0
for x in sorted(d,key=lambda x:x['name'].lower()):
    conf='High' if x['frames']>=5 else 'Medium' if x['frames']>=3 else 'Low'
    recs=', '.join(vmap.get(v,v) for v in x['videos'])
    st=idx.get(key(x['name']),'')
    ws.append([x['name'],conf,x['frames'],recs,st])
    if st: n_done+=1
    else: new.append([x['name'],conf,x['frames'],recs]); n_new+=1
for sh,w in ((ws,[44,11,11,20,48]),(new,[44,11,11,20])):
    for i,wd in enumerate(w): sh.column_dimensions[openpyxl.utils.get_column_letter(i+1)].width=wd
    for c in sh[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F3864')
    sh.freeze_panes='A2'; sh.auto_filter.ref=sh.dimensions
info=wb.create_sheet('Read me',0)
for line in ["Companies read from the 10 screen recordings (Crunchbase Advanced Search tables) in your Drive folder, 2 Nov 2026.",
             "Method: one frame per second, OCR of the 'Organization Name' column, then duplicates merged.",
             "Confidence = how many frames the name was read in: High 5+, Medium 3-4, Low 2. Low rows can be OCR misreads or cut-off names; check them before use.",
             f"Total companies: {len(d)}. Already templated in a delivered tab (by name match): {n_done}. Not yet templated: {n_new}.",
             "'Already templated?' matches on company name, so a few similar names may be matched or missed; check before building."]:
    info.append([line])
info.column_dimensions['A'].width=140
wb.save('Screen Recordings - Company List.xlsx')
import collections
print('total',len(d),'templated',n_done,'new',n_new)
print(collections.Counter(('High' if x['frames']>=5 else 'Medium' if x['frames']>=3 else 'Low') for x in d if not idx.get(key(x['name']))))
