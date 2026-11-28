import sys,re
for f in sys.argv[1:]:
    t=open(f,encoding='utf-8',errors='ignore').read()
    print('=====',f,len(t))
    for k in ['type','traded_as','owner','owners','parent','revenue','net_income','operating_income','num_employees','key_people','hq_location','hq_location_city','hq_location_country','location','area_served','website','founded','defunct','fate','successor']:
        m=re.search(r'\|\s*'+k+r'\s*=\s*(.*)',t)
        if m and m.group(1).strip(): print(k,':',re.sub(r'<ref.*?(</ref>|/>)','',m.group(1))[:200])
    for s in re.split(r'(?<=[.!?])\s+',re.sub(r'<ref.*?(</ref>|/>)','',t,flags=re.S)):
        if re.search(r'\b(2025|2026)\b',s) and len(s)<400: print('  *',s.strip()[:300])
