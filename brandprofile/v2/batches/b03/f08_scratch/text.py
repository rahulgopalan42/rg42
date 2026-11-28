"""scratch for f05_queue: html on stdin -> visible text on stdout"""
import sys, html.parser, re
class P(html.parser.HTMLParser):
    def __init__(s): super().__init__(); s.o=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style','svg','noscript'): s.skip+=1
        if t in ('p','div','li','h1','h2','h3','h4','tr','br','time','section'): s.o.append('\n')
    def handle_endtag(s,t):
        if t in ('script','style','svg','noscript') and s.skip: s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.o.append(d)
p=P(); p.feed(sys.stdin.buffer.read().decode('utf-8','replace'))
t=''.join(p.o); t=re.sub(r'[ \t\r]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t)
print(t)
