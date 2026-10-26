# Usage: python3 calendar_fix.py <rows.json> [<rows.json> ...] [--dry]
# Moves race lists to the 2027 calendar: drops Zandvoort and Barcelona (not on the 2027 calendar) and
# 2026-only qualifiers ("in its final year", "new in 2026"). Only touches the race-list sentence of
# market_overlap ("... Formula 1 calendar aligns ...: A, B and C."). Prints anything it cannot fix cleanly.
import json,re,sys
args=[a for a in sys.argv[1:] if not a.startswith('--')]; dry='--dry' in sys.argv
QUAL=[r",? in its (?:final|last) year",r",? the Dutch race.s final year",r",? (?:which is new|new (?:in|for) 2026|new this year|as a new race)",
      r"(?<=Zandvoort) in August",r"(?<=Barcelona) in June"]
MONTHS=[('Shanghai and Suzuka in March','Suzuka and Shanghai in April'),('Bahrain and Jeddah in April','Bahrain and Jeddah in March'),
 ('Melbourne in March','Melbourne in April'),('Shanghai in March','Shanghai in April'),('Suzuka in March','Suzuka in April'),
 ('Bahrain in April','Bahrain in March'),('Jeddah in April','Jeddah in March'),('Spielberg in June','Spielberg in July'),
 ('Mexico City in November','Mexico City in October'),('Qatar in November','Qatar in December'),('Lusail in November','Lusail in December'),
 ('Shanghai the week after Melbourne','Shanghai'),('Shanghai the week after','Shanghai'),('Madrid in 2026','Madrid'),('Montreal in June','Montreal in May')]
def fix_list(s):
    s=s.replace('the new Madrid race','Madrid')
    for a,b in MONTHS: s=s.replace(a,b)
    for q in QUAL: s=re.sub(q,'',s)
    for c in ['Zandvoort','Barcelona','Sepang','Imola']:
        s=re.sub(rf',\s*and {c}\b|\s+and {c}\b|,\s*{c}\b(?: in the Netherlands)?|\b{c}(?: in the Netherlands)?,\s*|\b{c} and ','',s)
    s=re.sub(r',\s*,',',',s); s=re.sub(r':\s*,\s*',': ',s); s=re.sub(r',\s*\.$','.',s)
    head,_,lst=s.partition(': ')
    if lst and ' and ' not in lst and ', ' in lst:
        i=lst.rfind(', '); lst=lst[:i]+' and '+lst[i+2:]
    elif lst and not re.search(r'\b(?:and|plus) [^,]+\.$',lst) and ', ' in lst:
        i=lst.rfind(', '); lst=lst[:i]+', and '+lst[i+2:]
    return head+': '+lst if lst else s
for f in args:
    rows=json.load(open(f)); ch=0
    for r in rows:
        if not isinstance(r,dict) or r.get('skip'): continue
        v=r.get('market_overlap') or ''
        parts=re.split(r'(?<=\.) ',v)
        new=[]
        for p in parts:
            if 'Formula 1' in p and ':' in p and re.search(r'Zandvoort|Barcelona|Sepang|Imola|final year|last year|new (?:in|for) 2026|new this year|which is new|new Madrid|as a new race|'+'|'.join(re.escape(a) for a,_ in MONTHS),p):
                q=fix_list(p)
                if re.search(r'Zandvoort|Barcelona|Sepang|Imola',q) or len(q.split(': ',1)[-1].split(','))<1: print('MANUAL',f,r['brand'],'|',q)
                new.append(q)
            else: new.append(p)
        nv=' '.join(new)
        if nv!=v:
            ch+=1; print(f,'|',r['brand'],'|',nv.split('. ')[-1][-150:]); r['market_overlap']=nv
    if ch and not dry: json.dump(rows,open(f,'w'),indent=1)
