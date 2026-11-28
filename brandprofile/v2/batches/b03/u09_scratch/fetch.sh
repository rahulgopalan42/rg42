#!/bin/bash
# usage: fetch.sh key url
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 research"
P=/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python
D=/home/user/rg42/brandprofile/v2/batches/b03/u09_scratch
r=$(curl -sL -A "$UA" --max-time 30 -o $D/pages/$1.html -w "%{http_code} %{url_effective}" "$2")
$P -I $D/txt.py $D/pages/$1.html > $D/pages/$1.txt 2>/dev/null
echo "$1 $r $(wc -l < $D/pages/$1.txt)"
