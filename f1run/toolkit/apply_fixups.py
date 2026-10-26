# Usage: python3 apply_fixups.py <fixups.json> -> applies [{file, brand, field, old, new}] string replacements in place; reports misses
import json,sys
fx=json.load(open(sys.argv[1])); cache={}
for f in fx:
    rows=cache.setdefault(f['file'],json.load(open(f['file'])))
    hit=[r for r in rows if r['brand']==f['brand']]
    if not hit: print('NO BRAND',f['brand']); continue
    r=hit[0]; v=r.get(f['field']) or ''
    if f['old'] not in v:
        print('ALREADY/MISS',f['brand'],f['field'],f['old'][:50]) if f['new'] not in v else None; continue
    r[f['field']]=v.replace(f['old'],f['new']); print('OK',f['brand'],f['field'])
for fn,rows in cache.items(): json.dump(rows,open(fn,'w'),indent=1,ensure_ascii=False)
