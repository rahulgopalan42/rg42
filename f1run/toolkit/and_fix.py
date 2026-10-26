# Usage: python3 and_fix.py <rows.json>... -> adds the final "and" to "in Formula 1: A (x), B (y), C (z)." lists in target_audience
import json,sys,re
for fn in sys.argv[1:]:
    rows=json.load(open(fn)); n=0
    for r in rows:
        ta=r.get('target_audience') or ''
        m=re.search(r'(in Formula 1: )([^.]*?)(\.)',ta)
        if not m: continue
        lst=m.group(2); parts=lst.split('), ')
        if len(parts)>=2 and ') and ' not in lst and not parts[-1].startswith('and '):
            new='), '.join(parts[:-1])+') and '+parts[-1]
            r['target_audience']=ta[:m.start(2)]+new+ta[m.end(2):]; n+=1
    json.dump(rows,open(fn,'w'),indent=1,ensure_ascii=False); print(fn,n)
