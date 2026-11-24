# QC for nb10 rows: stock sentence normalisation + checks. Usage: python3 -I qc10.py [--fix]
import json,glob,re,collections,sys
FIX='--fix' in sys.argv
STOCK='B2B brands are in the sport to host key clients, show their technology working under pressure and meet buyers worldwide.'
F=['designation','fit_reason','target_audience','market_overlap','market_reference','shared_values','f1_audience']
items=json.load(open('nb13/items.json')); names=[i['user_name'] for i in items]
iss=collections.defaultdict(list); seen={}; desig=collections.Counter()
for fn in sorted(glob.glob('nb13_[0-9][0-9]_rows.json')):
    R=json.load(open(fn)); ch=0
    for r in R:
        u=r.get('user_name'); seen[u]=fn
        dec=any(str(x).startswith('DECLINED') for x in r.get('flags',[]))
        if dec: continue
        ta=r.get('target_audience') or ''
        if r.get('variant')=='B2B':
            m=re.search(r'B2B brands are in the sport to[^.]*\.',ta)
            if not m: iss['no stock sentence'].append(u)
            elif m.group(0)!=STOCK and 'expertise' not in m.group(0):
                if FIX: r['target_audience']=ta.replace(m.group(0),STOCK); ch+=1
                iss['stock variant'].append(f'{u}: {m.group(0)[:90]}')
            if not ta.startswith('Your target customers are'): iss['TA opener'].append(u)
            if not re.search(r'Teams also introduce partners to each other',ta): iss['no intro sentence'].append(u)
        elif r.get('variant')=='B2C':
            if not r.get('f1_audience'): iss['B2C no f1_audience'].append(u)
            if not (r.get('fit_reason') or '').startswith('due to'): iss['B2C fit_reason'].append(u)
        else: iss['variant?'].append(f"{u}:{r.get('variant')}")
        desig[r.get('designation')]+=1
        if not (r.get('designation') or '').startswith('Official '): iss['designation'].append(u)
        for f in F:
            t=r.get(f) or ''
            if re.search(r'[—–]',t) or ' - ' in t: iss['dash'].append(f'{u}:{f}')
            if re.search(r'\b(actually|genuinely|honestly)\b',t,re.I): iss['banned word'].append(f'{u}:{f}')
            if re.search(r'Zandvoort|Barcelona|Sepang|Imola|Dutch Grand Prix|Spanish Grand Prix',t): iss['2027 calendar'].append(f'{u}:{f}')
            if re.search(r'\bCLEAR\b',t): iss['CLEAR mention'].append(f'{u}:{f}: '+re.search(r'.{0,60}\bCLEAR\b.{0,40}',t).group(0))
            if re.search(r'\bbold\b|\*\*',t): iss['markup'].append(f'{u}:{f}')
            if re.search(r'Edward Jones|NTT|AbbVie',t): iss['new-deal cite (check)'].append(f'{u}:{f}')
        mo=r.get('market_overlap') or ''
        if not re.search(r'aligns with the markets you are present in and expanding into|brings the sport to your home market|brings the sport close to',mo): iss['calendar form'].append(f'{u}: {mo[-110:]}')
        for f in ('target_audience','market_overlap','shared_values'):
            if not (r.get(f) or '').strip(): iss[f'empty {f}'].append(u)
        if not r.get('market_reference') and not any('Market reference dropped' in str(x) or 'market reference' in str(x).lower() for x in r.get('flags',[])): iss['MR empty no flag'].append(u)
        if r.get('brand') and r['brand'] not in ' '.join(str(r.get(f) or '') for f in ('shared_values','market_overlap','target_audience','market_reference','fit_reason')) and False: pass
    if FIX and ch: json.dump(R,open(fn,'w'),indent=1,ensure_ascii=False)
miss=[n for n in names if n not in seen]; extra=[s for s in seen if s not in names]
print('rows',len(seen),'missing',len(miss),miss[:20],'extra',extra[:20])
print('dup designations',[(d,c) for d,c in desig.items() if c>1][:15])
for k,v in iss.items(): print(f'\n## {k} ({len(v)})'); [print('  ',x) for x in v[:40]]
