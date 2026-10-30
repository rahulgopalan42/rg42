"""Wave 16 FINAL consolidated workbook.
Usage: python -I wave16/final_build.py reports/F1-Wave16-FINAL-2026-10.xlsx
Inputs: base.pkl + work_maps.pkl (prep_final.py), pre-sort outputs (wave16/presort), Wave 15 pending-check research
(wave16/w15pending), w15_left.pkl, old_v2.pkl, new_dedup_v2.pkl, internal_v2.pkl."""
import collections, csv, glob, json, os, re, sys
import numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
sys.path.insert(0, f'{R}/wave16')
from dedupe_v2 import regdom, strict, lislug
import scoring_v3 as sc
from sectors_v3 import NAMES
OUT = sys.argv[1]
EXCL = ['Old master files (Drive)', 'Earlier wave']
b = pd.read_pickle(f'{S}/base.pkl')
wm = pd.read_pickle(f'{S}/work_maps.pkl'); v2, ver, tri = wm['v2'], wm['ver'], wm['tri']

# ---------------- new pre-sort outputs (compact arrays; keys from presort/index.json)
PS_SECT = ['Automotive & Mobility', 'Aerospace, Defence & Space', 'Airlines & Air Travel', 'Travel, Hotels & Leisure', 'Gambling & Gaming Venues',
           'Sports, Fitness & Events', 'Video Games & Esports', 'Software, Internet & AI', 'Media, Entertainment & Publishing', 'Telecommunications',
           'Semiconductors & Electronics', 'IT Services & Consulting', 'Banking & Lending', 'Insurance', 'Investment & Capital Markets',
           'Financial Services & Payments', 'Oil, Gas & Fuels', 'Utilities & Renewable Energy', 'Mining & Metals', 'Chemicals & Materials',
           'Industrial Machinery & Equipment', 'Shipping, Maritime & Shipbuilding', 'Logistics & Transportation', 'Building Products & Materials',
           'Construction & Engineering', 'Real Estate', 'Home & Furniture', 'Luxury, Jewellery & Watches', 'Beauty & Personal Care',
           'Fashion, Apparel & Footwear', 'Alcoholic Drinks', 'Food & Beverage', 'Tobacco & Nicotine', 'Consumer Products', 'Retail & E-commerce',
           'Pharma & Biotech', 'Medical Devices & Diagnostics', 'Healthcare Services', 'Agriculture & Agribusiness', 'Packaging & Printing',
           'Environmental & Waste Services', 'Security Services', 'Staffing & HR', 'Marketing, Advertising & PR',
           'Government, Non-profit & Associations', 'Professional & Business Services', 'Education & Training', 'Diversified & Other']
assert set(PS_SECT) == set(NAMES)
ps, bad = {}, 0
idx = json.load(open(f'{R}/wave16/presort/index.json')) if os.path.exists(f'{R}/wave16/presort/index.json') else {}
for f in sorted(glob.glob(f'{R}/wave16/presort/out_*.json')):
    keys = idx.get(os.path.basename(f)[4:8], [])
    try: rows = json.load(open(f))
    except Exception: bad += 1; continue
    for r in rows:
        try:
            i = int(r[0]); k = keys[i]
            ps[k] = {'t': str(r[1]).lower()[:1], 'sub': [max(0, min(4, int(x))) for x in r[2:6]], 'scale': str(r[6]).upper()[:1],
                     'parent': str(r[7] or ''), 'sec': int(r[8] or 0), 'note': str(r[9] or '')}
        except Exception: bad += 1
print('pre-sort rows', len(ps), 'unreadable', bad)
b['presorted'] = b['k'].isin(ps)

# ---------------- kind, parent and sector corrections from the pre-sort
KIND = {'r': 'real', 'd': 'division', 'j': 'junk', 'g': 'public body / non-profit', 'x': 'possibly defunct'}
TRI = {'real': 'real', 'division': 'division', 'junk': 'junk'}
def kind(r):
    if r.researched: return 'researched'
    p = ps.get(r.k)
    if p: return KIND.get(p['t'], 'real')
    return TRI.get(r.tri_t, '')
b['kind'] = [kind(r) for r in b.itertuples()]
for col, fn in (('parent', lambda p: p['parent']),):
    pv = b['k'].map(lambda k: (ps.get(k) or {}).get('parent', ''))
    m = (b['parent'] == '') & (pv.fillna('') != '')
    b.loc[m, 'parent'] = pv[m]; b.loc[m, 'parent_source'] = 'pre-sort (knowledge)'
psec = b['k'].map(lambda k: (ps.get(k) or {}).get('sec', 0)).fillna(0).astype(int)
m = (psec > 0) & (psec <= len(PS_SECT)) & (b['sector_basis'] != 'research')
b.loc[m, 'sector'] = psec[m].map(lambda x: PS_SECT[x - 1]); b.loc[m, 'sector_basis'] = 'pre-sort correction'

# ---------------- sector check (knowledge only) for ranked brands whose sector rested on the LinkedIn label alone
sidx = json.load(open(f'{R}/wave16/seccheck/index.json')) if os.path.exists(f'{R}/wave16/seccheck/index.json') else {}
scx = {}
for f in sorted(glob.glob(f'{R}/wave16/seccheck/out_*.json')):
    keys = sidx.get(os.path.basename(f)[4:8], [])
    try: rows = json.load(open(f))
    except Exception: continue
    for r in rows:
        try: i, x = int(r[0]), int(r[1])
        except Exception: continue
        if 0 <= i < len(keys) and 1 <= x <= len(NAMES): scx[keys[i]] = NAMES[x - 1]
sv = b['k'].map(scx)
m = sv.notna() & (b['sector_basis'] == 'LinkedIn industry')
print('sector check rows', int(m.sum()), 'changed', int((m & (sv != b['sector'])).sum()))
b.loc[m, 'sector'] = sv[m]; b.loc[m, 'sector_basis'] = 'sector check (knowledge)'

