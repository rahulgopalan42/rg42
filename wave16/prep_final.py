"""Wave 16 final step 3: one row per confirmed-new brand (and possible duplicate) with every piece of free evidence
and all earlier work (pre-sort, research) mapped onto the corrected records. Writes base.pkl."""
import collections, csv, glob, json, os, re, sys
import pandas as pd
R = '/home/user/rg42'; W15 = f'{R}/wave15'
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
sys.path.insert(0, f'{R}/wave16')
from dedupe_v2 import regdom as regdom2, strict
from sectors_v3 import sector_of_industry, NAMES
csv.field_size_limit(10**9)
g = {'re': re}; exec(open(f'{R}/wave16/dedupe.py').read().split('SUF =')[0].split('import pandas')[0] +
                    'SL = ' + open(f'{R}/wave16/dedupe.py').read().split('SL = ')[1].split('SUF =')[0], g)
regdom1 = g['regdom']            # the key used by the earlier pre-sort / research files

allr = pd.read_pickle(f'{S}/new_all.pkl')
dd = pd.read_pickle(f'{S}/new_dedup_v2.pkl')
mm = pd.read_pickle(f'{S}/merge_map_v2.pkl')
dd['k'] = [d if d else 'n:' + str(n) for d, n in zip(dd['rd'], dd['name'])]
dd = dd[dd['dup_status'].isin(['new', 'maybe'])].copy()

# ---- map earlier work (keyed by the v1 domain key or 'n:'+name) onto the corrected rows
root = dict(zip(mm['drop'], mm['root']))
A = collections.defaultdict(set); B = {}
kk = dd['k'].to_dict()
for i, d, nm in zip(allr.index, allr['domain'], allr['name']):
    ri = root.get(i, i)
    if ri not in kk: continue
    k1 = regdom1(d) or 'n:' + str(nm)
    A[k1].add(kk[ri]); B[(k1, strict(nm))] = kk[ri]
def resolve(rid, company):
    k1 = rid or 'n:' + str(company)
    s = A.get(k1)
    if s and len(s) == 1: return next(iter(s))
    return B.get((k1, strict(company)))
def load_out(sub):
    d, lost = {}, 0
    for f in sorted(glob.glob(f'{R}/wave16/{sub}/out_*.json')):
        fi = f.replace('/out_', '/in_'); ins = json.load(open(fi)) if os.path.exists(fi) else []
        for i, r in enumerate(json.load(open(f))):
            src = ins[i] if i < len(ins) else {}
            rid = r.get('id') or ''
            comp = src.get('company') if (src.get('id') or '') == rid else (r.get('company') or '')
            k = resolve(rid, comp or r.get('company', ''))
            if k: d[k] = r
            else: lost += 1
    print(sub, 'records', len(d), 'not matched to a current new brand (now duplicates or merged)', lost)
    return d
ver, tri, v2 = load_out('verify'), load_out('triage'), load_out('verify2')
ps = load_out('presort') if glob.glob(f'{R}/wave16/presort/out_*.json') else {}

# ---- Clay revenue band: earlier Clay pulls (finer) else the Friday search filter
BANDS = ['75M-200M', '200M-500M', '500M-1B', '1B-10B', '10B-100B', '100B-1T']
band = {}
for f in glob.glob(f'{W15}/clay_*.tsv'):
    for r in csv.DictReader(open(f, encoding='utf-8', errors='replace'), delimiter='\t'):
        b = (r.get('annual_revenue') or '').strip()
        if b in BANDS:
            for d in {regdom2(r.get('domain', '')), regdom1(r.get('domain', ''))}:
                if d: band.setdefault(d, b)
def fband(s):
    s = s.lower().replace('$', '').replace(' ', '')
    if '1b-1t' in s: return '1B+'
    if '500m-1t' in s: return '500M+'
    if '200m-1b' in s: return '200M-1B'
    if '200m-500m' in s or '200-500m' in s: return '200M-500M'
    if '75m-200m' in s: return '75M-200M'
    return ''
ORDER = {'': 0, '75M-200M': 1, '200M-500M': 2, '200M-1B': 2, '500M+': 3, '1B+': 4}
dd['friday_band'] = dd['clay_search'].str.split(r' \|\| ').map(lambda xs: max((fband(x) for x in xs), key=lambda b: ORDER[b]))
dd['clay_band'] = [band.get(d) or fb for d, fb in zip(dd['rd'], dd['friday_band'])]

