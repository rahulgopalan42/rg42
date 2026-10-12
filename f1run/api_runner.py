#!/usr/bin/env python3
# F1 Oct-11 run: Apollo REST contact enrichment runner.
# Reads the account API key from apollo_api_key.txt at the repo root (gitignored).
# Phase 1: bulk-matches the pre-picked ids in f1run/burst_picks_slim.json (if present).
# Phase 2: for every brand in the QUEUE files not already covered, searches (free),
# picks up to 4 people by role priority, bulk-matches them (1 credit per match).
# Writes f1run/out/<queuefile>.contacts.json after each file and appends to
# f1run/out/progress.log. Resumable: brands already in an out file are skipped.
# HARD RULES: no phone reveals, no waterfall, no personal emails - those request
# flags are never sent. Cap 4 contacts per brand, verified-grade emails only.
import json, os, re, subprocess, sys, time
import urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F1 = os.path.join(ROOT, 'f1run')
OUT = os.path.join(F1, 'out')
os.makedirs(OUT, exist_ok=True)
KEY = open(os.path.join(ROOT, 'apollo_api_key.txt')).read().strip()
BASE = 'https://api.apollo.io/api/v1'
TITLES = ["marketing", "chief marketing officer", "vp marketing", "head of marketing",
          "brand", "partnerships", "business development", "chief revenue officer",
          "chief executive officer"]
KEEP_STATUS = {'verified', 'likely to engage', 'likely_to_engage'}
QUEUE = ['w2k_remaining.json', 'w3k_upandcoming.json', 'w4k_sheet23.json',
         'w5k_devtools.json', 'w6k_defense.json', 'w7k_consumer.json',
         'w8k_robotics.json', 'w9k_dcpower.json', 'w10k_photonics.json',
         'w11k_lawfirms.json', 'w12k_energy.json', 'w13k_eda.json',
         'w14k_otphysical.json', 'w15k_homeliving.json', 'w16k_services.json',
         'w17k_tools.json', 'w18k_telecomspace.json', 'w19k_mobility.json',
         'w20k_grc.json', 'w21k_machinetool.json', 'w22k_supercomputing.json']
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
HEXID = re.compile(r'^[a-f0-9]{24}$')

def log(msg):
    line = time.strftime('%H:%M:%S ') + msg
    print(line, flush=True)
    with open(os.path.join(OUT, 'progress.log'), 'a') as f:
        f.write(line + '\n')

def call(path, body, tries=5):
    for attempt in range(tries):
        req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method='POST',
                                     headers={'Content-Type': 'application/json',
                                              'Cache-Control': 'no-cache', 'x-api-key': KEY})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                log(f'429 rate limit, sleeping 65s (attempt {attempt+1})'); time.sleep(65); continue
            if e.code >= 500:
                time.sleep([5, 15, 45, 90, 90][min(attempt, 4)]); continue
            log(f'HTTP {e.code} on {path}: {e.read().decode()[:160]}')
            return None
        except Exception as ex:
            log(f'network error on {path}: {ex}'); time.sleep(10)
    return None

def score(title):
    t = (title or '').lower()
    if 'chief marketing' in t or re.search(r'\bcmo\b', t): return 100
    if 'marketing' in t and ('vp' in t or 'vice president' in t): return 90
    if 'marketing' in t and ('head' in t or 'director' in t): return 80
    if 'brand' in t and any(k in t for k in ('vp', 'head', 'director', 'manager', 'lead')): return 72
    if 'marketing' in t: return 65
    if any(k in t for k in ('partnership', 'business development', 'alliances', 'sponsorship')): return 58
    if 'chief revenue' in t or re.search(r'\bcro\b', t): return 52
    if 'sales' in t and any(k in t for k in ('vp', 'head', 'director', 'chief')): return 48
    if 'chief commercial' in t or re.search(r'\bcco\b', t): return 45
    if 'chief executive' in t or re.search(r'\bceo\b', t) or 'founder' in t: return 40
    return 10

ROLES = ['decision_maker', 'vp_marketing', 'cro', 'field_marketing']

def clean_domain(d):
    d = (d or '').strip()
    d = re.split(r'[\s(]', d)[0].strip()
    return d if '.' in d else ''

def search_brand(domain):
    body = {'q_organization_domains_list': [domain], 'person_titles': TITLES,
            'contact_email_status': ['verified', 'likely to engage'], 'per_page': 25, 'page': 1}
    r = call('/mixed_people/search', body)
    people = (r or {}).get('people') or []
    if not people:
        body.pop('contact_email_status')
        r = call('/mixed_people/search', body)
        people = (r or {}).get('people') or []
    return people

def bulk_match(ids):
    out = {}
    for i in range(0, len(ids), 10):
        chunk = ids[i:i+10]
        r = call('/people/bulk_match', {'details': [{'id': x} for x in chunk],
                                        'reveal_personal_emails': False})
        for m in ((r or {}).get('matches') or []):
            pid, email = m.get('id'), m.get('email') or ''
            status = (m.get('email_status') or '').lower()
            if pid and '@' in email and 'not_unlocked' not in email and status in KEEP_STATUS:
                out[pid] = {'email': email, 'name': m.get('name') or '', 'title': m.get('title') or ''}
        time.sleep(0.5)
    return out

def git_push(paths, msg):
    try:
        subprocess.run(['git', '-C', ROOT, 'add'] + paths, check=True, timeout=60)
        subprocess.run(['git', '-C', ROOT, 'commit', '-m', msg], check=True, timeout=60)
        for attempt in range(4):
            subprocess.run(['git', '-C', ROOT, 'pull', '--rebase', 'origin',
                            'claude/f1-sponsorship-email-s5c362'], timeout=120)
            p = subprocess.run(['git', '-C', ROOT, 'push', '-u', 'origin',
                                'claude/f1-sponsorship-email-s5c362'], timeout=120)
            if p.returncode == 0:
                return True
            time.sleep(2 ** (attempt + 1))
    except Exception as ex:
        log(f'git error: {ex}')
    return False

