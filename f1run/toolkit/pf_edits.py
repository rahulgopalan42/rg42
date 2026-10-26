# Edit pass for the Prepare First rows: skips (already on grid / insolvency / suspended / acquired),
# reference openers that count open seats, domain clean-up. Usage: python3 pf_edits.py in.json out.json
import json, re, sys
rows = json.load(open(sys.argv[1]))
SKIP = {
    'Exein': 'Already on the grid: Official Physical AI Security Partner of Haas since July 2026. Renewal/upgrade conversation only.',
    'Loop Earplugs': 'Already on the grid: Official Earplug Partner of McLaren since 2025, renewed March 2026. Second-team pitch only; opener naming McLaren would misfire.',
    'Aescape': 'Insolvency: assets now in Aescape Recovery Inc. under a new capital structure. Confirm counterpart before any outreach.',
    'Sleep Number Coproration': 'Chapter 11 (June 2026) and sold to SNBR Inc. (Sleep Country Canada) in July 2026. Marketing authority unclear.',
    'Ab&B Biotech': 'HKEX trading suspended since April 2026 pending audit; China HQ. Do not send until status is clear.',
    'Oasis Security': 'Acquired by Cyera (July 2026); site now states the acquisition. Brand may not survive, approach Cyera instead.',
}
REF_FIX = {
    'Ridgeline': "UBS, one of the world's largest wealth managers and a buyer of your kind of platform, has been a Team Partner of Mercedes since 2011, and 2026 is its sixteenth season with the team. Nuveen and BNY at Williams show the same buyers are in the sport.",
    'HGP Intelligent Energy': "Your buyers' world is on the grid. Uranium developer NexGen Energy partners Aston Martin, and the same team signed CoreWeave, an AI cloud operator of the kind your reactors are built to serve, in 2025. CoreWeave gets its name on the wind tunnel, its logo on the car and the team's compute migration as a public reference.",
    'Bluefors': "IBM, which builds the superconducting quantum computers your systems are made to cool, is a Premium Partner of Ferrari. IBM gets a public showcase: its consulting arm rebuilt the Scuderia Ferrari app and the team runs its data on watsonx.data.",
    'Biossil': "The closest company to your world, AbbVie, became Official Pharmaceutical Partner of McLaren in October 2026. It uses the team to carry its Race to Innovate campaign and funds autoimmune disease charities for every ten points McLaren scores.",
    'ABL Bio': "The nearest company to your world, AbbVie, became Official Pharmaceutical Partner of McLaren in October 2026, using the team to carry its Race to Innovate campaign and funding autoimmune disease charities for every ten points McLaren scores.",
}
out = []
for r in rows:
    b = r['brand']
    if b in SKIP:
        r['skip'] = SKIP[b]
    if b in REF_FIX:
        r['market_reference'] = REF_FIX[b]
    r['domain'] = re.sub(r'^(?:https?://)?(?:www\.)?([a-z0-9.-]+\.[a-z]+).*$', r'\1', (r.get('domain') or '').strip().lower())
    for f in ('target_audience', 'market_overlap', 'market_reference', 'shared_values', 'f1_audience', 'fit_reason'):
        t = r.get(f) or ''
        t = re.sub(r'\s*[—–]\s*', ', ', t).replace('!', '.')
        t = re.sub(r'\bUSD\s', '', t)
        r[f] = re.sub(r'\s{2,}', ' ', t).strip()
    out.append(r)
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print('rows', len(out), 'skipped', sum('skip' in r for r in out))