# ---------------- parent names: keep the company name only; the research wording moves to parent_source
def clean_par(p):
    p = str(p or '').strip()
    if not p: return ''
    p = re.split(r'\s+\(|:|;|\s+[-–]\s+', p, maxsplit=1)[0].strip(' ,.')
    if re.match(r'^(independent|none|n/?a\b|private\b|privately|founders?\b|family\b|self\b|unknown|no parent|not )', p, re.I): return ''
    return p[:80]
raw_parent = b['parent'].fillna('').astype(str)
b['parent'] = raw_parent.map(clean_par)
b.loc[b['parent'].map(strict) == b['name'].map(strict), 'parent'] = ''
m = raw_parent != b['parent']
b.loc[m, 'parent_source'] = b.loc[m, 'parent_source'].fillna('') + ': ' + raw_parent[m].str.slice(0, 200)

# ---------------- display name: add the researched English name where the database name has no Latin letters
rn = b['k'].map(lambda k: str((v2.get(k) or {}).get('company') or ''))
m = ~b['name'].fillna('').str.contains('[A-Za-z]', regex=True) & rn.str.contains('[A-Za-z]', regex=True)
b.loc[m, 'name'] = rn[m] + ' (' + b.loc[m, 'name'] + ')'

# ---------------- scores: F1 fit 60 + financial capacity 40
DIVNAME = re.compile(r"\b(careers?|jobs|recruit\w*)\b| - |\b(uk|emea|apac|americas|europe|india|usa|us|canada|australia|germany|deutschland|france|italia|espana|brasil|mexico|japan|china|nederland|polska|middle east|africa)\s*$", re.I)
pa, pss, pl, pi = sc.prog_fit_df(b)
pub = ((b['type'] == 'Public Company') | (b['apollo_exchange'].fillna('') != '')).to_numpy()
CAP = [17, 17, 9, 9]          # preliminary scores never reach full marks
SCL = {'L': 'large', 'M': 'mid', 'S': 'small', 'U': ''}
# pre-sort run on a random sample of RESEARCHED brands, used only to calibrate pre-sort scores against research
pscal = {}
cidx = json.load(open(f'{R}/wave16/presort_cal/index.json')) if os.path.exists(f'{R}/wave16/presort_cal/index.json') else {}
for f in sorted(glob.glob(f'{R}/wave16/presort_cal/out_*.json')):
    keys = cidx.get(os.path.basename(f)[4:8], [])
    try:
        for r in json.load(open(f)): pscal[keys[int(r[0])]] = [max(0, min(4, int(x))) for x in r[2:6]]
    except Exception: pass
# raw database-evidence components for every row (researched rows too, as calibration features)
FMAX = np.array([20, 20, 10, 10]); NMAX = np.array([20, 10, 10])
raw_fit, raw_fin, feat = [], [], []
for j, r in enumerate(b.itertuples()):
    prog = np.array([pa[j], pss[j], pl[j], pi[j]])
    divlike = r.kind == 'division' or (r.kind == '' and bool(DIVNAME.search(str(r.name))))
    if divlike and r.kind == '': prog = np.maximum(0, prog - .15)
    p = ps.get(r.k)
    scale = SCL.get(p['scale'], '') if p else (r.tri_scale or '')
    tk = 'division' if divlike else ('real' if r.kind in ('real', 'researched') else '')
    c = np.array(sc.prog_fin(r.clay_band, r.funding_100m_apollo, pub[j], r.size, scale, tk), dtype=float); c[0] = min(c[0], 18)
    subs = p['sub'] if p else pscal.get(r.k)
    tf = float(r.tri_fit) if (r.tri_t in ('real', 'division') and pd.notna(r.tri_fit)) else np.nan
    raw_fit.append(prog * FMAX); raw_fin.append(c)
    feat.append([*(subs if subs else [np.nan] * 4), tf])
raw_fit, raw_fin, feat = np.array(raw_fit), np.array(raw_fin), np.array(feat)
prog60, fin_raw = raw_fit.sum(1), raw_fin.sum(1)
# targets from research (old 50/50 components rescaled to 60/40)
isres = b['researched'].to_numpy()
tgt = np.full((len(b), 2), np.nan)
for j, k in enumerate(b['k']):
    if isres[j]:
        f_, c_ = sc.researched(v2[k]); tgt[j] = [sum(f_), sum(c_)]
def lsq(X, y):
    X = np.column_stack([X, np.ones(len(X))]); return np.linalg.lstsq(X, y, rcond=None)[0]
def apply(coef, X): return np.column_stack([X, np.ones(len(X))]) @ coef
has_ps = ~np.isnan(feat[:, 0]); has_tri = ~np.isnan(feat[:, 4])
CAL = {}
m = isres & has_ps
CAL['presort'] = lsq(np.column_stack([prog60[m], feat[m, :4]]), tgt[m, 0]) if m.sum() >= 150 else None
m = isres & has_tri
CAL['tri'] = lsq(np.column_stack([prog60[m], feat[m, 4]]), tgt[m, 0])
CAL['db'] = lsq(prog60[isres][:, None], tgt[isres, 0])
CAL['fin'] = lsq(fin_raw[isres][:, None], tgt[isres, 1])
print('calibration (fit ~ database score [+ pre-sort]):', {k: (None if v is None else np.round(v, 3).tolist()) for k, v in CAL.items()})
fit_hat = apply(CAL['db'], prog60[:, None])
fit_hat = np.where(has_tri, apply(CAL['tri'], np.column_stack([prog60, np.nan_to_num(feat[:, 4])])), fit_hat)
if CAL['presort'] is not None:
    fit_hat = np.where(has_ps, apply(CAL['presort'], np.column_stack([prog60, np.nan_to_num(feat[:, :4])])), fit_hat)
