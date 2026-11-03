# Usage: python3.13 -I contacts_sheet.py <names.txt> <final_send.json> <contacts.json {brand:{people,note}}> <out.xlsx> [alias=Brand ...]
import json, re, sys, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
names=[l.strip() for l in open(sys.argv[1]) if l.strip()]
rows={r['brand']:r for r in json.load(open(sys.argv[2]))}
C=json.load(open(sys.argv[3])); OUT=sys.argv[4]
AL=dict(a.split('=',1) for a in sys.argv[5:])
def status(r):
    if not r: return 'Template not built'
    if r.get('skip'): return 'Declined: '+re.sub(r'^DECLINED:\s*','',str(r['skip']))[:170]
    m=next((re.match(r'Reused: template first built in the (.+?) pack',str(f)) for f in r.get('flags',[]) if str(f).startswith('Reused:')),None)
    return f'Template reused ({m.group(1)} pack)' if m else 'Template built today'
wb=openpyxl.Workbook(); ws=wb.active; ws.title='Contacts'
ws.append(['#','Brand','Email name','Template status','Contact name','Title','Email','LinkedIn','Location','Contact note'])
s2=wb.create_sheet('Summary'); s2.append(['#','Brand','Template status','Contacts','Domain','Contact note'])
tot=0
for i,n in enumerate(names,1):
    b=AL.get(n,n); r=rows.get(b,{}); en=r.get('email_name') or b; st=status(r)
    c=C.get(b,{'people':[],'note':''}); ppl=c.get('people',[]); note=c.get('note','')
    if st.startswith('Declined'): ppl=[]; note='No contacts pulled (declined).'
    elif not ppl and not note: note='No contacts found.'
    s2.append([i,n,st,len(ppl),r.get('domain',''),note]); tot+=len(ppl)
    if not ppl: ws.append([i,n,en,st,'','','','','',note]); continue
    for j,p in enumerate(ppl): ws.append([i,n,en,st,p.get('name',''),p.get('title',''),p.get('email',''),p.get('linkedin',''),p.get('location',''),note if j==0 else ''])
for sh,widths in ((ws,[4,28,22,30,24,40,36,40,24,60]),(s2,[4,30,40,9,22,80])):
    for k,wd in enumerate(widths): sh.column_dimensions[openpyxl.utils.get_column_letter(k+1)].width=wd
    for c in sh[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F3864')
    sh.freeze_panes='A2'
    for row in sh.iter_rows(min_row=2):
        for c in row: c.alignment=Alignment(vertical='top',wrap_text=(sh is ws and c.column_letter in ('J','F')) or (sh is s2 and c.column_letter in ('C','F')))
wb.save(OUT); print('brands',len(names),'emails',tot,'with contacts',sum(1 for n in names if C.get(AL.get(n,n),{}).get('people') and not rows.get(AL.get(n,n),{}).get('skip')))
