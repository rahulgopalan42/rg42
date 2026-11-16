"""New brands (not on the 48-tab sheet), filed under the tab for their category (16 Nov 2026).
New tabs for the sectors the sheet has no tab for (quantum, nuclear, defence technology, space, robotics, AI infrastructure, crypto,
betting and prediction markets, brokers ...); the sheet's own tab names for everything else.
Sources: public revenue rankings of unlisted companies (newsec/ranking_rows.json, profiled in newsec/out), one web research file per
group (newsec/web/*.jsonl, each company with a capacity proof and its source) and the public unicorn list. Same parameter set as allsector.py.
Usage: newsectors.py [check|xlsx]"""
import glob, html, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b, allsector as a, allsector_notes as AN
OUT = os.path.join(b.R, 'reports', 'F1-NEW-BRANDS-BY-CATEGORY-2026-11-16.xlsx')
RORD = a.RORD
# how each research group is described in the "How Found" column
GROUPS = {'rank': 'Public revenue rankings of unlisted companies', 'brokers': 'Web research: brokers and trading platforms', 'crypto': 'Web research: crypto and prediction markets',
          'betting': 'Web research: betting and iGaming', 'pe_owned': 'Web research: private-equity-owned companies', 'professional': 'Web research: professional partnerships',
          'state_backed': 'Web research: state-backed brands', 'luxury_travel': 'Web research: luxury, private aviation and travel', 'sport_sponsors': 'Web research: unlisted sponsors of top-tier sport',
          'quantum_chips': 'Web research: quantum and AI chips', 'nuclear_energy': 'Web research: nuclear, fusion and energy transition', 'defence': 'Web research: defence technology',
          'space': 'Web research: space and satellites', 'robotics_mobility': 'Web research: robotics, autonomy and new mobility', 'ai_infra': 'Web research: AI infrastructure and data centres',
          'ai_models': 'Web research: AI models and applications', 'cyber_fintech': 'Web research: cybersecurity and fintech', 'consumer_creator': 'Web research: consumer health, creator and consumer brands',
          'unicorn_1': 'Public unicorn list, each company checked', 'unicorn_2': 'Public unicorn list, each company checked'}
# new tabs, in workbook order: (tab name, what it covers, pattern on the theme text)
NEW = [('NEW Quantum Computing', 'Quantum hardware, software and networking', r'quantum'),
       ('NEW AI Chips', 'AI chips, photonics and chip start-ups', r'chip|semiconductor'),
       ('NEW AI Infra & Data Centres', 'Data centres, GPU cloud and AI compute', r'infrastructure|data cent|gpu'),
       ('NEW AI Models & Applications', 'AI model developers, agents and applications', r'ai model|agents|application'),
       ('NEW Cybersecurity', 'Cybersecurity companies', r'cyber'),
       ('NEW Robotics & Autonomy', 'Robots, humanoids and self-driving', r'robot|humanoid|autonomous'),
       ('NEW EVs & New Mobility', 'Electric vehicles, charging and electric aircraft', r'\bevs?\b|charging|new mobility'),
       ('NEW Defence Technology', 'Defence technology and unlisted defence groups', r'defen[cs]e'),
       ('NEW Space & Satellites', 'Launch, satellites and space infrastructure', r'space|satellite'),
       ('NEW Nuclear & Fusion', 'Fusion, advanced reactors and nuclear fuel', r'nuclear|fusion'),
       ('NEW Energy Storage & Climate', 'Batteries, storage, renewables and industrial decarbonisation', r'storage|renewable|grid|climate|decarbon'),
       ('NEW Brokers & Trading', 'Online brokers and trading platforms', r'broker'),
       ('NEW Crypto & Digital Assets', 'Crypto exchanges, stablecoins and digital assets', r'crypto|digital asset|stablecoin'),
       ('NEW Betting & Prediction Mkts', 'Betting, iGaming and prediction markets', r'prediction|betting|igaming'),
       ('NEW Neobanks & Payments', 'Neobanks, payments and trading apps', r'neobank|payment|trading app'),
       ('NEW Consumer Health & Wearables', 'Telehealth, wearables, longevity and sports nutrition', r'health|glp|wearable|longevity'),
       ('NEW Creator, Gaming & Media', 'Creator economy, games, streaming and sports media', r'sport|gaming|creator|entertainment'),
       ('NEW Challenger Consumer Brands', 'Venture-backed consumer brands', r'consumer brand')]
