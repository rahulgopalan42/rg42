import json,re,subprocess,sys
P='/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python'
SUF=r'[,]?\s+(inc\.?|llc|ltd\.?|limited|gmbh|ag|sa|s\.a\.|spa|s\.p\.a\.|plc|corp\.?|corporation|holdings?|group|co\.?|company|bv|b\.v\.|nv|ab|as|oy|sas|srl|lp|l\.p\.|technologies|international)$'
def strip(n):
    n2=re.sub(r'\(.*?\)','',n).strip()
    prev=None
    while prev!=n2:
        prev=n2; n2=re.sub(SUF,'',n2,flags=re.I).strip()
    return n2
C=[json.loads(l) for l in open(sys.argv[1])]
args=[];idx=[]
for i,c in enumerate(C):
    vs={c['name']}
    s=strip(c['name']); 
    if s and s!=c['name']: vs.add(s)
    for a in c.get('aliases',[]): vs.add(a)
    for v in vs:
        args.append(v); idx.append(i)
        if c.get('website'): args.append(v+' | '+c['website']); idx.append(i)
res=[]
for k in range(0,len(args),60):
    out=subprocess.run([P,'-I','/home/user/rg42/brandprofile/v2/check.py']+args[k:k+60],capture_output=True,text=True,cwd='/home/user/rg42/brandprofile').stdout.strip().split('\n')
    assert len(out)==len(args[k:k+60]),(len(out),k,out[:3])
    res+=out
rank={'IN MASTER':0,'ALREADY DELIVERED':1,'F1 PARTNER':2,'LISTED':3,'POSSIBLE':4,'NEW':5}
for i,c in enumerate(C):
    lines=[r for r,j in zip(res,idx) if j==i]
    best=None;bl=''
    for l in lines:
        st=l.split(': ',1)[1] if ': ' in l else l
        key=next((k for k in rank if st.startswith(k)),'NEW')
        if best is None or rank[key]<rank[best]: best=key;bl=st
    c['check']=best; c['check_text']=bl; c['check_all']=lines
with open(sys.argv[2],'w') as f:
    for c in C: f.write(json.dumps(c)+'\n')
from collections import Counter; print(Counter(c['check'] for c in C))
