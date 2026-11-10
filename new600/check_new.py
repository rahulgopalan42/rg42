"""Check candidate companies against everything already delivered or on Rahul's sheets.
Usage: check_new.py "Name|website" ["Name|website" ...]   or   check_new.py --file names.txt (one "Name|website" per line)
Prints NEW or EXCLUDED(<reason>) per company. Also try the company's other names (legal name, former name, Chinese
pinyin name) - if ANY of them is EXCLUDED, treat the company as already covered."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from excl import why
args = sys.argv[1:]
if args[:1] == ['--file']: args = [l.strip() for l in open(args[1]) if l.strip()]
for a in args:
    n, _, w = a.partition('|'); r = why(n.strip(), w.strip())
    print(('EXCLUDED(' + r + ')' if r else 'NEW'), '|', a)
