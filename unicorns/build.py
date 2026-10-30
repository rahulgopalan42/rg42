"""Build reports/F1-PRIVATE-UNICORNS-1B-VALUATION-200M-FUNDING-2026-10-30.xlsx from research-agent rows
(unicorns/discover_out/*.json, unicorns/verify_out/*.json; 37-field rows, see unicorns/brief.md).
Rahul's rules (30 Oct 2026): private, valuation >= USD 1B, total equity funding >= USD 200M, worldwide, any sector.
Rows already on his sheets or on the 30 Oct new-brands list are kept and flagged, plus a tab without them."""
import glob, json, os, re, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, os.path.join(R, 'brands200')); from match import present, phrase_present, regdom, strict, loose
sys.path.insert(0, os.path.join(R, 'parents')); from sectors_v3 import NAMES
OUT = os.path.join(R, 'reports', 'F1-PRIVATE-UNICORNS-1B-VALUATION-200M-FUNDING-2026-10-30.xlsx')
F = ['brand', 'legal_name', 'parent', 'hq_country', 'hq_city', 'domain', 'sector', 'what', 'valuation_bn', 'valuation_date', 'valuation_basis',
     'funding_m', 'latest_round', 'status', 'investors', 'revenue_m', 'why', 'a', 's', 'l', 'n', 'f1_status', 'f1_deal', 'sport_deals', 'headcount',
     'fund_recency', 'brand_hires', 'competitor_f1', 'motorsport', 'expansion', 'race_footprint', 'founder', 'evidence', 'ceo', 'conf', 'source_url', 'note']
NEWFILES = ('u19', 'u20', 'u21')
s = lambda x: '' if x is None or (isinstance(x, float) and x != x) else str(x).strip()
rows, bad = [], 0
files = sorted(glob.glob(f'{H}/discover_out/*.json')) + sorted(glob.glob(f'{H}/ref/enrich_out_*.json')) + sorted(glob.glob(f'{H}/verify_out/*.json'))
for f in files:
    code = os.path.basename(f)[:-5]
    try: data = json.load(open(f))
    except Exception as e: print('bad file', f, e); continue
    for r in data:
        if isinstance(r, dict) and set(F) <= set(r): r = [r[k] for k in F] + [r.get('key', r.get('cbid', '')), r.get('check', '')][:{'discover_out': 0, 'enrich_out': 1}.get(next((x for x in ('discover_out', 'enrich_out') if x in f), ''), 2)]
        if isinstance(r, list) and len(r) == 37 and 'discover_out' in f: rows.append(dict(zip(F, r), file=code, verified=False, check='', vkey='', cbid=''))
        elif isinstance(r, list) and len(r) == 38 and 'enrich_out' in f: rows.append(dict(zip(F, r[:37]), file='CB Insights list', verified=False, check='', vkey=s(r[37])[2:] if s(r[37]).startswith('b:') else '', cbid='' if s(r[37]).startswith('b:') else s(r[37])))
        elif isinstance(r, list) and len(r) == 39 and 'verify_out' in f: rows.append(dict(zip(F, r[:37]), file='web check', verified=True, vkey=s(r[37]), check=s(r[38]).lower(), cbid=''))
        else: bad += 1
