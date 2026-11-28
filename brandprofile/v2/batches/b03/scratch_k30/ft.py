"""Fetch URL(s) with curl and print visible text (trimmed). Usage: ft.py URL [maxchars] [grep-regex]"""
import sys, subprocess, re, html
url = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 6000; pat = sys.argv[3] if len(sys.argv) > 3 else None
r = subprocess.run(['curl', '-sL', '--max-time', '40', '-A', 'Mozilla/5.0 (compatible; research-bot)', '-w', '\n__HTTP__%{http_code} %{url_effective}', url], capture_output=True)
raw = r.stdout.decode('utf-8', 'replace')
raw, _, code = raw.rpartition('\n__HTTP__')
t = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', raw)
links = re.findall(r'href="([^"#]+)"', raw) if pat == 'LINKS' else []
t = re.sub(r'(?s)<[^>]+>', ' ', t); t = html.unescape(t); t = re.sub(r'[ \t\r\f\v]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n', t)
print('HTTP', code, len(t))
if pat == 'LINKS':
    seen = []
    for l in links:
        if l not in seen: seen.append(l)
    print('\n'.join(seen[:mx])); sys.exit()
if pat:
    for m in re.finditer(pat, t, re.I):
        s = max(0, m.start() - 250); print('...', t[s:m.end() + 250].replace('\n', ' '), '...')
else:
    print(t[:mx])
