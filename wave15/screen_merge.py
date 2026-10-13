"""Merge stage-1 screening outputs.
Writes wave15/screen_kept.json (deduped survivors) and wave15/parents_new.json (parent brands of dropped
subsidiaries that are not yet in the user's files or our candidate list). Prints a tally."""
import json, glob, re, unicodedata, csv
from collections import Counter
W = '/home/user/rg42/wave15'


def strict(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)', '', s)
    s = s.replace('&', ' and ').replace('.', ' ').replace('/', ' ').replace(',', ' ')
    s = re.sub(r'\b(inc|incorporated|ltd|limited|plc|corp|corporation|co|company|group|holdings|holding|ag|sa|spa|se|nv|llc|lp|l p|gmbh|as|the|sas|bv|ab|pte|pty|pvt|international|bank|financial|services)\b', ' ', s)
    return re.sub(r'[^a-z0-9]', '', s)


known = json.load(open(f'{W}/known_index.json')); KN = set(known['names'])
TIES = {strict(k) for k in json.load(open('/home/user/rg42/wave14/f1_ties_found.json'))}
cands = json.load(open(f'{W}/w15_candidates.json'))
SP = set()
for row in csv.DictReader(open('/home/user/rg42/reports/f1-sponsor-competitor-map-ring2-2026-08.csv')):
    SP.add(strict(row.get('f1_sponsor')))
for row in csv.DictReader(open('/home/user/rg42/reports/f1-sponsor-competitor-map-2026-08.csv')):
    for x in (row.get('f1_sponsors_it_competes_with') or '').split(';'):
        for part in re.split(r'\(|\)| - ', x): SP.add(strict(part))
KL = [k for k in KN | SP if len(k) >= 4]


def near_known(pk):
    if pk in KN or pk in SP: return True
    for k in KL:
        if (len(k) >= 5 and pk.startswith(k)) or (len(pk) >= 5 and k.startswith(pk) and len(k) - len(pk) <= 8):
            return True
    return False

CK = {strict(r['name']) for r in cands}
inp = {}
for f in glob.glob(f'{W}/screen/in_*.json'):
    for r in json.load(open(f)): inp[r['id']] = r
kept, seen, parents, why = [], set(), Counter(), Counter()
n_out = 0
for f in sorted(glob.glob(f'{W}/screen/out_*.json')):
    try: rows = json.load(open(f))
    except Exception as e:
        print('BAD', f, e); continue
    for r in rows:
        n_out += 1
        base = inp.get(r.get('id'), {})
        if r.get('keep') is True or str(r.get('keep')).lower() == 'true':
            name = r.get('real_name') or r.get('company')
            k = strict(name)
            if k in KN or k in TIES or k in SP or strict(r.get('company')) in TIES:
                why['already in files / F1 sponsor (real name)'] += 1; continue
            if k in seen:
                why['duplicate survivor'] += 1; continue
            seen.add(k); kept.append({**base, **r, 'name': name})
        else:
            why[re.split(r'[:(,;]| of | by ', str(r.get('reason') or 'n/a'))[0].strip().lower()[:40]] += 1
            p = (r.get('parent') or '').strip()
            if p and 'subsidiar' in str(r.get('reason', '')).lower() + 'subsidiary':
                p = re.split(r'\s*\(|;|,\s*(?=[A-Z])', p)[0].strip()
                pk = strict(p)
                if len(pk) >= 3 and not near_known(pk) and pk not in KN and pk not in TIES and pk not in CK and not re.search(
                        r'city of|government|state of|ministry|municipal|republic|kingdom', p, re.I):
                    parents[p] += 1
json.dump(kept, open(f'{W}/screen_kept.json', 'w'), ensure_ascii=False, indent=0)
json.dump([{'name': p, 'children_seen': n} for p, n in parents.most_common()],
          open(f'{W}/parents_new.json', 'w'), ensure_ascii=False, indent=0)
print('screened', n_out, 'kept', len(kept), 'new parents', len(parents))
print('verdicts', Counter(r.get('verdict_guess') for r in kept))
print('top drop reasons', why.most_common(12))
print('top new parents', parents.most_common(25))
