# Merge pf_*_rows.json and run a compact QC: word counts, banned patterns, repeated references, flags.
import json, glob, re, collections, sys
rows = []
for f in sorted(glob.glob('pf_*_rows.json')):
    for r in json.load(open(f)):
        r['_chunk'] = f[3:5]; rows.append(r)
json.dump(rows, open('pf_all_rows.json', 'w'), indent=1)
print('rows', len(rows), 'B2B', sum(r['variant']=='B2B' for r in rows), 'B2C', sum(r['variant']=='B2C' for r in rows))
wc = lambda s: len((s or '').split())
F = ['target_audience','market_overlap','market_reference','shared_values','f1_audience']
issues = collections.defaultdict(list)
refs = collections.Counter()
for r in rows:
    b = r['brand']
    total = sum(wc(r.get(f)) for f in F)
    if total > 215: issues['long>215'].append(f'{b}:{total}')
    for f in F + ['fit_reason','designation']:
        t = r.get(f) or ''
        if re.search(r'[—–]', t): issues['dash'].append(f'{b}:{f}')
        if '!' in t: issues['exclam'].append(f'{b}:{f}')
        if re.search(r'\b(actually|genuinely|honestly|cutting.edge)\b', t, re.I): issues['banned word'].append(f'{b}:{f}')
        if '$' in t or re.search(r'\bUSD\b|\d+(\.\d+)?\s?(bn|billion|million|M\b)', t): issues['money'].append(f'{b}:{f}')
    ta = r.get('target_audience') or ''
    if r['variant']=='B2B' and re.search(r'\d+%|\d{2,}', ta): issues['stat in TA'].append(b)
    if r['variant']=='B2B' and not ta.startswith('Your target customers are'): issues['TA opener'].append(b)
    if r['variant']=='B2C' and not (r.get('fit_reason') or '').startswith('due to'): issues['fit_reason'].append(b)
    if r['variant']=='B2C' and not r.get('f1_audience'): issues['no f1_audience'].append(b)
    if not r.get('designation','').startswith('Official '): issues['designation'].append(b)
    if r.get('market_reference'):
        m = re.match(r'(?:Your (?:direct competitor|closest (?:rival|peer)[^,]*),? )?([A-Z][\w&\.\' ]+?)(?:,| has| became| joined| is| put| which)', r['market_reference'])
        refs[m.group(1).strip() if m else r['market_reference'][:25]] += 1
    if any('ALREADY ON THE GRID' in str(x) or 'already a' in str(x).lower() and 'partner' in str(x).lower() for x in r.get('flags',[])): issues['on grid'].append(b)
    if any('DECLINED' in str(x) for x in r.get('flags',[])): issues['declined'].append(b)
    if any(re.search(r'hard caution', str(x), re.I) for x in r.get('flags',[])): issues['hard caution'].append(b)
for k, v in issues.items(): print(f'{k} ({len(v)}):', '; '.join(v[:40]))
print('references:', refs.most_common(12))
dc = collections.Counter(r['designation'] for r in rows)
print('dup designations:', [(d,n) for d,n in dc.items() if n>1])
