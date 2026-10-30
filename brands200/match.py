"""Conservative 'already on the sheets?' matcher. A candidate counts as present if its website matches, or its name
(with legal suffixes and bracketed text removed) equals, prefixes or is prefixed by an excluded name (4+ chars), or an
excluded name of 7+ chars is the start or end of the candidate name. Errs towards excluding."""
import bisect, json, os, re
H = os.path.dirname(os.path.abspath(__file__))
SUFFIX = re.compile(r'\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|plc|ag|sa|se|nv|bv|gmbh|spa|srl|ab|asa|oyj|kk|pte|pty|holdings?|group|the|s\.a|s\.p\.a|tbk|bhd|berhad|jsc|pjsc|as|a/s|oy|lp|sab de cv|de cv)\b\.?', re.I)
def strict(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())
def loose(s): return strict(SUFFIX.sub(' ', re.sub(r'\(.*?\)', ' ', str(s))))
def regdom(d):
    d = re.sub(r'^(https?://)?(www\.)?', '', str(d or '').strip().lower()).split('/')[0]; p = d.split('.')
    if len(p) >= 3 and p[-2] in ('co', 'com', 'net', 'org', 'ac', 'gov', 'ne', 'or') and len(p[-1]) == 2: return '.'.join(p[-3:])
    return '.'.join(p[-2:]) if len(p) >= 2 else ''
ex = json.load(open(os.path.join(H, 'exclusion.json')))
NAMES = sorted({n for n in ex['names'] if len(n) >= 3}); NSET = set(NAMES); DOMS = set(ex['domains'])
FIRST = set(ex.get('first_words', []))
GENERIC = set('china chinese bank banco national first united american general global international new great royal grupo group the saudi emirates dubai abu qatar indian india japan japanese korea korean hong taiwan state city capital asia asian euro europe european north south east west central pacific atlantic western eastern northern southern standard universal premier prime golden silver metro public digital smart green blue red black white star sun power energy shanghai beijing shenzhen guangdong jiangsu zhejiang tokyo osaka mitsubishi sumitomo tata adani reliance siam thai malaysia singapore australian canadian british swiss german french italian spanish mexican brazilian'.split())
REV = sorted(n[::-1] for n in NAMES if len(n) >= 7)
def _prefixed(s, arr):
    i = bisect.bisect_left(arr, s); return i < len(arr) and arr[i].startswith(s)
def present(name, domain='', parent=''):
    d = regdom(domain)
    if d and d in DOMS: return 'website'
    for nm in (name, parent):
        if not nm: continue
        for k in {strict(nm), loose(nm)}:
            if len(k) < 3: continue
            if k in NSET: return 'name'
            if len(k) >= 4 and _prefixed(k, NAMES): return 'name variant'
            for j in range(7, len(k)):                                  # an excluded name is the start of this one
                if k[:j] in NSET: return 'name variant'
            if len(k) >= 7 and _prefixed(k[::-1], REV): return 'name variant'
            for j in range(len(k) - 7, 0, -1):                          # an excluded name is the end of this one
                if k[j:] in NSET and len(k) - j >= 7: return 'name variant'
        w0 = [strict(w) for w in re.sub(r'\(.*?\)', ' ', str(nm)).split() if strict(w)]
        if w0 and len(w0[0]) >= 5 and w0[0] not in GENERIC and w0[0] in FIRST: return 'shares first word'
        words = [strict(w) for w in SUFFIX.sub(' ', re.sub(r'\(.*?\)', ' ', str(nm))).split() if strict(w)]
        for i in range(1, len(words)):                                     # leading or trailing word span, e.g. "Saudi Aramco"
            for span in (''.join(words[:i]), ''.join(words[i:])):
                if len(span) >= 5 and span in NSET: return 'name variant'
    return ''

# phrase index (built from every short cell on both sheets): a brand whose full cleaned name appears as a phrase counts as present
_PH = None
LEGAL = re.compile(r"\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|plc|ag|sa|se|nv|bv|gmbh|spa|srl|ab|asa|oyj|kk|pte|pty|holdings?|group|the|tbk|bhd|berhad|jsc|pjsc|lp)\b\.?")
def phrase_present(name):
    global _PH
    if _PH is None:
        f = os.path.join(H, 'sheet_phrases.json'); _PH = set(json.load(open(f))) if os.path.exists(f) else set()
    w = re.findall(r"[a-z0-9&']+", LEGAL.sub(' ', re.sub(r'\(.*?\)', ' ', str(name).lower().replace('’', "'"))))
    ph = ' '.join(w)
    if not ph or (len(ph.replace(' ', '')) < 4 and '&' not in ph): return ''
    if ph in _PH: return 'name on sheets (phrase)'
    w0 = [x for x in w if x not in ('the',)]
    if w0 and len(w0[0]) >= 6 and w0[0] not in GENERIC and w0[0] not in GENERIC2 and w0[0] in _PH: return 'distinctive word on sheets'
    return ''
GENERIC2 = set('hainan sichuan hunan hubei fujian shandong henan anhui jiangxi yunnan guangxi hebei shanxi liaoning jilin ningbo xiamen tianjin chongqing wuhan nanjing hangzhou suzhou qingdao dalian hokkaido kyushu chugoku shikoku tohoku kansai nagoya yokohama kyoto mumbai delhi bengaluru chennai kolkata karnataka gujarat punjab kerala jakarta bangkok manila hanoi saigon istanbul ankara cairo riyadh jeddah kuwait bahrain muscat doha lagos nairobi johannesburg sydney melbourne toronto montreal vancouver calgary mexico brasil brazil chile peru colombia argentina madrid barcelona milano milan paris london berlin munich vienna zurich geneva oslo stockholm helsinki copenhagen warsaw prague budapest athens lisbon dublin amsterdam brussels american british german french italian spanish nordic baltic orient oriental atlantic pacific global international national general united standard premier capital pioneer advanced applied digital energy power health medical financial finance securities insurance industries industrial holdings resources minerals mining metals steel chemicals chemical pharma pharmaceutical biotech therapeutics technologies technology systems solutions services logistics shipping airlines airways motors automotive electric electronics telecom communications networks network media entertainment foods beverage brewery brewing retail stores properties property realty estate development construction engineering infrastructure partners investment investments ventures trading enterprises corporation company'.split())
