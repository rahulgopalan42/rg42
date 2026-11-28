import re,json
t=open('List_of_largest_oil_and_gas_companies_by_revenue.wiki',encoding='utf-8').read()
t=t.split('==Companies==')[1].split('== See also')[0]
rows=t.split('\n|-')
years=['2018','2019','2020','2021','2022','2023']
out=[]
for r in rows:
    cells=[c for c in r.split('\n| ') ]
    lines=[l for l in r.split('\n') if l.startswith('|') and not l.startswith('|+') and not l.startswith('|}')]
    if len(lines)<3: continue
    def clean(s):
        s=s.lstrip('|').strip(); s=re.sub(r'<ref[^>]*/>','',s); s=re.sub(r'<ref.*?</ref>','',s,flags=re.S); s=re.sub(r'<ref.*','',s); s=re.sub(r'\{\{Efn.*','',s)
        s=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',s); return s.strip()
    name=clean(lines[0]); m=re.search(r'\{\{flag\|([^}|]*)',lines[1]); c=m.group(1) if m else clean(lines[1])
    vals=[clean(l) for l in lines[2:8]]
    last=None
    for y,v in zip(years,vals):
        mm=re.match(r'([\d.]+)',v)
        if mm: last=(y,mm.group(1))
    out.append({'name':name,'country':c,'last':last})
json.dump(out,open('rev.json','w'),ensure_ascii=False); print(len(out))
print('; '.join(f"{o['name']} [{o['country']}] {o['last']}" for o in out))
