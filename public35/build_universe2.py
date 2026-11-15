"""Second universe: companies on the stockanalysis.com exchange lists that are not in the first universe.
 - parses <raw>/lists/<code>_<page>.html (ticker, name, market cap and revenue in the exchange currency)
 - converts to USD with a rate per currency taken from companies that are in both sources (median of market-cap ratios)
 - drops companies already in the first universe (same ticker on the same exchange, or same name) and second listings
 - keeps companies with revenue of USD 187M+ or a market value of USD 5B+ (these lists carry revenue only; below that no sector's capacity test can be met)
 - adds the LinkedIn industry and HQ city from the Clay exports in the repo where the name matches
Writes public35/data/universe2.json.gz.   Usage: build_universe2.py <raw dir>"""
import glob, gzip, html, json, os, re, statistics, sys, unicodedata
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); RAW = sys.argv[1]; D = os.path.join(RAW, 'lists')
SUFFIX = re.compile(r'\b(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|plc|ag|sa|se|nv|bv|gmbh|spa|srl|ab|asa|oyj|kk|pte|pty|holdings?|group|the|s\.a|s\.p\.a|tbk|bhd|berhad|jsc|pjsc|as|a/s|oy|lp|'
                    r'sab de cv|sapi de cv|sa de cv|de cv|sab|cv|public|pcl|publ|joint stock|class [abc]|ordinary shares?|adr|ads|pt|kgaa|ojsc|saa|sae|saog|psc|qpsc|kscp|tas|anonim sirketi|a s)\b\.?', re.I)
def loose(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()            # accents off: "América Móvil" = "America Movil"
    s = re.sub(r'\(.*?\)', ' ', s).replace('.', '').replace(',', ' ')                      # "N.V." -> "NV", "S.A.B. de C.V." -> "SAB de CV"
    return re.sub(r'[^a-z0-9]', '', SUFFIX.sub(' ', s).lower())
SUF = {'SHA': 'SS', 'SHE': 'SZ', 'HKG': 'HK', 'TYO': 'T', 'KRX': 'KS', 'KOSDAQ': 'KQ', 'TPE': 'TW', 'TPEX': 'TWO', 'NSE': 'NS', 'BOM': 'BO', 'LON': 'L', 'AIM': 'L', 'EPA': 'PA', 'ETR': 'DE',
       'BIT': 'MI', 'SWX': 'SW', 'AMS': 'AS', 'EBR': 'BR', 'ELI': 'LS', 'ISE': 'IR', 'BME': 'MC', 'STO': 'ST', 'HEL': 'HE', 'CPH': 'CO', 'OSL': 'OL', 'WSE': 'WA', 'IST': 'IS', 'ATH': 'AT',
       'BUD': 'BD', 'PRA': 'PR', 'BVB': 'RO', 'ASX': 'AX', 'NZE': 'NZ', 'TSX': 'TO', 'BVMF': 'SA', 'BMV': 'MX', 'SNSE': 'SN', 'BVC': 'CL', 'TADAWUL': 'SR', 'ADX': 'AE', 'DFM': 'AE',
       'QSE': 'QA', 'KWSE': 'KW', 'TLV': 'TA', 'JSE': 'JO', 'EGX': 'CA', 'CBSE': 'CS', 'NGX': 'LG', 'MSM': 'OM', 'BAX': 'BH', 'BKK': 'BK', 'KLSE': 'KL', 'IDX': 'JK', 'SGX': 'SI', 'PSE': 'PS',
       'HOSE': 'VN', 'PSX': 'PK', 'ICE': 'IC', 'NYSE': '', 'NASDAQ': '', 'AMEX': ''}
MULT = {'T': 1e12, 'B': 1e9, 'M': 1e6, 'K': 1e3}
def num(x):
    x = str(x).replace(',', '').strip(); m = re.fullmatch(r'(-?[\d.]+)([TBMK]?)', x)
    return float(m.group(1)) * MULT.get(m.group(2), 1) if m else None
def tkey(t, suf):
    t = re.sub(r'[._ ]', '-', str(t).upper())
    if suf == 'HK': t = t.lstrip('0')
    return t + '.' + suf if suf else t
EX = {e['code']: e for e in json.load(open(os.path.join(D, 'exchanges.json')))}
rows = []
for f in sorted(glob.glob(os.path.join(D, '*_*.html'))):
    code = os.path.basename(f).rsplit('_', 1)[0]
    if code not in EX or code not in SUF: continue
    if 'Symbol' not in re.findall(r'<th[^>]*>(.*?)</th>', open(f, encoding='utf-8').read(), re.S)[1]: continue      # the US pages use another layout
    for r in re.findall(r'<tr[^>]*>(.*?)</tr>', open(f, encoding='utf-8').read(), re.S):
        c = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)]; l = re.findall(r'href="(/(?:quote|stocks)/[^"]+)"', r)
        if len(c) >= 7 and l: rows.append({'code': code, 'tk': c[1], 'name': re.sub(r'\s+', ' ', c[2]), 'mc': num(c[3]), 'rev': num(c[6]), 'url': 'https://stockanalysis.com' + l[0]})
