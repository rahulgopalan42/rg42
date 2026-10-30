# Evidence layer, exec'd by build.py (namespace: u, pd, H, json, glob, re, os, s, loose, regdom).
# Each of Rahul's three tests is decided from sources independent of the research agents' memory:
#   private   - CB Insights' current unicorn list (it drops companies once they list or are acquired; fetched 30 Oct 2026)
#               cross-checked with Wikipedia's exited-unicorn table and the agents' status calls;
#   valuation - CB Insights valuation, or a later dated valuation with a source;
#   funding   - Apollo funded-company filter (total funding >= USD 200M, free lookup by website), research estimate as support;
#   identity  - the website maps to the same company in Apollo.
# Anything conflicting or resting on one weak source goes to the web check; web-check rows override everything.
cbi = pd.read_csv(os.path.join(H, 'ref', 'cbinsights_unicorns.csv'), dtype={'id': str})
dom = {}
for f in sorted(glob.glob(os.path.join(H, 'ref', 'domains_out_*.json'))):
    for r in json.load(open(f)): dom[r[0]] = r          # [id, company, domain, domain_conf, apollo_name, apollo_funding, identity_ok]
cbi['domain'] = cbi['id'].map(lambda i: regdom(dom.get(i, [''] * 7)[2]))
cbi['apollo_funding'] = cbi['id'].map(lambda i: dom.get(i, [''] * 7)[5])
cbi['identity_ok'] = cbi['id'].map(lambda i: dom.get(i, [''] * 7)[6])
APF = {}                                                 # registrable domain -> (apollo name, '>=200' | '<200' | 'not found')
for r in dom.values():
    if regdom(r[2]): APF[regdom(r[2])] = (s(r[4]), s(r[5]))
for _ex in sorted(glob.glob(os.path.join(H, 'ref', 'apollo_extra*_out.json'))):
    for r in json.load(open(_ex)): APF.setdefault(regdom(r[0]), (s(r[1]), s(r[2])))   # [domain, apollo_name, apollo_funding]
wx = pd.read_csv(os.path.join(H, 'ref', 'wikipedia_former_unicorns.csv'))
EXIT = {loose(n): (s(rsn), s(d)) for n, rsn, d in zip(wx['company'], wx['exit_reason'], wx['exit_date']) if loose(n) and not re.search(r'deval', s(rsn), re.I)}   # a down-round is not an exit
CN = {}
for r in cbi.itertuples(): CN.setdefault(loose(r.company), []).append(r.id)
CD = {r.domain: r.id for r in cbi.itertuples() if r.domain}
CB = cbi.set_index('id')
CTRY = {'usa': 'united states', 'us': 'united states', 'uk': 'united kingdom', 'uae': 'united arab emirates', 'korea': 'south korea'}
cn = lambda x: CTRY.get(s(x).lower(), s(x).lower())
def link(r):
    if r['cbid'] and r['cbid'] in CB.index: return r['cbid']
    for d in r['domains']:
        if d in CD: return CD[d]
    for nm in (r['brand'], r['legal_name']):
        ids = CN.get(loose(nm), []) if loose(nm) else []
        if len(ids) == 1 and (not r['hq_country'] or cn(CB.at[ids[0], 'country']) == cn(r['hq_country']) or len(loose(nm)) >= 6): return ids[0]
        for i in ids:
            if cn(CB.at[i, 'country']) == cn(r['hq_country']): return i
    return ''
