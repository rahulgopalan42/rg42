"""Novelty check: how many rows of an Apollo page are absent from the user's files AND from the pipeline. Usage: novelty.py <page_name> ..."""
import json,sys,re,pickle,glob
sys.path.insert(0,'/home/user/rg42/parents')
import inputs
old=inputs.old_datasets(); clay=inputs.clay_export()
def nd(s): return re.sub(r'^https?://(www\.)?','',str(s).lower()).split('/')[0].replace('www.','')
doms=set(old['domain'].dropna().map(nd))
for c in clay.columns:
    if 'domain' in c.lower() or c.lower()=='website': doms|=set(clay[c].dropna().map(nd))
def nk(s): return re.sub(r'[^a-z0-9]','',str(s).lower())
names=set(old['name'].dropna().map(nk))
for c in clay.columns:
    if 'name' in c.lower(): names|=set(clay[c].dropna().map(nk))
S='/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad'
par=pickle.load(open(S+'/parents/parents.pkl','rb')); pdoms=set(par['domain'].dropna().map(nd)); pnames=set(par['name'].map(nk))
seen=set()
for f in sorted(glob.glob('/home/user/rg42/parents/apollo/page_*.json')):
    if int(f[-8:-5])<232:
        for r in json.load(open(f)): seen.add(nd(r[2]))
for fn in sys.argv[1:]:
    rows=json.load(open(f'/home/user/rg42/parents/apollo/{fn}.json'))
    new=[r for r in rows if nd(r[2]) not in doms and nk(r[1]) not in names]
    new2=[r for r in new if nd(r[2]) not in pdoms and nk(r[1]) not in pnames and nd(r[2]) not in seen]
    print(fn, len(rows), 'not in user files:',len(new), 'also not in pipeline:',len(new2))
    for r in new2[:12]: print('   ',r[1],'|',r[2],'|',r[6],'|',r[8])
