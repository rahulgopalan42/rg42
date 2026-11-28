import re,sys
t=open(sys.argv[1]).read()
for p in sys.argv[2:]:
    for m in list(re.finditer(p,t,re.I))[:2]: print('>>',m.group(0)[:350])