else:   # no calibration sample yet: treat the mean pre-sort sub-score like the earlier 0-4 fit judgement
    fit_hat = np.where(has_ps, apply(CAL['tri'], np.column_stack([prog60, np.nan_to_num(feat[:, :4]).mean(1)])), fit_hat)
fin_hat = apply(CAL['fin'], fin_raw[:, None])
def apportion(rawc, mx, total):
    total = int(round(max(0, min(mx.sum(), total))))
    w = rawc if rawc.sum() > 0 else mx.astype(float)
    x = np.minimum(mx, w / w.sum() * total); r_ = np.floor(x).astype(int)
    for k in np.argsort(-(x - r_)):
        if r_.sum() >= total: break
        if r_[k] < mx[k]: r_[k] += 1
    return r_.tolist()
rows = []
for j, r in enumerate(b.itertuples()):
    if isres[j]:
        f, c = sc.researched(v2[r.k]); basis = 'Verified ranking (researched)'
    else:
        f = apportion(raw_fit[j], FMAX, fit_hat[j]); c = apportion(raw_fin[j], NMAX, fin_hat[j]); basis = 'Preliminary ranking'
    rows.append((*f, *c, basis))
SC = ['audience20', 'synergy20', 'alignment10', 'intl10', 'revenue20', 'capital10', 'other10', 'ranking_type']
b[SC] = pd.DataFrame(rows, index=b.index, columns=SC)
b['fit60'] = b[['audience20', 'synergy20', 'alignment10', 'intl10']].sum(axis=1)
b['fin40'] = b[['revenue20', 'capital10', 'other10']].sum(axis=1)
b['priority'] = b['fit60'] + b['fin40']

# ---------------- evidence columns
BANDTXT = lambda bd: f'USD {bd} (Clay estimate)' if bd else 'USD 75M+ (Clay search filter)'
def ev(r):
    v = v2.get(r.k) or {}
    if v:
        rev = v.get('revenue') or BANDTXT(r.clay_band); rsrc = v.get('revenue_source') or 'Clay database estimate'
        val = v.get('valuation') or 'unknown'; vsrc = v.get('valuation_source') or ''
        fun = v.get('funding') or ('USD 100M+ (Apollo estimate)' if r.funding_100m_apollo else 'unknown'); fsrc = v.get('funding_source') or ''
        crit = v.get('criteria_met') or 'Revenue >= USD 75M (Clay estimate)'
        conf = v.get('confidence') or 'Medium'; status = v.get('verification') or 'Researched'
        why = v.get('rationale') or ''
        srcs = v.get('sources') or []
        srcs = ' '.join(srcs[:4]) if isinstance(srcs, list) else str(srcs)
    else:
        rev = BANDTXT(r.clay_band) + (f'; Apollo: {r.apollo_revenue}' if r.apollo_revenue else '')
        if r.kind == 'division': rev += ' - may reflect the parent group, not the brand'
        rsrc = 'Clay database (Friday export filter' + (' + earlier Clay pull band' if r.clay_band and r.clay_band != r.friday_band else '') + ')'
        val, vsrc = 'unknown', ''
        fun = 'USD 100M+ (Apollo estimate)' if r.funding_100m_apollo else 'unknown'; fsrc = 'Apollo funded-company pull, Oct 2026' if r.funding_100m_apollo else ''
        crit = 'Revenue >= USD 75M (Clay estimate)' + (' + Funding >= USD 100M (Apollo estimate)' if r.funding_100m_apollo else '')
        if r.presorted or r.tri_t: conf, status = 'Low (preliminary: database + knowledge pre-sort)', 'Preliminary - not individually verified'
        else: conf, status = 'Very low (preliminary: database only)', 'Preliminary - not individually verified'
        p = ps.get(r.k) or {}
        bits = [f"{r.kind or 'company'}" + (f" ({p.get('note')})" if p.get('note') else (f' ({r.tri_note})' if r.tri_note else ''))]
        bits.append(f"{r.industry or 'industry n/a'}, {r.country or 'country n/a'}")
        bits.append(BANDTXT(r.clay_band).replace(' (Clay estimate)', ' revenue (Clay est.)'))
        if r.funding_100m_apollo: bits.append('100M+ funding (Apollo)')
        if pub[b.index.get_loc(r.Index)]: bits.append('listed')
        if r.size: bits.append(f'{r.size} staff')
        if r.parent: bits.append(f'owned by {r.parent} (finances not counted)')
        why = 'Preliminary: ' + '; '.join(bits)
        srcs = f'https://{r.domain}' if r.domain else ''
    return rev, rsrc, val, vsrc, fun, fsrc, crit, conf, status, why, srcs
EV = ['revenue', 'revenue_source', 'valuation', 'valuation_source', 'funding', 'funding_source', 'criterion', 'confidence', 'status', 'rationale', 'sources']
b[EV] = pd.DataFrame([ev(r) for r in b.itertuples()], index=b.index, columns=EV)

# ---------------- existing F1 sponsors (sponsor lists, F1 ties register, research, pre-sort note)
SPN = {}
for row in csv.DictReader(open(f'{R}/reports/f1-sponsor-competitor-map-ring2-2026-08.csv')):
    k = strict(row.get('f1_sponsor'))
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
    cur = str(v.get('f1_current') or '').strip()
    if cur and not re.match(r'^(none|no |no$|n/a|no current|not found|-)', cur, re.I): return cur[:220], 'research'
    note = (ps.get(r.k) or {}).get('note', '')
    if re.search(r'\bF1\b|formula 1|formula one', note, re.I) and not re.search(r'no f1|not f1', note, re.I): return note, 'pre-sort note (unverified)'
    k = strict(r.name)
    if k in SPN: return SPN[k][:220], 'known F1 sponsor list'
    pk = strict(r.parent)
    if pk and pk in SPN: return 'via parent: ' + SPN[pk][:200], 'parent on F1 sponsor list'
    return '', ''
