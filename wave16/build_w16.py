"""Wave 16 workbook from existing data only (Friday Clay CSVs + earlier Clay/Apollo pulls + Wave 15 notes + research outs).
Usage: python -I wave16/build_w16.py <out.xlsx>"""
import csv, glob, json, os, re, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
R = '/home/user/rg42'; W15 = f'{R}/wave15'
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
csv.field_size_limit(10**9)
g = {'re': re}; exec(open(f'{R}/wave16/dedupe.py').read().split('new = pd.read_pickle')[0].split('import pandas')[0] + open(f'{R}/wave16/dedupe.py').read().split('from rapidfuzz import process, fuzz')[1].split('new = pd.read_pickle')[0], g)
regdom, strict, core = g['regdom'], g['strict'], g['core']
p = pd.read_pickle(f'{S}/phase1.pkl')
dd = pd.read_pickle(f'{S}/new_dedup.pkl')
old = pd.read_pickle(f'{S}/old_all.pkl')

# ---------- finer Clay revenue band from earlier Clay pulls (free, already paid for)
BANDS = ['75M-200M', '200M-500M', '500M-1B', '1B-10B', '10B-100B', '100B-1T']
band = {}
for f in glob.glob(f'{W15}/clay_*.tsv'):
    for r in csv.DictReader(open(f, encoding='utf-8', errors='replace'), delimiter='\t'):
        d = regdom(r.get('domain', '')); b = (r.get('annual_revenue') or '').strip()
        if d and b in BANDS: band.setdefault(d, b)
fri = p['rev_estimate'].str.extract(r'USD (\S+)', expand=False).fillna('')
p['clay_band'] = p['rd'].map(band).fillna(fri.map({'75M-200M': '75M-200M', '200M-1B': '200M-1B', '500M+': '500M+'})).fillna('')
p['revenue_usd'] = p['clay_band'].map(lambda b: f'USD {b} (Clay estimate)' if b else 'USD 75M+ (Clay search filter)')

# ---------- verified research outputs (wave16/verify/out_*.json), if any
# rows without a domain get a name key; research/triage rows with a blank id are paired to their input row by position
p['k'] = [d if d else 'n:' + str(n) for d, n in zip(p['rd'], p['name'])]
def load_out(sub):
    d = {}
    for f in sorted(glob.glob(f'{R}/wave16/{sub}/out_*.json')):
        rows = json.load(open(f)); fin = f.replace('/out_', '/in_')
        ins = json.load(open(fin)) if os.path.exists(fin) else []
        for i, r in enumerate(rows):
            k = r.get('id') or ''
            if not k:
                if i < len(ins) and not ins[i].get('id'): k = 'n:' + str(ins[i].get('company', ''))
                else: continue
            d[k] = r
    return d
ver = load_out('verify')
VC = ['revenue', 'revenue_source', 'valuation', 'valuation_source', 'funding', 'funding_source', 'criteria_met',
      'verification', 'fit_score', 'fit_detail', 'parent', 'parent_source', 'f1_current', 'reason', 'sources']
for c in VC: p['v_' + c] = p['k'].map(lambda d: (ver.get(d) or {}).get(c, ''))
p['verified'] = p['k'].isin(ver)
tri = load_out('triage')
v2 = load_out('verify2')
p['tri_t'] = p['k'].map(lambda d: (tri.get(d) or {}).get('t', ''))
p['tri_fit'] = p['k'].map(lambda d: (tri.get(d) or {}).get('fit', None))
p['tri_scale'] = p['k'].map(lambda d: (tri.get(d) or {}).get('scale', ''))
p['tri_note'] = p['k'].map(lambda d: (tri.get(d) or {}).get('note', ''))
p['researched'] = p['k'].isin(v2)

def clean_parent(x):
    x = str(x or '').strip()
    if x.startswith('{'):
        try: x = json.loads(x).get('name', '')
        except Exception: x = ''
    if strict(x) in ('', 'none', 'india', 'china', 'usa', 'us', 'uk', 'the', 'unknown', 'na', 'nan') or len(strict(x)) < 3: return ''
    return x
