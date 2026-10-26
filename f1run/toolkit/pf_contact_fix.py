# Drop contacts that belong to a different company than the brand (manual review of email domains).
import json, sys
DROP_EMAILS = {'k.baldauf@shell.com', 'elliot.stevens@volta.ca', 'kevin.soler@volta.ca', 'iurie.boscanean@volta.ca',
               'innkeeper@thelodgeatponchasprings.com', 'philippe.dupont@vinci.com', 'annie@kose.com.my'}
d = json.load(open(sys.argv[1]))
n = 0
for r in d['rows']:
    before = len(r['people']); r['people'] = [p for p in r['people'] if p.get('email', '').lower() not in DROP_EMAILS]; n += before - len(r['people'])
json.dump(d, open(sys.argv[1], 'w'), indent=1); print('dropped', n)
