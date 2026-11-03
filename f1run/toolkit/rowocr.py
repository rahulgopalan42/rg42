# Row-level OCR of a Crunchbase results frame -> (column starts, [ {name,last,total,date,stage,industries,hq,desc,rank} ])
import subprocess,csv,io,re,sys
def tsv(img):
    out=subprocess.run(['tesseract',img,'-','--psm','11','tsv'],capture_output=True,text=True).stdout
    return [r for r in csv.DictReader(io.StringIO(out),delimiter='\t',quoting=csv.QUOTE_NONE) if (r.get('text') or '').strip()]
L=lambda w:int(w['left']); T=lambda w:int(w['top']); H=lambda w:int(w['height'])
def header(words):
    nm=[w for w in words if w['text'].lower() in ('name','name.')]
    org=[w for w in words if w['text'].lower().startswith('organiz')]
    if not org: return None
    o=org[0]
    near=[w for w in nm if abs(L(w)-L(o))<120]
    y=T(near[0]) if near else T(o)+H(o)//2
    hw=sorted([w for w in words if abs(T(w)-y)<8],key=L)
    st={'name':L(o)}; lasts=[L(w) for w in hw if w['text'].lower()=='last']
    for w in hw:
        t=w['text'].lower().strip('.,'); x=L(w)
        if t=='total': st.setdefault('total',x)
        elif t=='stage': st.setdefault('stage',x)
        elif t.startswith('industr'): st.setdefault('industries',x)
        elif t.startswith('headquart'): st.setdefault('hq',x)
        elif t.startswith('descript'): st.setdefault('desc',x)
        elif t=='cb': st.setdefault('rank',x)
        elif t.startswith('accelerat') or t.startswith('number'): st.setdefault('end',x)
    if lasts: st['last']=lasts[0]
    if 'total' in st:
        later=[x for x in lasts if x>st['total']]
        if later: st['date']=later[0]
    return y,dict(sorted(st.items(),key=lambda kv:kv[1]))
def rows(img):
    words=tsv(img); h=header(words)
    if not h: return None,[]
    y0,st=h; keys=list(st); xs=[st[k] for k in keys]
    xmax=st.get('end',st.get('rank',xs[-1])+140)
    def col(x):
        c=None
        for k,sx in zip(keys,xs):
            if x>=sx-8: c=k
        return c if c!='end' else None
    body=[w for w in words if T(w)>y0+14 and L(w)<xmax]
    nx0=st['name']; nx1=xs[keys.index('name')+1] if len(keys)>1 else nx0+200
    namew=sorted([w for w in body if nx0+14<=L(w)<nx1-4],key=lambda w:(T(w),L(w)))
    anchors=[]
    for w in namew:
        if anchors and abs(T(w)-anchors[-1]['y'])<=8: anchors[-1]['w'].append(w)
        else: anchors.append({'y':T(w),'w':[w]})
    out=[]
    for a in anchors:
        rec={'name':' '.join(w['text'] for w in sorted(a['w'],key=L))}
        for w in sorted(body,key=L):
            if nx0+14<=L(w)<nx1-4: continue
            if abs(T(w)-a['y'])<=7 or (0<T(w)-a['y']<=20 and col(L(w))=='desc'):
                c=col(L(w))
                if c and c!='name': rec.setdefault(c,[]).append(w['text'])
        out.append({k:(v if isinstance(v,str) else ' '.join(v)) for k,v in rec.items()})
    return st,out
if __name__=='__main__':
    st,o=rows(sys.argv[1]); print(st)
    for r in o: print(r)