p['parent'] = p['parent'].map(clean_parent)
p['parent_final'] = p['v_parent'].where(p['v_parent'] != '', p['parent'])
DIV = re.compile(r"( for | by |\b(uk|emea|apac|americas|europe|india|usa|us|canada|australia|germany|france|italia|espana|brasil|mexico|japan|china)\b.*$| - | division\b| unit\b)", re.I)
p['division_like'] = p['name'].str.contains(DIV, regex=True) & ~p['verified']

# ---------- scoring: F1 Fit (50) + Financial Capacity (50)
def gi(d, k, default=0):
    try: return int(float(d.get(k, default)))
    except Exception: return default
REVP = {'75M-200M': 3, '200M-500M': 6, '200M-1B': 6, '500M-1B': 8, '500M+': 8, '1B-10B': 11, '10B-100B': 14, '100B-1T': 14}
FITC = ['audience', 'synergy', 'alignment', 'international', 'category']
FINC = ['revenue_scale', 'capital', 'profitability_score', 'marketing']
rows = []
for r in p.itertuples():
    v = v2.get(r.k)
    if v:
        f = {k: gi(v, k) for k in FITC}; c = {k: gi(v, k) for k in FINC}; conf = v.get('confidence', 'Medium')
    else:
        fit4 = r.tri_fit if r.tri_t in ('real', 'division') and r.tri_fit is not None else r.fit_proxy
        try: fit4 = int(fit4)
        except Exception: fit4 = int(r.fit_proxy)
        big = r.size in ('1,001-5,000', '5,001-10,000', '10,001+') or r.type == 'Public Company'
        f = {'audience': round(fit4 / 4 * 12), 'synergy': round(fit4 / 4 * 12), 'alignment': round(fit4 / 4 * 8),
             'international': 3 if big else 2, 'category': 3}
        c = {'revenue_scale': REVP.get(r.clay_band, 3), 'capital': 4 if r.funding_100m_apollo else 2,
             'profitability_score': 5, 'marketing': 3}
        if r.tri_scale == 'large' and r.tri_t == 'real': c['revenue_scale'] = max(c['revenue_scale'], 11)
        conf = 'Low (knowledge pre-sort)' if r.tri_t else 'Very low (database only)'
    rows.append((sum(f.values()), sum(c.values()), conf, *[f[k] for k in FITC], *[c[k] for k in FINC]))
sc = pd.DataFrame(rows, index=p.index, columns=['fit50', 'fin50', 'confidence'] + FITC + FINC)
p = pd.concat([p, sc], axis=1)
p['fit'] = p['fit50']
p['priority'] = (p['fit50'] + p['fin50']).astype(int)
p['fit_basis'] = p['researched'].map({True: 'researched', False: 'preliminary'})

def status(r):
    v = v2.get(r.k)
    if v: return v.get('verification') or 'Researched'
    if r.tri_t == 'division': return 'Preliminary - division/sub-brand (pre-sort)'
    if r.tri_t == 'real': return 'Preliminary - real company (pre-sort), Clay revenue estimate'
    return 'Preliminary - Clay revenue estimate (unverified)'
p['research_status'] = [status(r) for r in p.itertuples()]
p['criteria'] = [((v2.get(r.k) or {}).get('criteria_met') or (r.v_criteria_met if r.verified and r.v_criteria_met else '') or
                  'Revenue >= USD 75M (Clay estimate)' + (' + Funding >= USD 100M (Apollo estimate)' if r.funding_100m_apollo else ''))
                 for r in p.itertuples()]


# ---------- existing F1 sponsors (known sponsor lists + research findings)
SPN = {}
for row in csv.DictReader(open(f'{R}/reports/f1-sponsor-competitor-map-ring2-2026-08.csv')):
    k = strict(row.get('f1_sponsor')); 
    if len(k) >= 3: SPN.setdefault(k, f"{row.get('f1_sponsor')} - {row.get('sponsor_f1_relationship', 'F1 partner')}")
