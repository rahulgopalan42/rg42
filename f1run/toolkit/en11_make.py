# Usage: python3 en10_make.py <name> <cs10 part ids...> -> writes en10_<name>_in.json from cs10_<id>_out.json, holding China-HQ brands
import json,sys,re
cs={r['user_name']:r for r in json.load(open('npw1/cs11_all.json'))}
rows=[];held=[]
for pid in sys.argv[2:]:
    for r in json.load(open(f'npw1/cs11_{pid}_out.json'))['rows']:
        if not r.get('picks'): continue
        if r['user_name'] in set(json.load(open('npw1/skip_enrich.json'))) if __import__('os').path.exists('npw1/skip_enrich.json') else set(): continue
        hq=cs.get(r['user_name'],{}).get('hq','')
        (held if re.search(r'China|Hong Kong|Russia|Iran',hq) else rows).append(r)
json.dump({'rows':rows},open(f'npw1/en11_{sys.argv[1]}_in.json','w'),indent=1,ensure_ascii=False)
h=json.load(open('npw1/en11_hold.json')) if __import__('os').path.exists('npw1/en11_hold.json') else {'rows':[]}
h['rows']+=held; json.dump(h,open('npw1/en11_hold.json','w'),indent=1,ensure_ascii=False)
print(sys.argv[1],'brands',len(rows),'picks',sum(len(r['picks']) for r in rows),'held',[r['user_name'] for r in held])