# ---- phase 0: build late-tab queue files if missing ----
TABS = [('Law Firms', 'w11k_lawfirms.json'), ('200 - Energy ', 'w12k_energy.json'),
        ('EDA', 'w13k_eda.json'), ('OT & Physical', 'w14k_otphysical.json'),
        ('Home & Living', 'w15k_homeliving.json'), ('Services', 'w16k_services.json'),
        ('Tools & Industrial Supply', 'w17k_tools.json'), ('Telecom & Space', 'w18k_telecomspace.json'),
        ('Mobility', 'w19k_mobility.json'), ('GRC & Risk', 'w20k_grc.json'),
        ('Machine Tool', 'w21k_machinetool.json'), ('Supercomputing', 'w22k_supercomputing.json')]
reg_path = os.path.join(F1, 'run11_brands.json')
if os.path.exists(reg_path):
    reg = json.load(open(reg_path))
    made = []
    for tab, fname in TABS:
        fpath = os.path.join(F1, fname)
        if not os.path.exists(fpath):
            brands = [{'brand': b['brand'], 'domain': b.get('domain', '')} for b in reg if b['tab'] == tab]
            json.dump(brands, open(fpath, 'w'), indent=0)
            made.append(f'{fname}({len(brands)})')
    if made:
        log('built queue files: ' + ', '.join(made))
        git_push([os.path.join(F1, f) for _, f in TABS if os.path.exists(os.path.join(F1, f))],
                 'contacts: late-tab queue files')

# ---- phase 1: pre-picked ids ----
slim_path = os.path.join(F1, 'burst_picks_slim.json')
phase1_rows = {}
if os.path.exists(slim_path):
    slim = json.load(open(slim_path))
    done_marker = os.path.join(OUT, 'phase1.contacts.json')
    if os.path.exists(done_marker):
        for row in json.load(open(done_marker))['rows']:
            phase1_rows[norm(row['brand'])] = row
        log(f'phase1 already done: {len(phase1_rows)} brands loaded')
    else:
        ids = [i for i in slim if HEXID.match(i)]
        log(f'phase1: matching {len(ids)} pre-picked ids')
        got = bulk_match(ids)
        for pid, info in got.items():
            meta = slim[pid]
            b = meta['brand']
            row = phase1_rows.setdefault(norm(b), {'brand': b, 'people': []})
            if len(row['people']) < 4 and not any(norm(p['name']) == norm(info['name']) for p in row['people']):
                row['people'].append({'name': info['name'] or meta['name'],
                                      'title': info['title'] or meta['title'],
                                      'role': meta['role'], 'email': info['email']})
        json.dump({'rows': list(phase1_rows.values())}, open(done_marker, 'w'), indent=0)
        log(f'phase1 done: {sum(len(r["people"]) for r in phase1_rows.values())} emails '
            f'across {len(phase1_rows)} brands')
        git_push([done_marker], 'contacts: phase1 pre-picked ids')

# ---- phase 2: per queue file ----
grand_brands = grand_emails = 0
for qf in QUEUE:
    qpath = os.path.join(F1, qf)
    if not os.path.exists(qpath):
        log(f'skip missing {qf}'); continue
    brands = json.load(open(qpath))
    opath = os.path.join(OUT, qf + '.contacts.json')
    rows = {norm(r['brand']): r for r in (json.load(open(opath))['rows'] if os.path.exists(opath) else [])}
    changed = False
    for b in brands:
        nb = norm(b['brand'])
        if nb in rows:
            continue
        if nb in phase1_rows:
            rows[nb] = phase1_rows[nb]; changed = True; continue
        dom = clean_domain(b.get('domain'))
        if not dom:
            rows[nb] = {'brand': b['brand'], 'people': [], 'note': 'no usable domain'}
            changed = True; log(f'{b["brand"]}: NO DOMAIN'); continue
        people = search_brand(dom)
        time.sleep(0.5)
        cands = [p for p in people if p.get('id') and HEXID.match(p['id'])]
        cands.sort(key=lambda p: score(p.get('title')), reverse=True)
        picks = [p for p in cands if score(p.get('title')) >= 40][:4] or cands[:2]
        seen, final = set(), []
        for p in picks:
            if norm(p.get('name')) in seen: continue
            seen.add(norm(p.get('name'))); final.append(p)
        got = bulk_match([p['id'] for p in final]) if final else {}
        ppl = []
        for p in final:
            if p['id'] in got and len(ppl) < 4:
                info = got[p['id']]
                ppl.append({'name': info['name'] or p.get('name') or '',
                            'title': info['title'] or p.get('title') or '',
                            'role': ROLES[len(ppl)] if len(ppl) < 4 else 'spare',
                            'email': info['email']})
        rows[nb] = {'brand': b['brand'], 'people': ppl}
        changed = True
        grand_emails += len(ppl)
        log(f'{b["brand"]}: {len(ppl)} emails')
        if len(rows) % 20 == 0:
            json.dump({'rows': list(rows.values())}, open(opath, 'w'), indent=0)
    grand_brands += len(brands)
    if changed or not os.path.exists(opath):
        json.dump({'rows': list(rows.values())}, open(opath, 'w'), indent=0)
        git_push([opath, os.path.join(OUT, 'progress.log')], f'contacts: {qf}')
        log(f'FILE DONE {qf}: {len(rows)} brands')
log(f'ALL DONE: {grand_brands} brands processed this run, {grand_emails} new emails')