df = pd.DataFrame(rows); print('rows', len(df), 'malformed', bad, 'files', len(files))
s = lambda x: '' if x is None or (isinstance(x, float) and x != x) else str(x).strip()
num = lambda x: pd.to_numeric(x, errors='coerce')
for c in ('valuation_bn', 'funding_m', 'revenue_m'): df[c] = num(df[c])
SIG = ('a', 's', 'l', 'n', 'headcount', 'fund_recency', 'brand_hires', 'competitor_f1', 'motorsport', 'expansion', 'race_footprint', 'founder')
for c in SIG: df[c] = num(df[c]).fillna(0).clip(0, 4).astype(int)
df['sector'] = num(df['sector']).fillna(48).clip(1, 48).astype(int)
for c in set(F) - set(SIG) - {'valuation_bn', 'funding_m', 'revenue_m', 'sector'}: df[c] = df[c].map(s)
df['status'] = df['status'].str.lower().replace({'below 1b': 'below_1b', 'listed': 'public', 'ipo': 'public'})
df['conf'] = df['conf'].str.upper().str[:1]
df = df[df['brand'] != ''].copy()
# unit slips: a valuation typed in millions, funding typed in billions
df.loc[df['valuation_bn'] > 2000, 'valuation_bn'] = df['valuation_bn'] / 1000
df.loc[(df['funding_m'] < 20) & (df['valuation_bn'] >= 1) & (df['funding_m'] > 0), 'funding_m'] = df['funding_m'] * 1000
df['vdate'] = df['valuation_date'].str.extract(r'(\d{4}(?:-\d{2})?)')[0].fillna('')
# group duplicates: same registrable domain or same cleaned name (union-find)
par = list(range(len(df))); df = df.reset_index(drop=True)
def find(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
seen = {}
for i, r in df.iterrows():
    for k in {('d', regdom(r['domain'])), ('n', loose(r['brand'])), ('n', loose(r['legal_name'])), ('n', loose(r['vkey'])), ('c', r['cbid'])}:
        if not k[1] or len(k[1]) < 3: continue
        if k in seen: par[find(i)] = find(seen[k])
        else: seen[k] = i
df['grp'] = [find(i) for i in range(len(df))]
CR = {'H': 3, 'M': 2, 'L': 1}
df['filled'] = df[['valuation_bn', 'funding_m', 'domain', 'hq_country', 'latest_round']].apply(lambda r: sum(bool(s(v)) for v in r), axis=1)
df['rk'] = df['verified'].astype(int) * 100 + df['vdate'].map(lambda d: int(d.replace('-', '')[:6].ljust(6, '0')) if d else 0) / 1e6 * 10 + df['conf'].map(CR).fillna(0) + df['filled'] / 10
out = []
for g, sub in df.groupby('grp'):
    enr = sub[sub['file'] == 'CB Insights list']           # scoring-pass rows: descriptive fields and scores only
    if len(enr) and len(sub) > len(enr): sub = sub[sub['file'] != 'CB Insights list']
    sub = sub.sort_values('rk', ascending=False); p = sub.iloc[0].copy()
    ver = sub[sub['verified']]
    if not len(ver):
        if p['funding_m'] != p['funding_m'] or p['funding_m'] < sub['funding_m'].max(): p['funding_m'] = sub['funding_m'].max()
        if p['valuation_bn'] != p['valuation_bn']: p['valuation_bn'] = sub['valuation_bn'].max()
        for c in ('domain', 'hq_country', 'hq_city', 'ceo', 'source_url', 'investors', 'latest_round', 'sport_deals'):
            if not p[c]: p[c] = next((v for v in sub[c] if v), '')
        for c in SIG: p[c] = int(round(sub[c].mean()))
        st = set(sub['status']); p['status_conflict'] = len(st - {''}) > 1
        p['status_all'] = '; '.join(f"{a}: {b}" for a, b in zip(sub['file'], sub['status']))
    else:
        p = ver.iloc[0].copy(); p['status_conflict'] = False; p['status_all'] = ''
    if len(enr) and len(sub) and sub.iloc[0]['file'] != 'CB Insights list':
        e = enr.iloc[0]
        for c in list(SIG) + ['why', 'what', 'sector', 'evidence', 'ceo', 'sport_deals', 'f1_status', 'f1_deal']: p[c] = e[c]
        if e['conf'] in ('H', 'M') and p['conf'] == 'L': p['conf'] = 'M'
    p['found_by'] = ', '.join(sorted(set(sub['file']) | set(enr['file'])))
    p['new_unicorn'] = any(f in NEWFILES for f in sub['file']) or bool(re.search(r'new unicorn|first.*billion|became a unicorn|minted', ' '.join(sub['note'] + ' ' + sub['latest_round']), re.I))
    p['dupes'] = len(sub)
    p['cbid'] = next((c for c in sub['cbid'] if c), '')
    nv = sub[~sub['verified']]
    p['exit_votes'] = int((nv['status'].isin(['public', 'acquired', 'defunct']) & nv['conf'].isin(['H', 'M'])).sum())
    p['agent_status'] = '; '.join(sorted(set(nv['status']) - {''}))
    p['agent_val'] = nv['valuation_bn'].max(); p['agent_vdate'] = max(nv['vdate'], default='')
    p['agent_fund'] = nv['funding_m'].max(); p['agent_conf'] = max(nv['conf'], key=lambda c: CR.get(c, 0), default='')
    p['domains'] = sorted(set(regdom(d) for d in sub['domain'] if regdom(d)))
    out.append(p)
u = pd.DataFrame(out).reset_index(drop=True); print('unique companies', len(u))
exec(open(os.path.join(H, 'evidence.py')).read())   # sets t_private / t_val / t_fund / ev_* / verdict from independent sources
u['banned'] = (u['note'] + ' ' + u['what'] + ' ' + u['brand']).str.contains(r'cannabis|marijuana|tobacco|cigarette|vape|nicotine', case=False) | (u['sector'] == 33)
UNSURE = re.compile(r'unsure|verify|unverified|former|reported|possible|rumou?r|\?', re.I)
NOTF1 = re.compile(r'formula e\b|indycar|nascar|esports|broadcast|licen[cs]|^none|not f1|\bex-|former', re.I)
u['f1_current'] = u['f1_status'].str.lower().eq('current') & ~u['f1_deal'].str.contains(UNSURE) & ~u['f1_deal'].str.contains(NOTF1)
# 2026 F1 sponsor rosters (Formula 1 + all 11 teams, compiled from team / F1 partner pages): a match sets the row aside whatever research said
_rf = os.path.join(H, 'ref', 'f1_sponsors_2026.json')
if os.path.exists(_rf):
    _ros = json.load(open(_rf)); RN = {}; RD = {}
    for x in _ros:
        if loose(x[0]) and len(loose(x[0])) >= 3: RN.setdefault(loose(x[0]), []).append(f"{x[2]} ({x[3]})")
        if regdom(x[1]): RD.setdefault(regdom(x[1]), []).append(f"{x[2]} ({x[3]})")
    def _roster(r):
        hits = RN.get(loose(r['brand']), []) + (RN.get(loose(r['legal_name']), []) if r['legal_name'] else [])
        for d in r['domains'] if isinstance(r['domains'], list) else []: hits += RD.get(d, [])
        return '; '.join(sorted(set(hits)))
    u['f1_roster'] = u.apply(_roster, axis=1)
    u.loc[u['f1_roster'] != '', 'f1_current'] = True
    u['f1_deal'] = u.apply(lambda r: r['f1_roster'] or r['f1_deal'], axis=1)
    print('on 2026 F1 rosters', int((u['f1_roster'] != '').sum()))
else:
    u['f1_roster'] = ''
# Rahul's sheets and the 30 Oct list
u['on_sheets'] = u.apply(lambda r: present(r['brand'], r['domain']) or (present(r['legal_name']) if r['legal_name'] else '') or phrase_present(r['brand']), axis=1)
nb = pd.read_pickle(os.path.join(R, 'brands200', 'new_brands.pkl'))
NB_N = set(nb['brand'].map(loose)) - {''}; NB_D = set(nb['domain'].map(regdom)) - {''}
u['on_30oct'] = u.apply(lambda r: 'yes' if loose(r['brand']) in NB_N or (regdom(r['domain']) and regdom(r['domain']) in NB_D) else '', axis=1)
# scoring (same frame as the 30 Oct list: fit /60 + capacity /40; capacity reads valuation, funding and revenue)
u['fit_core'] = ((u['a'] * 5 + u['s'] * 5 + u['l'] * 2.5 + u['n'] * 2.5) * 40 / 60).round(1)
u['fit_signals'] = (u['competitor_f1'].clip(0, 3) * 1.5 + u['motorsport'].clip(0, 3) * 1.5 + u['expansion'].clip(0, 3) * 4 / 3
                    + (u['race_footprint'].clip(0, 3) - 1).clip(lower=0) * 3.5 / 2 + u['founder'].clip(0, 3) * 3.5 / 3).round(1)
def finband(r):
    v = r['valuation_bn'] if r['valuation_bn'] == r['valuation_bn'] else 0
    f = r['funding_m'] if r['funding_m'] == r['funding_m'] else 0
    for lv, lf, pts in ((50, 5000, 20), (10, 2000, 17), (5, 1000, 14), (3, 600, 11), (2, 400, 8), (1, 200, 6)):
        if v >= lv or f >= lf: return pts
    return 3
def revpts(x):
    if x != x: return 0
    return 4 if x >= 1000 else 3 if x >= 250 else 2 if x >= 100 else 1 if x >= 25 else 0
u['cap_financial'] = u.apply(finband, axis=1)
u['cap_signals'] = (u['headcount'].clip(0, 4) * 1.5 + u['fund_recency'].clip(0, 4) * 1.5 + u['brand_hires'].clip(0, 3) * 4 / 3 + u['revenue_m'].map(revpts)).round(1)
u['fit'] = (u['fit_core'] + u['fit_signals']).clip(upper=60).round(1); u['capacity'] = (u['cap_financial'] + u['cap_signals']).clip(upper=40).round(1)
u['total'] = (u['fit'] + u['capacity']).round(1)
u['timing'] = (u['expansion'].clip(0, 3) * 2 + u['fund_recency'].clip(0, 4) * 1.5 + u['brand_hires'].clip(0, 3) * 2 + u['competitor_f1'].clip(0, 3)).round(1)
u['priority'] = (u['total'] + u['timing'] - u['conf'].map({'L': 6, 'M': 2}).fillna(6)).round(1)
def why_now(r):
    b = []
    if r['fund_recency'] >= 3: b.append('fresh round in 2025-26')
    if r['new_unicorn']: b.append('new unicorn')
    if r['expansion'] >= 2: b.append('expansion / launch / IPO prep')
    if r['brand_hires'] >= 2: b.append('new brand or marketing leadership')
    if r['competitor_f1'] >= 2: b.append('a rival is already in F1')
    if r['motorsport'] >= 2: b.append('motorsport-linked product')
    if r['founder'] >= 2: b.append('founder/CEO motorsport affinity')
    return '; '.join(b)
u['why_now'] = u.apply(why_now, axis=1)
u['sector_name'] = u['sector'].map(lambda i: NAMES[i - 1] if 1 <= i <= len(NAMES) else 'Diversified & Other')
# buckets
q = u['verdict'].eq('verified') & ~u['banned']
u['ok_check'] = u['verdict'].eq('verified')
u['bucket'] = 'out'
u.loc[q & u['f1_current'], 'bucket'] = 'f1'
u.loc[q & ~u['f1_current'], 'bucket'] = 'main'
u.loc[u['verdict'].isin(['needs web check', 'could not verify']) & ~u['banned'], 'bucket'] = 'unverified'
fail = u['verdict'].eq('failed') & ~u['banned'] & u['t_private']
near = fail & ((u['t_val'] & ~u['t_fund']) | (u['t_fund'] & ~u['t_val'] & (u['valuation_bn'] >= 0.75)))
u.loc[near, 'bucket'] = 'near'
def why_out(r):
    if r['banned']: return 'tobacco / nicotine / cannabis: F1 advertising restrictions'
    if r['verdict'] == 'failed':
        bits = [e for ok, e in ((r['t_private'], r['ev_private']), (r['t_val'], r['ev_val']), (r['t_fund'], r['ev_fund'])) if not ok]
        if bits: return ' | '.join(bits)
    if r['verdict'] in ('needs web check', 'could not verify'):
        return 'unconfirmed: ' + ' | '.join(e for ok, e in ((r['t_private'], r['ev_private']), (r['t_val'], r['ev_val']), (r['t_fund'], r['ev_fund'])) if not ok)
    st = r['status']
    if st == 'public': return 'listed on a stock exchange' + (f" ({r['note']})" if r['note'] else '')
    if st == 'acquired': return 'acquired' + (f" ({r['note']})" if r['note'] else '')
    if st == 'defunct': return 'defunct / wound down'
    if st == 'below_1b' or (r['valuation_bn'] == r['valuation_bn'] and r['valuation_bn'] < 1): return f"latest valuation under USD 1B ({fb(r['valuation_bn'])})"
    if r['valuation_bn'] != r['valuation_bn']: return 'valuation not confirmed'
    if not r['t_fund']: return f"funding under USD 200M or not confirmed ({fm(r['funding_m'])})"
    return 'status unclear: ' + (r['status'] or 'not given')
fm = lambda v: '' if v != v or v is None else f'{v:,.0f}'
fb = lambda v: '' if v != v or v is None else (f'{v:,.1f}' if v < 100 else f'{v:,.0f}')
u['why_out'] = u.apply(why_out, axis=1)
main = u[u['bucket'] == 'main'].sort_values(['priority', 'total', 'valuation_bn'], ascending=False).reset_index(drop=True)
main.insert(0, 'rank', range(1, len(main) + 1))
T1, T2 = 150, 500
main['tier'] = main['rank'].map(lambda k: 'Tier 1 - contact first' if k <= T1 else ('Tier 2' if k <= T2 else 'Tier 3'))
fresh = main[(main['on_sheets'] == '') & (main['on_30oct'] == '')]
newu = main[main['new_unicorn']]
nearm = u[u['bucket'] == 'near'].sort_values(['valuation_bn'], ascending=False)
f1 = u[u['bucket'] == 'f1'].sort_values('valuation_bn', ascending=False)
outd = u[u['bucket'] == 'out'].sort_values('brand')
unv = u[u['bucket'] == 'unverified'].sort_values('valuation_bn', ascending=False)
print(f"main {len(main)} | not on sheets/30 Oct {len(fresh)} | new unicorns {len(newu)} | near misses {len(nearm)} | current F1 {len(f1)} | left out {len(outd)} | could not verify {len(unv)}")
# workbook
wb = Workbook(); wb.remove(wb.active)
HF = PatternFill('solid', fgColor='1F3864'); AMB = PatternFill('solid', fgColor='FFF2CC'); BLUE = PatternFill('solid', fgColor='BDD7EE'); GRN = PatternFill('solid', fgColor='E2EFDA')
def sheet(title, header, data, widths, fills=None):
    ws = wb.create_sheet(title[:31]); ws.append(header)
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='top')
    for i, row in enumerate(data):
        ws.append(row)
        if fills and fills[i] is not None:
            for c in ws[ws.max_row]: c.fill = fills[i]
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'D2'; ws.auto_filter.ref = ws.dimensions
    return ws
