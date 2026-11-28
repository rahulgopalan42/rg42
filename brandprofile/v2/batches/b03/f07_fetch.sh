#!/bin/bash
# scratch helper for f07_queue: fetch public pages to text. usage: f07_fetch.sh tag URL [tag URL ...]
D=/home/user/rg42/brandprofile/v2/batches/b03/f07_scratch
P=/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python
while [ $# -gt 1 ]; do
  ( curl -sL --compressed --max-time 30 -A "Mozilla/5.0 (compatible; research-bot)" "$2" | $P -I /home/user/rg42/brandprofile/v2/batches/b03/f05_text.py > "$D/$1.txt" 2>/dev/null; echo "$1 $(wc -c < $D/$1.txt) $2" ) &
  shift 2
done
wait