GROUP_TAB = {'brokers': 'NEW Brokers & Trading', 'crypto': 'NEW Crypto & Digital Assets', 'betting': 'NEW Betting & Prediction Mkts'}
TEST = {'a': 'Equity raised of USD 150M or more', 'b': 'Published revenue of USD 300M or more', 'c': 'Valued at or bought for USD 1B or more since Nov 2023',
        'd': 'Already pays for a top-tier sports sponsorship', 'e': 'Owned by a state fund building the brand internationally'}
FLOOR = {'a': 150, 'b': 300, 'c': 1000}
# decisions made by hand after reading the lists: name -> reason it is left out
DROP = {}
# extra F1 links the roster match does not catch by name
F1_EXTRA = dict(AN.F1_OWNERS, **{'Cognition AI': 'Cognition (Aston Martin)', 'Arctic Wolf Networks': 'Arctic Wolf', 'Jet365': 'Alpine', 'Intel': 'McLaren', 'Gucci': 'Alpine title partner from 2027'})
# same company as a brand already on the sheet under a longer or shorter name: name -> name on the sheet
SAME = {}
clean = b.clean
def tab_for(theme, key, sector):
    if key in GROUP_TAB and not re.search(r'prediction', theme, re.I): return GROUP_TAB[key]
    t = theme.lower()
    for name, _, pat in NEW:
        if t and re.search(pat, t): return name
    return sector
def hq_fix(hq):
    parts = [p.strip() for p in clean(hq).strip(',').split(',') if p.strip()]
    return (parts[0] + ', ' + parts[-1] if len(parts) >= 2 and parts[0] != parts[-1] else parts[-1] if parts else 'Not recorded')
