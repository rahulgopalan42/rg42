# Clean + cluster OCR name lines from rec/names_*.json into a deduplicated company list -> rec/companies.json
import json,glob,re,collections
from rapidfuzz import fuzz, process
recs=collections.defaultdict(lambda: collections.Counter()); vids=collections.defaultdict(set)
BAD=re.compile(r'Organi[sz]ation|nization|Name v|results|Prev\b|Next\b|Last Funding|crunchbase|discover/|\$|—|Funding Amount|Total Funding',re.I)
def clean(n):
    n=n.replace('|','I').strip(" '\"`.,;:-_~*()[]{}«»©®")
    n=re.sub(r'^(?:[^A-Za-z0-9]{1,3}\s+|[a-z]{1,2}\s+(?=[A-Z0-9]))','',n)   # leading logo junk like "ee " or "() "
    n=re.sub(r'\bAl\b','AI',n); n=re.sub(r'\s{2,}',' ',n).strip()
    n=re.split(r'\s+[I|l1]\s+(?=Public|Private|[A-Z][a-z]{0,2}\b|$)|\s+(?:Public|Private|Delisted|Acquired|Closed)\b',n)[0].strip()
    toks=n.split(' ')
    while len(toks)>1:
        t=toks[-1]
        if (re.search(r"[^A-Za-z0-9&.'+\-()]",t) or len(t)==1 or re.fullmatch(r'[a-z]{1,2}',t) or re.fullmatch(r'(CN|CNY|SAR|INR|EUR|GBP|USD|HK|R\d*|\d{1,3})\S*',t)
            or t.endswith('...') or re.fullmatch(r'[A-Z][a-z]?\d+',t)):
            toks.pop(); continue
        break
    n=' '.join(toks).rstrip('.,;: ').replace('...','')
    if n.count('(')>n.count(')'): n+=')'
    return n
def ok(n):
    if len(n)<2 or len(n)>48 or BAD.search(n): return False
    if not re.search(r'[A-Za-z]{2}',n): return False
    return sum(ch.isalnum() for ch in n)/len(n)>0.7
for f in sorted(glob.glob('rec/names_*.json')):
    d=json.load(open(f)); t=d['title']
    for r in d['records']:
        for n in set(clean(x) for x in r['names']):
            if ok(n): recs[n.lower()][n]+=1; vids[n.lower()].add(t)
keys=sorted(recs,key=lambda k:-sum(recs[k].values()))
tot={k:sum(recs[k].values()) for k in keys}
assigned={}; clusters=[]
for k in keys:
    if k in assigned: continue
    members=[k]
    if len(k)>=5:
        for m,score,_ in process.extract(k,[x for x in keys if x not in assigned and x!=k and abs(len(x)-len(k))<=2],scorer=fuzz.ratio,limit=20):
            if score>=90: members.append(m)
    for m in members: assigned[m]=k
    var=collections.Counter()
    for m in members: var.update(recs[m])
    v=set().union(*(vids[m] for m in members))
    clusters.append({'name':var.most_common(1)[0][0],'frames':sum(var.values()),'variants':len(var),'videos':sorted(v)})
keep=[c for c in clusters if c['frames']>=3 or (c['frames']>=2 and len(c['name'])>=4)]
json.dump(keep,open('rec/companies.json','w'),indent=0)
print('clusters',len(clusters),'kept',len(keep))
print([c['name'] for c in keep[:40]]); print([ (c['name'],c['frames']) for c in keep[-40:]])