for row in csv.DictReader(open(f'{R}/reports/f1-sponsor-competitor-map-2026-08.csv')):
    if (row.get('already_in_f1') or '').upper().startswith('Y'):
        k = strict(row.get('brand'))
        if len(k) >= 3: SPN.setdefault(k, f"{row.get('brand')} - already in F1 (sponsor map)")
for k, v in json.load(open(f'{R}/wave14/f1_ties_found.json')).items():
    kk = strict(k)
    if len(kk) >= 3: SPN.setdefault(kk, f'{k} - {str(v)[:160]}')
def f1flag(r):
    v = v2.get(r.k) or {}
    cur = str(v.get('f1_current') or r.v_f1_current or '').strip()
    if cur and not re.match(r'^(none|no |n/a|no current|not found|-)', cur, re.I):
        return cur[:220], 'research'
    k = strict(r.name)
    if k in SPN: return SPN[k][:220], 'known F1 sponsor list'
    pk = strict(r.parent_final)
    if pk in SPN and pk: return 'via parent: ' + SPN[pk][:200], 'parent on F1 sponsor list'
    return '', ''
ff = [f1flag(r) for r in p.itertuples()]
p['f1_deal'] = [a for a, b in ff]; p['f1_flag_src'] = [b for a, b in ff]

# manual review: possible duplicates, failed verification, unclear ownership flagged by research
p['nap'] = p['k'].map(lambda d: (v2.get(d) or {}).get('not_a_prospect', ''))
p['v1_junk'] = p['verified'] & (p['v_verification'] == 'Not verified') & ~p['researched']
mr_mask = ((p['dup_status'] == 'maybe') | (p['tri_t'] == 'junk') | (p['nap'].fillna('') != '') | p['v1_junk']
           | (p['researched'] & (p['research_status'] == 'Not verified') & (p['criteria'].str.startswith('None'))))
mr = p[mr_mask].copy(); q = p[~mr_mask].copy()
q = q.sort_values(['priority', 'fit50', 'fin50'], ascending=False).reset_index(drop=True)
q['overall_rank'] = q.index + 1
q['sector_rank'] = q.groupby('sector').cumcount() + 1

def reason(r):
    v = v2.get(r.k)
    if v and v.get('rationale'): return v['rationale']
    bits = []
    if r.verified and r.v_reason: return r.v_reason
    bits.append(f'preliminary: fit {r.fit50}/50, capacity {r.fin50}/50' + (f' (pre-sort: {r.tri_note})' if r.tri_note else ''))
    bits.append(r.revenue_usd.replace('USD ', '').replace(' (Clay estimate)', ' rev est'))
    if r.funding_100m_apollo: bits.append('100M+ funding (Apollo)')
    if r.size: bits.append(f'{r.size} staff')
    if r.type == 'Public Company': bits.append('listed')
    if r.division_like: bits.append('looks like a division/regional page (-10)')
    if r.parent_final: bits.append(f'part of {r.parent_final}')
    return '; '.join(bits)
q['why'] = [reason(r) for r in q.itertuples()]

# ---------- parent company overlaps (new brand's parent = brand/parent in the old data)
on = old[old['name'] != ''].assign(sn=old['name'].map(strict))
on = on[on['sn'].str.len() >= 3].drop_duplicates('sn').set_index('sn')
po = []
for r in p[p['parent_final'] != ''].itertuples():
    ps = strict(r.parent_final)
    if len(ps) >= 3 and ps in on.index:
        o = on.loc[ps]
        po.append([r.parent_final, o['name'], o['source'], r.name, r.domain, r.sector,
                   'parent is in your old data (as a brand)', r.v_parent_source or ('Apollo owner field' if r.apollo_exchange or r.funding_100m_apollo else 'company description / Wave 15 note'),
                   r.v_funding or '', 'unverified' if not r.verified else r.v_verification])
