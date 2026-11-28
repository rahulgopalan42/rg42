import re,sys,json
def clean(s):
    s=re.sub(r'<ref[^>]*/>','',s); s=re.sub(r'<ref[^>]*>.*?</ref>','',s,flags=re.S)
    s=re.sub(r'\{\{[^{}]*\}\}','',s); s=re.sub(r'\{\{[^{}]*\}\}','',s)
    s=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',s)
    s=re.sub(r'\[https?://\S+ ([^\]]*)\]',r'\1',s)
    s=re.sub(r'<br\s*/?>',' ',s); s=re.sub(r'<[^>]+>','',s); s=s.replace('&nbsp;',' ')
    s=re.sub(r"'''?",'',s)
    return re.sub(r'\s+',' ',s).strip()
out=[]
for fn in sys.argv[1:]:
    txt=open(fn).read(); country=None
    for sec in re.split(r'\n==+([^=\n]+)==+\s*\n',txt)[1:]:
        pass
    parts=re.split(r'\n(==+[^=\n]+==+)\s*\n',txt)
    for i in range(1,len(parts),2):
        country=parts[i].strip('= ').strip(); body=parts[i+1]
        for tbl in re.findall(r'\{\|.*?\n\|\}',body,flags=re.S):
            rows=re.split(r'\n\|-[^\n]*',tbl)
            for r in rows:
                r=r.strip()
                if not r.startswith('|') or r.startswith('{|') : continue
                r=r.replace('\n',' ')
                r=re.sub(r'^\|','',r)
                r=re.sub(r'\|\|\|','||',r)
                cells=[clean(c) for c in r.split('||')]
                cells=[re.sub(r'^align=\w+\|\s*','',c) for c in cells]
                if len(cells)<2: continue
                op=cells[1]; subs=cells[3] if len(cells)>3 else ''; own=cells[-1] if len(cells)>4 else ''
                out.append({'country':country,'operator':op,'subs':subs[:60],'own':own[:150],'src':fn})
for o in out: print(json.dumps(o,ensure_ascii=False))
