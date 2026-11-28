import json,glob,sys,re
def n(s): return re.sub(r'[^a-z0-9]','',s.lower())
names={}
for f in glob.glob('*.jsonl'):
    if f.startswith(('disc_','dups_','in_')) or 't11_packaging' in f: continue
    for l in open(f):
        try: d=json.loads(l)
        except: continue
        for x in [d.get('name','')]+list(d.get('aliases') or []):
            if x: names[n(x)]=(f,d.get('name'))
for q in sys.argv[1:]:
    k=n(q); hits=[v for kk,v in names.items() if k and (k==kk or (len(k)>4 and len(kk)>4 and (k in kk or kk in k)))]
    print(q,'->',hits[:3] if hits else 'clear')