# ---- Apollo funded pulls (funding >= USD 100M per Apollo), listing, owner
ap = {}
for f in glob.glob(f'{W15}/apollo_*.tsv'):
    for r in csv.DictReader(open(f, encoding='utf-8', errors='replace'), delimiter='\t'):
        d = regdom2(r.get('primary_domain') or '')
        if d: ap[d] = r
m = dd['rd'].map(lambda d: ap.get(d) if d else None)
dd['funding_100m_apollo'] = m.notna()
dd['apollo_revenue'] = m.map(lambda r: r.get('organization_revenue_printed', '') if isinstance(r, dict) else '')
dd['apollo_exchange'] = m.map(lambda r: r.get('publicly_traded_exchange', '') if isinstance(r, dict) else '')
dd['apollo_owner'] = m.map(lambda r: r.get('owned_by_organization', '') if isinstance(r, dict) else '')

# ---- Wave 15 screening notes (same website)
w15 = {}
for f in glob.glob(f'{W15}/screen/out_*.json'):
    for r in json.load(open(f)):
        k = regdom2(r.get('id', ''))
        if k: w15[k] = r
pw = dd['rd'].map(lambda d: w15.get(d) if d else None)
dd['w15_note'] = pw.map(lambda r: (f"W15 screen (old rules): {'kept' if r.get('keep') is True else 'dropped - ' + str(r.get('reason', ''))}; "
                                   f"{r.get('scale_evidence', '')}")[:220] if isinstance(r, dict) else '')
dd['w15_parent'] = pw.map(lambda r: r.get('parent', '') if isinstance(r, dict) else '')
dd['w15_scale'] = pw.map(lambda r: r.get('scale_evidence', '') if isinstance(r, dict) else '')

# ---- parents: research > Apollo owner > Wave 15 > company description
def clean_parent(x):
    x = str(x or '').strip()
    if x.startswith('{'):
        try: x = json.loads(x).get('name', '')
        except Exception: x = ''
    if strict(x) in ('', 'none', 'india', 'china', 'usa', 'us', 'uk', 'the', 'unknown', 'na', 'nan', 'independent', 'self') or len(strict(x)) < 3: return ''
    return x
PAT = re.compile(r"\b(?:a |an )?(?:wholly[- ]owned )?(?:subsidiary|division|unit|member|part|brand|company|business|affiliate) of (?:the )?([A-Z][\w&.'\- ]{2,60}?)(?=[,.;)]| and | which | that | in | since |$)")
dd['parent_hint'] = dd['description'].fillna('').str.extract(PAT, expand=False).fillna('')
def parent_of(r):
    for x, src in (((v2.get(r.k) or {}).get('parent'), 'research'), ((ver.get(r.k) or {}).get('parent'), 'research'),
                   ((ps.get(r.k) or {}).get('p'), 'pre-sort (knowledge)'), ((tri.get(r.k) or {}).get('parent'), 'pre-sort (knowledge)'),
                   (r.apollo_owner, 'Apollo owner field'), (r.w15_parent, 'Wave 15 screen'), (r.parent_hint, 'company description')):
        x = clean_parent(x)
        if x and strict(x) != strict(r.name): return x, src
    return '', ''
pp = [parent_of(r) for r in dd.itertuples()]
dd['parent'] = [a for a, b in pp]; dd['parent_source'] = [b for a, b in pp]

