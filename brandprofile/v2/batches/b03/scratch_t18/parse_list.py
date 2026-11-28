import re,sys,json
src=sys.argv[1]; url=sys.argv[2]
out=[]
for line in open(src,encoding='utf-8'):
    m=re.match(r'^(\*+)\s*(.*)',line.strip())
    if not m: continue
    t=m.group(2)
    t=re.sub(r'<ref[^>]*/>','',t); t=re.sub(r'<ref.*?</ref>','',t); t=re.sub(r'<ref.*','',t)
    t=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',t)
    t=re.sub(r'\[http\S+\s([^\]]*)\]',r'\1',t)
    t=re.sub(r"'''?",'',t)
    parts=re.split(r'\s+[—–-]\s+',t,1)
    name=parts[0].strip(); loc=parts[1].strip() if len(parts)>1 else ''
    if name: out.append({'name':name,'loc':loc,'level':len(m.group(1))})
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False)
print(len(out))
