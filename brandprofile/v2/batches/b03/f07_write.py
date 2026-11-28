"""scratch writer for f07_queue: fills default fields and appends records. usage: import and call w(rec, dest)"""
import json
IN={json.loads(l)['name']:json.loads(l) for l in open('/home/user/rg42/brandprofile/v2/batches/b03/in_f07.jsonl')}
B='/home/user/rg42/brandprofile/v2/batches/b03/'
def w(r, inname, dest='main'):
    i=IN[inname]
    d={"name":"","website":"","aliases":[],"hq_city":"","hq_country":i.get('hq_country',''),"sector":i.get('sector',''),"subsector":i.get('subsector',''),
       "desc":"","products":"","model":"B2B","customers":"","ownership_type":"requires verification","parent_immediate":"","parent_ultimate":"",
       "parent_listed":"none","pe_swf_owner":"","minority_investors":"","marketing_autonomy":"unknown","marketing_autonomy_basis":"","parent_backing":"",
       "employees":None,"countries":None,"stores_or_sites":"","markets":"","expansion_markets":"","reach":"Domestic","route":"none","fin":[],
       "qualifying_metric":"","alt_indicators":[],"exception_note":"","profitability":"unknown","profitability_basis":"","distress":"",
       "sponsorships":[],"signals":[],"fit":{},"fit_rationale":"","customer_overlap":"","category_conflict":"none found","f1_markets":"",
       "access":{"owner_led":"unknown","marketing_head_identified":"no","structure":"mid","roles":""},"compliance":"","outstanding":"",
       "sources":[],"verified":"2026-11-28","conf":"medium","signals_checked":"no"}
    if r.pop('_infin',True):
        kind='estimated' if i.get('via')=='Clay' else 'reported'
        if 'est.' in i.get('figure','') or 'estimate' in i.get('figure','').lower(): kind='estimated'
        m=i.get('metric') if i.get('metric') not in ('none',None,'') else 'transaction_value'
        d['fin'].append({"metric":m,"value_orig":i['figure'],"usd_m":i.get('usd_m'),"period":"","published":"","kind":kind,"source":i['source']})
    fin_extra=r.pop('fin',[])
    d.update(r); d['fin']=d['fin']+fin_extra
    if not d['name']: d['name']=inname
    d['discovered_via']=i.get('via',''); d['discovery_source']=i.get('source','')
    for k in ('b2b','ecosystem','technical','hospitality','geography','brand','consumer','category'): d['fit'].setdefault(k,0)
    if i['source'] not in d['sources']: d['sources'].append(i['source'])
    f=B+('f07_queue.jsonl' if dest=='main' else 'watch_f07_queue.jsonl')
    open(f,'a').write(json.dumps(d,ensure_ascii=False)+'\n')
    print('wrote',dest,d['name'])
def dup(name,why):
    open(B+'dups_f07_queue.jsonl','a').write(json.dumps({"name":name,"why":why},ensure_ascii=False)+'\n'); print('dup',name)
def patch(name, upd, dest='main'):
    f=B+('f07_queue.jsonl' if dest=='main' else 'watch_f07_queue.jsonl')
    L=[json.loads(l) for l in open(f)]
    for d in L:
        if d['name']==name:
            for k,v in upd.items():
                if k in ('signals','sources','sponsorships','fin','alt_indicators') and isinstance(v,list): d[k]=d[k]+[x for x in v if x not in d[k]]
                else: d[k]=v
    open(f,'w').write(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in L)); print('patched',name)
