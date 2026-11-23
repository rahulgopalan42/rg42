"""All-sector list of companies that are not listed on a stock exchange, under the parameter set agreed on 16 Nov 2026:
scope = operating, not listed; remove F1 partners, funds, single-project vehicles, closed companies and companies owned by a listed group;
capacity = equity raised of USD 150M+ (any date) or another proof; reason to buy now = raised in the past 12 months, IPO preparation,
opening in new regions, marketing activity (each confirmed from a source); reach labelled, expansion flagged.
Usage: allsector.py [check|select|xlsx]"""
import glob, html, json, os, re, sys
from collections import Counter, defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b, expand_screen as e
SUBS = True      # rule change of 18 Nov 2026: subsidiaries are in scope and every row names its parent company
OUT = os.path.join(b.R, 'reports', 'F1-NON-LISTED-PROSPECTS-ALL-SECTORS-v3-2026-11-23.xlsx' if SUBS and os.path.exists(os.path.join(H, 'newsec', 'refresh', 'decisions.json')) else 'F1-NON-LISTED-PROSPECTS-ALL-SECTORS-v2-2026-11-18.xlsx' if SUBS else 'F1-NON-LISTED-PROSPECTS-ALL-SECTORS-2026-11-16.xlsx')
BAR = 150e6; RORD = {'Global': 0, 'International': 1, 'Regional': 2, 'Domestic': 3}
IPO = re.compile(r'\bIPO\b|initial public offering|plans? to (list|go public)|preparing to (list|go public)|stock market listing|public listing|filed (confidentially )?(for|to) (an? )?(IPO|listing|list|go public)', re.I)
NEG = re.compile(r'\bno (verified|known|confirmed|international)|not confirmed|unverified|unconfirmed|presumed|not detailed|not known', re.I)
EXP = re.compile(r'expanding|expansion (into|in|across|to)|launch(ing|ed|es)? in|entering|entered|plans? to (enter|launch|open|expand)|opening (in|offices)|rolling out|new (office|market|hub)s? in', re.I)
# hand corrections to the web signal check (16 Nov 2026), with the reason
SIG_FIX = {'09-0055': {'ipo': 'none'},        # Beast Industries: only a remark about a possible future IPO, no filing or banks
           '45-0008': {'regions': 'lead'},    # Soho House Tokyo: the only source is a weak aggregator page
           '16-0034': {'marketing': 'lead'},  # FNZ: the appointment is a communications chief, not a marketing chief
           '47-0014': {'ipo': 'lead'},         # upGrad: listing-plan article could not be dated
           '06-0009': {'regions': 'lead'}}       # Bupa Romania: the page does not say it is a new market
KEEP = {'08-0035': 'Owned by Blackstone funds since 2021 (an investment firm)'}      # QTS: investment-firm ownership, not a listed operating group
DROP = {'32-0060': 'Shares trade publicly over the counter in the United States (LKNCY)'}   # Luckin Coffee
def sentences(t): return [s.strip() for s in re.split(r'(?<=[.;])\s+', t or '') if s.strip()]
def par_keys(par):
    """names to test against the listed universe: the parent as written, and any names in brackets after it"""
    base = re.sub(r'\s*\([^)]*\)', '', par); ins = re.findall(r'\(([^)]*)\)', par)
    out = [base] + [q for i in ins for q in re.split(r',|;|/| and | via | with ', i)]
    return [k for k in (b.loose(re.sub(r'(?i)^(owned by|majority owner|majority|part of|via|a unit of|subsidiary of)\s+', '', o.strip())) for o in out) if k]
