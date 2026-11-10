"""'Is this company already in the project?' against new600/excluded.json (every delivered workbook, Rahul's sheets,
research pools, screen-recording rows). why(name, website) -> 'website' | 'name' | 'name variant' | ''."""
import json, os, sys, bisect
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import loose, strict, regdom
_ex = json.load(open(os.path.join(H, 'excluded.json')))
NS = set(_ex['names']); DS = set(_ex['domains']); NL = sorted(n for n in NS if len(n) >= 5)
GENERIC_DOM = {'linkedin.com', 'facebook.com', 'google.com', 'github.io', 'wixsite.com', 'medium.com', 'notion.site', 'linktr.ee'}
def why(name, web=''):
    d = regdom(web or '')
    if d and d in DS and d not in GENERIC_DOM: return 'website'
    for k in {strict(name), loose(name)}:
        if len(k) < 2: continue
        if k in NS: return 'name'
        if len(k) >= 6:
            i = bisect.bisect_left(NL, k)
            if i < len(NL) and NL[i].startswith(k) and len(NL[i]) - len(k) <= 4: return 'name variant'
            for j in range(len(k) - 1, 5, -1):
                if k[:j] in NS and len(k) - j <= 3: return 'name variant'
    return ''
