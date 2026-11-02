# Usage: python3 oxford_fix.py <rows.json>... -> removes Oxford commas from grid-name lists, the stock B2B sentence and calendar lines
import json,sys,re
for fn in sys.argv[1:]:
    rows=json.load(open(fn)); n=0
    for r in rows:
        for f in ('target_audience','market_overlap'):
            t=r.get(f) or ''; o=t
            t=t.replace('), and ',') and ').replace('under pressure, and meet','under pressure and meet')
            t=re.sub(r'(expanding into: [^.]*?), and ([A-Z][^.,]*\.)$',r'\1 and \2',t)
            if t!=o: r[f]=t; n+=1
    json.dump(rows,open(fn,'w'),indent=1,ensure_ascii=False); print(fn,n)
