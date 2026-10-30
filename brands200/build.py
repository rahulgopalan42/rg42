"""Build reports/F1-NEW-BRANDS-200M-FUNDING-OR-100M-LISTED-REVENUE-2026-10-30.xlsx from agent outputs
(brands200/verify_out/*.json and brands200/discover_out/*.json, 38-field rows, see verify_brief.md).
Rules (Rahul, 30 Oct 2026): total funding > USD 200M (any ownership type) OR listed with revenue/ARR >= USD 100M;
not on MASTER REFERENCE OCT or the parent-company prospects workbook (brands200/match.py)."""
import glob, json, os, re, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
sys.path.insert(0, H); from match import present, regdom, strict, phrase_present
sys.path.insert(0, os.path.join(R, 'parents')); from sectors_v3 import NAMES
OUT = os.path.join(R, 'reports', 'F1-NEW-BRANDS-200M-FUNDING-OR-100M-LISTED-REVENUE-2026-10-30.xlsx')
F = ['key', 'status', 'brand', 'parent', 'hq_country', 'domain', 'type', 'ticker', 'revenue_m', 'revenue_year', 'funding_m', 'qualifies', 'rule',
     'sector', 'approach', 'why', 'a', 's', 'l', 'n', 'fin', 'f1_status', 'f1_deal', 'headcount', 'fund_recency', 'pe_owned', 'brand_hires',
     'competitor_f1', 'motorsport', 'expansion', 'race_footprint', 'founder', 'evidence', 'ceo', 'conf', 'note', 'sport_deals', 'cmo']
rows, bad = [], 0
for f in sorted(glob.glob(f'{H}/verify_out/chunk_*.json')) + sorted(glob.glob(f'{H}/discover_out/s*.json')):
    src = 'connector' if 'verify_out' in f else 'research agent'
    try: data = json.load(open(f))
    except Exception as e: print('bad file', f, e); continue
    for r in data:
        if isinstance(r, list) and len(r) == 38: rows.append(dict(zip(F, r), src=src, file=os.path.basename(f)))
        else: bad += 1
df = pd.DataFrame(rows); print('rows', len(df), 'malformed', bad)
ap = {}
if os.path.exists(f'{H}/apollo_check/funding200_ids.json'):
    j = json.load(open(f'{H}/apollo_check/funding200_ids.json')); ap = {'checked': set(j.get('checked_batches', [])), 'ids': set(j.get('ids', []))}
num = lambda x: pd.to_numeric(x, errors='coerce')
for c in ('revenue_m', 'funding_m'): df[c] = num(df[c])
for c in ('a', 's', 'l', 'n', 'headcount', 'fund_recency', 'pe_owned', 'brand_hires', 'competitor_f1', 'motorsport', 'expansion', 'race_footprint', 'founder'):
    df[c] = num(df[c]).fillna(0).clip(0, 4).astype(int)
df['sector'] = num(df['sector']).fillna(48).clip(1, 48).astype(int)
s = lambda x: '' if x is None or (isinstance(x, float) and x != x) else str(x)
for c in ('status', 'qualifies', 'type', 'f1_status', 'conf', 'brand', 'parent', 'domain', 'ticker', 'f1_deal', 'note'): df[c] = df[c].map(s)
df['brand'] = df.apply(lambda r: r['brand'] or r['key'].split(':', 1)[-1], axis=1)
# money rule, re-applied on the figures (agents' "Y" is not taken on trust)
df['listed'] = df['type'].str.lower().eq('listed') | df['ticker'].str.contains(':')
# Apollo's funding field on subsidiaries often holds an acquisition price or the parent's figure (spot-check 30 Oct): count it for independent companies only
df['apollo200'] = df['key'].str.startswith('ap:') & df['key'].str[3:].isin(ap.get('ids', set())) & (df['status'] == 'P')
df['fund_unconfirmed'] = df['funding_m'].isna() & df['qualifies'].eq('Y') & df['rule'].map(s).eq('funding') & ~df['apollo200']
df['q_fund'] = (df['funding_m'] > 200) | df['apollo200'] | df['fund_unconfirmed']
df['rev_unconfirmed'] = df['listed'] & df['revenue_m'].isna() & df['qualifies'].eq('Y') & df['rule'].map(s).eq('listed_revenue')
df['q_rev'] = df['listed'] & ((df['revenue_m'] >= 100) | df['rev_unconfirmed'])
df['qual'] = df['q_fund'] | df['q_rev']
def crit(r):
    out = []
    if r['funding_m'] > 200: out.append(f"Funding ~USD {r['funding_m']:,.0f}M (research estimate)")
    if r['apollo200']: out.append('Funding > USD 200M (Apollo funding filter)')
    if r['fund_unconfirmed']: out.append('Funding believed > USD 200M (figure not confirmed)')
    if r['q_rev'] and not r['rev_unconfirmed']: out.append(f"Listed ({r['ticker'] or 'exchange-listed'}), revenue ~USD {r['revenue_m']:,.0f}M ({s(r['revenue_year']) or 'latest'})")
    if r['rev_unconfirmed']: out.append(f"Listed ({r['ticker'] or 'exchange-listed'}), revenue believed >= USD 100M (figure not confirmed)")
    return '; '.join(out)
