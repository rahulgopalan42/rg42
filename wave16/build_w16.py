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
ver = {}
for f in sorted(glob.glob(f'{R}/wave16/verify/out_*.json')):
    for r in json.load(open(f)): ver[r['id']] = r
VC = ['revenue', 'revenue_source', 'valuation', 'valuation_source', 'funding', 'funding_source', 'criteria_met',
      'verification', 'fit_score', 'fit_detail', 'parent', 'parent_source', 'f1_current', 'reason', 'sources']
for c in VC: p['v_' + c] = p['rd'].map(lambda d: (ver.get(d) or {}).get(c, ''))
p['verified'] = p['rd'].isin(ver)

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

# ---------- scoring (documented in README)
FIN = {'75M-200M': 8, '200M-500M': 14, '200M-1B': 14, '500M-1B': 20, '500M+': 22, '1B-10B': 26, '10B-100B': 30, '100B-1T': 30}
def fin_pts(r):
    v = FIN.get(r.clay_band, 8)
    if r.funding_100m_apollo: v = max(v, 14)
    if r.verified and r.v_verification in ('Verified', 'Partially verified'):
        try: v = int(ver[r.rd].get('financial_points', v))
        except Exception: pass
    return v
REACH = {'10,001+': 10, '5,001-10,000': 8, '1,001-5,000': 6, '501-1,000': 4, '201-500': 2}
p['fit'] = [int(r.v_fit_score) if r.verified and str(r.v_fit_score).isdigit() else r.fit_proxy for r in p.itertuples()]
p['fit_basis'] = p['verified'].map({True: 'researched', False: 'preliminary (sector-based)'})
p['fin_points'] = [fin_pts(r) for r in p.itertuples()]
p['reach_points'] = [min(10, REACH.get(r.size, 0) + (2 if r.type == 'Public Company' else 0)) for r in p.itertuples()]
p['verif_points'] = p['v_verification'].map({'Verified': 10, 'Partially verified': 5}).fillna(0)
p['priority'] = (p['fit'] * 12.5 + p['fin_points'] + p['reach_points'] + p['verif_points'] - p['division_like'].map({True: 10, False: 0})).clip(lower=0).round(1)

def status(r):
    if r.verified: return r.v_verification or 'Researched'
    return 'Preliminary - Clay revenue estimate (unverified)'
p['research_status'] = [status(r) for r in p.itertuples()]
p['criteria'] = [(r.v_criteria_met if r.verified and r.v_criteria_met else
                  'Revenue >= USD 75M (Clay estimate)' + (' + Funding >= USD 100M (Apollo estimate)' if r.funding_100m_apollo else ''))
                 for r in p.itertuples()]


# manual review: possible duplicates, failed verification, unclear ownership flagged by research
mr_mask = (p['dup_status'] == 'maybe') | p['research_status'].isin(['Not verified', 'Failed', 'Unclear'])
mr = p[mr_mask].copy(); q = p[~mr_mask].copy()
q = q.sort_values(['priority', 'fin_points', 'reach_points'], ascending=False).reset_index(drop=True)
q['overall_rank'] = q.index + 1
q['sector_rank'] = q.groupby('sector').cumcount() + 1

def reason(r):
    bits = []
    if r.verified and r.v_reason: return r.v_reason
    bits.append(f'fit {r.fit}/4 ({r.fit_basis})')
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
MH = ['overall rank', 'sector rank', 'brand', 'sector', 'website', 'annual revenue (USD)', 'revenue source / date',
      'valuation (USD)', 'valuation source / date', 'total funding (USD)', 'funding source / date', 'financial criterion met',
      'F1 fit (0-4)', 'fit basis', 'priority score (0-100)', 'reason for ranking', 'financial verification status',
      'parent company', 'country', 'staff', 'type', 'source links', 'source CSV', 'prior note (Wave 15)']
def mrow(r, sec_first=False):
    return [r.overall_rank, r.sector_rank, r.name, r.sector, r.domain,
            r.v_revenue or r.revenue_usd, r.v_revenue_source or 'Clay (search filter / band)',
            r.v_valuation or 'not yet researched', r.v_valuation_source,
            r.v_funding or ('USD 100M+ (Apollo estimate)' if r.funding_100m_apollo else 'not yet researched'),
            r.v_funding_source or ('Apollo funded-company pull, Oct 2026' if r.funding_100m_apollo else ''),
            r.criteria, r.fit, r.fit_basis, r.priority, r.why, r.research_status, r.parent_final, r.country, r.size, r.type,
            (' '.join(r.v_sources[:3]) if isinstance(r.v_sources, list) else str(r.v_sources or '')), r.source_csv, r.w15_note]
