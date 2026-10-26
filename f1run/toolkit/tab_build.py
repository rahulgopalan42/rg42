# Generic tab builder: merge <prefix>_NN_rows.json, apply the standard edit pass, write <out>.json.
# Usage: python3 tab_build.py <prefix> <out.json> [--skip "Brand=reason" ...] [--name "Brand=Email name" ...] [--ref "Brand=new market_reference" ...]
import json, glob, re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('prefix'); ap.add_argument('out')
ap.add_argument('--skip', action='append', default=[]); ap.add_argument('--name', action='append', default=[]); ap.add_argument('--ref', action='append', default=[])
a = ap.parse_args()
kv = lambda lst: dict(x.split('=', 1) for x in lst)
SKIP, NAME, REF = kv(a.skip), kv(a.name), kv(a.ref)
NOISE = re.compile(r'^(Length|Grid check|Web search budget|User note|Batch note \(all|Research note: (shared )?web ?search|Sources opened|Sources: f1salaries)', re.I)
rows = []
for f in sorted(glob.glob(f'{a.prefix}_[0-9][0-9]_rows.json')):
    rows += json.load(open(f))
for r in rows:
    b = r['brand']
    if b in SKIP: r['skip'] = SKIP[b]
    elif not r.get('variant') or any(str(f).startswith('DECLINED') for f in r.get('flags', [])):
        r['skip'] = next((str(f) for f in r.get('flags', []) if str(f).startswith('DECLINED')), 'Not built by research agent (no template fields returned).')
    if b in NAME: r['email_name'] = NAME[b]
    if b in REF: r['market_reference'] = REF[b]
    r['domain'] = re.sub(r'^(?:https?://)?(?:www\.)?([a-z0-9.-]+\.[a-z]+).*$', r'\1', (r.get('domain') or '').strip().lower())
    r['flags'] = [f for f in r.get('flags', []) if not NOISE.match(str(f))]
    for f in ('target_audience', 'market_overlap', 'market_reference', 'shared_values', 'f1_audience', 'fit_reason'):
        t = r.get(f) or ''
        t = re.sub(r'\s*[—–]\s*', ', ', t).replace('!', '.')
        t = re.sub(r'\bUSD\s', '', t)
        if r.get('email_name'): t = t.replace(b, r['email_name'])
        r[f] = re.sub(r'\s{2,}', ' ', t).strip()
    mr = r.get('market_reference') or ''
    if re.match(r'(No |None of |Few )', mr):          # never count open seats in the email
        rest = re.sub(r'^[^.]*\.\s*', '', mr, count=1)
        r['market_reference'] = (rest[0].upper() + rest[1:]) if rest else ''
        print('REF-OPENER fixed', b, '::', r['market_reference'][:90])
    if r['variant'] == 'B2C' and not (r.get('fit_reason') or '').startswith('due to'): print('FIT', b)
    if not re.match(r'^[a-z0-9.-]+\.[a-z]+$', r['domain']): print('DOMAIN', b, r['domain'])
    for fl in r['flags']:
        if re.search(r'hard caution|ALREADY ON THE GRID', str(fl)): print('CAUTION', b, '::', str(fl)[:120])
json.dump(rows, open(a.out, 'w'), indent=1)
print(a.prefix, 'rows', len(rows), 'B2C', sum(r['variant'] == 'B2C' for r in rows), 'skipped', sum('skip' in r for r in rows), 'flagged', sum(1 for r in rows if r.get('variant_flag') and not r.get('skip')))
