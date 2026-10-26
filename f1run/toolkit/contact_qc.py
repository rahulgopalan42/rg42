# Usage: python3 contact_qc.py <prefix> <contacts.json>  -> prints brands whose contacts look off-domain; writes <prefix>_fix_in.json
import json,re,glob,sys
pre,cf=sys.argv[1],sys.argv[2]
norm=lambda s: re.sub(r'[^a-z0-9]','',s.lower())
w={norm(r['brand']):r for r in json.load(open(cf))['rows']}
fix=[]
for f in sorted(glob.glob(f'{pre}_[0-9][0-9]_rows.json')):
    for r in json.load(open(f)):
        if not r.get('variant'): continue
        d=(r.get('domain') or '').lower().replace('www.','')
        root=d.split('.')[0]
        c=w.get(norm(r['brand']))
        ppl=c['people'] if c else []
        doms=[p['email'].split('@')[1].lower() for p in ppl]
        good=[x for x in doms if x==d or x.endswith('.'+d) or (len(root)>3 and root[:5] in x.replace('-',''))]
        if not ppl or len(good)==0:
            print(f"{r['brand']} | row domain {d} | contacts {doms}")
            fix.append({'brand':r['brand'],'domain':d})
json.dump(fix,open(f'{pre}_fix_in.json','w'),indent=1); print(len(fix),'to fix')