u['cbid'] = u.apply(link, axis=1)
u['in_cbi'] = u['cbid'] != ''
# CB Insights unicorns that no research row covered are added as records of their own (scored by the enrich pass)
_have = set(u['cbid'])
_add = []
for r in cbi.itertuples():
    if r.id in _have: continue
    _add.append(dict(brand=r.company, legal_name='', parent='', hq_country=r.country, hq_city=s(r.city), domain=r.domain, sector=48, what=s(r.industry),
                     valuation_bn=r.valuation_bn, valuation_date='', vdate='', valuation_basis='CB Insights', funding_m=float('nan'), latest_round='', status='private',
                     investors=s(r.investors), revenue_m=float('nan'), why='', f1_status='', f1_deal='', sport_deals='', evidence='', ceo='', conf='L', source_url='',
                     note='not yet scored', file='CB Insights list', verified=False, check='', vkey='', cbid=r.id, in_cbi=True, found_by='CB Insights list', new_unicorn=False,
                     dupes=1, exit_votes=0, agent_status='', agent_val=float('nan'), agent_vdate='', agent_fund=float('nan'), agent_conf='', domains=[r.domain] if r.domain else [],
                     status_conflict=False, status_all='', **{k: 0 for k in SIG}))
if _add: u = pd.concat([u, pd.DataFrame(_add)], ignore_index=True)
print('linked to CB Insights', int(u['in_cbi'].sum()), '| CB Insights-only records added', len(_add))
u['cbi_val'] = u['cbid'].map(lambda i: CB.at[i, 'valuation_bn'] if i else float('nan'))
u['cbi_joined'] = u['cbid'].map(lambda i: s(CB.at[i, 'joined'])[:7] if i else '')
u['new_unicorn'] = u['new_unicorn'] | (u['cbi_joined'] >= '2025-01')
if 'cbi_val' in u:
    m = u['in_cbi'] & ~u['verified'] & (u['domain'] == '')
    u.loc[m, 'domain'] = u.loc[m, 'cbid'].map(lambda i: CB.at[i, 'domain'])
    m = u['in_cbi'] & ~u['verified'] & (u['hq_country'] == '')
    u.loc[m, 'hq_country'] = u.loc[m, 'cbid'].map(lambda i: CB.at[i, 'country'])
def apollo(r):
    ds = list(r['domains']) + ([CB.at[r['cbid'], 'domain']] if r['cbid'] and CB.at[r['cbid'], 'domain'] else [])
    res = [APF[d] for d in ds if d in APF]
    if any(x[1] == '>=200' for x in res): return '>=200', next(x[0] for x in res if x[1] == '>=200')
    if any(x[1] == '<200' for x in res): return '<200', next(x[0] for x in res if x[1] == '<200')
    return ('not found' if res else 'not checked'), ''
_ap = u.apply(apollo, axis=1); u['apollo_funding'] = [a for a, b in _ap]; u['apollo_name'] = [b for a, b in _ap]
def ident(r):
    if r['cbid'] and dom.get(r['cbid'], [''] * 7)[6] == 'Y': return 'Y'
    if r['apollo_name']:
        a, b = loose(r['apollo_name']), loose(r['brand'])
        return 'Y' if a and b and (a.startswith(b[:5]) or b.startswith(a[:5])) else '?'
    return '?'
u['identity'] = u.apply(ident, axis=1)
u['exit_wiki'] = u['brand'].map(lambda b: EXIT.get(loose(b), ('', ''))[0])
u['exit_wiki_date'] = u['brand'].map(lambda b: EXIT.get(loose(b), ('', ''))[1])
GOOD = {'H', 'M'}
NC = {}                                                  # news verification rulings (newscheck_brief.md)
for f in sorted(glob.glob(os.path.join(H, 'newscheck_out', '*.json'))):
    try:
        for x in json.load(open(f)):
            if isinstance(x, list) and len(x) == 9: NC[s(x[0])] = x
    except Exception as e: print('bad news file', f, e)
