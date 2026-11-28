#!/bin/bash
# scratch helper for f02_queue: fetch a public page and print text around keywords. usage: f02_grab.sh URL "regex" [n]
curl -sL --max-time 25 -A "Mozilla/5.0 (compatible; research-bot)" "$1" | sed 's/<[^>]*>/ /g; s/\\"/"/g' | tr -s ' \n\t' ' ' | grep -oiE ".{0,220}($2).{0,220}" | head -${3:-15}