# F1 partners and team owners added to the roster in Nov 2026 that the name matcher does not hold: used to flag their subsidiaries
_P = ['Adobe', 'SharkNinja', 'Logitech', 'Wynn Resorts', 'Caesars Entertainment', 'Bradesco', 'Stratasys', 'AbbVie', 'Arctic Wolf', 'Revolut', 'BWT']
F1_PARENT_EXTRA = [(re.compile(r'\b' + re.escape(n) + r'\b'), n + ' is a current F1 partner') for n in _P] + [
    (re.compile(r'\bIntel\b'), 'Intel is a current F1 partner'), (re.compile(r'\bRakuten\b'), 'Rakuten becomes a Ferrari partner from 2027'), (re.compile(r'(?i)mercado ?libre'), 'Mercado Libre is a current F1 partner'),
    (re.compile(r'(?i)daimler truck'), 'Daimler Truck (Mercedes-Benz Trucks) is a current F1 partner'), (re.compile(r'(?i)\bhonda\b'), 'Honda supplies the Aston Martin power unit'),
    (re.compile(r'(?i)mercedes-benz group'), 'Mercedes-Benz owns an F1 team'), (re.compile(r'(?i)^ferrari\b'), 'Ferrari is an F1 team')]
def f1_txt(note):
    """the F1 link of a subsidiary's group, in plain words"""
    if not note.startswith(b.F1_SUB): return ''
    t = note[len(b.F1_SUB):].rstrip('.')
    if '(owner:' not in t: return '. F1 link: ' + t
    t = re.sub(r'\s*\(owner: .*\)$', '', t).replace(' - parent / owner', '')
    m = re.match(r'^([^()]+?) - (.+)$', t)
    return '. F1 partner in the group: ' + (f'{m.group(1)} ({m.group(2)})' if m else t)
def parent_txt(x):
    """the Parent Company column"""
    st = x['status']; par = b.clean(x['parent'])
    if st == 'subsidiary':
        if not par: return 'Parent not named in the profile'
        t = par + (' (listed)' if x.get('par_listed') and 'listed' not in par.lower() else '')
        f = f1_txt(x['f1note'])
        if not f and x.get('now'):
            l = b.f1_link(re.sub(r'\s*\(.*$', '', par))[0]
            f = ('. F1 partner in the group: ' + re.sub(r'^([^()]+?) - (.+)$', r'\1 (\2)', l.replace(' - parent / owner', ''))) if l else ''
        if not f:
            e_ = next((t for pat, t in F1_PARENT_EXTRA if pat.search(par)), '')
            f = '. F1 link in the group: ' + e_ if e_ else ''
        return (t.rstrip('.') + f) if f else t
    if st == 'private': return ('None: owned by an investment firm' + (f' ({par})' if par else '')) if x.get('pe') else 'None (independent company)'
    if st == 'state-owned': return 'None: state-owned' + (f' ({par})' if par else '')
    if st == 'listed': return par or 'None (listed itself)'
    return par or 'Not confirmed'