def decide(r):
    """returns (t_private, t_val, t_fund, verdict, ev_private, ev_val, ev_fund); t_* in {True, False, None (unsure)}"""
    if r['verified']:
        ok = r['check'] in ('confirmed', 'corrected')
        tp = r['status'] == 'private'; tv = r['valuation_bn'] >= 1; tf = r['funding_m'] >= 200
        v = 'verified' if ok and tp and tv and tf else ('failed' if ok else 'could not verify')
        src = f"web check {r['check']}" + (f" ({r['source_url']})" if r['source_url'] else '')
        return tp, tv, tf, v, src, src, src
    # private
    if r['in_cbi'] and not r['exit_wiki'] and r['exit_votes'] == 0: tp, ep = True, 'CB Insights current private-unicorn list (30 Oct 2026)'
    elif r['in_cbi']: tp, ep = None, f"conflict: on CB Insights list but {'Wikipedia exit ' + r['exit_wiki'] + ' ' + r['exit_wiki_date'] if r['exit_wiki'] else 'research says ' + r['agent_status']}"
    elif r['status'] in ('public', 'acquired', 'defunct') and r['conf'] in GOOD: tp, ep = False, f"research: {r['status']}" + (f" (Wikipedia: {r['exit_wiki']} {r['exit_wiki_date']})" if r['exit_wiki'] else '')
    elif r['exit_wiki']: tp, ep = False, f"Wikipedia exited unicorns: {r['exit_wiki']} {r['exit_wiki_date']}"
    elif r['status'] in ('private', 'below_1b') and r['agent_vdate'] >= '2026-01' and r['source_url'] and r['exit_votes'] == 0:
        tp, ep = True, f"priced private round {r['agent_vdate']} (source: {r['source_url'][:80]}); too recent for CB Insights list; no listing or exit found"
    elif r['status'] in ('private', 'below_1b'): tp, ep = None, 'research only (not on CB Insights unicorn list)'
    else: tp, ep = False, f"research: {r['status'] or 'unknown'}"
    if r['parent'] and loose(r['parent']) != loose(r['brand']) and tp: tp, ep = None, ep + f"; majority owner named: {r['parent']}"
    # valuation
    av, cv = r['agent_val'], r['cbi_val']
    if cv == cv and cv >= 1:
        tv = True; ev = f"CB Insights USD {cv:,.2f}B"
        if av == av and av > cv and r['agent_vdate'] >= '2025-07' and r['agent_conf'] in GOOD: ev += f"; later reported USD {av:,.2f}B ({r['agent_vdate']})"
    elif av == av and av >= 1 and r['source_url'] and r['agent_vdate'] >= '2025-07': tv, ev = True, f"reported USD {av:,.2f}B ({r['agent_vdate']}), source: {r['source_url'][:80]}"
    elif av == av and av >= 1: tv, ev = None, f"research USD {av:,.2f}B ({r['agent_vdate'] or 'date n/a'}), not on CB Insights list"
    elif av == av: tv, ev = False, f"research USD {av:,.2f}B"
    else: tv, ev = None, 'no valuation found'
    # funding
    ap, af = r['apollo_funding'], r['agent_fund']
    if ap == '>=200': tf, ef = True, 'Apollo: total funding >= USD 200M' + (f"; research ~USD {af:,.0f}M" if af == af else '')
    elif ap == '<200' and af == af and af >= 200: tf, ef = None, f"conflict: Apollo < USD 200M, research ~USD {af:,.0f}M"
    elif ap == '<200': tf, ef = False, 'Apollo: total funding < USD 200M' + (f"; research ~USD {af:,.0f}M" if af == af else '')
    elif af == af and af >= 200: tf, ef = None, f"research ~USD {af:,.0f}M only (Apollo {ap})"
    elif af == af: tf, ef = False, f"research ~USD {af:,.0f}M (Apollo {ap})"
    else: tf, ef = None, f'no funding figure (Apollo {ap})'
    x = NC.get(r['brand'])
    if x and s(x[1]).upper() != 'N' and s(x[6]).lower() in ('confirmed', 'corrected'):
        st, nv_, nm, fok, evd = s(x[2]).lower(), x[3], s(x[4]), s(x[5]).upper(), s(x[7])
        if st in ('public', 'acquired', 'defunct'): tp, ep = False, f"news: {st} - {evd}"
        elif st == 'private':
            if tp is None: tp = True
            ep += f" | news: {evd}"
        try: nv_ = float(nv_)
        except (TypeError, ValueError): nv_ = None
        if nv_ is not None and nv_ >= 1:
            if tv is None: tv = True
            ev += f" | news: USD {nv_:,.2f}B ({nm})"
        elif nv_ is not None and nv_ < 1 and s(x[6]).lower() == 'corrected': tv, ev = False, f"news: USD {nv_:,.2f}B ({nm}) - {evd}"
        elif nv_ is None and s(x[6]).lower() == 'corrected' and st == 'private': tv, ev = None, f"news: valuation no longer supported ({s(x[8])})"
        if st == 'unknown' and tp: tp, ep = None, f"news: status unclear - {s(x[8])}"
        if re.search(r"not (truly |clearly )?independent|isn't independent|likely not .?independent|majority[- ]owned|majority (owner|stake|control|holder)|PE[- ]owned|PE majority|\b(?!founder|family|employee|privately)[A-Za-z]+-owned\b|take-private|subsidiary of|[a-z]+-controlled|controlled by", s(x[8]), re.I) and not re.search(r'still independent|minority|no majority|none majority|not majority', s(x[8]), re.I) and tp:
            tp, ep = False, f"not independent: {s(x[8])}"
        if fok == 'Y' and tf is None: tf, ef = True, ef + ' | news: total raised >= USD 200M'
        elif fok == 'N' and tf is None: tf, ef = False, ef + ' | news: total raised < USD 200M'
        elif fok == 'N' and tf: tf, ef = None, ef + ' | conflict: news suggests < USD 200M'
    # Rahul, 30 Oct (2nd request): valuation is no longer a pass/fail test - private + USD 200M+ raised qualifies; valuation is shown
    if tp is False or tf is False: v = 'failed'
    elif tp and tf and r['identity'] != 'N': v = 'verified'
    else: v = 'needs web check'
    return tp, tv, tf, v, ep, ev, ef
