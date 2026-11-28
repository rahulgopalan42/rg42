import re,sys
for fn in sys.argv[1:]:
    t=open(fn).read()
    if 'Wikimedia Error' in t: print('ERR',fn); continue
    if t.startswith('#REDIRECT'): print('REDIRECT',fn,t[:100]); continue
    print('=====',fn)
    for k in ['type','traded_as','owner','parent','revenue','net_income','operating_income','num_employees','key_people','area_served','website','founded','hq_location_city','hq_location_country','location']:
        m=re.search(r'^\|\s*'+k+r'\s*=\s*(.*)$',t,re.M)
        if m and m.group(1).strip():
            v=re.sub(r'<ref[^>]*>.*?</ref>|<ref[^/]*/>','',m.group(1)); print(' ',k,':',v[:220])
    body=re.split(r'\n\}\}\n',t,1)[-1]
    lead=re.sub(r'<ref[^>]*>.*?</ref>|<ref[^/]*/>','',body)[:900].replace('\n',' ')
    print('  LEAD:',lead)
