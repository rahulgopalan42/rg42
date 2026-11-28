#!/bin/bash
# fetch raw wikitext slowly
cd /home/user/rg42/brandprofile/v2/batches/b03/scratch_k30/wiki
while read -r t; do
  [ -z "$t" ] && continue
  f=$(echo "$t" | tr ' /&()' '_____').txt
  [ -s "$f" ] && continue
  for i in 1 2 3; do
    code=$(curl -s -L -A "research-client/1.0 (generic)" --max-time 30 -o "$f" -w '%{http_code}' "https://en.wikipedia.org/w/index.php?action=raw&title=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "$t")")
    if [ "$code" = "200" ]; then echo "OK $t"; break; fi
    rm -f "$f"; echo "ERR $code $t"; sleep 30
  done
  sleep 12
done