df['criterion'] = df.apply(crit, axis=1)
# not on Rahul's sheets: check brand, domain, parent
df['on_sheets_self'] = df.apply(lambda r: present(r['brand'], r['domain']) or present(r['key'].split(':', 1)[-1]) or phrase_present(r['brand']) or phrase_present(r['key'].split(':', 1)[-1]), axis=1)
df['on_sheets_parent'] = df.apply(lambda r: (present(r['parent']) or phrase_present(r['parent'])) if r['parent'] and strict(r['parent']) != strict(r['brand']) else '', axis=1)
UNSURE = re.compile(r'unsure|verify|unverified|former|reported|possible|\?', re.I)
NOTF1 = re.compile(r'formula e\b|indycar|nascar|broadcast|licen[cs]|none|not f1|\bex-|former', re.I)
df['f1_current'] = df['f1_status'].str.lower().eq('current') & ~df['f1_deal'].str.contains(UNSURE) & ~df['f1_deal'].str.contains(NOTF1)
df['dk'] = df.apply(lambda r: regdom(r['domain']) or strict(r['brand']), axis=1)
# scoring: old parameters (core fit 40 + financial evidence 20) + new signal parameters (fit 20 + capacity 20)
df['fit_core'] = ((df['a'] * 5 + df['s'] * 5 + df['l'] * 2.5 + df['n'] * 2.5) * 40 / 60).round(1)
df['fit_signals'] = (df['competitor_f1'].clip(0, 3) * 1.5 + df['motorsport'].clip(0, 3) * 1.5 + df['expansion'].clip(0, 3) * 4 / 3
                     + (df['race_footprint'].clip(0, 3) - 1).clip(lower=0) * 3.5 / 2 + df['founder'].clip(0, 3) * 3.5 / 3).round(1)
def finband(r):
    rv, fu = r['revenue_m'] if r['revenue_m'] == r['revenue_m'] else 0, r['funding_m'] if r['funding_m'] == r['funding_m'] else 0
    for lim_r, lim_f, pts in ((10000, 3000, 20), (3000, 1500, 17), (1000, 750, 14), (500, 400, 11), (250, 250, 8), (100, 200, 6)):
        if rv >= lim_r or fu >= lim_f: return pts
    return 5 if r['apollo200'] else 3
df['cap_financial'] = df.apply(finband, axis=1)
df['cap_signals'] = (df['headcount'].clip(0, 4) * 1.5 + df['fund_recency'].clip(0, 4) * 1.5 + df['pe_owned'].clip(0, 3) * 4 / 3 + df['brand_hires'].clip(0, 3) * 4 / 3).round(1)
df['fit'] = (df['fit_core'] + df['fit_signals']).clip(upper=60).round(1); df['capacity'] = (df['cap_financial'] + df['cap_signals']).clip(upper=40).round(1)
df['total'] = (df['fit'] + df['capacity']).round(1)
df['sector_name'] = df['sector'].map(lambda i: NAMES[i - 1] if 1 <= i <= len(NAMES) else 'Diversified & Other')
# buckets
df['banned'] = (df['note'] + ' ' + df['brand'] + ' ' + df['why'].map(s)).str.contains(r'cannabis|marijuana|tobacco|cigarette|vape|nicotine', case=False) | (df['sector'] == 33)
ok = df['status'].isin(['P', 'S']) & df['qual'] & (df['on_sheets_self'] == '') & ~df['banned']
df['bucket'] = 'excluded'
df.loc[ok & df['f1_current'], 'bucket'] = 'f1'
df.loc[ok & ~df['f1_current'] & (df['on_sheets_parent'] != ''), 'bucket'] = 'parent_on_sheets'
df.loc[ok & ~df['f1_current'] & (df['on_sheets_parent'] == ''), 'bucket'] = 'new'
def why_out(r):
    if r['on_sheets_self']: return f"already on your sheets ({r['on_sheets_self']})"
    if r['status'] == 'X': return 'not a prospect: ' + (r['note'] or 'fund / vehicle / defunct / absorbed')
    if r['status'] == 'U': return 'not recognised; not verified'
    if r['banned']: return 'tobacco / nicotine / cannabis: F1 advertising restrictions'
    if not r['qual']: return 'does not meet the money rule on known figures' + (f" ({r['note']})" if r['note'] else '')
    return ''
