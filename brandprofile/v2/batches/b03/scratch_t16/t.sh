#!/bin/bash
# usage: t.sh URL [regex] [limit] [ctx]
F=/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/page.html
curl -sL -m 25 -A "Mozilla/5.0 (research; rg42-bot)" "$1" -o $F
/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I /home/user/rg42/brandprofile/v2/batches/b03/scratch_t16/tx.py $F "${2:-}" "${3:-3000}" "${4:-0}"