pod = pd.DataFrame(po, columns=['parent company', 'brand in old database', 'where (old file | tab)', 'brand in new database',
                                'new brand website', 'new brand sector', 'ownership relationship', 'evidence', 'parent financials (verified)', 'status'])
# new brands sharing a parent with each other (flag only)
sp = p[p['parent_final'] != ''].groupby(p['parent_final'].map(strict))['name'].agg(lambda x: '; '.join(sorted(set(x))[:12]))
cnt = p[p['parent_final'] != ''].groupby(p['parent_final'].map(strict)).size()
shared = pd.DataFrame({'parent (as written)': p[p['parent_final'] != ''].groupby(p['parent_final'].map(strict))['parent_final'].first(),
                       'new brands with this parent': sp, 'count': cnt})
shared = shared[shared['count'] >= 2].sort_values('count', ascending=False)

# ---------- excluded duplicates
ex = dd[dd['dup_status'] == 'dup'][['name', 'domain', 'dup_reason', 'matched_in', 'source_csv']]

# ---------- write workbook
bold = Font(bold=True, color='FFFFFF'); fill = PatternFill('solid', fgColor='1F3864')
wb = Workbook(write_only=True)
def sheet(title, header, rows, widths=None):
    ws = wb.create_sheet(title[:31])
    if widths:
        for i, w in enumerate(widths): ws.column_dimensions[chr(65 + i) if i < 26 else 'A' + chr(65 + i - 26)].width = w
    ws.freeze_panes = 'C2'
    ws.append(header)
    for r in rows: ws.append(r)
MH = ['overall rank', 'sector rank', 'brand', 'sector', 'website', 'PRIORITY SCORE (0-100)', 'F1 fit (0-50)',
      'financial capacity (0-50)', 'research confidence', 'research status', 'rationale',
      'annual revenue (USD)', 'revenue source / date', 'valuation (USD)', 'valuation source / date',
      'total funding (USD)', 'funding source / date', 'profitability', 'profitability source', 'marketing / sponsorship evidence',
      'financial criterion met', 'audience (15)', 'synergy (15)', 'alignment (10)', 'international (5)', 'category (5)',
      'revenue & scale (15)', 'valuation/capital (10)', 'profitability (15)', 'marketing capacity (10)',
      'existing F1 sponsor / deal', 'parent company', 'country', 'staff', 'type', 'source links', 'source CSV']
def mrow(r):
    v = v2.get(r.k) or {}
    src = v.get('sources') or r.v_sources or ''
    src = ' '.join(src[:4]) if isinstance(src, list) else str(src)
    return [r.overall_rank, r.sector_rank, r.name, r.sector, r.domain, r.priority, r.fit50, r.fin50, r.confidence,
            r.research_status, r.why,
            v.get('revenue') or r.v_revenue or r.revenue_usd, v.get('revenue_source') or r.v_revenue_source or 'Clay (search filter / band)',
            v.get('valuation') or r.v_valuation or 'unknown', v.get('valuation_source') or r.v_valuation_source,
            v.get('funding') or r.v_funding or ('USD 100M+ (Apollo estimate)' if r.funding_100m_apollo else 'unknown'),
            v.get('funding_source') or r.v_funding_source or ('Apollo funded-company pull, Oct 2026' if r.funding_100m_apollo else ''),
            v.get('profitability', 'unknown'), v.get('profitability_source', ''), v.get('marketing_evidence', 'unknown'),
            r.criteria, r.audience, r.synergy, r.alignment, r.international, r.category,
            r.revenue_scale, r.capital, r.profitability_score, r.marketing,
            r.f1_deal, r.parent_final, r.country, r.size, r.type, src, r.source_csv]
