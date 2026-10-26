# Edit pass for Prepare First chunks 11-21 + display-name fixes for all rows. Usage: python3 pf_edits_B.py
import json, re
SKIP = {
    'Reve': 'Shut its image product on 27 Sep 2026 after an OpenAI investment; pivot product not yet announced. Hold until a product exists.',
    'Observe': 'Acquired by Snowflake (closed Feb 2026); now a Snowflake product line. Approach Snowflake marketing instead.',
    'MaintainX': 'Acquired by Autodesk (closed 3 Aug 2026); sponsorship sign-off now sits with Autodesk. Approach Autodesk instead.',
    'Celestial AI': 'No longer standalone: Marvell completed the acquisition on 2 Feb 2026. Approach Marvell Technology if wanted.',
}
# brand name as it should read inside the email (hook and Company column); contacts still keyed by the list name
EMAIL_NAME = {'Curapox': 'Curaprox', 'Nextop AI': 'Nexthop AI', 'Auradine': 'Velaura AI', 'Main Func': 'Genspark',
              'Huel UK/HQ': 'Huel', 'BIC HQ': 'BIC', 'Kose America': 'KOSE America', 'Vinci4D.AI': 'Vinci', 'Wispr AI': 'Wispr',
              'Etched AI': 'Etched', 'Science': 'Science Corporation', 'Radar': 'RADAR', 'Axiom': 'Axiom Math',
              'Atlas Data Storage': 'Atlas (AtlasBase)', 'Unconventional AI': 'Unconventional', 'Coway HQ': 'Coway',
              'humans&': 'humans&', 'Thrive Holdings': 'Thrive Holdings', 'Hadrian Automation': 'Hadrian', 'Celestial AI': 'Celestial AI'}
DOMAIN_FIX = {'Unconventional AI': '', 'Erebor': '', 'Observe': 'observeinc.com', 'Atlas Data Storage': 'atlasbase.com', 'Auradine': 'velaura.ai'}
NOISE = re.compile(r'^(Length:|Grid check: sector\.world|Web search budget|User note:|Batch note \(all 10 rows\)|Research note: WebSearch)', re.I)
rows = json.load(open('pf_B_rows.json'))
for r in rows:
    b = r['brand']
    if b in SKIP: r['skip'] = SKIP[b]
    if b in DOMAIN_FIX: r['domain'] = DOMAIN_FIX[b]
    r['domain'] = re.sub(r'^(?:https?://)?(?:www\.)?([a-z0-9.-]+\.[a-z]+).*$', r'\1', (r.get('domain') or '').strip().lower())
    r['flags'] = [f for f in r.get('flags', []) if not NOISE.match(str(f))]
    for f in ('target_audience', 'market_overlap', 'market_reference', 'shared_values', 'f1_audience', 'fit_reason'):
        t = r.get(f) or ''
        t = re.sub(r'\s*[—–]\s*', ', ', t).replace('!', '.')
        t = re.sub(r'\bUSD\s', '', t)
        r[f] = re.sub(r'\s{2,}', ' ', t).strip()
json.dump(rows, open('pf_B_edited.json', 'w'), indent=1)
A = json.load(open('pf_edited.json'))
for r in A:
    r['flags'] = [f for f in r.get('flags', []) if not NOISE.match(str(f))]
allrows = A + rows
for r in allrows:
    if r['brand'] in EMAIL_NAME and EMAIL_NAME[r['brand']] != r['brand']:
        r['email_name'] = EMAIL_NAME[r['brand']]
        # fields were written with the list name in a few cases; swap to the email name
        for f in ('target_audience', 'market_overlap', 'market_reference', 'shared_values', 'fit_reason'):
            r[f] = r[f].replace(r['brand'], r['email_name'])
json.dump(allrows, open('pf_final_rows.json', 'w'), indent=1)
print('A', len(A), 'B', len(rows), 'total', len(allrows), 'skipped', sum('skip' in r for r in allrows))
json.dump([{'brand': r['brand'], 'domain': r['domain']} for r in rows if not r.get('skip') and r['domain']], open('pf_enrich_in_B.json', 'w'), indent=0)
print('to enrich B:', len([r for r in rows if not r.get('skip') and r['domain']]))