def load():
    A, rows, L = a.load()
    PA = b.pb.assemble(); listed = {b.loose(html.unescape(c['name'])) for c in PA['U'].values()} | {b.loose(x['name']) for x in rows if x['status'] == 'listed'}
    onsheet = {}
    for x in rows:
        onsheet.setdefault(b.loose(x['name']), x['name']); onsheet.setdefault(b.loose(x['r']['brand']), x['name'])
    for d in A['f1x']: onsheet.setdefault(b.loose(d['name']), d['name'])
    out = []; left = []; drop = Counter(); seen = {}
    def leave(rec, why, show=True):
        drop[why.split(':')[0]] += 1
        if show: left.append((rec['name'], GROUPS.get(rec.get('key', ''), ''), why))
    def add(rec):
        k = b.loose(rec['name'])
        if not k: return
        if k in seen: drop['Found twice (kept once)'] += 1; return
        if rec['name'] in DROP: return leave(rec, DROP[rec['name']])
        l, _ = b.f1_link(rec['name'])
        if l or rec['name'] in F1_EXTRA or rec.get('f1'): return leave(rec, 'Current F1 partner or owner of one: ' + str(l or F1_EXTRA.get(rec['name']) or rec.get('f1')))
        if k in onsheet or rec['name'] in SAME: return leave(rec, 'Already on your sheet: ' + (SAME.get(rec['name']) or onsheet[k]), show=False)
        if k in listed or rec.get('status') == 'listed': return leave(rec, 'Listed on a stock exchange')
        if rec.get('status') in ('defunct', 'non-commercial'): return leave(rec, 'Closed or not a commercial company')
        if rec.get('status') == 'subsidiary':
            par = clean(rec.get('parent'))
            if not par or b.loose(par) in listed or b.f1_link(par)[0]: return leave(rec, 'Owned by a listed group or an F1 partner: ' + (par or 'owner not named'))
            rec['ownership'] = f'Owned by {par} (unlisted)'
        seen[k] = rec; out.append(rec)
    # 1. ranking companies, profiled from the ranking line
    R = {d['id']: d for d in json.load(open(os.path.join(H, 'newsec', 'ranking_rows.json'), encoding='utf-8'))}
    P = {}
    for f in sorted(glob.glob(os.path.join(H, 'newsec', 'out', 'out_*.jsonl'))):
        for l in open(f, encoding='utf-8'):
            try: d = json.loads(l); P[d['id']] = d
            except Exception: pass
    for rid, r in R.items():
        p = P.get(rid)
        if not p: continue
        rev = r.get('revenue_usd_bn'); f1 = clean(p.get('f1')); f1 = '' if f1.lower() in ('', 'none', 'no', 'n/a', '-') else f1
        dec = b.f1_decide(f1) if f1 else ('', '')
        add({'key': 'rank', 'name': clean(p.get('name')) or r['name'], 'hq': clean(p.get('hq')) or r.get('hq', ''), 'sector': p.get('sector') if p.get('sector') in b.FIT else 'Diversified & Other',
             'industry': clean(p.get('industry')), 'desc': clean(p.get('desc')), 'theme': '',
             'ownership': {'family': 'Family-owned', 'co-operative': 'Co-operative', 'partnership': 'Partnership'}.get(r.get('ownership'), 'Private, owner not stated in the ranking'),
             'basis': 'b', 'detail': f"Revenue about USD {rev} billion ({r.get('revenue_year')}), as published in: {r.get('ranking')}", 'usd_m': rev * 1000 if isinstance(rev, (int, float)) else None,
             'year': str(r.get('revenue_year', '')), 'source': r.get('source', ''), 'sponsorships': '', 'reach': clean(p.get('reach')).title() if clean(p.get('reach')).title() in RORD else 'Domestic',
             'reach_basis': clean(p.get('basis')).lower(), 'markets': clean(p.get('markets')), 'signals': {}, 'rationale': clean(p.get('rationale')), 'rel': p.get('rel') if p.get('rel') in (1, 2, 3, 4, 5) else 2,
             'conf': clean(p.get('conf')).lower() or 'low', 'status': clean(p.get('status')).lower(), 'parent': clean(p.get('parent')), 'changed': clean(p.get('changed')), 'stage': 'commercial',
             'f1': f1 if dec[0] == 'exclude' else '', 'f1note': f1 if f1 and dec[0] != 'exclude' else '', 'web': False})
    # 2. web research files, one per group
    for p in sorted(glob.glob(os.path.join(H, 'newsec', 'web', '*.jsonl'))):
        key = os.path.basename(p)[:-6]
        for l in open(p, encoding='utf-8'):
            if not l.strip(): continue
            try: d = json.loads(l)
            except Exception: drop['Unreadable line'] += 1; continue
            bas = clean(d.get('capacity_basis')).lower()[:1]; um = d.get('capacity_usd_m'); um = um if isinstance(um, (int, float)) else None
            rec = {'key': key, 'name': clean(d.get('name'))}
            if not rec['name']: continue
            if bas not in TEST or not clean(d.get('capacity_source')).startswith('http'): leave(rec, 'Capacity not shown from a page'); continue
            if bas in FLOOR and (um is None or um < FLOOR[bas]): leave(rec, f'Capacity figure missing or below the threshold: {clean(d.get("capacity_detail"))}'); continue
            sector = d.get('sector') if d.get('sector') in b.FIT else 'Diversified & Other'
            rec.update({'hq': clean(d.get('hq')), 'sector': sector, 'industry': clean(d.get('industry')), 'desc': clean(d.get('desc')), 'theme': clean(d.get('theme')),
                        'ownership': clean(d.get('ownership')) or 'Private, owner not stated', 'basis': bas, 'detail': clean(d.get('capacity_detail')), 'usd_m': um, 'year': clean(d.get('capacity_year')),
                        'source': clean(d.get('capacity_source')), 'sponsorships': clean(d.get('sponsorships')), 'reach': clean(d.get('reach')).title() if clean(d.get('reach')).title() in RORD else 'Domestic',
                        'reach_basis': 'web', 'markets': clean(d.get('markets')), 'signals': d.get('signals') if isinstance(d.get('signals'), dict) else {}, 'rationale': clean(d.get('rationale')),
                        'rel': d.get('rel') if d.get('rel') in (1, 2, 3, 4, 5) else 2, 'conf': clean(d.get('conf')).lower() or 'medium', 'status': 'private', 'parent': '', 'changed': '',
                        'stage': 'pre-revenue' if clean(d.get('stage')).lower().startswith('pre') else 'commercial', 'f1': '', 'f1note': '', 'web': True})
            add(rec)
    for x in out:
        S = {}
        for k in a.SIG:
            v = clean((x['signals'] or {}).get(k))
            S[k] = ('Not yet checked', '') if not v else ('Confirmed', v) if re.search(r'https?://', v) and re.search(r'202[56]', v) else ('Lead only', v)
        x['S'] = S; x['nconf'] = sum(1 for v in S.values() if v[0] == 'Confirmed')
        x['rank'] = 'High' if x['nconf'] >= 2 else 'Medium' if x['nconf'] == 1 else 'To Verify'
        x['fit'] = round(0.25 * b.FIT[x['sector']] * 10 + 0.50 * b.REL[x['rel']] + 0.25 * b.REACH[x['reach']], 1)
        x['hq'] = hq_fix(x['hq']); x['country'] = x['hq'].split(',')[-1].strip()
        x['tab'] = tab_for(x['theme'], x['key'], x['sector'])
    out.sort(key=lambda x: ({'High': 0, 'Medium': 1, 'To Verify': 2}[x['rank']], RORD[x['reach']], -x['fit'], -(x['usd_m'] or 0), x['name']))
    return out, left, drop, onsheet
