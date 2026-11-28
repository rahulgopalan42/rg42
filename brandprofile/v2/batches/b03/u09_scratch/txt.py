import sys,re,html
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
s=re.sub(r'(?is)<(script|style|svg|noscript)[^>]*>.*?</\1>',' ',s)
s=re.sub(r'(?s)<[^>]+>','\n',s)
s=html.unescape(s)
lines=[l.strip() for l in s.split('\n')]
out=[];prev=None
for l in lines:
    if l and l!=prev: out.append(l)
    prev=l
print('\n'.join(out))
