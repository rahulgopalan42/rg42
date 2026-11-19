"""Checks a screen output file against its input.  Usage: np_check_screen.py <in.txt> <out.txt>"""
import sys
inp = [l.split('|')[0].strip() for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
out = [l.strip().split('|') for l in open(sys.argv[2], encoding='utf-8') if l.strip()]
bad = []
if [o[0].strip() for o in out] != inp: bad.append(f'symbols differ from the input ({len(out)} lines out, {len(inp)} in)')
bad += [f'bad line: {"|".join(o)}' for o in out if len(o) != 2 or o[1].strip() not in ('1', '2', '3', '4', '5', '?')][:20]
n45 = sum(1 for o in out if len(o) == 2 and o[1].strip() in ('4', '5'))
print(('OK' if not bad else 'PROBLEMS:\n' + '\n'.join(bad)) + f' | scored 4 or 5: {n45} of {len(out)}')
