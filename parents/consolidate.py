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

# ---------------------------------------------------------------- knowledge scoring of connector-sourced records
# parents/score_out/chunk_*.json: Sonnet's parent check and scores for the Apollo/Lusha-only records (see score_brief.md)
SF = ['in_name', 'status', 'parent_name', 'hq_country', 'domain', 'type', 'ticker', 'val_bn', 'val_basis', 'val_date', 'funding_m',
      'sector', 'brand', 'approach', 'why', 'a', 's', 'l', 'n', 'fin', 'f1', 'subs', 'conf', 'qualifies', 'note']
scored = {}
for f in sorted(glob.glob(f'{R}/parents/score_out/chunk_*.json')):
    try:
        for r in json.load(open(f)):
            if isinstance(r, list) and len(r) == 25: scored[strict(r[0])] = dict(zip(SF, r))
    except Exception as e: print('bad score file', f, e)
print('scored connector records', len(scored))
excluded = []        # [name, domain, reason, sources]
def kfields(sc):
    d = {k: sc.get(k) for k in ('hq_country', 'domain', 'type', 'ticker', 'val_basis', 'val_date', 'sector', 'brand', 'approach', 'why', 'fin', 'f1', 'conf')}
    d['val_bn'] = num(sc.get('val_bn')); d['funding_m'] = num(sc.get('funding_m'))
    for k in ('a', 's', 'l', 'n'):
        try: d[k] = max(0, min(4, int(sc.get(k) or 0)))
        except Exception: d[k] = 1
    try: d['sector'] = max(1, min(48, int(sc.get('sector') or 48)))
    except Exception: d['sector'] = 48
    d['subs'] = [str(x) for x in sc.get('subs') or []]
    d['note'] = sc.get('note') or ''; d['qualifies_k'] = sc.get('qualifies') or '?'
    return {k: v for k, v in d.items() if v not in (None, '')}
n_applied = collections.Counter()
for key in list(recs):
    r = recs[key]
    if 'knowledge' in r['sources']: continue
    sc = None
    for nm in r['names'] | {r.get('name', '')}:
        sc = scored.get(strict(nm))
        if sc: break
    if not sc: continue
    st = sc['status']; n_applied[st] += 1
    if st == 'X':
        excluded.append([r.get('name'), r.get('domain', ''), 'not a prospect: ' + (sc.get('note') or 'fund vehicle / public body / defunct / absorbed'), ', '.join(sorted(r['sources']))])
        for nm in r['names']: alias.pop(strict(nm), None)
        del recs[key]; continue
    if st == 'U':
        r['conf'] = 'U'; r['note'] = sc.get('note') or 'not recognised by knowledge model'; continue
    if st == 'S' and sc.get('parent_name') and strict(sc['parent_name']) != strict(r.get('name', '')):
        pname = sc['parent_name']; pdom = sc.get('domain') or ''
        pk = resolve(pname, pdom) or pkey(pname, pdom)
        if pk == key: pk = 'n:' + strict(pname)
        child_names = set(r['names']) | {r.get('name', '')}
        tgt = add(pk, 'knowledge-scored', name=pname, names=[pname], **kfields(sc))
        tgt['sources'] |= r['sources']; tgt['children'] |= child_names | r['children']; tgt['subs'] |= r['subs']
        if r.get('apollo_funding'): tgt.setdefault('apollo_funding', r['apollo_funding'])
        tgt.setdefault('apollo_funded_child', r.get('name'))
        for nm in child_names: alias[strict(nm)] = pk
        if pdom: alias.setdefault(regdom(pdom), pk)
        del recs[key]; continue
    # status P: fill the record with knowledge fields (keep the connector's own values where knowledge is blank)
    r['sources'].add('knowledge-scored')
    for k, v in kfields(sc).items():
        if k == 'subs': r['subs'] |= set(v)
        elif k == 'domain' and r.get('domain'): continue
        else: r[k] = v
    for s_ in r['subs']: alias.setdefault(strict(s_), key)
