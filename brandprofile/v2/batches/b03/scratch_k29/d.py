import json,sys
# usage: d.py country source  ; stdin lines: name|website|sector|subsector|figure|metric|usd_m|check|stage|why[|parent]
c,src=sys.argv[1],sys.argv[2]
out=open("disc_k29_levant_central_asia.jsonl","a")
for l in sys.stdin:
    l=l.rstrip("\n")
    if not l.strip(): continue
    f=l.split("|")+[""]*11
    r={"name":f[0],"website":f[1],"hq_country":c,"sector":f[2],"subsector":f[3],"figure":f[4],"metric":f[5] or "none","usd_m":(float(f[6]) if f[6] else None),"source":src,"check":f[7],"stage":f[8],"why":f[9]}
    if f[10]: r["parent"]=f[10]
    out.write(json.dumps(r,ensure_ascii=False)+"\n")