REFRESH = '23 Nov 2026'      # events since 1 Nov 2026 applied to the brands on the sheet (newsec/refresh/decisions.json, key "sheet"); '' = the 18 Nov build
CHANGES = []
def load():
    b.SUBS_IN = SUBS
    A, rows = e.load()
    rp = os.path.join(H, 'newsec', 'refresh', 'decisions.json')
    RD = json.load(open(rp, encoding='utf-8')).get('sheet', {}) if REFRESH and os.path.exists(rp) else {}; CHANGES.clear()
    PA = b.pb.assemble(); listed = {b.loose(html.unescape(c['name'])) for c in PA['U'].values()} | {b.loose(x['name']) for x in rows if x['status'] == 'listed'}
    W = {}
    for f in sorted(glob.glob(os.path.join(H, 'signals', 'out_*.jsonl'))):
        for l in open(f, encoding='utf-8'):
            try: d = json.loads(l); W[d['id']] = d
            except Exception: pass
    out = []
    npath = os.path.join(H, 'newsec', 'now_owned.json'); NOW = json.load(open(npath, encoding='utf-8')) if SUBS and os.path.exists(npath) else {}
    for x in rows:
        nw = NOW.get(x['r']['id'])
        if nw and x['status'] == 'listed':          # listed on the sheet, since bought (subsidiaries research of 18 Nov 2026): now a subsidiary, or privately held under an investment firm
            x['was'] = 'listed'; x['status'] = 'subsidiary' if nw['parent'] else 'private'; x['parent'] = nw['parent'] or nw['pe']; x['now'] = nw
        acts = RD.get(x['name'], []); x['chg'] = []
        for d in acts:                                   # refresh of 23 Nov 2026: a new parent is set before the ownership text is written
            if d.get('action') == 'parent' and x['status'] not in ('listed', 'non-commercial', 'defunct'):
                x['status'] = 'subsidiary'; x['parent'] = b.clean(d.get('parent'))
        st = x['status']; par = b.clean(x['parent']); pk = b.loose(re.sub(r'\s*\([^)]*\)', '', par)) if par else ''
        if st in ('listed', 'non-commercial', 'defunct') or x['stage'] not in ('commercial', 'pre-revenue'): continue
        gone = next((d for d in acts if d.get('action') == 'drop'), None)
        if gone:
            x['dropped'] = b.clean(gone.get('why')); x['dropped23'] = True
            CHANGES.append([x['name'], 'Removed', b.clean(gone.get('why')), b.clean(gone.get('date')), b.clean(gone.get('source')), 'Your sheet: ' + x['r'].get('tab', x['sector'])]); continue
        x['par_listed'] = bool(par) and any(k in listed for k in par_keys(par))
        if st == 'subsidiary' and not SUBS and (not par or pk in listed): continue      # old rule: owned by a listed group (or owner not named) was out of scope
        w = W.get(x['r']['id']); rid = x['r']['id']
        if rid in DROP: x['dropped'] = DROP[rid]; continue
        if w and w.get('listed_or_acquired') and rid not in KEEP: x['dropped'] = w['listed_or_acquired']; continue                                              # the web check found it is now listed or owned by a listed group
        pe = any('(investment firm)' in t for _, t in x['notes']) or rid in KEEP or bool(x.get('now') and x['now']['pe'])
        x['pe'] = pe
        x['own'] = ('Private, owned by an investment firm' if pe else 'Private') if st == 'private' else 'State-owned' if st == 'state-owned' else \
                   ((f"Subsidiary of {par}" + (' (a listed company)' if x['par_listed'] else '')) if par else 'Subsidiary: parent not named') if st == 'subsidiary' else 'Ownership not confirmed'
        x['core'] = st in ('private', 'state-owned') or (SUBS and st == 'subsidiary' and bool(par))
        x['cap_pass'] = x['amt'] >= BAR or bool(x.get('now'))
        x['basis'] = (f"Total funding raised {x['fund_txt']} (Crunchbase, recorded Oct-Nov 2026; includes debt where Crunchbase counts it)" if x['cap_pass'] else
                      'Not established: recorded funding is below USD 150M or unreadable' + ('' if not x['fund_txt'] else f" ({x['fund_txt']})"))
        if x.get('now'): x['basis'] = 'Bought for USD 1B or more since Nov 2023: ' + x['now']['detail'] + ' (' + x['now']['source'] + ')'
        last = b.pb.dt(x['date'].isoformat()) if x['date'] else ''
        S = {}
        S['raise'] = ('Confirmed', f'Last funding round {last} (Crunchbase record)') if x['age'] is not None and x['age'] <= 12 else ('Not met', f'Last funding round {last} (Crunchbase record)') if last else ('Not yet checked', '')
        ch = b.clean(x['e'].get('changed')); mk = b.clean(x['e'].get('markets'))
        lead_ipo = next((s for s in sentences(ch) if IPO.search(s) and not re.search(r'postponed|shelved|withdr|cancel|abandon', s, re.I)), '')
        lead_exp = next((s for s in sentences(mk) if EXP.search(s) and not NEG.search(s)), '')
        S['ipo'] = ('Lead only', lead_ipo + ' (profile note, not confirmed)') if lead_ipo else ('Not yet checked', '')
        S['regions'] = ('Lead only', lead_exp + ' (profile note, not confirmed)') if lead_exp else ('Not yet checked', '')
        S['marketing'] = ('Not yet checked', '')
        if w:
            for k in ('ipo', 'regions', 'marketing'):
                v = w.get(k) or {}
                fx = SIG_FIX.get(rid, {}).get(k)
                if fx == 'none': S[k] = ('Checked: nothing found', 'Web search on 16 Nov 2026'); continue
                if fx == 'lead': S[k] = ('Lead only', f"{b.clean(v.get('detail'))} (weak or undated source: {b.clean(v.get('source'))})"); continue
                if v.get('status') == 'confirmed': S[k] = ('Confirmed', f"{b.clean(v.get('detail'))} ({b.clean(v.get('date')) or 'date not given'}; {b.clean(v.get('source'))})")
                else: S[k] = ('Checked: nothing found', 'Web search on 16 Nov 2026')
        for d in acts:
            why = b.clean(d.get('why')); when = b.clean(d.get('date')); src = b.clean(d.get('source'))
            if d.get('action') == 'signal':
                for k, v in (d.get('signals') or {}).items():
                    if d.get('lead') and S.get(k, ('',))[0] == 'Confirmed': continue        # a report of talks does not replace a confirmed signal
                    S[k] = ('Lead only' if d.get('lead') else 'Confirmed', b.clean(v))
            if d.get('action') in ('signal', 'parent', 'note', 'sponsorship'):
                x['chg'].append(why + (f' ({when})' if when and when not in why else '')); CHANGES.append([x['name'], 'Updated', why, when, src, 'Your sheet: ' + x['r'].get('tab', x['sector'])])
        x['chgtxt'] = ('Updated on 23 Nov 2026: ' + '; '.join(x['chg'])) if x['chg'] else 'No change found'
        x['S'] = S; x['nconf'] = sum(1 for v in S.values() if v[0] == 'Confirmed'); x['webchecked'] = bool(w)
        x['rank'] = ('High' if x['nconf'] >= 2 else 'Medium' if x['nconf'] == 1 else 'To Verify') if x['cap_pass'] and x['core'] else 'To Verify'
        x['expanding'] = 'Yes (confirmed)' if S['regions'][0] == 'Confirmed' else 'Possibly (lead only)' if S['regions'][0] == 'Lead only' else ''
        out.append(x)
    out.sort(key=lambda x: ({'High': 0, 'Medium': 1, 'To Verify': 2}[x['rank']], -x['nconf'], RORD[x['reach']], -x['score'], -x['amt']))
    return A, rows, out
