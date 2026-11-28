#!/bin/bash
# usage: f.sh url outfile
curl -sL -m 40 -A "Mozilla/5.0 (compatible; research-bot/1.0)" "$1" -o "$2"; echo "$(wc -c <"$2") $2"
