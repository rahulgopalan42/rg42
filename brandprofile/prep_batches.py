"""Writes in/in_NNN.jsonl (120 brands each, in tab order) from data/brands.json.gz.  Usage: prep_batches.py [per file]"""
import gzip, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); per = int(sys.argv[1]) if len(sys.argv) > 1 else 120
B = json.load(gzip.open(os.path.join(H, 'data', 'brands.json.gz'), 'rt', encoding='utf-8'))
KEEP = re.compile(r'listed|last funding|low OCR|tobacco', re.I)
n = 0
for i in range(0, len(B), per):
    n += 1
    with open(os.path.join(H, 'in', f'in_{n:03d}.jsonl'), 'w', encoding='utf-8') as fh:
        for r in B[i:i + per]:
            d = {'id': r['id'], 'brand': r['brand'], 'tab': r['sector'], 'subsector': r['subsector'], 'country': r['country'], 'loc': r['loc'], 'funding': r['funding'], 'last': r['last'],
                 'about': r['about'], 'about_conf': r['about_conf'].replace(' - check', '')}
            if r['about_conf'] != 'high' or not r['about']: d['cb_desc'] = r['cb_desc']
            fl = '; '.join(x.strip() for x in r['flags'].split(';') if KEEP.search(x))
            if fl: d['flags'] = fl
            if r['user_added']: d['user_added'] = True
            if r['orig_brand']: d['note'] = f"the user renamed this from '{r['orig_brand']}'"
            fh.write(json.dumps({k: v for k, v in d.items() if v != ''}, ensure_ascii=False) + '\n')
print(n, 'files,', len(B), 'brands')