EXTRA = ['Theme', 'Ownership Type', 'Stage', 'Parameter 3: Capacity Basis', 'Parameter 4a: Raised Money in Past 12 Months', 'Parameter 4b: Preparing an IPO', 'Parameter 4c: Opening in New Regions',
         'Parameter 4d: Marketing Activity', 'Confirmed Reasons to Buy (0-4)', 'Expanding?']
COLS = [c if c != 'Priority Score (0-100)' else 'Fit Score (0-100)' for c in b.COLS] + EXTRA
WIDTH = b.WIDTH + [28, 24, 12, 44, 34, 34, 40, 40, 11, 16]
SIG = ('raise', 'ipo', 'regions', 'marketing')
COLS2 = COLS[:28] + ['Parent Company'] + COLS[28:] + (['Change Since the 18 Nov List'] if REFRESH else []); WIDTH2 = WIDTH[:28] + [36] + WIDTH[28:] + ([48] if REFRESH else [])
def sig(x, k): return x['S'][k][0] + (': ' + x['S'][k][1] if x['S'][k][1] else '')
def fit(x): return round(0.25 * b.FIT[x['sector']] * 10 + 0.50 * b.REL[x['rel']] + 0.25 * b.REACH[x['reach']], 1)
def cells(x):
    c = b.cells(x)
    notes = [t for _, t in x['notes'] if not t.startswith('Investment category not assigned')]
    if x['stage'] == 'pre-revenue': notes.insert(0, 'Pre-revenue: no sales yet, so any sponsorship would be paid from funding')
    if x.get('now'): notes.insert(0, 'Was listed when the sheet was profiled and has since been bought: the financial figures shown are its last as a listed company'); c[6] = 'Not listed: owned by ' + x['parent'] + ' (was listed)'; c[8] = 'Not applicable (no longer listed)'
    if not x['core']: notes.insert(0, 'Ownership to confirm before outreach: ' + x['own'])
    if x['status'] == 'subsidiary' and x['cap_pass']: notes.insert(0, 'Subsidiary: the funding shown is the company\'s own record and may date from before its parent bought it')
    c[2] = 'Qualifies' if x['cap_pass'] else 'To Verify'; c[3] = x['rank']; c[19] = 'Plausible Capacity' if x['cap_pass'] else 'Not Established'
    c[20] = '; '.join(notes) or 'None flagged'; c[21] = fit(x)
    return c + [x['theme'], x['own'], 'Pre-revenue' if x['stage'] == 'pre-revenue' else 'Selling', x['basis']] + [sig(x, k) for k in SIG] + [x['nconf'], x['expanding'], parent_txt(x)]