W = [8, 7, 32, 26, 22, 10, 8, 9, 18, 26, 60, 22, 30, 18, 26, 20, 26, 18, 26, 30, 28, 7, 7, 7, 7, 7, 7, 7, 7, 7, 24, 24, 14, 12, 14, 40, 18]
n_ver = int(q['verified'].sum())
readme = [['F1 Wave 16 - Friday Clay export: new brands, financially screened and ranked'], [''],
 ['What this is'], ['All 13 Friday Clay CSVs, deduplicated against your MASTER REFERENCE OCT, Upload 11 Oct, To Upload Oct 11, Wave 14 V4 and every earlier wave.'],
 ['Financial rule: qualifies on ANY ONE of revenue >= USD 75M, valuation >= USD 1B, total funding raised >= USD 100M (cumulative).'],
 ['Every Friday CSV was pulled with a Clay revenue filter of USD 75M+, so every brand carries preliminary revenue evidence (Clay ESTIMATE, not verified).'], [''],
 ['Research status'], ['  Preliminary - Clay revenue estimate (unverified): screened from existing data only.'],
 ['  Verified / Partially verified: independently checked with sources and dates (see source links).'],
 ['  Manual Review tab: possible duplicates, failed or unclear verification, unclear ownership.'],
 ['  One tab per sector: see the companion file ending -SECTORS.xlsx (split out to keep file sizes manageable).'], [''],
 ['OVERALL SPONSORSHIP PRIORITY SCORE (0-100) = F1 FIT (50) + FINANCIAL CAPACITY (50)'],
 ['  F1 fit: audience overlap 15, commercial synergies 15, brand alignment 10, international presence 5, category opportunity 5.'],
 ['  Financial capacity: revenue & scale 15, valuation/funding/capital 10, profitability & cash flow 15, marketing/sponsorship capacity 10.'],
 ['  Unknown figures are scored conservatively (profitability 5/15, marketing 3/10, capital 2/10) - never assumed strong or weak.'],
 ['  Researched brands: every component scored from evidence with sources (confidence High/Medium/Low).'],
 ['  Not yet researched: PRELIMINARY scores from Clay band, Apollo funding flag and a knowledge-only pre-sort (confidence Low / Very low).'],
 ['  Clay revenue = the >= USD 75M Clay search filter (database estimate). Verified figures replace estimates.'], [''],
 ['Counts'], [f'  Rows in the 13 CSVs: {len(pd.read_pickle(f"{S}/new_all.pkl")):,}   Unique companies: {len(dd) + len(pd.read_pickle(f"{S}/internal_dups.pkl")) - len(pd.read_pickle(f"{S}/internal_dups.pkl")):,}'],
 [f'  Excluded as duplicates of old/earlier-wave brands: {len(ex):,}   Possible duplicates (Manual Review): {(p.dup_status == "maybe").sum():,}'],
 [f'  New brands ranked: {len(q):,}   of which independently verified so far: {n_ver:,}'],
 [f'  Parent-company overlaps with old data: {len(pod):,}   Parents shared by 2+ new brands: {len(shared):,}'],
 [f'  Already F1 sponsors (directly or via parent) - listed on the Existing F1 Sponsors tab and flagged in the ranking: {(q.f1_deal != "").sum():,}'], [''],
 ['Do not treat parent-company finances as the brand\'s own. Figures marked "estimate" come from Clay/Apollo databases and must be confirmed before outreach.']]
ws = wb.create_sheet('00 READ ME'); ws.column_dimensions['A'].width = 140
for l in readme: ws.append(l)
ws.append(['']); ws.append(['Brands per sector', 'count'])
for s, c in q['sector'].value_counts().sort_index().items(): ws.append([s, int(c)])
sheet('01 Master Ranking', MH, (mrow(r) for r in q.itertuples()), W)
f1s = q[q['f1_deal'] != '']
sheet('Existing F1 Sponsors', ['overall rank', 'brand', 'sector', 'website', 'PRIORITY SCORE (0-100)', 'F1 deal / relationship', 'how identified', 'research status', 'parent company', 'country'],
      ([r.overall_rank, r.name, r.sector, r.domain, r.priority, r.f1_deal, r.f1_flag_src, r.research_status, r.parent_final, r.country] for r in f1s.itertuples()),
      [8, 32, 26, 22, 10, 70, 24, 26, 24, 14])