print('rows parsed', len(rows), '| exchanges', len({r['code'] for r in rows}))
U = json.load(gzip.open(os.path.join(H, 'data', 'universe.json.gz'), 'rt'))
def ukey(sym):
    m = re.search(r'\.([A-Z]+)$', sym)
    return tkey(sym[:m.start()], m.group(1)) if m else tkey(sym, '')
ut = {ukey(c['sym']): c for c in U}; un = {loose(html.unescape(c['name'])) for c in U}
ratio = defaultdict(list)
for r in rows:
    c = ut.get(tkey(r['tk'], SUF[r['code']]))
    if c and r['mc'] and c.get('mcap'): ratio[EX[r['code']]['cur']].append(c['mcap'] / r['mc'])
byname = defaultdict(list); un_mc = {loose(html.unescape(c['name'])): c.get('mcap') for c in U}
for r in rows:                                                       # exchanges whose tickers are written differently in the two sources: match on the name instead
    m = un_mc.get(loose(r['name']))
    if m and r['mc']: byname[EX[r['code']]['cur']].append(m / r['mc'])
FX = {cur: statistics.median(v) for cur, v in ratio.items() if len(v) >= 5}; FX['USD'] = 1.0
for cur, v in byname.items():
    if cur not in FX and len(v) >= 5: FX[cur] = statistics.median(v)
known = {loose(r['name']) for r in rows if tkey(r['tk'], SUF[r['code']]) in ut}          # names of companies matched to the first universe on any listing
print('USD per unit of currency (from', sum(len(v) for v in ratio.values()), 'matched companies):', {k: round(v, 5) for k, v in sorted(FX.items())})
print('currencies with no rate (skipped):', sorted({EX[r['code']]['cur'] for r in rows} - set(FX)))
FOREIGN_LINE = {'LON': r'^0[A-Z0-9]{3}$', 'AIM': r'^0[A-Z0-9]{3}$', 'BVMF': r'(3[1-59])$', 'BIT': r'^\d', 'BME': r'^X[A-Z]{3,}', 'BKK': r'\d{2}$'}            # international order-book lines, Brazilian and Thai depositary receipts, Borsa Italiana global lines, Latibex lines in Madrid
SKIP_EX = {'NYSE', 'NASDAQ', 'AMEX', 'ETR', 'TSX'}                                       # well covered by the first universe; their lists mix in many foreign or dual listings
GROUP = {'Hong Kong': 'China', 'Macau': 'China'}
first = defaultdict(list)
for c in U:
    if not c.get('mcap'): continue
    e = (loose(html.unescape(c['name'])), c['mcap'], c.get('revenue') or 0, c['sym'])
    first[GROUP.get(c['country'], c['country'])].append(e)
    if '.' not in c['sym'] or c['sym'].endswith('.F'): first['*'].append(e)          # US-listed receipts and Frankfurt lines of companies whose home listing is elsewhere
def same_company(name, country, mc, rev):
    """the same company in the first universe under another ticker: (a) one name starts with the other and the market values are within 15%,
    or (b) for companies above USD 10B, market value and revenue both within 15%"""
    if not mc: return ''
    k = loose(name)
    for n, m, rv, sym in first[GROUP.get(country, country)] + first['*']:
        near = abs(mc / m - 1) < 0.15
        if near and len(n) >= 5 and len(k) >= 5 and (k.startswith(n) or n.startswith(k)): return sym
        if mc >= 1e10 and near and rev and rv and abs(rev / rv - 1) < 0.15: return sym
    return ''
