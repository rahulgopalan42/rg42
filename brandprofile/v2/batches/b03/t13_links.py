"""Scratch helper: print links on a page matching a regex. usage: t13_links.py URL REGEX"""
import sys, re, subprocess
from urllib.parse import urljoin
u, rx = sys.argv[1], sys.argv[2]
raw = subprocess.run(['curl', '-sL', '--max-time', '25', '-A', 'Mozilla/5.0 (compatible; research-bot)', u], capture_output=True).stdout.decode('utf-8', 'ignore')
seen = set()
for h in re.findall(r'href=["\']([^"\'#]+)', raw):
    a = urljoin(u, h)
    if re.search(rx, a, re.I) and a not in seen: seen.add(a); print(a)
print(f'[{len(raw)} bytes]')