PAT = 28      # the Parent Company column sits after Ownership Type in the workbook
CHGCOL = 'Change Since the 18 Nov List'
def cells2(x): c = cells(x); return c[:PAT] + [c[-1]] + c[PAT:-1] + ([x.get('chgtxt', 'No change found')] if REFRESH else [])
def reason_out(x, listed):
    st = x['status']; par = b.clean(x['parent']); pk = b.loose(re.sub(r'\s*\([^)]*\)', '', par)) if par else ''
    if x.get('dropped23'): return 'Changed since the 18 Nov list: ' + x['dropped']
    if x.get('dropped'): return 'Now listed or owned by a listed group (web check, 16 Nov 2026): ' + x['dropped']
    if st == 'listed': return 'Listed on a stock exchange' + (f" ({x['ticker_txt']})" if x['ticker_txt'] else '')
    if st == 'defunct': return 'Closed or absorbed'
    if st == 'non-commercial' or x['stage'] == 'non-commercial': return 'Public body or non-profit'
    if x['stage'] == 'fund': return 'Investment fund or holding vehicle'
    if x['stage'] == 'project': return 'Single-project vehicle'
    if st == 'subsidiary': return f'Owned by a listed group ({par})' if par else 'Owned by another company (owner not named)'
    return ''
def all_rows(A, rows, L):
    PA = b.pb.assemble(); listed = {b.loose(html.unescape(c['name'])) for c in PA['U'].values()} | {b.loose(x['name']) for x in rows if x['status'] == 'listed'}
    inscope = {id(x) for x in L}; out = []; order = {r['id']: i for i, r in enumerate(A['B'])}
    for x in rows:
        r = x['r']
        if id(x) in inscope:
            out.append((order[r['id']], [r['brand'], x['name'], r['sector'], x['hq'], x['own'], parent_txt(x), 'Yes' if x['core'] else 'Yes, if ownership is confirmed', '', 'Yes' if x['cap_pass'] else 'Not shown', x['basis']] +
                        [sig(x, k) for k in SIG] + [x['nconf'], x['reach'], x['expanding'], x['rank']]))
        else:
            out.append((order[r['id']], [r['brand'], x['name'], r['sector'], x['hq'], x['status'].capitalize(), parent_txt(x), 'No', reason_out(x, listed)] + ['Not assessed (out of scope)'] * 2 + [''] * 4 + ['', x['reach'], '', 'Out of scope']))
    for d in A['f1x']:
        r = d['r']; out.append((order[r['id']], [r['brand'], d['name'], r['sector'], '', 'Current F1 partner', d.get('parent') or '', 'No', ('Current F1 partner, or the owner of one: ' if SUBS else 'Current F1 partner, or owned by one: ') + d['why']] + ['Not assessed (out of scope)'] * 2 + [''] * 4 + ['', '', '', 'Out of scope']))
    return [v for _, v in sorted(out, key=lambda t: t[0])]
