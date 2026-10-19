"""Parent-company prospects, step 2: merge every discovery source into one record per ultimate parent and
cross-reference against all existing datasets.
Sources: parents/discover/cat_*.json (knowledge discovery), parents/apollo/page_*.json (Apollo, funding >= 100M),
parents/lusha/page_*.json (Lusha, funding >= 100M).
Existing datasets: old_v2.pkl (Old Google Drive master files + previous prospect workbooks/CSVs, every worksheet),
new_all.pkl (Friday Clay exports), Wave 16 final ranking (previous prospect workbook).
Writes parents.pkl (one row per parent, with category A/B/C), subs_hits.pkl, dups.pkl."""
import collections, glob, json, os, re, sys
import pandas as pd
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
P = f'{S}/../parents'; os.makedirs(P, exist_ok=True)
sys.path.insert(0, f'{R}/wave16')
from dedupe_v2 import regdom, strict, core, lislug
from sectors_v3 import NAMES
GENERIC_PARENT = {'', 'none', 'na', 'nan', 'independent', 'private', 'public', 'family', 'founders', 'management', 'employees', 'government', 'state'}

# ---------------------------------------------------------------- knowledge discovery
F = ['name', 'hq_country', 'domain', 'type', 'ticker', 'val_bn', 'val_basis', 'val_date', 'funding_m', 'sector', 'brand', 'approach',
     'why', 'a', 's', 'l', 'n', 'fin', 'f1', 'subs', 'conf']
rows, bad = [], 0
for f in sorted(glob.glob(f'{R}/parents/discover/cat_*.json')):
    cat = os.path.basename(f)[4:6]
    try: data = json.load(open(f))
    except Exception: bad += 1; continue
    for r in data:
        if not isinstance(r, list) or len(r) != 21: bad += 1; continue
        d = dict(zip(F, r)); d['cat'] = cat; rows.append(d)
disc = pd.DataFrame(rows)
print('discovery rows', len(disc), 'bad', bad, 'categories', disc['cat'].nunique() if len(disc) else 0)
def num(x):
    try: return float(x) if x is not None and x != '' else None
    except Exception: return None
for c in ('val_bn', 'funding_m'): disc[c] = disc[c].map(num)
for c in ('a', 's', 'l', 'n'): disc[c] = pd.to_numeric(disc[c], errors='coerce').fillna(1).clip(0, 4).astype(int)
disc['sector'] = pd.to_numeric(disc['sector'], errors='coerce').fillna(48).clip(1, 48).astype(int)
disc['subs'] = disc['subs'].map(lambda x: [str(s) for s in x] if isinstance(x, list) else [])
disc['qualifies'] = (disc['val_bn'].fillna(0) >= 1) | (disc['funding_m'].fillna(0) >= 100)
print('discovery qualifying', int(disc['qualifies'].sum()))

# ---------------------------------------------------------------- Apollo / Lusha pulls
AF = ['id', 'name', 'domain', 'linkedin', 'founded', 'exchange', 'owner_name', 'owner_site', 'revenue_printed', 'sic0', 'naics0']
ap = []
for f in sorted(glob.glob(f'{R}/parents/apollo/page_*.json')):
    try:
        for r in json.load(open(f)):
            if isinstance(r, list) and len(r) == 11: ap.append(dict(zip(AF, r)))
    except Exception: pass
ap = pd.DataFrame(ap, columns=AF)
LF = ['lusha_id', 'name', 'domain', 'country', 'industry', 'size', 'revenue_range', 'total_funding', 'last_round', 'is_ipo', 'linkedin']
lu = []
for f in sorted(glob.glob(f'{R}/parents/lusha/page_*.json')):
    try:
        for r in json.load(open(f)):
            if isinstance(r, list) and len(r) == 11: lu.append(dict(zip(LF, r)))
    except Exception: pass
lu = pd.DataFrame(lu, columns=LF)
print('apollo rows', len(ap), 'lusha rows', len(lu))