sheet('Parent Company Overlaps', list(pod.columns), pod.values.tolist(), [28, 28, 40, 30, 24, 26, 30, 30, 24, 14])
sheet('Shared Parents (new brands)', ['parent', 'new brands with this parent', 'count'], shared.values.tolist(), [34, 120, 8])
sheet('Excluded Duplicates', ['brand (new file)', 'website', 'reason excluded', 'already in (file | tab)', 'source CSV'], ex.values.tolist(), [34, 26, 50, 50, 20])
MRH = ['brand', 'website', 'sector', 'why in manual review', 'possible match / note', 'matched in', 'revenue (Clay estimate)', 'country', 'staff', 'source CSV']
sheet('Manual Review', MRH, ([r.name, r.domain, r.sector, 'possible duplicate' if r.dup_status == 'maybe' else r.research_status,
                              r.dup_reason or r.v_reason, r.matched_in, r.revenue_usd, r.country, r.size, r.source_csv] for r in mr.itertuples()),
      [32, 24, 26, 26, 50, 40, 26, 14, 12, 18])
wb.save(sys.argv[1])
# sector tabs go in a second workbook so each file stays under GitHub's 100MB limit
out2 = re.sub(r'\.xlsx$', '-SECTORS.xlsx', sys.argv[1])
wb = Workbook(write_only=True)
ws = wb.create_sheet('00 READ ME'); ws.column_dimensions['A'].width = 140
ws.append(['F1 Wave 16 - one tab per sector. Same columns and scores as 01 Master Ranking in ' + os.path.basename(sys.argv[1]) + '.'])
ws.append(['sector rank = rank within the sector; overall rank = rank across all sectors.']); ws.append([''])
ws.append(['Sector', 'brands'])
for sec, c in q['sector'].value_counts().sort_index().items(): ws.append([sec, int(c)])
for sec in sorted(q['sector'].unique()):
    sheet(sec, MH, (mrow(r) for r in q[q['sector'] == sec].itertuples()), W)
wb.save(out2)
# compact shortlist that opens comfortably in Google Sheets
out3 = re.sub(r'\.xlsx$', '-SHORTLIST.xlsx', sys.argv[1]).replace('-PRELIM', '')
wb = Workbook(write_only=True)
ws = wb.create_sheet('00 READ ME'); ws.column_dimensions['A'].width = 140
for l in [['F1 Wave 16 - shortlist (small enough for Google Sheets). Full data: ' + os.path.basename(sys.argv[1]) + ' and its -SECTORS file.'], [''],
          ['01 Researched Prospects: every brand researched with sources, ranked by PRIORITY SCORE, current F1 sponsors removed.'],
          ['02 Top 5,000 (all): the top 5,000 of the full ranking excluding current F1 sponsors; rows not yet researched carry PRELIMINARY scores (see research status).'],
          ['03 Existing F1 Sponsors: brands already in F1 directly or via a parent.'], [''],
          ['PRIORITY SCORE (0-100) = F1 FIT (50) + FINANCIAL CAPACITY (50); unknown figures scored conservatively.']]: ws.append(l)
nf = q[q['f1_deal'] == '']
sheet('01 Researched Prospects', MH, (mrow(r) for r in nf[nf['researched']].itertuples()), W)
sheet('02 Top 5,000 (all)', MH, (mrow(r) for r in nf.head(5000).itertuples()), W)
sheet('03 Existing F1 Sponsors', MH, (mrow(r) for r in f1s.itertuples()), W)
wb.save(out3)
q.to_pickle(f'{S}/ranked.pkl')
print('ranked', len(q), 'manual review', len(mr), 'excluded', len(ex), 'parent overlaps', len(pod), 'shared parents', len(shared), 'sectors', q['sector'].nunique())