COLS = a.COLS[:23] + ['On Your Sheet?', 'Category Tab (This Workbook)', 'Closest Tab on Your Existing Sheet', 'Theme', 'Ownership Type', 'Stage', 'Parameter 3: Capacity Test Passed',
                      'Capacity Evidence', 'Capacity Source', 'Sports Sponsorships Found'] + a.COLS[30:35] + ['Expanding?', 'How Found']
WIDTH = b.WIDTH[:23] + [12, 26, 26, 28, 26, 12, 34, 46, 46, 40, 36, 36, 40, 40, 11, 34, 34]
def cells(x):
    notes = []
    if x['stage'] == 'pre-revenue': notes.append('Pre-revenue: no sales yet, so any sponsorship would be paid from funding')
    if not x['web']: notes.append('Profile written from the ranking line and general knowledge, not looked up on the web: check headquarters, ownership and reach before outreach')
    if x['reach_basis'] == 'inferred': notes.append('Geographic reach inferred, not confirmed')
    if x['conf'] == 'low': notes.append('Low-confidence line: check before outreach')
    if x['changed']: notes.append(x['changed'])
    if x['f1note']: notes.append('F1 note: ' + x['f1note'])
    if x['basis'] in ('d', 'e'): notes.append('No financial figure found: capacity rests on ' + ('an existing sports sponsorship' if x['basis'] == 'd' else 'state-fund ownership'))
    sig = lambda k: x['S'][k][0] + (': ' + x['S'][k][1] if x['S'][k][1] else '')
    liq = ('Valuation or deal value: ' + x['detail']) if x['basis'] == 'c' else ('Equity raised: ' + x['detail']) if x['basis'] == 'a' else 'Not found'
    exp = x['S']['regions']
    return [x['name'], x['hq'], 'Qualifies', x['rank'], x['desc'], x['sector'] + (': ' + x['industry'] if x['industry'] else ''), 'Private (not listed)',
            x['usd_m'] * 1e6 if x['basis'] == 'b' and x['usd_m'] else 'Not found in the sources used', 'Not applicable (not listed)', 'Not found', 'Not found', liq, 'Not Disclosed', x['reach'], x['markets'],
            x['rationale'], x['year'] or 'Not stated', x['source'], b.F1_NOTE, 'Plausible Capacity', '; '.join(notes) or 'None flagged', x['fit'], x['conf'].title(),
            'No (new brand)', x['tab'], x['sector'], x['theme'], x['ownership'], 'Pre-revenue' if x['stage'] == 'pre-revenue' else 'Selling', TEST[x['basis']], x['detail'], x['source'], x['sponsorships']] + \
           [sig(k) for k in a.SIG] + [x['nconf'], ('Yes: ' + exp[1]) if exp[0] == 'Confirmed' else ('Possibly: ' + exp[1]) if exp[0] == 'Lead only' else 'Not yet checked', GROUPS.get(x['key'], x['key'])]
def tabs(L):
    """ordered list of (tab name, rows): new-sector tabs first, then the sheet's own tabs, each without Domestic brands"""
    new = [n for n, _, _ in NEW]; old = list(b.FIT)
    T = [(n, [x for x in L if x['tab'] == n and x['reach'] != 'Domestic']) for n in new + old]
    return [(n, r) for n, r in T if r]
