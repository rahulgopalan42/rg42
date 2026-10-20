"""Wave 16 Phase 1: screen every new company programmatically (no web searches).
Inputs: scratchpad new_dedup.pkl (dedupe.py), Apollo funded pulls, Wave 15 screening notes.
Output: wave16/phase1_screen.csv.gz (one row per new company) + research queue order."""
import csv, glob, json, re
import pandas as pd
R = '/home/user/rg42'; W15 = f'{R}/wave15'
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
csv.field_size_limit(10**8)
# --- reuse the Wave 15 sector map (Clay industry / keyword -> sector code)
src = open(f'{W15}/build_w15.py').read()
ns = {'re': re}
exec(src[src.index('# ---------------------------------------------------------------- sectors'):src.index('SANCTION = [')], ns)
fn = src[src.index('def sector_of(r):'):src.index('def tabname(code):')]
exec(fn, ns)
bc = open(f'{W15}/build_checked.py').read()
exec(bc[bc.index('XMAP = {'):bc.index('def tab_of(')], ns)
SECT, XMAP, sector_of = ns['S'], ns['XMAP'], ns['sector_of']

def sector_name(code):
    if code in SECT: return SECT[code]
    if code.startswith('X'):
        k = re.sub(r'^X[\s\-:]*', '', code).strip().lower()
        return XMAP.get(k, 'NEW Other')
    return 'NEW Other'

new = pd.read_pickle(f'{S}/new_dedup.pkl')
new = new[new['dup_status'].isin(['new', 'maybe'])].copy()
new['code'] = [sector_of({'name': n, 'domain': d, 'industry': i, 'naics': '', 'country': c})
               for n, d, i, c in zip(new['name'], new['domain'], new['industry'], new['country'])]
new['sector'] = new['code'].map(sector_name)

# --- revenue estimate from the Clay search filter (database estimate, NOT verified)
def band(s):
    s = s.lower().replace('$', '').replace(' ', '')
    if '1b-1t' in s or '500m-1t' in s: return (3, 'USD 500M+ (Clay band)')
    if '200m-1b' in s or '200m-500m' in s or '200-500m' in s: return (2, 'USD 200M-1B (Clay band)')
    if '75m-200m' in s: return (1, 'USD 75M-200M (Clay band)')
    return (0, '')
bb = new['clay_search'].str.split(r' \|\| ').map(lambda xs: max(band(x) for x in xs))
new['rev_tier'] = bb.map(lambda b: b[0]); new['rev_estimate'] = bb.map(lambda b: b[1])

# --- Apollo funded pulls: total funding >= USD 100M (Apollo database), revenue, listing, owner
ap = {}
for f in glob.glob(f'{W15}/apollo_*.tsv'):
    for r in csv.DictReader(open(f, encoding='utf-8', errors='replace'), delimiter='\t'):
        d = (r.get('primary_domain') or '').lower().strip()
        if d: ap[d] = r
import importlib.util
spec = importlib.util.spec_from_file_location('dd', f'{R}/wave16/dedupe.py')
regdom = None
exec(open(f'{R}/wave16/dedupe.py').read().split('SUF =')[0], g := {'re': re})
regdom = g['regdom']
apr = {regdom(k): v for k, v in ap.items()}
m = new['rd'].map(apr)
new['funding_100m_apollo'] = m.notna()
new['apollo_revenue'] = m.map(lambda r: r.get('organization_revenue_printed', '') if isinstance(r, dict) else '')
new['apollo_exchange'] = m.map(lambda r: r.get('publicly_traded_exchange', '') if isinstance(r, dict) else '')
new['apollo_owner'] = m.map(lambda r: r.get('owned_by_organization', '') if isinstance(r, dict) else '')

# --- Wave 15 screening notes for the same domain (prior research, may be stale)
w15 = {}
for f in glob.glob(f'{W15}/screen/out_*.json'):
    for r in json.load(open(f)):
        k = regdom(r.get('id', ''))
        if k and r.get('scale_evidence') or r.get('reason'):
            w15[k] = r
pw = new['rd'].map(w15)
new['w15_note'] = pw.map(lambda r: (f"W15 screen: {'kept' if r.get('keep') is True else 'dropped - ' + str(r.get('reason', ''))}; "
                                    f"{r.get('scale_evidence', '')}")[:200] if isinstance(r, dict) else '')
new['w15_parent'] = pw.map(lambda r: r.get('parent', '') if isinstance(r, dict) else '')