# ---- sector: research correction > pre-sort correction > LinkedIn industry
OLD2NEW = [(r'automotive|mobility|commercial vehicle', 'Automotive & Mobility'), (r'aviation|aerospace|defen|space', 'Aerospace, Defence & Space'),
           (r'travel|hospitality|hotel', 'Travel, Hotels & Leisure'), (r'gambl|lotter', 'Gambling & Gaming Venues'),
           (r'sport|fitness', 'Sports, Fitness & Events'), (r'gaming|media|publishing|entertain', 'Media, Entertainment & Publishing'),
           (r'telecom', 'Telecommunications'), (r'chip|semicon|electronic|consumer electronics|photonic|eda', 'Semiconductors & Electronics'),
           (r'saas|software|ai |cloud|devtools|observability|cyber|grc|ucaas|data', 'Software, Internet & AI'),
           (r'it services|consult', 'IT Services & Consulting'), (r'bank', 'Banking & Lending'), (r'insur', 'Insurance'),
           (r'asset|private equity|trading|investment', 'Investment & Capital Markets'), (r'fintech|payment|financ', 'Financial Services & Payments'),
           (r'oil|gas|fuel', 'Oil, Gas & Fuels'), (r'energy|utilit|power|grid|renewab', 'Utilities & Renewable Energy'),
           (r'mining|metal|commodit', 'Mining & Metals'), (r'chemical|material|gases', 'Chemicals & Materials'),
           (r'machine|robot|automation|industrial|tools|packaging machinery|test|tic|mech', 'Industrial Machinery & Equipment'),
           (r'maritime|ship', 'Shipping, Maritime & Shipbuilding'), (r'logistic|transport|rail', 'Logistics & Transportation'),
           (r'construction|engineering', 'Construction & Engineering'), (r'real estate|building', 'Real Estate'), (r'home|furniture|living', 'Home & Furniture'),
           (r'luxury|watch|jewel', 'Luxury, Jewellery & Watches'), (r'beauty|cosmetic|personal care', 'Beauty & Personal Care'),
           (r'fashion|apparel|footwear', 'Fashion, Apparel & Footwear'), (r'beer|spirit|wine|alcohol', 'Alcoholic Drinks'),
           (r'food|beverage', 'Food & Beverage'), (r'tobacco|nicotine', 'Tobacco & Nicotine'), (r'retail|e-commerce|consumer', 'Retail & E-commerce'),
           (r'pharma|biotech|cdmo|cro', 'Pharma & Biotech'), (r'medtech|medical device', 'Medical Devices & Diagnostics'),
           (r'health|medical', 'Healthcare Services'), (r'agri', 'Agriculture & Agribusiness'), (r'packaging', 'Packaging & Printing'),
           (r'staffing|talent|hr', 'Staffing & HR'), (r'marketing|advertis', 'Marketing, Advertising & PR'),
           (r'law|legal', 'Professional & Business Services'), (r'education|edtech', 'Education & Training'), (r'security', 'Security Services')]
def map_old(s):
    s = str(s or '').strip()
    if not s or s.lower() in ('none', 'no', '-', 'n/a'): return ''
    if s in NAMES: return s
    for rx, new in OLD2NEW:
        if re.search(rx, s, re.I): return new
    return ''
def sector_of(r):
    v = map_old((v2.get(r.k) or {}).get('sector_override'))
    if v: return v, 'research'
    x = (ps.get(r.k) or {}).get('sec')
    if isinstance(x, int) and 1 <= x <= len(NAMES): return NAMES[x - 1], 'pre-sort correction'
    return sector_of_industry(r.industry), 'LinkedIn industry'
sx = [sector_of(r) for r in dd.itertuples()]
dd['sector'] = [a for a, b in sx]; dd['sector_basis'] = [b for a, b in sx]

# ---- attach earlier work
dd['tri_t'] = dd['k'].map(lambda k: (tri.get(k) or {}).get('t', ''))
dd['tri_fit'] = dd['k'].map(lambda k: (tri.get(k) or {}).get('fit'))
dd['tri_scale'] = dd['k'].map(lambda k: (tri.get(k) or {}).get('scale', ''))
dd['tri_note'] = dd['k'].map(lambda k: (tri.get(k) or {}).get('note', ''))
dd['researched'] = dd['k'].isin(v2)
dd['v1'] = dd['k'].isin(ver)
dd['presorted'] = dd['k'].isin(ps)
pd.to_pickle({'v2': v2, 'ver': ver, 'tri': tri, 'ps': ps}, f'{S}/work_maps.pkl')
dd.to_pickle(f'{S}/base.pkl')
print('base rows', len(dd), dd['dup_status'].value_counts().to_dict())
print('researched', int(dd['researched'].sum()), 'pre-sorted (earlier)', int((dd['tri_t'] != '').sum()), 'pre-sorted (new)', int(dd['presorted'].sum()))
print('clay band', dd['clay_band'].replace('', 'filter only').value_counts().to_dict())
print('with parent', int((dd['parent'] != '').sum()), 'sectors', dd['sector'].nunique())
