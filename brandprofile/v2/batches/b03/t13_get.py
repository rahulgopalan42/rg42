"""Scratch helper for t13_real_estate: fetch a public page, strip scripts/styles/tags, print snippets around a regex
(or the first N chars of text when regex is '-'). usage: t13_get.py URL REGEX [max_snippets|chars]"""
import sys, re, html, subprocess
url, rx = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
raw = subprocess.run(['curl', '-sL', '--max-time', '25', '-A', 'Mozilla/5.0 (compatible; research-bot)', url], capture_output=True).stdout.decode('utf-8', 'ignore')
raw = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', raw)
t = html.unescape(re.sub(r'<[^>]+>', ' ', raw)); t = re.sub(r'\s+', ' ', t)
if rx == '-': print(t[:n]); sys.exit()
out, last = [], -1
for m in re.finditer(rx, t, re.I):
    if m.start() < last: continue
    s = max(0, m.start() - 220); e = min(len(t), m.end() + 260); out.append(t[s:e]); last = e
    if len(out) >= n: break
print('\n--\n'.join(out) if out else f'[no match; {len(t)} chars]')