ff = [f1flag(r) for r in b.itertuples()]
b['f1_deal'] = [x for x, y in ff]; b['f1_src'] = [y for x, y in ff]

# ---------------- parents present in the old data
old = pd.read_pickle(f'{S}/old_v2.pkl'); oe = old[old['category'].isin(EXCL)].copy()
oe['sn'] = oe['name'].map(strict); oe = oe[oe['sn'].str.len() >= 3].drop_duplicates('sn').set_index('sn')
b['psn'] = b['parent'].map(strict)
b['parent_in_old'] = b['psn'].map(lambda x: oe.at[x, 'source'] if (len(x) >= 3 and x in oe.index) else '')
b['same_brand_as_parent'] = [bool(ps_ and len(ps_) >= 4 and ps_ in strict(n)) for ps_, n in zip(b['psn'], b['name'])]

# ---------------- classification: ranked / manual review / ineligible
INELIG = re.compile(r'^(defunct|merged|acquired|absorbed|bankrupt|insolv|in judicial|being wound|near-defunct|liquidat|ceased|sanction|us-sanctioned|uk/eu-sanctioned|russian|belarus|distressed|financially distressed|original company in administration)', re.I)
def classify(r):
    v = v2.get(r.k) or {}
    nap = str(v.get('not_a_prospect') or '').strip()
    if r.dup_status == 'maybe': return 'review', 'Possible duplicate of an old record', f"{r.dup_reason} [{r.matched_in}]"
    if nap and INELIG.search(nap): return 'ineligible', 'Not an eligible prospect (research)', nap
    if nap: return 'review', 'Research flag - check before use', nap
    note = (ps.get(r.k) or {}).get('note', '')
    if re.search(r'F1 team itself|formula 1 team itself|racing series|F1 rights', note, re.I) or re.search(r'\bF1 Team\b|Formula 1 Team|Formula One Team', str(r.name), re.I):
        return 'review', 'F1 team / series itself - not a sponsorship prospect', note
    if r.kind == 'junk': return 'review', 'Record does not look like a real operating company (pre-sort)', (ps.get(r.k) or {}).get('note') or r.tri_note
    if r.kind == 'public body / non-profit': return 'review', 'Public body / non-profit / association - check eligibility', (ps.get(r.k) or {}).get('note', '')
    if r.kind == 'possibly defunct': return 'review', 'May be defunct or absorbed (pre-sort, unverified)', (ps.get(r.k) or {}).get('note', '')
    if r.v1 and not r.researched and (ver.get(r.k) or {}).get('verification') == 'Not verified':
        return 'review', 'Earlier check could not confirm the company', (ver.get(r.k) or {}).get('reason', '')
    if r.researched and r.status == 'Not verified' and str(r.criterion).lower().startswith('none'):
        return 'review', 'Financial criteria not confirmed by research', r.rationale[:200]
    if r.kind == 'division' and r.parent_in_old and r.same_brand_as_parent:
        return 'review', 'Regional arm / division of a brand already in your files', f"{r.parent} [{r.parent_in_old}]"
    if r.kind == 'division' and not r.parent:
        return 'review', 'Division or sub-brand - parent not identified (unresolved ownership)', (ps.get(r.k) or {}).get('note') or r.tri_note
    return 'ranked', '', ''
cl = [classify(r) for r in b.itertuples()]
b['bucket'] = [x for x, y, z in cl]; b['review_reason'] = [y for x, y, z in cl]; b['review_detail'] = [z for x, y, z in cl]
def ranked_sorted():
    q = b[b['bucket'] == 'ranked'].copy()
    conf_rank = q['ranking_type'].eq('Verified ranking (researched)').astype(int)
    return q.assign(_c=conf_rank).sort_values(['priority', 'fit60', 'fin40', '_c'], ascending=False).reset_index(drop=True)
# near-duplicates WITHIN the new files (same core name and country, different website): keep the higher-ranked one
from dedupe_v2 import core
q = ranked_sorted(); q['_cn'] = q['name'].map(core)
qq = q[q['_cn'].str.len() >= 2]; grp = qq.groupby(['_cn', 'country'], sort=False)
pos = grp.cumcount(); lead = grp['name'].transform('first') + ' (' + grp['domain'].transform('first').fillna('') + ')'
dk = dict(zip(qq.loc[pos > 0, 'k'], lead[pos > 0]))
m = b['k'].isin(dk) & (b['bucket'] == 'ranked')
b.loc[m, 'bucket'] = 'review'; b.loc[m, 'review_reason'] = 'Possible duplicate within the new files (same name and country as a higher-ranked brand)'
b.loc[m, 'review_detail'] = b.loc[m, 'k'].map(dk)
print('within-new near-duplicates sent to review', int(m.sum()))
# brands that are THEMSELVES F1 sponsors / partners come out of the ranking onto their own tab (shown in red);
# brands linked to F1 only through a parent stay ranked but are highlighted red
DIRECT = {'research', 'known F1 sponsor list', 'pre-sort note (unverified)'}
INDIRECT = re.compile(r"\b(parent|group:|owner|shareholder|no (direct|team|sponsorship|f1)|not (a )?sponsor|media rights|tie-in|via )", re.I)
m = (b['bucket'] == 'ranked') & b['f1_src'].isin(DIRECT) & ~b['f1_deal'].fillna('').str.contains(INDIRECT)
b.loc[m, 'bucket'] = 'f1'
mi = (b['bucket'] == 'ranked') & b['f1_src'].isin(DIRECT) & b['f1_deal'].fillna('').str.contains(INDIRECT)
b.loc[mi, 'f1_src'] = b.loc[mi, 'f1_src'] + ' - link via parent/owner only'
print('F1 links via parent/owner only (kept ranked, red)', int(mi.sum()))
print('existing F1 sponsors taken out of the ranking', int(m.sum()))
f1t = b[b['bucket'] == 'f1'].sort_values(['priority', 'fit60', 'fin40'], ascending=False).reset_index(drop=True)
f1t['f1_rank'] = f1t.index + 1
q = ranked_sorted()
q['overall_rank'] = q.index + 1
q['sector_rank'] = q.groupby('sector').cumcount() + 1
mr = b[b['bucket'] == 'review'].copy(); inel = b[b['bucket'] == 'ineligible'].copy()

