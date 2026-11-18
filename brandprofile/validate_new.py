"""Checks on the new-brands workbook (run after newsectors.py xlsx)."""
import sys, json; sys.path.insert(0,'/home/user/rg42/brandprofile')
from openpyxl import load_workbook
from collections import Counter
import bp_build as b
import newsectors as ns
p=ns.OUT
wb=load_workbook(p,read_only=True)
SK=('Summary','Key','Left Out','On Your Sheet - Now Unlisted','Capacity To Confirm','Clay Leads (Unconfirmed)','Deals Announced - Watch')
tot_new=0; tot_have=0; names=Counter(); allrows=None; dom=0
for ws in wb.worksheets:
    if ws.title in SK: continue
    rows=list(ws.iter_rows(values_only=True)); hdr=rows[0]; body=rows[1:]
    assert len(hdr)==41 and hdr[28]=='Parent Company', (ws.title,len(hdr))
    i_on=hdr.index('On Your Sheet?'); i_tab=hdr.index('Category Tab (This Workbook)'); i_reach=hdr.index('Geographic Reach')
    new=[r for r in body if r[i_on]=='No (new brand)']; have=[r for r in body if r[i_on]=='Yes']
    assert len(new)+len(have)==len(body), ws.title
    bl=[(r[0],hdr[j]) for r in body for j in (0,1,3,4,5,13,15,17,28,30,31,32,33) if r[j] in (None,'')]
    assert not bl, (ws.title, bl[:5])
    if ws.title=='All New Brands': allrows=body; assert not have; continue
    if ws.title=='Domestic': assert all(r[i_reach]=='Domestic' for r in body) and not have; dom=len(body); continue
    assert all(r[i_tab][:31]==ws.title for r in body) and all(r[i_reach]!='Domestic' for r in body), ws.title
    tot_new+=len(new); tot_have+=len(have)
    for r in new: names[r[0]]+=1
    flags=[r[i_on] for r in body]; assert flags==sorted(flags), ws.title
print(len(wb.sheetnames),'tabs | category-tab new',tot_new,'+ domestic',dom,'=',tot_new+dom,'| All New Brands',len(allrows),'| on-sheet rows on NEW tabs',tot_have,'| dup',[n for n,c in names.items() if c>1])
assert tot_new+dom==len(allrows)
print('roster match:', [r[0] for r in allrows if b.f1_link(r[0])[0]])
hdr=[c for c in next(wb['All New Brands'].iter_rows(values_only=True))]
ih=hdr.index('How Found'); print('by pass:', Counter('subsidiaries pass' if str(r[ih]).startswith('Subsidiaries pass') else 'second' if str(r[ih]).startswith('Second pass') else 'first' for r in allrows))
io=hdr.index('Ownership Type'); ipc=hdr.index('Parent Company')
subs=[r for r in allrows if not str(r[ipc]).startswith(('None','Not stated'))]
print('with a parent company:', len(subs), '| F1 link in the group:', sum(1 for r in subs if 'F1 link' in str(r[ipc])), '| parent column values:', Counter(str(r[ipc]).split('(')[0].split(':')[0].strip()[:28] for r in allrows if str(r[ipc]).startswith(('None','Not stated'))).most_common(6))
print('priority', Counter(r[3] for r in allrows), '| reach', Counter(r[13] for r in allrows))
print('revenue cells numeric:', sum(1 for r in allrows if isinstance(r[7],(int,float))))
for t in ('Capacity To Confirm','Clay Leads (Unconfirmed)','Deals Announced - Watch','Left Out','On Your Sheet - Now Unlisted'):
    ws=wb[t]; n=sum(1 for _ in ws.iter_rows(values_only=True))-1; print(t,n)
conf={r[0] for r in wb['Capacity To Confirm'].iter_rows(values_only=True)}; leads={r[0] for r in wb['Clay Leads (Unconfirmed)'].iter_rows(values_only=True)}; main={r[0] for r in allrows}
print('overlap main/confirm',len(main&conf),'| main/leads',len(main&leads),'| confirm/leads',len(conf&leads))
import os; print(round(os.path.getsize(p)/1e6,2),'MB')
ws=wb['Summary']
for r in ws.iter_rows(values_only=True, max_row=8): print('  ',(r[0] if r else ''))