# Apollo: the record's parent is the owner where Apollo knows one; otherwise the company itself is the parent
ap['rd'] = ap['domain'].map(lambda d: regdom(d or ''))
ap['owner_rd'] = ap['owner_site'].map(lambda d: regdom(d or ''))
ap['owner_sn'] = ap['owner_name'].fillna('').map(strict)
ap['own'] = ap['owner_name'].fillna('').map(lambda x: strict(x) not in GENERIC_PARENT)
lu['rd'] = lu['domain'].map(lambda d: regdom(d or ''))

# ---------------------------------------------------------------- one record per parent
def pkey(name, dom):
    rd = regdom(dom or '')
    return rd if rd else 'n:' + strict(name)
recs = {}      # key -> record
alias = {}     # strict name / domain -> key
def add(key, src, **kw):
    r = recs.setdefault(key, {'sources': set(), 'subs': set(), 'children': set(), 'names': set()})
    r['sources'].add(src)
    for k, v in kw.items():
        if v in (None, '', [], {}): continue
        if k in ('subs', 'children', 'names'): r[k] |= set(v)
        elif k not in r or r[k] in (None, ''): r[k] = v
    return r
# knowledge discovery first (richest records)
for d in disc.itertuples():
    k = pkey(d.name, d.domain)
    for s in d.subs: alias.setdefault(strict(s), k)
    alias.setdefault(strict(d.name), k)
    if d.domain: alias.setdefault(regdom(d.domain), k)
    add(k, 'knowledge', name=d.name, hq_country=d.hq_country, domain=d.domain, type=d.type, ticker=d.ticker, val_bn=d.val_bn,
        val_basis=d.val_basis, val_date=d.val_date, funding_m=d.funding_m, sector=d.sector, brand=d.brand, approach=d.approach,
        why=d.why, a=d.a, s=d.s, l=d.l, n=d.n, fin=d.fin, f1=d.f1, subs=d.subs, conf=d.conf, cat=d.cat, names=[d.name])
# Apollo: attach to a known parent via owner or own identity; otherwise create a parent record
def resolve(name, dom):
    sn, rd = strict(name), regdom(dom or '')
    if rd and rd in recs: return rd
    if rd and rd in alias: return alias[rd]
    if sn in alias: return alias[sn]
    return None
for a in ap.itertuples():
    if a.own:
        pk = resolve(a.owner_name, a.owner_site) or pkey(a.owner_name, a.owner_site)
        add(pk, 'apollo', name=a.owner_name, domain=a.owner_site, children=[a.name], names=[a.owner_name])
        alias.setdefault(a.owner_sn, pk)
        if a.rd: alias.setdefault(a.rd, pk)
        recs[pk].setdefault('apollo_funded_child', a.name)
    else:
        pk = resolve(a.name, a.domain) or pkey(a.name, a.domain)
        add(pk, 'apollo', name=a.name, domain=a.domain, names=[a.name], apollo_funding='>= USD 100M total funding (Apollo filter)',
            exchange=a.exchange, revenue_printed=a.revenue_printed, linkedin=a.linkedin, naics0=a.naics0)
        alias.setdefault(strict(a.name), pk)
        if a.rd: alias.setdefault(a.rd, pk)
for l in lu.itertuples():
    pk = resolve(l.name, l.domain) or pkey(l.name, l.domain)
    add(pk, 'lusha', name=l.name, domain=l.domain, hq_country=l.country, names=[l.name], lusha_funding=l.total_funding,
        lusha_industry=l.industry, lusha_revenue=l.revenue_range, lusha_ipo=l.is_ipo, linkedin=l.linkedin)
    alias.setdefault(strict(l.name), pk)
    if l.rd: alias.setdefault(l.rd, pk)
par = pd.DataFrame([{**{k: (sorted(v) if isinstance(v, set) else v) for k, v in r.items()}, 'key': key} for key, r in recs.items()])
par['sn'] = par['name'].map(strict); par['rd'] = par['domain'].fillna('').map(regdom)
# same parent reached under two keys (name key vs domain key): keep the first, record the duplicate
dups = []
seen = {}
keep = []
for r in par.itertuples():
    k2 = r.rd or r.sn
    if k2 in seen:
        dups.append([r.name, r.domain, 'same parent as ' + seen[k2], ', '.join(r.sources)]); continue
    seen[k2] = r.name; keep.append(r.Index)