LAST = ['LON', 'AIM', 'SWX', 'EPA', 'BIT', 'BMV', 'ASX', 'HKG', 'SGX']            # venues that also list foreign companies: a company's home listing is read first and kept
rows.sort(key=lambda r: LAST.index(r['code']) + 1 if r['code'] in LAST else 0)
new = {}; stat = Counter()
for r in rows:
    cur = EX[r['code']]['cur']; suf = SUF[r['code']]
    if r['code'] in SKIP_EX: stat['exchange already well covered'] += 1; continue
    if r['code'] in FOREIGN_LINE and re.search(FOREIGN_LINE[r['code']], r['tk']): stat['foreign line or depositary receipt'] += 1; continue
    if r['code'] == 'BMV' and not re.search(r'de C\.?V\.?|S\.?A\.?B\.?|^fibra', r['name'], re.I): stat['foreign line or depositary receipt'] += 1; continue
    if cur not in FX: stat['no rate'] += 1; continue
    k = tkey(r['tk'], suf); nm = loose(r['name'])
    if k in ut or nm in un or nm in known or len(nm) < 2 or re.search(r'Taiwan Semiconductor Manufacturing', r['name']): stat['already in the first universe'] += 1; continue
    mc = r['mc'] * FX[cur] if r['mc'] else None; rev = r['rev'] * FX[cur] if r['rev'] else None
    if not ((rev or 0) >= 1.87e8 or (mc or 0) >= 5e9): stat['below the discovery floor'] += 1; continue
    if same_company(r['name'], EX[r['code']]['country'], mc, rev): stat['already in the first universe (other ticker)'] += 1; continue      # revenue-only data: under USD 187M no sector test can reach USD 3M a year
    x = {'sym': r['tk'].upper() + ('.' + suf if suf else ''), 'name': r['name'], 'country': EX[r['code']]['country'], 'mcap': mc, 'revenue': rev, 'cats': [], 'src': 'sa',
         'sa': {'exchange': EX[r['code']]['name'], 'code': r['code'], 'cur': cur, 'fx': FX[cur], 'url': r['url']}}
    if nm in new: stat['second listing'] += 1; continue                # A+H shares, NSE+BSE, depositary receipts: the first (home) listing is kept
    new[nm] = x
# symbols must be unique across both universes
seen = {c['sym'] for c in U}; out = []
for x in new.values():
    if x['sym'] in seen: x['sym'] = x['sym'] + '@' + x['sa']['code']
    seen.add(x['sym']); out.append(x)
clay = {}
CN = {'usa': 'united states', 'uk': 'united kingdom', 'korea': 'south korea', 'uae': 'united arab emirates'}
for f in sorted(glob.glob(os.path.join(R, 'wave15', 'clay_export_*.tsv'))):
    with open(f, encoding='utf-8', errors='ignore') as fh:
        hdr = fh.readline().rstrip('\n').split('\t')
        for line in fh:
            p = line.rstrip('\n').split('\t')
            if len(p) < len(hdr): continue
            r = dict(zip(hdr, p)); k = (loose(r['name']), CN.get(r['country'].lower(), r['country'].lower()))
            if k[0] and (k not in clay or r['type'] == 'Public Company'): clay[k] = r
nclay = 0
for x in out:
    r = clay.get((loose(x['name']), x['country'].lower())) or (clay.get((loose(x['name']), 'china')) if x['country'] == 'Hong Kong' else None)
    if r: x['clay'] = {'city': r['locality'], 'industry': r['industry'], 'domain': r['domain'], 'type': r['type'], 'size': r['size']}; nclay += 1
json.dump(out, gzip.open(os.path.join(H, 'data', 'universe2.json.gz'), 'wt'), ensure_ascii=False)
print(dict(stat)); print('new companies', len(out), '| with a LinkedIn industry hint', nclay)
print('by country', Counter(x['country'] for x in out).most_common(30))
print('revenue 1B+', sum(1 for x in out if (x['revenue'] or 0) >= 1e9), '| 300M-1B', sum(1 for x in out if 3e8 <= (x['revenue'] or 0) < 1e9), '| under 300M', sum(1 for x in out if (x['revenue'] or 0) < 3e8))