web = lambda d: f'https://{d}' if d and '.' in d and ' ' not in d else 'not found - check'
MH = ['Outreach Priority', 'Tier', 'Brand', 'HQ Country', 'HQ City', 'Website', 'Industry / Sector', 'What they do', 'Valuation (USD bn)', 'Valuation date',
      'Total Funding (USD M)', 'Latest round', 'Top investors', 'Revenue / ARR (USD M)', 'New unicorn 2025-26', 'Already on your sheets?', 'On 30 Oct new-brands list?',
      'Why contact now', 'Why F1 fits', 'Priority score', 'F1 Fit (/60)', 'Financial Capacity (/40)', 'Total (/100)', 'Other sport deals', 'CEO / founder',
      'Signal evidence', 'Research confidence', 'News check', 'News evidence / source', 'Note', 'Found by']
MW = [9, 20, 26, 13, 14, 28, 24, 38, 10, 9, 11, 38, 30, 11, 9, 18, 10, 38, 42, 8, 8, 8, 8, 30, 22, 42, 9, 11, 40, 30, 14]
def mrow(r):
    return [r['rank'], r['tier'], r['brand'], r['hq_country'], r['hq_city'], web(regdom(r['domain']) or r['domain']), r['sector_name'], r['what'],
            fb(r['valuation_bn']), r['vdate'], fm(r['funding_m']), r['latest_round'], r['investors'], fm(r['revenue_m']), 'yes' if r['new_unicorn'] else '',
            r['on_sheets'], r['on_30oct'], r['why_now'], r['why'], r['priority'], r['fit'], r['capacity'], r['total'], r['sport_deals'], r['ceo'],
            r['evidence'], r['conf'] or 'L', r['news_check'] or 'sources only', r['news_evidence'] or r['source_url'], r['note'], r['found_by']]
