import json,glob,re,sys
def n(s): return re.sub(r'[^a-z0-9]','',s.lower())
seen={}
for f in glob.glob('*.jsonl'):
    if f.startswith(('in_','sig_','disc_')) or 't15_' in f: continue
    for l in open(f):
        try: r=json.loads(l)
        except: continue
        for k in [r.get('name',''), (r.get('website') or '').replace('www.','')]:
            if k: seen.setdefault(n(k),f)
for fn in sys.argv[1:]:
    for line in open(fn):
        nm,_,site=line.partition('|'); nm=nm.strip(); site=site.strip()
        for k in [n(nm), n(site)]:
            if k and k in seen: print(nm,'->',seen[k]); break