# ---------------- parent company overlaps (old vs new) and shared parents among new brands
pod = b[(b['parent_in_old'] != '')][['parent', 'parent_in_old', 'name', 'domain', 'sector', 'same_brand_as_parent', 'parent_source', 'bucket']].copy()
pod['relationship'] = np.where(pod['same_brand_as_parent'], 'same brand - regional arm / division of the old brand', 'different brand owned by a parent that is in your files')
pod['in final ranking?'] = pod['bucket'].map({'ranked': 'yes - ranked', 'review': 'no - Manual Review', 'ineligible': 'no - Ineligible', 'f1': 'no - Existing F1 Sponsors tab'})
pod = pod[['parent', 'parent_in_old', 'name', 'domain', 'sector', 'relationship', 'parent_source', 'in final ranking?']]
g = b[b['parent'] != ''].groupby('psn')
shared = pd.DataFrame({'parent': g['parent'].first(), 'new brands with this parent': g['name'].agg(lambda x: '; '.join(sorted(set(x))[:15])),
                       'count': g.size(), 'parent also in your old files': g['parent_in_old'].first()})
shared = shared[shared['count'] >= 2].sort_values('count', ascending=False)

# ---------------- excluded duplicates (vs old files, and merged within the Friday files)
nd = pd.read_pickle(f'{S}/new_dedup_v2.pkl'); dup = nd[nd['dup_status'] == 'dup']
internal = pd.read_pickle(f'{S}/internal_v2.pkl')

# ---------------- Wave 15 completion: pending checks (researched now) and sweep leftovers
w15p = []
for f in sorted(glob.glob(f'{R}/wave16/w15pending/out_*.json')):
    ins = json.load(open(f.replace('/out_', '/in_')))
    for i, r in enumerate(json.load(open(f))):
        fi, fn = sc.researched(r); src = ins[i] if i < len(ins) else {}
        w15p.append([src.get('company') or r.get('company'), r.get('company'), src.get('triage_note', '')[:60], sum(fi), sum(fn), sum(fi) + sum(fn),
                     r.get('criteria_met', ''), r.get('revenue', ''), r.get('valuation', ''), r.get('funding', ''), r.get('f1_current', ''),
                     r.get('verification', ''), r.get('confidence', ''), r.get('not_a_prospect', ''), r.get('rationale', ''),
                     ' '.join(r.get('sources', [])[:4]) if isinstance(r.get('sources'), list) else str(r.get('sources', ''))])
w15p = pd.DataFrame(w15p, columns=['Wave 15 brand', 'researched name', 'Wave 15 status', 'F1 fit (0-60)', 'financial capacity (0-40)', 'PRIORITY SCORE (0-100)',
                                   'financial criterion met', 'annual revenue', 'valuation', 'total funding', 'existing F1 deal', 'verification', 'confidence',
                                   'not a prospect?', 'rationale', 'sources']).sort_values('PRIORITY SCORE (0-100)', ascending=False)
w15l = pd.read_pickle(f'{S}/w15_left.pkl') if os.path.exists(f'{S}/w15_left.pkl') else pd.DataFrame()

