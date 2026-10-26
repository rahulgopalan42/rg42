# Usage: python3 dedup_check.py <prefix> [own_tab]  -> lists rows in <prefix>_NN_rows.json whose domain or name matches a brand already delivered (f1run/runs/*_rows.json)
import json,glob,re,sys
n=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
nd=lambda d:(d or '').lower().replace('www.','').strip('/')
dom={};nam={}
for f in glob.glob('/home/user/rg42/f1run/runs/*_rows.json'):
    try: rows=json.load(open(f))
    except: continue
    if isinstance(rows,dict): rows=rows.get('rows',[])
    for r in rows:
        if not isinstance(r,dict) or r.get('skip') or not r.get('variant'): continue
        tab=f.split('/')[-1].replace('_rows.json','')
        if r.get('domain'): dom[nd(r['domain'])]=(tab,r['brand'])
        nam[n(r['brand'])]=(tab,r['brand'])
for f in sorted(glob.glob(f'{sys.argv[1]}_[0-9][0-9]_rows.json')):
    for r in json.load(open(f)):
        hit=dom.get(nd(r.get('domain'))) or nam.get(n(r['brand']))
        if not hit:
            b=n(r['brand'])
            hit=next((v for k,v in nam.items() if len(b)>4 and (k.startswith(b) or b.startswith(k)) and min(len(k),len(b))>=5),None)
        if hit and (len(sys.argv)<3 or hit[0]!=sys.argv[2]): print(f,'|',r['brand'],r.get('domain'),'-> already in',hit)
