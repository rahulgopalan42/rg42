# Usage: python3 prechunk.py  -> dedups non-red tabs vs delivered runs, in-flight red-tab chunks, exclusions and each other; writes <prefix>_NN.json chunks
import json,glob,re
R='/home/user/rg42/f1run/runs/'
plan=json.load(open(R+'build_plan.json')); excl=json.load(open(R+'exclusions.json'))
def norm(s): return re.sub(r'\b(inc|corp|corporation|ltd|limited|plc|llc|ag|sa|se|nv|co|company|group|holdings|technologies|the)\b|[^a-z0-9 ]','',(s or '').lower()).split()
def key(s): return ' '.join(norm(s))
def dom(d): return re.sub(r'^(https?://)?(www\.)?','',(d or '').lower()).split('/')[0]
seen={}
for f in glob.glob(R+'*_rows.json'):
    for r in json.load(open(f)):
        if r.get('variant'): seen.setdefault(dom(r.get('domain')),f.split('/')[-1]); seen.setdefault(key(r['brand']),f.split('/')[-1])
for p in ['ego','ms','siai','am']:
    for f in glob.glob(f'{p}_[0-9][0-9].json'):
        for r in json.load(open(f)): seen.setdefault(dom(r.get('domain')),f); seen.setdefault(key(r['brand']),f)
ex={key(x) for x in (excl if isinstance(excl,list) else excl.get('names',[]))}
tabs={'ERP Finance':'erp','GRC Risk':'grc','Automation':'aut','Vertical Saas':'vs','Space':'sp'}
dropped=[]
for t,p in tabs.items():
    keep=[]
    for r in plan[t]:
        d,k=dom(r.get('domain')),key(r['brand'])
        hit=(d and seen.get(d)) or seen.get(k) or ('EXCLUSION' if k in ex else None)
        if hit: dropped.append((t,r['brand'],hit)); continue
        if d: seen[d]=t
        seen[k]=t; keep.append(r)
    for i in range(0,len(keep),10):
        json.dump(keep[i:i+10],open(f'{p}_{i//10:02d}.json','w'),indent=1)
    print(t,p,len(plan[t]),'->',len(keep),'chunks',(len(keep)+9)//10)
for x in dropped: print('DROP',*x)
