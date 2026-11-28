# usage: python get.py URL [kw1,kw2] [chars]
import sys,re,html,subprocess
u=sys.argv[1]; kws=sys.argv[2].split(',') if len(sys.argv)>2 and sys.argv[2] else []; n=int(sys.argv[3]) if len(sys.argv)>3 else 300
t=subprocess.run(['curl','-sL','--max-time','25','-A','Mozilla/5.0 (compatible; research-bot)',u],capture_output=True).stdout.decode('utf8','ignore')
links=re.findall(r'href="([^"]+)"',t)
t=re.sub(r'(?s)<(script|style|noscript).*?</\1>','',t); t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
if not kws: print(t[:n*10])
else:
  for k in kws:
    if k.startswith('@'):
      print('LINKS',k,sorted(set(l for l in links if k[1:].lower() in l.lower()))[:25]); continue
    for m in list(re.finditer(re.escape(k),t,re.I))[:4]:
      print(f'[{k}]',t[max(0,m.start()-n):m.end()+n]); print('--')
