"""Second, independent pass: writes check_in/in_NNN.jsonl for the key brands (marked x by the user, added by the user, or High
priority after the first pass), with the Wikipedia summary attached where one was found.
Usage: prep_check.py ids            -> data/check_ids.txt and data/check_names.json (run fetch_wiki.py on them next)
       prep_check.py batches <wiki.jsonl> [per file=90]"""
import gzip, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build
if sys.argv[1] == 'ids':
    A = bp_build.assemble(); key = {}
    for x in A['rows']:
        r = x['r']
        if r['mark'] or r['user_added'] or x['priority'] == 'High': key[r['id']] = x['name']
    for d in A['f1x']:
        if d['r']['mark'] or d['r']['user_added']: key[d['r']['id']] = d['name']
    order = [r['id'] for r in A['B'] if r['id'] in key]
    open(os.path.join(H, 'data', 'check_ids.txt'), 'w').write('\n'.join(order) + '\n')
    json.dump(key, open(os.path.join(H, 'data', 'check_names.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(order), 'key brands |', sum(1 for x in A['rows'] if x['priority'] == 'High'), 'High |', sum(1 for r in A['B'] if r['mark']), 'marked x')
else:
    W = {}
    for l in open(sys.argv[2], encoding='utf-8'):
        try: d = json.loads(l); W[d['id']] = d['wiki']
        except Exception: pass
    per = int(sys.argv[3]) if len(sys.argv) > 3 else 90
    ids = [l.strip() for l in open(os.path.join(H, 'data', 'check_ids.txt')) if l.strip()]
    src = {}
    for f in sorted(os.listdir(os.path.join(H, 'in'))):
        for l in open(os.path.join(H, 'in', f), encoding='utf-8'):
            d = json.loads(l); src[d['id']] = d
    os.makedirs(os.path.join(H, 'check_in'), exist_ok=True); os.makedirs(os.path.join(H, 'check'), exist_ok=True); n = 0
    for i in range(0, len(ids), per):
        n += 1
        with open(os.path.join(H, 'check_in', f'in_{n:03d}.jsonl'), 'w', encoding='utf-8') as fh:
            for k in ids[i:i + per]:
                d = dict(src[k])
                if W.get(k): d['wiki'] = W[k]
                fh.write(json.dumps(d, ensure_ascii=False) + '\n')
    print(n, 'files,', len(ids), 'brands,', sum(1 for k in ids if W.get(k)), 'with a Wikipedia summary')
