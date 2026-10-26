# Usage: python3 review.py <rows.json> -> compact review: brand, domain, variant, overlap, ref, first flags
import json,sys
for r in json.load(open(sys.argv[1])):
    fl=r.get('flags') or []
    if isinstance(fl,str): fl=[fl]
    print('==',r.get('brand'),'|',r.get('domain'),'|',r.get('variant'),'| SKIP '+str(r.get('skip')) if r.get('skip') else '')
    print('  OV:',r.get('market_overlap',''))
    print('  REF:',(r.get('market_reference') or '')[:160])
    for f in fl[:3]: print('  FL:',f[:260])