ALLCOLS = ['Brand (as on your sheet)', 'Company Name', 'Tab in Your Sheet', 'Headquarters', 'Ownership / Status', 'Parent Company', 'Parameters 1-2: In Scope?', 'Why Not (if out of scope)', 'Parameter 3: Can It Pay?', 'Capacity Basis',
           'Parameter 4a: Raised Money in Past 12 Months', 'Parameter 4b: Preparing an IPO', 'Parameter 4c: Opening in New Regions', 'Parameter 4d: Marketing Activity', 'Confirmed Reasons (0-4)',
           'Parameter 5: Reach', 'Expanding?', 'Result']
def write(A, rows, L, path):
    import write_xlsx as wx, allsector_notes as N
    from openpyxl import Workbook
    from openpyxl.cell import WriteOnlyCell
    from openpyxl.utils import get_column_letter
    wb = Workbook(write_only=True)
    def grid(title, cols, widths, data, freeze='B2', height=None):
        ws = wb.create_sheet(title[:31]); ws.freeze_panes = freeze
        for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
        ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{max(len(data) + 1, 2)}'; ws.row_dimensions[1].height = 44; hdr = []
        for c in cols:
            x = WriteOnlyCell(ws, value=c); x.font = wx.HFONT; x.fill = wx.HEAD; x.alignment = wx.HALIGN; hdr.append(x)
        ws.append(hdr)
        for i, r in enumerate(data, 2):
            if height: ws.row_dimensions[i].height = height
            out = []
            for v in r:
                x = WriteOnlyCell(ws, value=v); x.alignment = wx.WRAP
                if isinstance(v, str) and v in ('High', 'Medium', 'To Verify'): x.fill = wx.FILLS[v]
                out.append(x)
            ws.append(out)
    core = [x for x in L if x['core'] and x['cap_pass']]; other = [x for x in L if not (x['core'] and x['cap_pass'])]
    data = {id(x): cells2(x) for x in L}; COLS = COLS2; WIDTH = WIDTH2
    wx.text_sheet(wb, 'Summary', N.summary(A, rows, L, core, other), widths=(150,))
    if REFRESH and CHANGES:
        order = {'Removed': 0, 'Updated': 1}
        grid('Changes Since 18 Nov', ['Company', 'Change', 'What Happened', 'Date', 'Source', 'Where It Sits'], (34, 12, 90, 16, 60, 40), sorted(CHANGES, key=lambda r: (order.get(r[1], 9), r[0].lower())), height=30)
    grid('All Brands - Parameters', ALLCOLS, (30, 30, 26, 24, 26, 34, 14, 40, 12, 44, 30, 30, 34, 34, 10, 13, 14, 12), all_rows(A, rows, L))
    wx.sheet(wb, 'Prospects - All Sectors', COLS, WIDTH, [data[id(x)] for x in core])
    wx.sheet(wb, 'High and Medium', COLS, WIDTH, [data[id(x)] for x in core if x['rank'] in ('High', 'Medium') and x['reach'] != 'Domestic'])
    tabs = []
    for r in A['B']:
        if r['sector'] not in tabs: tabs.append(r['sector'])
    for t in tabs: wx.sheet(wb, re.sub(r'[\\/*?:\[\]]', ' ', t), COLS, WIDTH, [data[id(x)] for x in core if x['r']['sector'] == t and x['reach'] != 'Domestic'])
    wx.sheet(wb, 'Domestic', COLS, WIDTH, [data[id(x)] for x in core if x['reach'] == 'Domestic'])
    wx.sheet(wb, 'Ownership To Confirm', COLS, WIDTH, [data[id(x)] for x in other])
    B = N.beyond(rows, A)
    grid('Beyond Your Sheet', N.BCOLS, (30, 24, 26, 48, 18, 14, 10, 34, 46, 22, 30), B, height=32)
    grid('Sectors To Add', N.SCOLS, (34, 40, 50, 60, 50), N.sectors(rows, B), freeze='B2', height=75)
    wx.text_sheet(wb, 'Key', N.KEY)
    wb.save(path)
    return tabs, core, other, B
