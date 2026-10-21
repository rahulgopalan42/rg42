# Apollo REST contact enrichment for a small brand list (same hard rules as f1run/api_runner.py),
# widened to reach 3 to 4 verified senior or mid-level contacts per brand from the marketing and
# commercial team (CMO, VP marketing, brand, comms, partnerships, BD, CRO, sales, CEO, COO, strategy).
# Usage: python3 mini_enrich.py <brands.json> <out.contacts.json> [--dry] [--topup existing.json]
#   brands.json = [{"brand": ..., "domain": ...}, ...]
#   --dry: free searches only, prints the ranked candidate pool per brand, spends nothing.
#   --topup existing.json: keeps the people already banked for each brand and only matches new,
#          better-ranked candidates so the final four are the most senior verified people.
#   Domain search falling empty -> free company-name lookup -> people search by organisation id.
# HARD RULES: no phone reveals, no waterfall, no personal emails. Verified-grade work emails only.
import json, os, re, sys, time
import urllib.request, urllib.error

SCRATCH = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(SCRATCH, 'apollo_key.txt')).read().strip()
BASE = 'https://api.apollo.io/api/v1'
TITLES = ["marketing", "chief marketing officer", "vp marketing", "head of marketing", "brand",
          "communications", "partnerships", "business development", "commercial",
          "chief revenue officer", "sales", "growth", "chief executive officer", "founder",
          "president", "chief operating officer", "strategy", "corporate development"]
SENIORITIES = ["owner", "founder", "c_suite", "partner", "vp", "head", "director", "manager"]
STATUS = ['verified', 'likely to engage']
KEEP_STATUS = {'verified', 'likely to engage', 'likely_to_engage'}
ROLES = ['decision_maker', 'vp_marketing', 'cro', 'field_marketing']
MAX_MATCH_PER_BRAND = 10
SENIOR_FLOOR = 58          # scores at or above this count as senior or mid-level
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
HEXID = re.compile(r'^[a-f0-9]{24}$')

HARD_EXCLUDE = ('counsel', 'legal', 'analyst', 'analytics', 'board', 'independent director',
                'advisor', 'adviser', 'intern', 'consultant')
EXCLUDE = ('engineer', 'scientist', 'geolog', 'chemist', 'metallurg', 'software', 'developer',
           'data ', 'finance', 'financial', 'accountant', 'accounting', 'controller', 'treasur',
           'compliance', 'human resources', 'people', 'talent', 'recruit', 'information technology',
           ' it ', 'cyber', 'supply chain', 'procurement', 'plant', 'process ', 'maintenance',
           'laborator', 'technician', 'drill', 'mine manager', 'health', 'safety', 'environment',
           'permitting', 'land ', 'assistant', 'chief of staff', 'office manager', 'receptionist',
           'administrat', 'payroll', 'logistics', 'warehouse', 'quality', 'construction',
           'project manager', 'product manager', 'research')
KEEP_ANYWAY = ('marketing', 'brand', 'partnership', 'business development', 'communications',
               'commercial', 'revenue', 'sponsorship', 'growth')


def call(path, body, tries=4):
    for attempt in range(tries):
        req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method='POST',
                                     headers={'Content-Type': 'application/json',
                                              'Cache-Control': 'no-cache', 'x-api-key': KEY})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print('429 rate limit, sleeping 65s'); time.sleep(65); continue
            if e.code >= 500:
                time.sleep([5, 15, 45, 90][min(attempt, 3)]); continue
            print(f'HTTP {e.code} on {path}: {e.read().decode()[:160]}')
            return None
        except Exception as ex:
            print(f'network error on {path}: {ex}'); time.sleep(10)
    return None


def score(title):
    t = ' ' + (title or '').lower() + ' '
    if any(k in t for k in HARD_EXCLUDE):
        return 0
    if any(k in t for k in EXCLUDE) and not any(k in t for k in KEEP_ANYWAY):
        return 0
    junior = any(k in t for k in ('specialist', 'coordinator', 'associate', 'executive assistant'))
    senior = any(k in t for k in ('chief', 'vp', 'vice president', 'svp', 'evp', 'head', 'director', 'lead'))
    is_vp = 'vice president' in t or ' vp' in t or 'svp' in t or 'evp' in t
    if 'chief marketing' in t or ' cmo ' in t: return 100
    if 'marketing' in t and senior: return 95
    if any(k in t for k in ('brand', 'communications', 'demand generation', 'growth')) and senior: return 88
    if any(k in t for k in ('partnership', 'business development', 'alliances', 'sponsorship')) and senior: return 85
    if 'chief commercial' in t or ' cco ' in t or ('commercial' in t and senior): return 82
    if 'chief revenue' in t or ' cro ' in t or ('sales' in t and senior): return 78
    if junior: return 50
    if 'marketing' in t or 'brand' in t or 'communications' in t or 'growth' in t: return 72
    if any(k in t for k in ('partnership', 'business development', 'alliances', 'sponsorship', 'commercial')): return 70
    if 'chief executive' in t or ' ceo ' in t or 'founder' in t: return 66
    if ('president' in t and not is_vp) or 'managing director' in t or 'chief operating' in t or ' coo ' in t: return 62
    if any(k in t for k in ('strategy', 'corporate development', 'investor relations',
                            'public affairs', 'government affairs', 'external affairs',
                            'sustainability', 'chief strategy')): return 58
    if 'sales' in t or 'account' in t or 'customer' in t: return 50
    if senior or 'manager' in t: return 35
    return 20