print('scoring applied', dict(n_applied), '| excluded as non-prospects', len(excluded))
par = pd.DataFrame([{**{k: (sorted(v) if isinstance(v, set) else v) for k, v in r.items()}, 'key': key} for key, r in recs.items()])
par['sn'] = par['name'].map(strict); par['rd'] = par['domain'].fillna('').map(regdom)
# same parent reached under two keys (name key vs domain key): keep the first, record the duplicate
dups = []
seen = {}
keep = []
for r in par.itertuples():
    keys2 = [k for k in (r.rd, r.sn) if k and (k != r.sn or len(r.sn) >= 4)]      # website, or a distinctive name
    hit = next((k for k in keys2 if k in seen), None)
    if hit:
        dups.append([r.name, r.domain, 'same parent as ' + seen[hit], ', '.join(r.sources)]); continue
    for k in keys2: seen[k] = r.name
    keep.append(r.Index)
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
def hits(sn, rd, name_ok=True):
    """a website match always counts; a name match needs a distinctive name (6+ chars) unless name_ok is forced"""
    h = []
    if rd: h += by_rd.get(rd, [])
    if name_ok and len(sn) >= 6: h += by_sn.get(sn, [])
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
    short_name_unmatched = (not ph) and 3 <= len(r.sn) < 6 and not r.rd and len(by_sn.get(r.sn, [])) > 0
    if ph:
        cat_ = 'B'; basis = 'parent itself listed'
    elif sub_hits:
        cat_ = 'B'; basis = 'subsidiary / brand listed'
    elif short_name_unmatched:
        cat_ = 'C'; basis = 'short name matches existing records; website unknown - confirm identity'
    else:
        cat_ = 'A'; basis = ''
    ds_set = sorted({h[1] for h in ph} | {h[1][1] for h in sub_hits}, key=lambda x: RANK[x])
    out.append({'overlap_cat': cat_, 'overlap_basis': basis, 'parent_listed': 'yes' if ph else 'no',
                'parent_where': '; '.join(f"{h[1]}: {h[2]}" for h in ph[:3]),
                'existing_brands': '; '.join(f"{s} ({h[1]}: {h[2]})" for s, h in sub_hits[:4]),
                'datasets': ', '.join(ds_set)})
par = pd.concat([par, pd.DataFrame(out)], axis=1)
# financial evidence: a known valuation/funding figure, the Apollo funding filter on the parent's own record, or the Lusha
# funding filter. A parent inferred only from Apollo's 'owned by' field has no evidence of its own -> Manual Review.
src_has = lambda tag: par['sources'].map(lambda x: tag in x)
par['group_funding'] = par['apollo_funded_child'].notna() if 'apollo_funded_child' in par else False
par['has_fin'] = (par['val_bn'].fillna(0) >= 1) | (par['funding_m'].fillna(0) >= 100) | par['apollo_funding'].notna() | src_has('lusha') | par['group_funding']
par['fin_basis'] = ''
par.loc[par['val_bn'].fillna(0) >= 1, 'fin_basis'] = 'valuation >= USD 1B (' + par['val_basis'].fillna('').astype(str) + ' ' + par['val_date'].fillna('').astype(str) + ')'
m = (par['fin_basis'] == '') & (par['funding_m'].fillna(0) >= 100); par.loc[m, 'fin_basis'] = 'cumulative funding >= USD 100M (knowledge)'
m = (par['fin_basis'] == '') & par['apollo_funding'].notna(); par.loc[m, 'fin_basis'] = 'total funding >= USD 100M (Apollo database filter)'
m = (par['fin_basis'] == '') & src_has('lusha'); par.loc[m, 'fin_basis'] = 'total funding >= USD 100M (Lusha database filter)'
m = (par['fin_basis'] == '') & par['group_funding']
par.loc[m, 'fin_basis'] = 'cumulative funding >= USD 100M at group level (subsidiary ' + par.loc[m, 'apollo_funded_child'].astype(str) + ' per Apollo filter); parent\'s own figure unverified'
par.loc[~par['has_fin'] | (par['sn'].str.len() < 3), 'overlap_cat'] = 'C'
par['clay_only'] = (par['overlap_cat'] == 'B') & (par['datasets'] == 'Friday Clay Exports')
par['needs_score'] = par['a'].isna() if 'a' in par else True
par.to_pickle(f'{P}/parents.pkl')
print('overlap only with the unworked Friday Clay export:', int(par['clay_only'].sum()), '| needs knowledge scoring:', int(par['needs_score'].sum()))
pd.DataFrame(dups, columns=['parent', 'domain', 'reason', 'sources']).to_pickle(f'{P}/dups.pkl')
pd.DataFrame(excluded, columns=['parent', 'domain', 'reason', 'sources']).to_pickle(f'{P}/excluded.pkl')
print(par['overlap_cat'].value_counts().to_dict())
print(par.groupby('overlap_cat')['sources'].apply(lambda x: collections.Counter(tuple(s) for s in x).most_common(4)).to_string()[:1500])
