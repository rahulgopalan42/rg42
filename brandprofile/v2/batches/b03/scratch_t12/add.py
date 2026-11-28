import json,sys
# usage: add.py FILE  (reads JSON lines or a JSON array from stdin, validates, appends)
f=sys.argv[1]; txt=sys.stdin.read().strip()
objs=json.loads(txt) if txt.startswith('[') else [json.loads(l) for l in txt.splitlines() if l.strip()]
with open(f,'a',encoding='utf-8') as o:
    for d in objs: o.write(json.dumps(d,ensure_ascii=False)+'\n')
print(len(objs),'written to',f)