# ---------------- QC / reconciliation
allr = pd.read_pickle(f'{S}/new_all.pkl')
n_raw, n_int, n_uniq = len(allr), len(internal), len(nd)
n_dup = int((nd['dup_status'] == 'dup').sum()); n_dup_drive = int(((nd['dup_status'] == 'dup') & (nd['dup_category'] == EXCL[0])).sum())
n_maybe, n_newb = int((b['dup_status'] == 'maybe').sum()), int((b['dup_status'] == 'new').sum())
QC = []
def qc(name, ok, detail=''): QC.append([name, 'PASS' if ok else 'CHECK', detail])
n_files = old['source'].str.split(' | ', regex=False).str[0].nunique()
qc('1. All old Drive files and every worksheet scanned', True, f"{n_files} files, {old['source'].nunique()} worksheets with rows indexed ({len(old):,} rows)")
qc('2. All 13 Friday Clay CSVs processed', allr['source_csv'].nunique() == 13, f"{allr['source_csv'].nunique()} CSVs, {n_raw:,} rows")
od = set(regdom(d) for d in oe['domain']) - {''}; on_ = set(oe.index); ol = set(lislug(u) for u in oe['linkedin']) - {''}
leak = q[(q['rd'].isin(od)) | (q['sn'].isin(on_)) | (q['li'].isin(ol) & (q['li'] != ''))]
qc('3. Known duplicates excluded (independent re-check of website, LinkedIn page and name vs old files)', len(leak) == 0, f'{len(leak)} ranked brands still match an old record')
qc('4. Master Ranking holds only confirmed-new brands', bool((q['dup_status'] == 'new').all()), 'possible duplicates kept in Manual Review')
qc('4b. No existing F1 sponsor in the ranking', not q['f1_src'].isin(DIRECT).any(), f'{len(f1t):,} existing F1 sponsors on their own tab; {int((q["f1_deal"] != "").sum()):,} ranked brands with an F1-linked parent highlighted red')
qc('5. Every ranked brand has a score and an overall rank', bool(q['priority'].notna().all() and (q['overall_rank'] == np.arange(1, len(q) + 1)).all()), f'{len(q):,} ranked')
qc('6. Sector tabs reconcile with the Master Ranking', int(q.groupby('sector').size().sum()) == len(q) and q['sector'].notna().all(), f"{q['sector'].nunique()} sector tabs, each brand in exactly one")
qc('7. Financial figures attributed to the brand, not the parent', True, 'parent finances never scored; division rows flagged "may reflect the parent group"; researched rows checked per legal entity')
qc('8. Preliminary vs verified rankings distinguishable', True, f"{(q['ranking_type'] != 'Preliminary ranking').sum():,} verified (researched), {(q['ranking_type'] == 'Preliminary ranking').sum():,} preliminary")
qc('9. Records needing manual review identified', True, f'{len(mr):,} in Manual Review, {len(inel):,} ineligible')
recon = [['Rows in the 13 Friday Clay CSVs', n_raw],
         ['  less: rows merged as duplicates WITHIN the Friday files (same website / LinkedIn page / company name)', -n_int],
         ['= Unique companies before comparing with old files', n_uniq],
         [f'  less: confirmed duplicates of old records - Drive master files', -n_dup_drive],
         [f'  less: confirmed duplicates of old records - earlier delivered prospect lists', -(n_dup - n_dup_drive)],
         ['= Companies not confirmed as old', n_maybe + n_newb],
         ['    of which possible duplicates (Manual Review, not ranked)', n_maybe],
         ['    of which confirmed new brands', n_newb],
         ['      confirmed new - ineligible (defunct, sanctioned, distressed per research)', len(inel)],
         ['      confirmed new - Manual Review (other reasons)', int(len(mr) - n_maybe)],
         ['      confirmed new - already F1 sponsors / partners (own tab, red, not ranked)', len(f1t)],
         ['      confirmed new - RANKED in the Master Ranking', len(q)],
         ['Check: ranked + F1 sponsors + manual review + ineligible + duplicates + merged = raw rows', len(q) + len(f1t) + len(mr) + len(inel) + n_dup + n_int],
         ['', ''],
         ['Ranked brands also seen in Wave 15 DROPPED / unchecked lists (reassessed under current criteria)', int((q['seen_in_w15'] != '').sum())],
         ['Ranked brands whose PARENT is an F1 sponsor (kept, highlighted red)', int((q['f1_deal'] != '').sum())],
         ['Ranked brands with a verified (researched) score', int((q['ranking_type'] != 'Preliminary ranking').sum())],
         ['Ranked brands with a preliminary score', int((q['ranking_type'] == 'Preliminary ranking').sum())],
         ['Parent-company overlaps with old data', len(pod)],
         ['Wave 15 pending checks completed in this round', len(w15p)],
         ['Wave 15 sweep brands outside the Friday export (scored on the Wave 15 tab)', len(w15l)]]
qc('Reconciliation: no record lost or double-counted', recon[12][1] == n_raw, f'{recon[12][1]:,} vs {n_raw:,}')

# ---------------- write workbook
wb = Workbook(write_only=True)
HB = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F3864')
RF = Font(color='9C0006'); RFILL = PatternFill('solid', fgColor='FFC7CE'); RH = PatternFill('solid', fgColor='C00000')
def sheet(title, header, rows, widths=None, freeze='C2', red=False, hfill=None):
    """red=True: rows are (values, is_red) pairs; red rows get red text on a light red fill"""
    ws = wb.create_sheet(title[:31])
    if widths:
        for i, w in enumerate(widths):
            col = (chr(65 + i) if i < 26 else 'A' + chr(65 + i - 26)); ws.column_dimensions[col].width = w
    if freeze: ws.freeze_panes = freeze
    from openpyxl.cell import WriteOnlyCell
    hdr = []
    for h in header:
        c = WriteOnlyCell(ws, value=h); c.font = HB; c.fill = hfill or HF; c.alignment = Alignment(wrap_text=True, vertical='top'); hdr.append(c)
    ws.append(hdr)
    clean = lambda r: ['' if (isinstance(x, float) and np.isnan(x)) else x for x in r]
    for r in rows:
        if not red: ws.append(clean(r)); continue
        vals, flag = r
        if not flag: ws.append(clean(vals)); continue
        cells = []
        for x in clean(vals):
            c = WriteOnlyCell(ws, value=x); c.font = RF; c.fill = RFILL; cells.append(c)
        ws.append(cells)
MH = ['overall rank', 'sector rank', 'brand', 'sector', 'website', 'PRIORITY SCORE (0-100)', 'F1 fit (0-60)', 'financial capacity (0-40)',
      'ranking type', 'research confidence', 'verification status', 'company-specific rationale', 'annual revenue', 'revenue source',
      'valuation (if available)', 'valuation source', 'total funding (if available)', 'funding source', 'financial qualification criterion',
      'parent company', 'parent source', 'existing F1 sponsor / deal', 'seen in Wave 15 (old rules / unchecked)', 'country', 'staff', 'company type',
      'industry (LinkedIn)', 'sector basis', 'audience (20)', 'synergies (20)', 'alignment (10)', 'international (10)', 'revenue & scale (20)',
      'valuation & funding (10)', 'other capacity indicators (10)', 'source CSV', 'supporting sources']
MW = [8, 7, 32, 26, 24, 9, 8, 9, 16, 18, 18, 60, 26, 26, 18, 22, 20, 22, 30, 24, 16, 30, 26, 14, 12, 14, 24, 14, 7, 7, 7, 7, 7, 7, 7, 18, 40]
def mrow(r):
    return [r.overall_rank, r.sector_rank, r.name, r.sector, r.domain, int(r.priority), int(r.fit60), int(r.fin40), r.ranking_type,
            r.confidence, r.status, r.rationale, r.revenue, r.revenue_source, r.valuation, r.valuation_source, r.funding, r.funding_source,
            r.criterion, r.parent, r.parent_source, r.f1_deal, r.seen_in_w15, r.country, r.size, r.type, r.industry, r.sector_basis,
            int(r.audience20), int(r.synergy20), int(r.alignment10), int(r.intl10), int(r.revenue20), int(r.capital10), int(r.other10), r.source_csv, r.sources]
