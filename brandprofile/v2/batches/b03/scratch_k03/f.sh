#!/bin/bash
# usage: f.sh URL [maxchars]
UA="Mozilla/5.0 (compatible; research-bot/1.0)"
curl -s -L -m 40 -A "$UA" "$1" | /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I -c "
import sys,re,html
s=sys.stdin.read()
s=re.sub(r'(?is)<(script|style|svg|noscript)[^>]*>.*?</\1>',' ',s)
t=html.unescape(re.sub(r'<[^>]+>','\n',s))
t='\n'.join(l.strip() for l in t.split('\n') if l.strip())
print(t[:int(sys.argv[1])])" ${2:-6000}
