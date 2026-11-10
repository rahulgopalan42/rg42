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

# name variants for a stricter check: bracket contents, the name without brackets, and the name without a leading
# place prefix ("Shenzhen", "Jiangsu", ...) or trailing generic words ("Technology", "Group", ...)
import re
PLACES = ('beijing shanghai shenzhen guangzhou tianjin chongqing hangzhou nanjing suzhou wuxi ningbo xiamen fuzhou qingdao jinan '
          'wuhan changsha chengdu xian zhengzhou hefei kunming dalian shenyang harbin changchun foshan dongguan zhuhai '
          'jiangsu zhejiang guangdong fujian shandong henan hebei hubei hunan anhui jiangxi sichuan shaanxi shanxi yunnan guizhou '
          'guangxi hainan liaoning jilin heilongjiang gansu qinghai ningxia xinjiang tibet inner mongolia china chinese hong kong '
          'taiwan pt bank').split()
GENERIC_TAIL = re.compile(r'\b(technology|technologies|tech|group|holdings?|industrial|industries|industry|co|company|corp|corporation|'
                          r'limited|ltd|inc|science|sci|development|international|stock|joint|share|shares|tbk|berhad|bhd|plc|ag|sa)\b\.?', re.I)
def variants(name):
    n = str(name or ''); out = {n}
    out |= {m.strip() for m in re.findall(r'\(([^)]+)\)', n)}
    base = re.sub(r'\([^)]*\)', ' ', n).strip(); out.add(base)
    w = base.split()
    while w and w[0].lower().strip(',') in PLACES: w = w[1:]
    core = ' '.join(w); out.add(core)
    out.add(GENERIC_TAIL.sub(' ', core).strip())
    return {re.sub(r'\s+', ' ', v).strip() for v in out if len(re.sub(r'[^a-z0-9]', '', v.lower())) >= 4}
def why_all(name, former='', web=''):
    r = why(name, web)
    if r: return r
    for nm in [name] + ([former] if former else []):
        for v in variants(nm):
            r = why(v)
            if r: return f'{r} via "{v}"'
    return ''