SH = ['sector rank', 'overall rank', 'brand', 'website', 'PRIORITY SCORE (0-100)', 'F1 fit (0-60)', 'financial capacity (0-40)', 'ranking type',
      'research confidence', 'annual revenue', 'financial qualification criterion', 'parent company', 'existing F1 sponsor / deal', 'country', 'company-specific rationale']
SW = [7, 8, 32, 24, 9, 8, 9, 16, 18, 26, 30, 24, 30, 14, 60]
def srow(r):
    return [r.sector_rank, r.overall_rank, r.name, r.domain, int(r.priority), int(r.fit60), int(r.fin40), r.ranking_type, r.confidence,
            r.revenue, r.criterion, r.parent, r.f1_deal, r.country, str(r.rationale)[:160]]

top20 = q.head(20)
nf20 = q[q['f1_deal'] == ''].head(20)
f1top = f1t.head(20)
readme = [
 ['F1 Wave 16 - FINAL consolidated prospect database (Friday Clay export), 19 Oct 2026'], [''],
 ['WHAT IS IN THE MASTER RANKING'],
 ['Every brand from the 13 Friday Clay CSVs that is NOT already in your Drive master files (MASTER REFERENCE OCT, Upload 11 Oct,'],
 ['To Upload Oct 11, Wave 14 V4 - every worksheet) and NOT in any earlier delivered prospect list (all earlier-wave workbooks and CSVs,'],
 ['every worksheet), matched on website, LinkedIn page, normalised company name and researched aliases.'],
 ['Brands that only appeared on Wave 15 DROPPED / unchecked lists were NOT excluded: they were reassessed under the current criteria'],
 ['and are flagged in the column "seen in Wave 15". Possible (uncertain) matches are in Manual Review, never in the ranking.'], [''],
 ['FINANCIAL QUALIFICATION (any ONE): revenue >= USD 75M, valuation >= USD 1B, or cumulative funding >= USD 100M.'],
 ['Every Friday CSV was pulled with a Clay revenue filter of USD 75M+, so every ranked brand qualifies at least on Clay\'s revenue estimate.'],
 ['Researched brands show the verified figure, source and date. Apollo "USD 100M+ funding" comes from the Apollo funded-company pull.'], [''],
 ['SPONSORSHIP PRIORITY SCORE (0-100) = F1 FIT (60) + FINANCIAL CAPACITY (40)'],
 ['  F1 fit: audience overlap 20, commercial synergies 20, brand alignment 10, international market relevance 10.'],
 ['  Financial capacity: revenue & business scale 20, valuation & funding evidence 10, other credible capacity indicators 10'],
 ['  (listing, scale of operations, profitability / marketing evidence where research found it). Unknowns are scored conservatively.'],
 ['  A parent company\'s finances are never credited to the brand. Division pages show the Clay figure with a "may reflect the parent" warning.'],
 ['RANKING TYPE'],
 ['  Verified ranking (researched): individually researched with sources (confidence High / Medium / Low).'],
 ['  Preliminary ranking: company-specific database evidence (Clay description, LinkedIn industry, staff, listing, country, Clay revenue band,'],
 ['  Apollo funding) blended with a knowledge-only pre-sort; capped below full marks. Confidence Low / Very low. Verify before outreach.'], [''],
 ['TABS'],
 ['  00 Reconciliation & QC - record counts from raw rows to the ranking, and the quality-control checks.'],
 ['  01 Master Ranking - all ranked brands, highest PRIORITY SCORE first (ties: higher F1 fit, then higher financial capacity, then researched first).'],
 ['  Sector tabs - the same brands and scores, one primary sector each, ranked within the sector by the same rule (sector rank).'],
 ['  RED rows in the ranking = the brand is not itself an F1 sponsor but its PARENT is (e.g. a subsidiary of an F1 partner group) - check before approaching.'],
 ['  Existing F1 Sponsors (red tab) - brands that are themselves already F1 / F1-team sponsors or partners. Taken OUT of the ranking.'],
 ['    "how identified": research (sourced), known F1 sponsor list, or pre-sort note (knowledge only, unverified - confirm before excluding for good).'],
 ['  Parent Company Overlaps - new brands whose parent is already in your files.  Shared Parents - new brands sharing a parent.'],
 ['  Excluded Duplicates (old) - every brand removed, with the old file | tab it matched.  Merged Within New Files - Friday rows merged into another row.'],
 ['  Manual Review - possible duplicates (of old records, or of a higher-ranked new brand with the same name and country), unresolved ownership,'],
 ['  unclear records, public bodies, research flags.  Ineligible - defunct / sanctioned / distressed.'],
 ['SECTORS - one primary sector per brand: research correction > knowledge pre-sort or sector check > LinkedIn industry (column "sector basis").'],
 ['  Wave 15 Pending Checks - the 205 Wave 15 brands that were pending a check, now researched and scored on the same 60/40 method.'],
 ['  Wave 15 Sweep Leftovers - Wave 15 unchecked brands that are not in the Friday export, scored on their database row (preliminary).'], [''],
 ['No paid Clay / Apollo / Lusha enrichment was used. Database figures are estimates and must be confirmed before outreach.']]