if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    A, rows, L = load(); core = [x for x in L if x['core']]
    print('in scope', len(L), '| core (private or state-owned)', len(core), '| ownership to confirm', len(L) - len(core), dict(Counter(x['own'].split(' ')[0] for x in L if not x['core'])))
    print('core: capacity passes', sum(x['cap_pass'] for x in core), '| pre-revenue', sum(x['stage'] == 'pre-revenue' for x in core), '| rank', dict(Counter(x['rank'] for x in core)), '| reach', dict(Counter(x['reach'] for x in core)))
    print('signals (core):', {k: dict(Counter(x['S'][k][0] for x in core)) for k in ('raise', 'ipo', 'regions', 'marketing')})
    if cmd == 'select':
        C = [x for x in core if x['cap_pass'] and x['S']['raise'][0] == 'Confirmed' and x['reach'] in ('Global', 'International') and x['stage'] == 'commercial' and not x['f1note'] and not x['webchecked']]
        C.sort(key=lambda x: (-x['score'], -x['amt'])); pick = []; seen = Counter()
        for x in C:
            if seen[x['sector']] < 2: pick.append(x); seen[x['sector']] += 1
        for x in C:
            if len(pick) >= int(sys.argv[2]): break
            if x not in pick: pick.append(x)
        pick = pick[:int(sys.argv[2])]; os.makedirs(os.path.join(H, 'signals_in'), exist_ok=True); os.makedirs(os.path.join(H, 'signals'), exist_ok=True)
        per = int(sys.argv[3]); first = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        for i in range(0, len(pick), per):
            with open(os.path.join(H, 'signals_in', f'in_{first + i // per:03d}.jsonl'), 'w', encoding='utf-8') as fh:
                for x in pick[i:i + per]:
                    fh.write(json.dumps({'id': x['r']['id'], 'name': x['name'], 'hq': x['hq'], 'sector': x['sector'], 'what_it_does': b.clean(x['e'].get('desc')), 'last_funding_round': b.pb.dt(x['date'].isoformat())}, ensure_ascii=False) + '\n')
        print('candidates', len(C), '| picked', len(pick), '| sectors covered', len({x['sector'] for x in pick}), '| files', (len(pick) + per - 1) // per)
        print('; '.join(x['name'] for x in pick[:40]))
    if cmd == 'xlsx':
        tabs, core, other, B = write(A, rows, L, OUT); print(OUT)
        from openpyxl import load_workbook
        wb = load_workbook(OUT, read_only=True); n = lambda t: sum(1 for _ in wb[t].iter_rows(values_only=True)) - 1
        allb = n('All Brands - Parameters'); pros = n('Prospects - All Sectors'); dom = n('Domestic'); sec = sum(n(t[:31]) for t in tabs); own = n('Ownership To Confirm')
        print('CHECK every brand of the sheet accounted for:', allb, '== 18851', allb == len(A['B']))
        print('CHECK sector tabs + Domestic = Prospects:', sec, '+', dom, '=', pros, sec + dom == pros)
        print('CHECK prospects + ownership-to-confirm = in scope:', pros, '+', own, '=', len(L), pros + own == len(L))
        print('tabs', len(wb.sheetnames), '| High', sum(x['rank'] == 'High' for x in core), '| Medium', sum(x['rank'] == 'Medium' for x in core), '| To Verify', sum(x['rank'] == 'To Verify' for x in core), '| beyond-sheet rows', len(B))
