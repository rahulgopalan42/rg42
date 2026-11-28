import re,sys,html
t=open(sys.argv[1],errors='ignore').read()
t=re.sub(r'<(script|style)[^>]*>.*?</\1>','',t,flags=re.S|re.I)
t=re.sub(r'<(br|/p|/div|/tr|/li|/h\d|/dd|/dt|/th|/td)[^>]*>','\n',t,flags=re.I)
t=html.unescape(re.sub(r'<[^>]+>',' ',t))
lines=[re.sub(r'[ \t　]+',' ',l).strip() for l in t.split('\n')]
lines=[l for l in lines if l]
pat=sys.argv[2]; lim=int(sys.argv[3]); ctx=int(sys.argv[4])
out=[]
for i,l in enumerate(lines):
    if not pat or re.search(pat,l,re.I):
        out.append(l+(('  >> '+' / '.join(lines[i+1:i+1+ctx])) if ctx else ''))
print('\n'.join(out)[:lim])