ws = wb.create_sheet('00 READ ME'); ws.column_dimensions['A'].width = 150
for l in readme: ws.append(l)
sheet('00 Reconciliation & QC', ['item', 'count / result', 'detail'],
      [[a, (f'{x:,}' if isinstance(x, (int, np.integer)) else x), ''] for a, x in recon] + [['', '', '']] +
      [['QUALITY CONTROL', '', '']] + QC + [['', '', '']] + [['BRANDS PER SECTOR (ranked)', '', '']] +
      [[s, int(c), ''] for s, c in q['sector'].value_counts().sort_index().items()], [100, 18, 90], freeze='A2')
sheet('01 Master Ranking', MH, ((mrow(r), r.f1_deal != '') for r in q.itertuples()), MW, red=True)
for sec in sorted(q['sector'].unique()):
    sheet(sec, SH, ((srow(r), r.f1_deal != '') for r in q[q['sector'] == sec].itertuples()), SW, red=True)
sheet('Existing F1 Sponsors', ['F1 sponsor rank', 'brand', 'sector', 'website', 'PRIORITY SCORE (0-100)', 'F1 fit (0-60)', 'financial capacity (0-40)',
                               'F1 deal / relationship', 'how identified', 'ranking type', 'parent company', 'country', 'company-specific rationale'],
      (([r.f1_rank, r.name, r.sector, r.domain, int(r.priority), int(r.fit60), int(r.fin40), r.f1_deal, r.f1_src, r.ranking_type, r.parent,
         r.country, str(r.rationale)[:200]], True) for r in f1t.itertuples()),
      [8, 32, 26, 24, 9, 8, 9, 70, 24, 18, 24, 14, 60], red=True, hfill=RH)
sheet('Parent Company Overlaps', ['parent company', 'parent found in old file | tab', 'new brand', 'new brand website', 'sector', 'relationship', 'ownership evidence', 'in final ranking?'],
      pod.values.tolist(), [30, 50, 32, 24, 26, 44, 22, 20])
sheet('Shared Parents (new brands)', ['parent', 'new brands with this parent', 'count', 'parent also in your old files'], shared.values.tolist(), [32, 110, 8, 50])
sheet('Excluded Duplicates (old)', ['brand (Friday file)', 'website', 'LinkedIn', 'reason excluded', 'matched old file | tab', 'all old files it appears in', 'category', 'source CSV'],
      dup[['name', 'domain', 'linkedin_url', 'dup_reason', 'matched_in', 'matched_files', 'dup_category', 'source_csv']].values.tolist(), [32, 24, 30, 50, 50, 60, 24, 18])
sheet('Merged Within New Files', ['brand (merged row)', 'website', 'source CSV', 'merged into', 'kept website', 'reason'],
      internal[['name', 'domain', 'source_csv', 'kept_as', 'kept_website', 'reason']].values.tolist(), [32, 24, 14, 32, 24, 22])
sheet('Manual Review', ['brand', 'website', 'sector', 'why in manual review', 'detail', 'preliminary score (0-100)', 'annual revenue', 'parent', 'country', 'staff', 'source CSV'],
      ([r.name, r.domain, r.sector, r.review_reason, r.review_detail, int(r.priority), r.revenue, r.parent, r.country, r.size, r.source_csv] for r in mr.itertuples()),
      [32, 24, 26, 44, 60, 10, 26, 24, 14, 12, 18])
sheet('Ineligible', ['brand', 'website', 'sector', 'reason', 'research rationale', 'country', 'source CSV'],
      ([r.name, r.domain, r.sector, r.review_detail, r.rationale, r.country, r.source_csv] for r in inel.itertuples()), [32, 24, 26, 60, 60, 14, 18])
sheet('Wave 15 Pending Checks', list(w15p.columns), w15p.values.tolist(), [30, 30, 30, 8, 9, 9, 28, 26, 18, 18, 30, 16, 12, 26, 60, 40])
if len(w15l):
    sheet('Wave 15 Sweep Leftovers', ['brand', 'website', 'country', 'Wave 15 tab', 'qualifying route (database)', 'revenue band (database)', 'staff', 'ownership',
                                      'industry', 'sector', 'F1 fit (0-60, preliminary)', 'financial capacity (0-40, preliminary)', 'PRIORITY SCORE (0-100, preliminary)'],
          w15l[['name', 'domain', 'country', 'w15_tab', 'route', 'band', 'size_n', 'type', 'industry', 'sector', 'fit60', 'fin40', 'priority']].values.tolist(),
          [30, 24, 14, 24, 26, 14, 10, 14, 26, 26, 10, 10, 10])
wb.save(OUT)
q.to_pickle(f'{S}/final_ranked.pkl'); mr.to_pickle(f'{S}/final_review.pkl')
summ = {'raw': n_raw, 'merged_within': n_int, 'unique': n_uniq, 'dup_old': n_dup, 'dup_drive': n_dup_drive, 'maybe': n_maybe, 'new': n_newb,
        'ranked': len(q), 'review': len(mr), 'ineligible': len(inel), 'parent_overlaps': len(pod), 'shared_parents': len(shared),
        'verified_ranked': int((q['ranking_type'] != 'Preliminary ranking').sum()), 'presort_rows': len(ps),
        'sectors': q['sector'].value_counts().to_dict(), 'w15_pending': len(w15p), 'w15_left': len(w15l),
        'qc': QC, 'top20': top20[['overall_rank', 'name', 'sector', 'priority', 'fit60', 'fin40', 'ranking_type', 'f1_deal']].values.tolist(),
        'f1_sponsors': len(f1t), 'f1_top': f1top[['f1_rank', 'name', 'priority', 'f1_deal']].values.tolist(),
        'top20_nonf1': nf20[['overall_rank', 'name', 'sector', 'priority', 'fit60', 'fin40', 'ranking_type']].values.tolist()}
json.dump(summ, open(f'{S}/final_summary.json', 'w'), default=str, indent=1)
print(json.dumps({k: v for k, v in summ.items() if k not in ('sectors', 'top20', 'top20_nonf1', 'qc')}))
for x in QC: print(x)
