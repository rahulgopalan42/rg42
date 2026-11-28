import json,glob,sys,re
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
idx={}
for f in glob.glob('*.jsonl'):
    if f.startswith(('disc','dups','in_')) or 't10_utilities' in f: continue
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        keys=[r.get('name','')]+(r.get('aliases') or [])
        w=(r.get('website') or '').lower().replace('www.','').split('/')[0]
        for k in keys:
            if k: idx[norm(k)]=(f,r.get('name'))
        if w: idx['W'+w]=(f,r.get('name'))
for line in open(sys.argv[1]):
    line=line.strip()
    if not line: continue
    parts=[p.strip() for p in line.split('|')]
    n=norm(parts[0]); hit=idx.get(n)
    if not hit and len(parts)>1: hit=idx.get('W'+parts[1].lower())
    if not hit:
        for k,v in idx.items():
            if not k.startswith('W') and len(n)>5 and len(k)>5 and (n in k or k in n): hit=v;break
    if hit: print(parts[0],'->',hit)