W = [8, 7, 32, 26, 22, 26, 22, 18, 18, 22, 22, 30, 7, 14, 9, 50, 26, 26, 14, 12, 14, 40, 18, 40]
n_ver = int(q['verified'].sum())
readme = [['F1 Wave 16 - Friday Clay export: new brands, financially screened and ranked'], [''],
 ['What this is'], ['All 13 Friday Clay CSVs, deduplicated against your MASTER REFERENCE OCT, Upload 11 Oct, To Upload Oct 11, Wave 14 V4 and every earlier wave.'],
 ['Financial rule: qualifies on ANY ONE of revenue >= USD 75M, valuation >= USD 1B, total funding raised >= USD 100M (cumulative).'],
 ['Every Friday CSV was pulled with a Clay revenue filter of USD 75M+, so every brand carries preliminary revenue evidence (Clay ESTIMATE, not verified).'], [''],
 ['Research status'], ['  Preliminary - Clay revenue estimate (unverified): screened from existing data only.'],
 ['  Verified / Partially verified: independently checked with sources and dates (see source links).'],
 ['  Manual Review tab: possible duplicates, failed or unclear verification, unclear ownership.'], [''],
 ['Priority score (0-100) = F1 fit (0-4) x 12.5 [max 50] + financial capability [max 30] + scale/reach [max 10] + verification confidence [max 10]'],
 ['  F1 fit: 1 point each - sells in 3+ F1 markets; affluent or senior-B2B audience; performance/tech/precision/luxury/global story; uncrowded F1 category.'],
 ['  Until a brand is researched its fit is a PRELIMINARY sector-based estimate (column "fit basis").'],
 ['  Financial capability: revenue band 75-200M=8, 200-500M=14, 500M-1B=20, 1-10B=26, 10B+=30; funding 100M+ counts at least 14; verified figures replace estimates.'],
 ['  Scale/reach: staff 10,001+=10, 5,001-10,000=8, 1,001-5,000=6, 501-1,000=4, 201-500=2; +2 if listed. Verification: verified=10, partial=5, estimate=0.'],
 ['  Strategic fit carries the most weight (50 of 100), so size alone cannot top the ranking.'],
 ['  Names that look like a division, product page or regional office (e.g. "X for HR", "X UK & EMEA") lose 10 points until researched.'], [''],
 ['Counts'], [f'  Rows in the 13 CSVs: {len(pd.read_pickle(f"{S}/new_all.pkl")):,}   Unique companies: {len(dd) + len(pd.read_pickle(f"{S}/internal_dups.pkl")) - len(pd.read_pickle(f"{S}/internal_dups.pkl")):,}'],
 [f'  Excluded as duplicates of old/earlier-wave brands: {len(ex):,}   Possible duplicates (Manual Review): {(p.dup_status == "maybe").sum():,}'],
 [f'  New brands ranked: {len(q):,}   of which independently verified so far: {n_ver:,}'],
 [f'  Parent-company overlaps with old data: {len(pod):,}   Parents shared by 2+ new brands: {len(shared):,}'], [''],
 ['Do not treat parent-company finances as the brand\'s own. Figures marked "estimate" come from Clay/Apollo databases and must be confirmed before outreach.']]
ws = wb.create_sheet('00 READ ME'); ws.column_dimensions['A'].width = 140
for l in readme: ws.append(l)
ws.append(['']); ws.append(['Brands per sector', 'count'])
for s, c in q['sector'].value_counts().sort_index().items(): ws.append([s, int(c)])
sheet('01 Master Ranking', MH, (mrow(r) for r in q.itertuples()), W)
for s in sorted(q['sector'].unique()):
    sheet(s, MH, (mrow(r) for r in q[q['sector'] == s].itertuples()), W)
sheet('Parent Company Overlaps', list(pod.columns), pod.values.tolist(), [28, 28, 40, 30, 24, 26, 30, 30, 24, 14])
sheet('Shared Parents (new brands)', ['parent', 'new brands with this parent', 'count'], shared.values.tolist(), [34, 120, 8])
sheet('Excluded Duplicates', ['brand (new file)', 'website', 'reason excluded', 'already in (file | tab)', 'source CSV'], ex.values.tolist(), [34, 26, 50, 50, 20])
MRH = ['brand', 'website', 'sector', 'why in manual review', 'possible match / note', 'matched in', 'revenue (Clay estimate)', 'country', 'staff', 'source CSV']
sheet('Manual Review', MRH, ([r.name, r.domain, r.sector, 'possible duplicate' if r.dup_status == 'maybe' else r.research_status,
                              r.dup_reason or r.v_reason, r.matched_in, r.revenue_usd, r.country, r.size, r.source_csv] for r in mr.itertuples()),
      [32, 24, 26, 26, 50, 40, 26, 14, 12, 18])
wb.save(sys.argv[1])
q.to_pickle(f'{S}/ranked.pkl')
print('ranked', len(q), 'manual review', len(mr), 'excluded', len(ex), 'parent overlaps', len(pod), 'shared parents', len(shared), 'sectors', q['sector'].nunique())
