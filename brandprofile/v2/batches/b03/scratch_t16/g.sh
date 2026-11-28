#!/bin/bash
# usage: g.sh URL  -> prints links matching pattern $2 (optional)
curl -sL -m 25 -A "Mozilla/5.0 (research; rg42-bot)" "$1" -o /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/page.html
/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I -c "
import re,sys,html
t=open('/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/page.html',errors='ignore').read()
pat=sys.argv[1]
for m in re.finditer(r'<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>',t,re.S):
    txt=re.sub(r'<[^>]+>','',m.group(2)).strip()
    if re.search(pat,m.group(1)+' '+txt,re.I): print(m.group(1),'|',txt[:60].replace('\n',' '))
" "${2:-company|about|profile|outline|概要|news|press}" | sort -u | head -40