par = par.loc[keep].reset_index(drop=True)
print('parents', len(par), 'merged duplicate parent records', len(dups))

# ---------------------------------------------------------------- existing datasets
old = pd.read_pickle(f'{S}/old_v2.pkl')
old['ds'] = old['category'].map(lambda c: 'Old Google Drive' if c == 'Old master files (Drive)' else 'Previous prospect workbooks')
clay = pd.read_pickle(f'{S}/new_all.pkl')
ex = pd.concat([pd.DataFrame({'name': old['name'], 'domain': old['domain'], 'ds': old['ds'], 'where': old['source']}),
                pd.DataFrame({'name': clay['name'], 'domain': clay['domain'], 'ds': 'Friday Clay Exports', 'where': clay['source_csv']})], ignore_index=True)
ex['sn'] = ex['name'].map(strict); ex['rd'] = ex['domain'].map(lambda d: regdom(d or ''))
RANK = {'Old Google Drive': 0, 'Previous prospect workbooks': 1, 'Friday Clay Exports': 2}
by_sn = collections.defaultdict(list); by_rd = collections.defaultdict(list)
for sn, rd, ds, wh, nm in zip(ex['sn'], ex['rd'], ex['ds'], ex['where'], ex['name']):
    if len(sn) >= 3: by_sn[sn].append((RANK[ds], ds, wh, nm))
    if rd: by_rd[rd].append((RANK[ds], ds, wh, nm))
def hits(sn, rd):
    h = []
    if rd: h += by_rd.get(rd, [])
    if len(sn) >= 3: h += by_sn.get(sn, [])
    return sorted(set(h))

out = []
for r in par.itertuples():
    ph = hits(r.sn, r.rd)                                   # parent itself present?
    sub_hits = []
    for s in sorted(set(r.subs) | set(r.children)):
        ss = strict(s)
        if len(ss) < 4: continue
        hh = hits(ss, '')
        if hh: sub_hits.append((s, hh[0]))
    core_only = (not ph) and len(core(r.name)) >= 5 and any(len(core(x)) >= 5 and core(x) == core(r.name) for x in [])  # placeholder
    if ph:
        cat_ = 'B'; basis = 'parent itself listed'
    elif sub_hits:
        cat_ = 'B'; basis = 'subsidiary / brand listed'
    else:
        cat_ = 'A'; basis = ''
    ds_set = sorted({h[1] for h in ph} | {h[1][1] for h in sub_hits}, key=lambda x: RANK[x])
    out.append({'overlap_cat': cat_, 'overlap_basis': basis, 'parent_listed': 'yes' if ph else 'no',
                'parent_where': '; '.join(f"{h[1]}: {h[2]}" for h in ph[:3]),
                'existing_brands': '; '.join(f"{s} ({h[1]}: {h[2]})" for s, h in sub_hits[:4]),
                'datasets': ', '.join(ds_set)})
par = pd.concat([par, pd.DataFrame(out)], axis=1)
# uncertain: no financial figure from any source, or a generic / very short parent name
par['has_fin'] = (par['val_bn'].fillna(0) >= 1) | (par['funding_m'].fillna(0) >= 100) | par['apollo_funding'].notna() | par['lusha_funding'].notna() \
    if 'lusha_funding' in par else (par['val_bn'].fillna(0) >= 1) | (par['funding_m'].fillna(0) >= 100) | par['apollo_funding'].notna()
par.loc[~par['has_fin'] | (par['sn'].str.len() < 3), 'overlap_cat'] = 'C'
par.to_pickle(f'{P}/parents.pkl')
pd.DataFrame(dups, columns=['parent', 'domain', 'reason', 'sources']).to_pickle(f'{P}/dups.pkl')
print(par['overlap_cat'].value_counts().to_dict())
print(par.groupby('overlap_cat')['sources'].apply(lambda x: collections.Counter(tuple(s) for s in x).most_common(4)).to_string()[:1500])