def check(L, left, drop, onsheet):
    bad = []
    names = Counter(b.loose(x['name']) for x in L)
    bad += [('twice', x['name']) for x in L if names[b.loose(x['name'])] > 1]
    bad += [('on sheet', x['name']) for x in L if b.loose(x['name']) in onsheet]
    bad += [('F1', x['name']) for x in L if b.f1_link(x['name'])[0]]
    bad += [('no source', x['name']) for x in L if not x['source']]
    bad += [('tab', x['name']) for x in L if x['tab'] not in b.FIT and x['tab'] not in [n for n, _, _ in NEW]]
    n_tabs = sum(len(r) for _, r in tabs(L)) + sum(1 for x in L if x['reach'] == 'Domestic')
    if n_tabs != len(L): bad.append(('tab rows do not add up', n_tabs))
    return bad
def near(L, onsheet):
    """new names that begin like a name on the sheet (or the reverse): to be read by hand"""
    keys = sorted(onsheet); out = []
    for x in L:
        k = b.loose(x['name'])
        if len(k) < 4: continue
        hit = [onsheet[s] for s in keys if s != k and ((s.startswith(k) and len(s) <= len(k) + 14) or (len(s) >= 5 and k.startswith(s)))][:3]
        if hit: out.append((x['name'], x['tab'], hit))
    return out
