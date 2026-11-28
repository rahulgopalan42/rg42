import json,glob,re,sys
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
ex={}
for f in glob.glob('*.jsonl'):
    if 't10_utilities' in f or f.startswith(('disc','dups')): continue
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        for k in [r.get('name','')]+(r.get('aliases') or []):
            if k: ex[norm(k)]=f
        w=(r.get('website') or '').lower().replace('www.','').split('/')[0]
        if w: ex[w]=f
chk={}
for l in open(sys.argv[1]):
    if ': ' in l:
        n,res=l.split(': ',1); chk[n.strip()]=res.strip()
for n,res in chk.items():
    if not res.startswith('NEW'): continue
    h=ex.get(norm(n))
    print(('EXCL '+h) if h else 'OK', '|', n)
