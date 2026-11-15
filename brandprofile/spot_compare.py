"""Blind web spot-check: 75 randomly drawn brands (25 High, 25 Medium, 25 Lower) looked up on the web without sight of the profile.
data/spot_sample_before.json = the profile values when the sample was drawn; data/spot_web.jsonl = what the web showed.   Usage: spot_compare.py [1 2 3]"""
import json, sys, os, re
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'); ours = json.load(open(D + '/spot_sample_before.json', encoding='utf-8'))
RS = ['Domestic', 'Regional', 'International', 'Global']
def ctry(h): return re.sub(r'[^a-z]', '', (h or '').split(',')[-1].lower()).replace('unitedstatesofamerica', 'unitedstates').replace('usa', 'unitedstates').replace('uk', 'unitedkingdom')
def city(h): return re.sub(r'[^a-z]', '', (h or '').split(',')[0].lower()) if ',' in (h or '') else ''
GROUPS = {'1': 'H', '2': 'M', '3': 'L'}
for n in sys.argv[1:] or ['1', '2', '3']:
    tot = dict(n=0, found=0, hqc=0, hqcity=0, cityn=0, status=0, reach0=0, reach1=0, reachn=0)
    for l in open(f'{D}/spot_web.jsonl', encoding='utf-8'):
        w = json.loads(l); o = ours[w['id']]
        if o['group'] != GROUPS[n]: continue
        tot['n'] += 1
        if not w.get('found'): print('NOT FOUND', w['id'], o['name']); continue
        tot['found'] += 1; flags = []
        if ctry(w['hq']) == ctry(o['hq']): tot['hqc'] += 1
        else: flags.append(f"HQ country: ours {o['hq']} / web {w['hq']}")
        if city(w['hq']) and city(o['hq']):
            tot['cityn'] += 1
            if city(w['hq']) == city(o['hq']): tot['hqcity'] += 1
            elif ctry(w['hq']) == ctry(o['hq']): flags.append(f"HQ city: ours {o['hq']} / web {w['hq']}")
        if w['status'] == o['status']: tot['status'] += 1
        else: flags.append(f"status: ours {o['status']} ({o['parent'] or o['ticker']}) / web {w['status']} ({w.get('parent') or w.get('ticker')})")
        if w['reach'] in RS and o['reach'] in RS:
            tot['reachn'] += 1; d = abs(RS.index(w['reach']) - RS.index(o['reach']))
            if d == 0: tot['reach0'] += 1
            elif d == 1: tot['reach1'] += 1; flags.append(f"reach 1 step: ours {o['reach']} ({o['basis']}) / web {w['reach']} - {w.get('evidence', '')[:110]}")
            else: flags.append(f"REACH {d} steps: ours {o['reach']} ({o['basis']}) / web {w['reach']} - {w.get('evidence', '')[:110]}")
        if flags: print(w['id'], '|', o['name'], f"[conf {o['conf']}] |", ' || '.join(flags), ('|| changed: ' + w['changed'][:90]) if w.get('changed') else '')
    print('SAMPLE', n, tot)
