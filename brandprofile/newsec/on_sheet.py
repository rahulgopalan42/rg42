"""Usage: on_sheet.py "Name one" "Name two" ...   Says for each name whether it is already on the user's sheet, listed, or a current F1 partner."""
import json, os, re, sys, unicodedata
H = os.path.dirname(os.path.abspath(__file__))
K = json.load(open(os.path.join(H, 'known.json'), encoding='utf-8'))
sys.path.insert(0, os.path.dirname(H))
SUF = re.compile(r'\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|plc|sa|ag|se|nv|bv|gmbh|spa|srl|ab|as|oy|pte|pty|holdings?|group|the)\b')
def loose(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().replace('&', ' and ')
    s = re.sub(r'[^a-z0-9 ]', ' ', s); s = SUF.sub(' ', s)
    return re.sub(r'\s+', '', s)
try:
    import bp_build as b; lf = b.loose
except Exception: lf = loose
def near(n):
    q = lf(n)
    if len(q) < 3: return []
    return [v for k, v in K.items() if (k.startswith(q) or (len(k) >= 5 and q.startswith(k)) or (len(q) < 5 and k.startswith(q) and len(k) <= len(q) + 18)) and k != q][:4]
for n in sys.argv[1:]:
    hit = K.get(lf(n)) or K.get(loose(n))
    if hit: print(f"{n}: ALREADY KNOWN - {hit[1]} as {hit[0]}"); continue
    c = near(n)
    print(f"{n}: " + ('POSSIBLY KNOWN (same company? if yes, leave it out) - ' + '; '.join(v[0] + ' [' + v[1] + ']' for v in c) if c else 'new'))
