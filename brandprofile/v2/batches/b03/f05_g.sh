#!/bin/bash
# scratch: grep context in fetched text. usage: f05_g.sh tag regex [n]
grep -oiE ".{0,220}($2).{0,220}" /home/user/rg42/brandprofile/v2/batches/b03/f05_scratch/$1.txt | head -${3:-8}; echo "-----"