_d = u.apply(decide, axis=1)
u['news_check'] = u['brand'].map(lambda b: ((s(NC[b][6]).lower() + (' (no relevant news; rests on CB Insights + Apollo)' if s(NC[b][1]).upper() in ('N', '?') or not s(NC[b][7]) else ' by news')) if b in NC else ''))
u['news_evidence'] = u['brand'].map(lambda b: s(NC[b][7]) if b in NC else '')
def _nval(r):
    x = NC.get(r['brand'])
    try: return (float(x[3]), s(x[4])) if x and s(x[1]).upper() != 'N' and x[3] is not None and float(x[3]) > 0 else (None, '')
    except (TypeError, ValueError): return (None, '')
u['news_val'] = u.apply(_nval, axis=1)
for k, c in enumerate(['t_private', 't_val', 't_fund', 'verdict', 'ev_private', 'ev_val', 'ev_fund']): u[c] = [x[k] for x in _d]
# displayed valuation: newest well-sourced figure
u['valuation_bn'] = u.apply(lambda r: r['valuation_bn'] if r['verified'] else (max(r['cbi_val'], r['agent_val']) if r['cbi_val'] == r['cbi_val'] and r['agent_val'] == r['agent_val'] and r['agent_vdate'] >= '2025-07' and r['agent_conf'] in GOOD
                                                                              else (r['cbi_val'] if r['cbi_val'] == r['cbi_val'] else r['agent_val'])), axis=1)
u['vdate'] = u.apply(lambda r: r['vdate'] or (r['cbi_joined'] and 'joined ' + r['cbi_joined']), axis=1)
_nv = u['news_val'].map(lambda x: x[0]); _nm = u['news_val'].map(lambda x: x[1])
_use = _nv.notna() & ((_nm > u['vdate'].str.replace('joined ', '')) | u['valuation_bn'].isna())
u['valuation_bn'] = [float(n) if k else v for k, n, v in zip(_use, _nv, u['valuation_bn'])]; u['vdate'] = [m if k else d for k, m, d in zip(_use, _nm, u['vdate'])]
for c in ('t_private', 't_val', 't_fund'): u[c] = u[c].map(lambda x: bool(x) if x is not None else False)
print(u['verdict'].value_counts().to_dict())