flag = lambda r: AMB if r['conf'] in ('L', '') or r['status_conflict'] else (GRN if r['new_unicorn'] else None)
by_c = main['hq_country'].value_counts()
summary = [['Item', 'Value'],
    ['Built', '30 Oct 2026 for Rahul Gopalan (SPORTFIVE F1 partnerships)'],
    ['Rules', 'Private company (not listed, not acquired), valuation of USD 1B or more, total equity funding of USD 200M or more. Worldwide, every sector.'],
    ['Private unicorns that pass all three tests (main list)', len(main)],
    ['   of which not on your sheets and not on the 30 Oct new-brands list', len(fresh)],
    ['   of which new unicorns of 2025-26 (green rows)', len(newu)],
    ['Near misses (one test just failed: e.g. unicorn with under USD 200M raised)', len(nearm)],
    ['Pass all tests but already have a current F1 deal (set aside)', len(f1)],
    ['Checked and left out (listed, acquired, defunct, under USD 1B)', len(outd)],
    ['Pass on paper but the web check found no reliable source (separate tab, not in the main list)', len(unv)],
    ['Verification', 'Every row in the main list was checked on the web on 30 Oct 2026 (identity and website, private status, latest valuation, total funding, latest round) because connector data can be wrong. Web check = confirmed (claims held) or corrected (figures fixed; see Note).'],
    ['Outreach order', f'Ranked by Outreach Priority = Total score + timing (fresh round, expansion or IPO prep, new marketing leadership, a rival already in F1) minus a penalty for lower-confidence rows. Tier 1 = top {T1}, Tier 2 = {T1 + 1}-{T2}, Tier 3 = the rest. Sector tabs keep the same order.'],
    ['Scoring', 'Total /100 = F1 Fit /60 (audience overlap, commercial synergies, brand alignment, international relevance, plus signals: rival in F1, motorsport link, expansion moment, race-market footprint, founder affinity) + Financial Capacity /40 (valuation and funding bands, headcount, funding recency, marketing hires, revenue).'],
    ['Already on your sheets?', 'Checked against every name and website on MASTER REFERENCE OCT and the 2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS workbook (name, spelling variant or website match). These rows are kept in the main list and flagged; the NOT ON YOUR SHEETS tab leaves them out.'],
    ['Sources', 'Research agents by sector and region (own knowledge plus web search of funding news and monthly new-unicorn round-ups), cross-checked against the Apollo and Clay funded-company databases (total funding USD 200M+). Crunchbase data allowance was exhausted until 1 Nov 2026 and Lusha and Apollo paid credits were used up, so their free search tools were used.'],
    ['Confidence', 'Valuations are the latest reported figures (priced rounds, credible press reports or tenders) and are estimates, not audited records. Amber rows = lower confidence or conflicting status; check before outreach.']]
