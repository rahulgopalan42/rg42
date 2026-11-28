"""Scratch helper for t13_real_estate: fetch raw wikitext of a Wikipedia article and print infobox fields plus sentences matching a regex.
usage: t13_wiki.py Title REGEX [n] [lang]"""
import sys, re, subprocess, time
t, rx = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 10; lang = sys.argv[4] if len(sys.argv) > 4 else 'en'
raw = subprocess.run(['curl', '-sL', '--max-time', '25', '-A', 'Mozilla/5.0 (compatible; research-bot)', f'https://{lang}.wikipedia.org/w/index.php?title={t}&action=raw'], capture_output=True).stdout.decode('utf-8', 'ignore')
if len(raw) < 200: print('[short]', raw[:200]); sys.exit()
for l in raw.split('\n'):
    if re.match(r'\s*\|\s*(type|traded_as|owner|parent|revenue|operating_income|net_income|assets|aum|num_employees|key_people|founded|hq_location_country|location_country|area_served|subsid)\w*\s*=', l):
        print('IB', re.sub(r'<ref.*?(</ref>|/>)', '', l).strip()[:260])
txt = re.sub(r'<ref[^>]*/>', '', raw); txt = re.sub(r'(?s)<ref.*?</ref>', '', txt); txt = re.sub(r'\{\{[^{}]*\}\}', '', txt)
k = 0
for s in re.split(r'(?<=[.!?])\s+', txt):
    if re.search(rx, s, re.I) and not s.strip().startswith('|'):
        print('--', s.strip()[:400]); k += 1
        if k >= n: break
