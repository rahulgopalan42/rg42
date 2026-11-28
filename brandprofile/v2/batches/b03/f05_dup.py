"""scratch for f05_queue: append DUPS lines from stdin 'name<TAB>why'"""
import json,sys
with open('/home/user/rg42/brandprofile/v2/batches/b03/dups_f05_queue.jsonl','a',encoding='utf-8') as f:
    for l in sys.stdin:
        if '\t' in l:
            n,w=l.rstrip('\n').split('\t',1); f.write(json.dumps({"name":n,"why":w},ensure_ascii=False)+'\n')
