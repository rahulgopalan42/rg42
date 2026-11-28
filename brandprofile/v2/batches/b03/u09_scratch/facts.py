import sys,re
for k in sys.argv[1:]:
    try: t=open(f'pages/{k}.txt').read().split('\n')
    except: continue
    h=open(f'pages/{k}.html',errors='ignore').read()
    print('=====',k)
    pat=re.compile(r'(employ|people|colleagues|countr|revenue|turnover|sales of|billion|million|\bbn\b|\$\s?\d|€\s?\d|EUR|USD|SEK|NOK|locations|sites|plants|factories|offices|customers|founded|since 19|since 20|owned by|acquired|portfolio company|Formula|F1|motorsport|racing|sponsor)',re.I)
    seen=set()
    for l in t:
        if pat.search(l) and 8<len(l)<400 and l not in seen:
            seen.add(l); print('  ',l[:300])
    links=sorted(set(re.findall(r'href="([^"#]*(?:about|news|press|media|company|who-we|history|facts|investor|sponsor)[^"#]*)"',h,re.I)))
    print('  LINKS:',' '.join(links[:25]))