# --- parent hints (company description, Apollo owner, Wave 15)
PAT = re.compile(r"\b(?:a |an )?(?:wholly[- ]owned )?(?:subsidiary|division|unit|member|part|brand|company|business|affiliate) of (?:the )?([A-Z][\w&.'\- ]{2,60}?)(?=[,.;)]| and | which | that | in | since |$)")
new['parent_hint'] = new['description'].str.extract(PAT, expand=False).fillna('')
new['parent'] = new['apollo_owner'].where(new['apollo_owner'] != '', new['w15_parent'])
new['parent'] = new['parent'].where(new['parent'] != '', new['parent_hint']).fillna('').str.strip()

# --- Phase 1 financial status
def fstat(r):
    crit = []
    if r.rev_tier >= 1: crit.append('Revenue (estimate)')
    if r.funding_100m_apollo: crit.append('Funding (estimate)')
    return ' + '.join(crit) if crit else 'No data - needs verification'
new['phase1_criteria'] = [fstat(r) for r in new.itertuples()]

# --- preliminary F1-fit proxy (0-4) from sector + scale, per the established framework
CROWDED = {'01', '12', '14', '17', '24', '43'}          # banking, crypto/trading, cyber, cloud, logistics, automotive
AUD = {'03', '05', '06', '07', '08', '09', '10', '11', '13', '15', '16', '17', '19', '22', '25', '26', '28', '29', '31',
       '37', '38', '42', '47', '48', '49', '50', '53', '12', '14', '01'}
ALIGN = {'03', '05', '11', '13', '17', '23', '27', '28', '29', '32', '33', '35', '36', '37', '38', '40', '43', '48',
         '52', '56', '15', '08', '14', '22', '26', '34', '44', '45', '30'}
XALIGN = ('Aviation', 'Watches', 'Sporting', 'Consumer Electronics', 'Private Aviation', 'Quantum', 'Gaming', 'Batteries', 'Sports')
XAUD = ('Wealth', 'Asset Mgmt', 'Watches', 'Private Aviation', 'Sporting', 'Consumer Electronics', 'Real Estate', 'Gambling', 'Retail', 'Sports')
def fit(r):
    c, s = r.code[:2], r.sector
    big = r.size in ('1,001-5,000', '5,001-10,000', '10,001+') or r.type == 'Public Company'
    p = int(big)
    p += int(c in AUD or any(x in s for x in XAUD))
    p += int(c in ALIGN or any(x in s for x in XALIGN))
    p += int(c not in CROWDED and 'Beer' not in s and 'Oil' not in s)
    return p
new['fit_proxy'] = [fit(r) for r in new.itertuples()]
# financial strength proxy (0-30): revenue band and Apollo funding count the same way
new['fin_proxy'] = new['rev_tier'].map({0: 0, 1: 8, 2: 16, 3: 24}) + new['funding_100m_apollo'].map({True: 16, False: 0})
new['fin_proxy'] = new['fin_proxy'].clip(upper=30)
new['size_bonus'] = new['size'].map({'10,001+': 6, '5,001-10,000': 4, '1,001-5,000': 2}).fillna(0)
new['pre_score'] = (new['fit_proxy'] / 4 * 60 + new['fin_proxy'] + new['size_bonus']).round(1)
new = new.sort_values(['pre_score', 'fin_proxy'], ascending=False).reset_index(drop=True)
new['prelim_rank'] = new.index + 1
keep = ['prelim_rank', 'name', 'domain', 'rd', 'sector', 'industry', 'size', 'type', 'country', 'city', 'linkedin_url',
        'rev_estimate', 'funding_100m_apollo', 'apollo_revenue', 'apollo_exchange', 'parent', 'parent_hint', 'w15_note',
        'phase1_criteria', 'fit_proxy', 'fin_proxy', 'pre_score', 'dup_status', 'dup_reason', 'matched_in', 'source_csv', 'description']
new[keep].to_pickle(f'{S}/phase1.pkl')
new[keep].drop(columns=['description']).to_csv(f'{R}/wave16/phase1_screen.csv.gz', index=False, compression='gzip')
print('screened', len(new))
print(new['phase1_criteria'].value_counts().to_dict())
print('fit_proxy', new['fit_proxy'].value_counts().sort_index().to_dict())
print('top sectors', new['sector'].value_counts().head(12).to_dict())
print('with parent', (new['parent'] != '').sum())
print(new.head(15)[['name', 'sector', 'rev_estimate', 'funding_100m_apollo', 'fit_proxy', 'pre_score']].to_string())
