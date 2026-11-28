import re,html,glob,sys
seen={}
for f in sorted(glob.glob('ard_*_*.html')):
    s=open(f,encoding='utf-8',errors='ignore').read()
    s=re.sub(r'(?is)<(script|style|svg)[^>]*>.*?</\1>',' ',s)
    t=[x.strip() for x in html.unescape(re.sub(r'<[^>]+>','\n',s)).split('\n') if x.strip()]
    for i,l in enumerate(t):
        if re.match(r'^\d{2} \w+ \d{4}$',l) and i>=3 and t[i-3] in ('Buyout','Expansion','Growth','Co-Investment'):
            name=t[i-2];country=t[i-1];sector=t[i+1]
            desc=t[i+3] if i+3<len(t) else ''
            site=''
            for k in range(i+3,min(i+40,len(t))):
                if t[k].startswith('http') and 'linkedin' not in t[k] and 'ardian' not in t[k]: site=t[k];break
            seen[name]=(t[i-3],country,l,sector,site,desc[:120])
for k,v in sorted(seen.items()): print(k,'|',' | '.join(v))
print(len(seen),file=sys.stderr)