df['why_out'] = df.apply(why_out, axis=1)
df = df.sort_values(['total', 'fit', 'capacity'], ascending=False)
new = df[df['bucket'] == 'new'].drop_duplicates('dk'); seen = set(new['dk'])
pos = df[df['bucket'] == 'parent_on_sheets'].drop_duplicates('dk'); pos = pos[~pos['dk'].isin(seen)]; seen |= set(pos['dk'])
f1 = df[df['bucket'] == 'f1'].drop_duplicates('dk'); f1 = f1[~f1['dk'].isin(seen)]
exc = df[df['bucket'] == 'excluded'].drop_duplicates('dk')
# a subsidiary whose parent is itself on the new list is folded into the parent's row (one group, one row)
pk = {strict(b): i for i, b in zip(new.index, new['brand'])} | {strict(p_): i for i, p_, st in zip(new.index, new['parent'], new['status']) if st == 'P' and p_}
new['group_brands'] = ''
fold = []
for i, r in new.iterrows():
    if r['status'] == 'S' and r['parent']:
        j = pk.get(strict(r['parent']))
        if j is not None and j != i and new.at[j, 'status'] == 'P':
            new.at[j, 'group_brands'] = (new.at[j, 'group_brands'] + '; ' if new.at[j, 'group_brands'] else '') + r['brand']; fold.append(i)
new = new.drop(index=fold)
print('subsidiaries folded into their parent row', len(fold))
new = new.reset_index(drop=True); new.insert(0, 'rank', range(1, len(new) + 1))
print('new', len(new), '| brands of groups on your sheets', len(pos), '| current F1', len(f1), '| excluded', len(exc))
# workbook
wb = Workbook(); wb.remove(wb.active)
HF = PatternFill('solid', fgColor='1F3864'); AMB = PatternFill('solid', fgColor='FFF2CC'); BLUE = PatternFill('solid', fgColor='BDD7EE')
def sheet(title, header, data, widths, fills=None):
    ws = wb.create_sheet(title[:31]); ws.append(header)
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='top')
    for i, row in enumerate(data):
        ws.append(row)
        if fills and fills[i] is not None:
            for c in ws[ws.max_row]: c.fill = fills[i]
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
fm = lambda v: '' if v != v or v is None else f'{v:,.0f}'
MH = ['Rank', 'Brand', 'Ultimate Parent', 'HQ Country', 'Industry / Sector', 'Website', 'Company Type', 'Ticker', 'Revenue / ARR (USD M)', 'Revenue year',
      'Total Funding (USD M)', 'Qualifies on', 'Recommended Approach', 'Why this brand', 'F1 Fit (/60)', 'Financial Capacity (/40)', 'Total (/100)',
      'Fit: core (/40)', 'Fit: signals (/20)', 'Capacity: financial (/20)', 'Capacity: signals (/20)', 'Affordability evidence', 'Signal evidence',
      'Other sport deals', 'CEO / founder', 'CMO / marketing head', 'Research confidence', 'Source', 'Note', 'Group brands also found']
MW = [6, 28, 26, 14, 24, 22, 11, 14, 11, 8, 11, 40, 10, 45, 8, 8, 8, 8, 8, 8, 8, 32, 45, 30, 20, 20, 9, 13, 30, 30]
def mrow(r, rk):
    return [rk, r['brand'], r['parent'] or r['brand'], r['hq_country'], r['sector_name'], regdom(r['domain']) or r['domain'], r['type'], r['ticker'],
            fm(r['revenue_m']), s(r['revenue_year']), fm(r['funding_m']), r['criterion'], {'G': 'Group', 'B': 'Brand'}.get(s(r['approach']).upper()[:1], ''),
            s(r['why']), r['fit'], r['capacity'], r['total'], r['fit_core'], r['fit_signals'], r['cap_financial'], r['cap_signals'], s(r['fin']),
            s(r['evidence']), s(r['sport_deals']), s(r['ceo']), s(r['cmo']), r['conf'], r['src'], r['note'], s(r.get('group_brands', ''))]
