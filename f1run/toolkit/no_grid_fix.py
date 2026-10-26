# Usage: python3 no_grid_fix.py <prefix>  -> strips leading "No X is on the grid." style sentences (v8 bans them) from row fields, in place
import json,glob,re,sys
pat=re.compile(r'(?:^|(?<=\. ))No [^.]*?(?:on the grid|in Formula 1|on the Formula 1 grid)[^.]*\.\s*')
for f in sorted(glob.glob(f'{sys.argv[1]}_[0-9][0-9]_rows.json')):
    rows=json.load(open(f)); ch=0
    for r in rows:
        for k in ['target_audience','market_overlap','market_reference','shared_values','f1_audience']:
            v=r.get(k) or ''; nv=pat.sub('',v).strip()
            if nv!=v:
                r[k]=nv[:1].upper()+nv[1:] if nv else ''; ch+=1; print(f,r['brand'],k,'->',r[k][:110])
    if ch: json.dump(rows,open(f,'w'),indent=1)