summary += [['', '']] + [[f'HQ country: {k}', int(v)] for k, v in by_c.head(25).items()]
summary += [['', '']] + [[f'Sector: {k}', int(v)] for k, v in main['sector_name'].value_counts().items()]
sheet('SUMMARY', summary[0], summary[1:], [70, 120])
sheet('PRIVATE UNICORNS (MASTER)', MH, [mrow(r) for _, r in main.iterrows()], MW, [flag(r) for _, r in main.iterrows()])
sheet('NOT ON YOUR SHEETS', MH, [mrow(r) for _, r in fresh.iterrows()], MW, [flag(r) for _, r in fresh.iterrows()])
sheet('NEW UNICORNS 2025-26', MH, [mrow(r) for _, r in newu.iterrows()], MW, [flag(r) for _, r in newu.iterrows()])
for sec in NAMES:
    sub = main[main['sector_name'] == sec]
    if not len(sub): continue
    sheet(re.sub(r'[\[\]\*\?/\\:]', '-', sec)[:31], ['Sector Rank'] + MH, [[i] + mrow(r) for i, (_, r) in enumerate(sub.iterrows(), 1)], [7] + MW, [flag(r) for _, r in sub.iterrows()])
SH = ['Brand', 'HQ Country', 'Website', 'Sector', 'What they do', 'Valuation (USD bn)', 'Valuation date', 'Total Funding (USD M)', 'Latest round', 'Status', 'Reason', 'Note', 'Source']
srow = lambda r, why: [r['brand'], r['hq_country'], web(regdom(r['domain'])), r['sector_name'], r['what'], fb(r['valuation_bn']), r['vdate'], fm(r['funding_m']),
                       r['latest_round'], r['status'], why, r['note'], r['source_url']]
SW = [26, 13, 26, 24, 36, 10, 9, 11, 36, 10, 46, 30, 40]
sheet('NEAR MISSES', SH, [srow(r, r['why_out']) for _, r in nearm.iterrows()], SW)
sheet('CURRENT F1 DEAL (SET ASIDE)', SH[:9] + ['F1 deal'], [srow(r, '')[:9] + [r['f1_deal']] for _, r in f1.iterrows()], SW[:9] + [45], [BLUE] * len(f1))
sheet('CHECKED - LEFT OUT', SH, [srow(r, r['why_out']) for _, r in outd.iterrows()], SW)
sheet('COULD NOT VERIFY', SH, [srow(r, r['why_out']) for _, r in unv.iterrows()], SW, [AMB] * len(unv))
for ws in wb.worksheets:
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=False)
os.makedirs(os.path.dirname(OUT), exist_ok=True); wb.save(OUT); print('saved', OUT)
u.to_pickle(os.path.join(H, 'all.pkl')); main.to_pickle(os.path.join(H, 'main.pkl'))