prelim = lambda r: AMB if r['conf'] in ('L', '') or r['rev_unconfirmed'] or r['fund_unconfirmed'] else None
summary = [['Item', 'Value'],
    ['Built', '30 Oct 2026 for Rahul Gopalan (SPORTFIVE F1 partnerships)'],
    ['Money rule', 'Total funding above USD 200M (any ownership type: public, private, founder-owned, family, PE-backed, partnership) OR listed company with revenue / ARR of USD 100M or more. Nothing else qualifies.'],
    ['Not on your sheets', 'Every brand was checked against every company, brand, subsidiary and website on MASTER REFERENCE OCT (all 59 tabs) and the 2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS workbook (all tabs), including spelling variants.'],
    ['New brands (main list and sector tabs)', len(new)],
    ['Brands whose parent group is already on your sheets (separate tab)', len(pos)],
    ['Qualifying brands with a current F1 deal (set aside)', len(f1)],
    ['Checked and left out (on sheets, not qualified, funds/vehicles, unrecognised)', len(exc)],
    ['Scoring', 'Total /100 = F1 Fit /60 (core fit 40: audience overlap, commercial synergies, brand alignment, international relevance; plus fit signals 20: competitor in F1, motorsport adjacency, expansion moment, race-market footprint, founder/CEO affinity) + Financial Capacity /40 (financial evidence 20 from revenue/funding bands; capacity signals 20: headcount, funding recency, PE ownership, brand-building hires). Cheque size assumed about USD 2.5M a year.'],
    ['Sources', 'Connectors: Apollo funded-company database (total funding filter) and a public market-cap listing of exchange-listed companies; Apollo free lookup confirmed the USD 200M funding filter for Apollo-sourced rows. Crunchbase allowance was exhausted until 1 Nov 2026 and Apollo paid credits until 11 Nov 2026. Research agents identified, verified and scored every row and added brands by sector.'],
    ['Confidence', 'Figures are research estimates from public knowledge up to mid-2026, not audited records. Amber rows = low confidence; check figures before outreach.']]
summary += [['', '']] + [[f'New brands: {k}', int(v)] for k, v in new['sector_name'].value_counts().items()]
sheet('SUMMARY', summary[0], summary[1:], [60, 120])
sheet('NEW BRANDS (MASTER)', MH, [mrow(r, r['rank']) for _, r in new.iterrows()], MW, [prelim(r) for _, r in new.iterrows()])
for sec in NAMES:
    sub = new[new['sector_name'] == sec]
    if not len(sub): continue
    t = re.sub(r'[\[\]\*\?/\\:]', '-', sec)[:31]
    sheet(t, ['Sector Rank'] + MH, [[i] + mrow(r, r['rank']) for i, (_, r) in enumerate(sub.iterrows(), 1)], [7] + MW, [prelim(r) for _, r in sub.iterrows()])
pos = pos.reset_index(drop=True)
sheet('PARENT ALREADY ON SHEETS', ['Rank', 'Brand', 'Parent on your sheets (match)'] + MH[3:], [[i, r['brand'], f"{r['parent']} ({r['on_sheets_parent']})"] + mrow(r, i)[3:] for i, (_, r) in enumerate(pos.iterrows(), 1)], [6, 28, 34] + MW[3:])
sheet('CURRENT F1 DEAL (SET ASIDE)', ['Brand', 'Parent', 'HQ Country', 'Sector', 'F1 deal', 'Qualifies on', 'Total (/100)'],
      [[r['brand'], r['parent'], r['hq_country'], r['sector_name'], r['f1_deal'], r['criterion'], r['total']] for _, r in f1.iterrows()], [28, 28, 14, 24, 45, 45, 9], [BLUE] * len(f1))
sheet('CHECKED - LEFT OUT', ['Brand / record', 'Parent', 'Website', 'Reason left out', 'Status', 'Source'],
      [[r['brand'], r['parent'], r['domain'], r['why_out'] or 'duplicate', r['status'], r['src']] for _, r in exc.iterrows()], [32, 28, 22, 70, 8, 13])
for ws in wb.worksheets:
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(vertical='top', wrap_text=False)
wb.save(OUT); print('saved', OUT)
new.to_pickle(os.path.join(H, 'new_brands.pkl'))
