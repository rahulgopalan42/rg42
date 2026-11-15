"""Second, independent pass on the key brands, with the Wikipedia summary attached where one was found.
  prep_check.py ids marked            -> data/check_ids_A.txt: brands the user marked x or added
  prep_check.py ids high              -> data/check_ids_B.txt: High-priority brands after the first pass that are not in A
                                         (both also write data/check_names.json for fetch_wiki.py)
  prep_check.py batches <wiki.jsonl> <ids file> <first file number> [per file=90] [web]   -> check_in/in_NNN.jsonl (or web_in/ for the web pass)"""
import gzip, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
if sys.argv[1] == 'ids':
    import bp_build
    A = bp_build.assemble(); names = {x['r']['id']: x['name'] for x in A['rows']}; names.update({d['r']['id']: d['name'] for d in A['f1x']})
    marked = [r['id'] for r in A['B'] if r['mark'] or r['user_added']]
    if sys.argv[2] == 'marked': ids = marked; out = 'check_ids_A.txt'
    else:
        high = {x['r']['id'] for x in A['rows'] if x['priority'] == 'High'}
        ids = [r['id'] for r in A['B'] if r['id'] in high and r['id'] not in set(marked)]; out = 'check_ids_B.txt'
    open(os.path.join(H, 'data', out), 'w').write('\n'.join(ids) + '\n')
    json.dump(names, open(os.path.join(H, 'data', 'check_names.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(ids), 'brands ->', out, '|', len(A['missing']), 'brands still without a first-pass profile')
else:
    W = {}
    for l in open(sys.argv[2], encoding='utf-8'):
        try: d = json.loads(l); W[d['id']] = d['wiki']
        except Exception: pass
    ids = [l.strip() for l in open(sys.argv[3]) if l.strip()]; n = int(sys.argv[4]) - 1; per = int(sys.argv[5]) if len(sys.argv) > 5 else 90
    IN, OUT = ('web_in', 'web') if len(sys.argv) > 6 and sys.argv[6] == 'web' else ('check_in', 'check')
    src = {}
    for f in sorted(os.listdir(os.path.join(H, 'in'))):
        for l in open(os.path.join(H, 'in', f), encoding='utf-8'):
            d = json.loads(l); src[d['id']] = d
    os.makedirs(os.path.join(H, IN), exist_ok=True); os.makedirs(os.path.join(H, OUT), exist_ok=True); first = n + 1
    for i in range(0, len(ids), per):
        n += 1
        with open(os.path.join(H, IN, f'in_{n:03d}.jsonl'), 'w', encoding='utf-8') as fh:
            for k in ids[i:i + per]:
                d = dict(src[k])
                if W.get(k): d['wiki'] = W[k]
                fh.write(json.dumps(d, ensure_ascii=False) + '\n')
    print(f'files {first:03d}-{n:03d},', len(ids), 'brands,', sum(1 for k in ids if W.get(k)), 'with a Wikipedia summary,', sum(1 for k in ids if k not in W), 'not looked up')