def find_org(name):
    """Free company lookup by name -> (id, primary_domain, name) or None."""
    r = call('/mixed_companies/search', {'q_organization_name': name, 'per_page': 5, 'page': 1})
    for o in (r or {}).get('organizations') or []:
        if norm(name) in norm(o.get('name')) or norm(o.get('name')) in norm(name):
            return o.get('id'), o.get('primary_domain'), o.get('name')
    orgs = (r or {}).get('organizations') or []
    return (orgs[0].get('id'), orgs[0].get('primary_domain'), orgs[0].get('name')) if orgs else None


def search_brand(domain, brand):
    pool = {}

    def run(body):
        r = call('/mixed_people/api_search', body)
        for p in (r or {}).get('people') or []:
            pid = p.get('id')
            if pid and HEXID.match(pid) and pid not in pool:
                p['_name'] = (p.get('name') or f"{p.get('first_name') or ''} {p.get('last_name') or ''}").strip()
                pool[pid] = p
        time.sleep(0.4)

    def sweep(base):
        run({**base, 'person_titles': TITLES, 'contact_email_status': STATUS, 'per_page': 50})
        run({**base, 'person_seniorities': SENIORITIES, 'contact_email_status': STATUS, 'per_page': 100})
        if len(pool) < 8:
            run({**base, 'person_seniorities': SENIORITIES, 'per_page': 100})
        if len(pool) < 4:
            run({**base, 'per_page': 100})

    note = ''
    if domain:
        sweep({'q_organization_domains_list': [domain], 'page': 1})
    if not pool:
        org = find_org(brand)
        if org:
            oid, odom, oname = org
            note = f'via company lookup: {oname} ({odom})'
            sweep({'organization_ids': [oid], 'page': 1})
    return list(pool.values()), note


def ranked(people):
    seen, out = set(), []
    for p in sorted(people, key=lambda p: score(p.get('title')), reverse=True):
        if score(p.get('title')) <= 0:
            continue
        key = norm(p['_name']) or p['id']
        if key in seen:
            continue
        seen.add(key); out.append(p)
    return out


def bulk_match(ids):
    out = {}
    for i in range(0, len(ids), 10):
        r = call('/people/bulk_match', {'details': [{'id': x} for x in ids[i:i + 10]],
                                        'reveal_personal_emails': False})
        for m in ((r or {}).get('matches') or []):
            pid, email = m.get('id'), m.get('email') or ''
            status = (m.get('email_status') or '').lower()
            if pid and '@' in email and 'not_unlocked' not in email and status in KEEP_STATUS:
                out[pid] = {'email': email, 'name': m.get('name') or '', 'title': m.get('title') or ''}
        time.sleep(0.5)
    return out


def finalize(people):
    """Best four by seniority score; juniors only fill gaps."""
    people = sorted(people, key=lambda p: score(p.get('title')), reverse=True)[:4]
    for i, p in enumerate(people):
        p['role'] = ROLES[i]
    return people


def main():
    src, dst = sys.argv[1], sys.argv[2]
    dry = '--dry' in sys.argv
    existing = {}
    if '--topup' in sys.argv:
        for r in json.load(open(sys.argv[sys.argv.index('--topup') + 1]))['rows']:
            existing[norm(r['brand'])] = r.get('people') or []
    brands = json.load(open(src))
    rows, total, credits = [], 0, 0
    for b in brands:
        dom = (b.get('domain') or '').strip().lower()
        people, note = search_brand(dom, b['brand'])
        orgs = sorted({(p.get('organization') or {}).get('name') or '?' for p in people})
        cands = ranked(people)
        print(f'{b["brand"]} [{dom or "-"}] -> {len(people)} found, {len(cands)} usable; orgs={orgs[:3]} {note}')
        for p in cands[:8]:
            print(f'      {score(p.get("title")):>3}  {p["_name"] or "?"}  |  {p.get("title")}')
        if dry:
            continue
        have = list(existing.get(norm(b['brand']), []))
        # search results often carry first names only, so match on first name + title as well
        have_keys = {norm(p['name']) for p in have} | {norm(p['name'].split()[0]) + '|' + norm(p.get('title'))
                                                       for p in have if p.get('name')}
        queue = [p for p in cands if norm(p['_name']) not in have_keys and
                 norm(p['_name'].split()[0] if p['_name'] else '') + '|' + norm(p.get('title')) not in have_keys]
        used = 0
        while queue and used < MAX_MATCH_PER_BRAND:
            seniors = [p for p in have if score(p.get('title')) >= SENIOR_FLOOR]
            if len(seniors) >= 4:
                break
            nxt = queue[0]
            # stop when the next candidate cannot improve the final four
            if len(have) >= 4 and score(nxt.get('title')) <= min(score(p.get('title')) for p in have):
                break
            need = max(1, 4 - len(seniors))
            batch = queue[:min(need, MAX_MATCH_PER_BRAND - used)]
            queue = queue[len(batch):]
            used += len(batch)
            got = bulk_match([p['id'] for p in batch])
            for p in batch:
                if p['id'] in got:
                    info = got[p['id']]
                    if info['email'].lower() in {h['email'].lower() for h in have}:
                        continue
                    have.append({'name': info['name'] or p['_name'], 'title': info['title'] or p.get('title') or '',
                                 'email': info['email']})
        final = finalize(have)
        credits += used
        rows.append({'brand': b['brand'], 'people': final})
        total += len(final)
        print(f'   => {len(final)} verified ({used} new matches): ' + '; '.join(f'{p["name"]} ({p["title"][:35]})' for p in final))
    if dry:
        print('DRY RUN: no credits spent')
        return
    json.dump({'rows': rows}, open(dst, 'w'), indent=0)
    print(f'DONE: {total} emails across {len(rows)} brands, {credits} credits used -> {dst}')


if __name__ == '__main__':
    main()