def write(L, left, drop, path):
    import write_xlsx as wx
    from openpyxl import Workbook
    from openpyxl.cell import WriteOnlyCell
    from openpyxl.utils import get_column_letter
    wb = Workbook(write_only=True)
    n = len(L); rc = Counter(x['reach'] for x in L); bc = Counter(x['basis'] for x in L); rk = Counter(x['rank'] for x in L); T = tabs(L)
    tc = Counter(x['tab'] for x in L); ctry = Counter(x['country'] for x in L); newn = [nm for nm, _, _ in NEW]
    n_new = sum(tc[t] for t in newn); desk = sum(1 for x in L if not x['web'])
    S = [('New brands for your sheet, filed by category (16 Nov 2026)',),
         [f"{n:,} companies that are not on your 48-tab sheet. Each is unlisted, is not a current F1 partner or the owner of one, and passes the capacity test with a source. Headquarters in {len(ctry)} countries."],
         [f"{n_new:,} sit on {sum(1 for t in newn if tc[t])} new tabs for sectors your sheet has no tab for (tab names start with NEW). {n - n_new:,} sit under {sum(1 for t in b.FIT if tc[t])} of your existing tab names."],
         ['Each brand is on one tab only. Domestic brands are on the Domestic tab, not on the category tabs; the All New Brands tab holds every brand.'], [],
         ('New sector tabs (all brands, including Domestic)',)] + [[f"{t[4:]}: {tc[t]} - {what}"] for t, what, _ in NEW if tc[t]] + [[],
         ('Your existing tabs that gain brands (all brands, including Domestic)',)] + [[f"{t}: {tc[t]}"] for t in b.FIT if tc[t]] + [[],
         ('How each company passes parameter 3 (can it pay)',)] + [[f"{TEST[k]}: {bc[k]}"] for k in 'abcde' if bc[k]] + [[],
         ('Reach',), [f"Global {rc['Global']}; International {rc['International']}; Regional {rc['Regional']}; Domestic {rc['Domestic']}."], [],
         ('Headquarters',), ['; '.join(f'{c} {v}' for c, v in ctry.most_common(25)) + ('; others ' + str(sum(v for c, v in ctry.most_common()[25:])) if len(ctry) > 25 else '') + '.'], [],
         ('Priority under the parameters',),
         [f"High {rk['High']}; Medium {rk['Medium']}; To Verify {rk['To Verify']}. Most are To Verify because the four reasons to buy (parameter 4) have not been looked up for these companies yet. A reason is shown only where the research came across it."], [],
         ('Found but left out',)] + [[f"{v} - {k}"] for k, v in drop.most_common()] + [[],
         ('How the list was made',),
         [f"{n - desk:,} companies come from web research on 16 Nov 2026, one group at a time across all regions, and from the public unicorn list with each company checked. Each carries the fact that makes it qualify and the page it comes from."],
         [f"{desk:,} companies come from public revenue rankings of unlisted companies. The revenue is the ranking figure. Their headquarters city, description and reach were written from the ranking line and general knowledge, not looked up, and each is flagged in Verification Notes."],
         ['This is a first pass, not the full universe. Each group was researched once. Before a company was researched it was checked against your sheet, so brands you already have were skipped.']]
    wx.text_sheet(wb, 'Summary', S, widths=(170,))
    data = {id(x): cells(x) for x in L}
    wx.sheet(wb, 'All New Brands', COLS, WIDTH, [data[id(x)] for x in L])
    for name, rows in T: wx.sheet(wb, name, COLS, WIDTH, [data[id(x)] for x in rows])
    wx.sheet(wb, 'Domestic', COLS, WIDTH, [data[id(x)] for x in L if x['reach'] == 'Domestic'])
    ws = wb.create_sheet('Left Out')
    for j, w in enumerate((40, 48, 90), 1): ws.column_dimensions[get_column_letter(j)].width = w
    hdr = []
    for c in ['Company', 'How Found', 'Why it is not on the list']:
        x = WriteOnlyCell(ws, value=c); x.font = wx.HFONT; x.fill = wx.HEAD; x.alignment = wx.HALIGN; hdr.append(x)
    ws.append(hdr)
    for row in sorted(left, key=lambda r: (r[2].split(':')[0], r[0])): ws.append(list(row))
    K = [('What this workbook is', 'New brands only: none of them is on your 48-tab sheet. Same parameter set as the all-sector workbook.'),
         ('Tabs', 'Tabs starting with NEW are sectors your sheet has no tab for. The other category tabs carry your own tab names, so the rows can be pasted under the matching tab. Each brand is on one tab.'),
         ('Category Tab / Closest Tab on Your Existing Sheet', 'The tab the brand is filed under here, and the tab on your current sheet it would otherwise belong to.'),
         ('Parameter 3: capacity test passed', 'One of: equity raised of USD 150M or more in total (no limit on the date of the last round); published revenue of USD 300M or more; valued at or bought for USD 1B or more since Nov 2023; already pays for a top-tier sports sponsorship; owned by a state fund building the brand internationally. Capacity Evidence and Capacity Source give the fact and the page.'),
         ('Annual Revenue (USD)', 'Filled only where the test passed is published revenue; the figure is the one on the source page. Otherwise "Not found in the sources used".'),
         ('Parameter 4 columns', 'Confirmed = the research found it, with date and page. Lead only = found without a date or page. Not yet checked = not looked up. A full check takes two web searches per company.'),
         ('Outreach Priority', 'High = two or more confirmed reasons to buy; Medium = one; To Verify = none confirmed yet.'),
         ('Stage', 'Pre-revenue companies are kept and labelled.'),
         ('Geographic Reach', 'Global, International, Regional or Domestic. Domestic brands are on the Domestic tab.'),
         ('Fit Score (0-100)', 'Sector fit (25%), relevance to F1 (50%) and reach (25%). Orders companies inside the same priority.'),
         ('Left Out tab', 'Companies the research found that are current F1 partners or their owners, listed, owned by a listed group, closed, or whose capacity could not be shown from a page.')]
    wx.text_sheet(wb, 'Key', K)
    wb.save(path)
if __name__ == '__main__':
    L, left, drop, onsheet = load()
    print(len(L), 'new brands | by source', dict(Counter(x['key'] for x in L)))
    print('left out', dict(drop))
    print('reach', dict(Counter(x['reach'] for x in L)), '| basis', dict(Counter(x['basis'] for x in L)), '| rank', dict(Counter(x['rank'] for x in L)), '| countries', len(Counter(x['country'] for x in L)))
    print('tabs', [(n, len(r)) for n, r in tabs(L)], '| domestic', sum(1 for x in L if x['reach'] == 'Domestic'))
    bad = check(L, left, drop, onsheet); print('CHECK', 'ok' if not bad else bad[:20])
    if len(sys.argv) > 1 and sys.argv[1] == 'near':
        for r in near(L, onsheet): print(r)
    if len(sys.argv) > 1 and sys.argv[1] == 'xlsx':
        if bad: sys.exit('not written: checks failed')
        write(L, left, drop, OUT); print(OUT)
