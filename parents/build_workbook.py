"""Parent-company prospects, step 3: score (60/40), categorise and write
'2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS.xlsx'. Input: parents.pkl, dups.pkl, excluded.pkl from consolidate.py."""
import collections, json, math, os, re, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad'
P = f'{S}/parents'; OUT = f'{R}/reports/2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS.xlsx'
sys.path.insert(0, f'{R}/wave16')
from sectors_v3 import NAMES
par = pd.read_pickle(f'{P}/parents.pkl'); dups = pd.read_pickle(f'{P}/dups.pkl'); excl = pd.read_pickle(f'{P}/excluded.pkl')
ver = pd.read_pickle(f'{P}/verified.pkl') if os.path.exists(f'{P}/verified.pkl') else pd.DataFrame(columns=['key', 'val_bn', 'val_date', 'val_basis', 'src'])
TODAY = '2026-10-19'

def s(x): return '' if x is None or (isinstance(x, float) and math.isnan(x)) else str(x)
def f(x):
    try: return None if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)
    except Exception: return None
def clean_domain(d):
    d = s(d).strip().lower(); d = re.sub(r'^https?://', '', d); d = re.sub(r'^www\.', '', d); return d.split('/')[0]

# ---------------------------------------------------------------- verified figures override knowledge figures
if len(ver):
    vm = ver.set_index('key')
    for k, row in vm.iterrows():
        m = par['key'] == k
        if m.any() and f(row['val_bn']):
            par.loc[m, ['val_bn', 'val_date', 'val_basis']] = [row['val_bn'], row['val_date'], row['val_basis']]
            par.loc[m, 'verified_src'] = row['src']
if 'verified_src' not in par: par['verified_src'] = ''

# ---------------------------------------------------------------- qualification and F1 status
for c in ('a', 's', 'l', 'n'): par[c] = pd.to_numeric(par[c], errors='coerce')
par['val_bn'] = par['val_bn'].map(f); par['funding_m'] = par['funding_m'].map(f)
par['sector'] = pd.to_numeric(par['sector'], errors='coerce').fillna(48).astype(int)
par['scored'] = par['a'].notna()
for c in ('a', 's', 'l', 'n'): par[c] = par[c].fillna(1).clip(0, 4)
par['qual'] = ''
par.loc[par['val_bn'].fillna(0) >= 1, 'qual'] = 'Valuation >= USD 1B'
m = (par['qual'] == '') & (par['funding_m'].fillna(0) >= 100); par.loc[m, 'qual'] = 'Cumulative funding >= USD 100M'
m = (par['qual'] == '') & par['apollo_funding'].notna(); par.loc[m, 'qual'] = 'Cumulative funding >= USD 100M (Apollo database filter; amount not disclosed)'
m = (par['qual'] == '') & par['sources'].map(lambda x: 'lusha' in x); par.loc[m, 'qual'] = 'Cumulative funding >= USD 100M (Lusha database filter; amount not disclosed)'
par['qualifies_k'] = par.get('qualifies_k', pd.Series('', index=par.index)).fillna('')
# knowledge says it clearly does not qualify, and no figure contradicts that -> excluded
not_q = (par['qualifies_k'] == 'N') & (par['val_bn'].fillna(0) < 1) & (par['funding_m'].fillna(0) < 100)
f1 = par['f1'].fillna('').astype(str)
UNSURE = re.compile(r'unsure|verify|unverified|former|past|\?|reported|possible|check|ended|expired|until 20', re.I)
par['f1_current'] = (f1.str.strip() != '') & ~f1.str.contains(UNSURE)
par['f1_check'] = (f1.str.strip() != '') & f1.str.contains(UNSURE)

# ---------------------------------------------------------------- scores
par['fit'] = (par['a'] * 5 + par['s'] * 5 + par['l'] * 2.5 + par['n'] * 2.5).round(1)
def rev_bn(x):
    x = s(x).upper().replace('$', '').replace(',', '')
    mm = re.match(r'([\d.]+)\s*([KMBT]?)', x)
    if not mm: return None
    v = float(mm.group(1)); return v * {'': 1e-9, 'K': 1e-6, 'M': 1e-3, 'B': 1, 'T': 1000}[mm.group(2)]
par['rev_bn'] = par['revenue_printed'].map(rev_bn) if 'revenue_printed' in par else None
def capacity(r):
    v = r['val_bn'] or 0; fu = r['funding_m'] or 0; rv = r['rev_bn'] or 0
    # revenue & scale /20: valuation is the scale proxy; Apollo revenue lifts it where known
    sc = 20 if v >= 100 else 17 if v >= 30 else 14 if v >= 10 else 11 if v >= 3 else 8 if v >= 1 else 6 if fu >= 100 else 5
    if rv >= 10: sc = max(sc, 18)
    elif rv >= 1: sc = max(sc, 14)
    elif rv >= 0.25: sc = max(sc, 10)
    # valuation & funding /10
    vf = 10 if v >= 50 else 8 if v >= 10 else 6 if v >= 1 else 7 if fu >= 1000 else 5 if fu >= 300 else 4 if fu >= 100 else 2
    # other indicators /10: affordability evidence, listed/state ownership, confidence, sports sponsorship record
    oth = 3
    fin = s(r['fin']); typ = s(r['type']).lower()
    if fin: oth += 3
    if re.search(r'sponsor|partner|title|team|league|olympic|uefa|fifa|nba|nfl', fin, re.I): oth += 1
    if typ in ('listed', 'state'): oth += 2
    if s(r['conf']) == 'H': oth += 1
    return sc, vf, min(oth, 10)
cap = par.apply(capacity, axis=1, result_type='expand'); cap.columns = ['cap_scale', 'cap_val', 'cap_other']
par = pd.concat([par, cap], axis=1)
par['capacity'] = par['cap_scale'] + par['cap_val'] + par['cap_other']
par['total'] = (par['fit'] + par['capacity']).round(1)
par['preliminary'] = (~par['scored']) | par['conf'].fillna('').isin(['L', 'U']) | (par['val_bn'].isna() & par['funding_m'].isna())
par['confidence'] = par.apply(lambda r: 'Preliminary - not scored (connector record only)' if not r['scored'] else
                              {'H': 'High', 'M': 'Medium', 'L': 'Low (figures from memory)', 'U': 'Low - identity unconfirmed'}.get(s(r['conf']), 'Medium'), axis=1)
def rationale(r):
    bits = []
    if r['a'] >= 3: bits.append('strong F1 audience overlap')
    if r['s'] >= 3: bits.append('clear activation / hospitality or technology-showcase use')
    if r['l'] >= 3: bits.append('brand fits performance, innovation or premium positioning')
    if r['n'] >= 3: bits.append('active across F1 race markets')
    v = r['val_bn']; fu = r['funding_m']
    if v: bits.append(f"USD {v:,.1f}B {s(r['val_basis']) or 'valuation'}")
    elif fu: bits.append(f"USD {fu:,.0f}M raised")
    else: bits.append('funding >= USD 100M per database filter; size unverified')
    if s(r['fin']): bits.append(s(r['fin']))
    return '; '.join(bits).capitalize()
par['rationale'] = par.apply(rationale, axis=1)
def sources(r):
    src = []
    if 'knowledge' in r['sources'] or 'knowledge-scored' in r['sources']:
        src.append(f"Research knowledge base (figures as of {s(r['val_date']) or 'n/a'}, confidence {s(r['conf']) or 'M'})")
    if 'apollo' in r['sources']: src.append('Apollo.io company database, pulled 2026-10-19 (total funding >= USD 100M filter)')
    if 'lusha' in r['sources']: src.append('Lusha company database, pulled 2026-10-19 (total funding >= USD 100M filter)')
    if s(r.get('verified_src')): src.append(f"Verified: {r['verified_src']} ({TODAY})")
    return '; '.join(src)
par['sources_txt'] = par.apply(sources, axis=1)
par['val_txt'] = par.apply(lambda r: f"USD {r['val_bn']:,.1f}B ({s(r['val_basis']) or 'valuation'}, {s(r['val_date']) or 'date n/a'})" if r['val_bn'] else '', axis=1)
par['fund_txt'] = par.apply(lambda r: f"USD {r['funding_m']:,.0f}M" if r['funding_m'] else ('>= USD 100M (database filter, amount not disclosed)' if 'database filter' in r['qual'] else ''), axis=1)
par['approach_txt'] = par['approach'].map(lambda x: {'G': 'Group-Level', 'B': 'Brand-Level'}.get(s(x), 'Group-Level'))
par['sector_name'] = par['sector'].map(lambda i: NAMES[int(i) - 1] if 1 <= int(i) <= 48 else NAMES[47])
par['website'] = par['domain'].map(clean_domain)
par['type_txt'] = par['type'].fillna('').astype(str).str.capitalize().replace({'Pe-backed': 'PE-backed', '': 'Unknown'})
par['brand_txt'] = par.apply(lambda r: s(r['brand']) or s(r['name']), axis=1)
par['why_txt'] = par['why'].fillna('').astype(str)

# ---------------------------------------------------------------- categories
par['bucket'] = ''
par.loc[par['overlap_cat'] == 'A', 'bucket'] = 'A'
par.loc[par['overlap_cat'] == 'B', 'bucket'] = 'B'
par.loc[par['overlap_cat'] == 'C', 'bucket'] = 'C'
par.loc[par['conf'].fillna('') == 'U', 'bucket'] = 'C'
par.loc[par['sn'].str.len() < 3, 'bucket'] = 'C'
par.loc[not_q, 'bucket'] = 'XQ'
par.loc[par['f1_current'], 'bucket'] = 'F1'
def rank(df):
    df = df.sort_values(['total', 'fit', 'val_bn'], ascending=[False, False, False], na_position='last').reset_index(drop=True)
    df.insert(0, 'rank', range(1, len(df) + 1)); return df
A = rank(par[par['bucket'] == 'A']); B = rank(par[par['bucket'] == 'B']); C = par[par['bucket'] == 'C'].sort_values('total', ascending=False)
F1 = par[par['bucket'] == 'F1'].sort_values('total', ascending=False); XQ = par[par['bucket'] == 'XQ']
print('A', len(A), 'B', len(B), 'C', len(C), 'F1', len(F1), 'not qualified', len(XQ), 'dups', len(dups), 'excluded', len(excl))

# ---------------------------------------------------------------- workbook
wb = Workbook(); wb.remove(wb.active)
HF = PatternFill('solid', fgColor='1F3864'); RED = PatternFill('solid', fgColor='F8CBAD'); AMB = PatternFill('solid', fgColor='FFF2CC'); GRN = PatternFill('solid', fgColor='E2EFDA')
def sheet(title, header, rows, widths=None, fills=None, freeze='B2'):
    ws = wb.create_sheet(title[:31])
    ws.append(header)
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='top')
    for i, row in enumerate(rows):
        ws.append(row)
        if fills is not None and fills[i] is not None:
            for c in ws[ws.max_row]: c.fill = fills[i]
    for i, w in enumerate(widths or [], 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = freeze; ws.auto_filter.ref = ws.dimensions
    return ws
MH = ['Overall Rank', 'Parent Company Name', 'HQ Country', 'Industry / Sector', 'Website', 'Company Type', 'Valuation / Market Cap',
      'Cumulative Funding', 'Qualification Criterion Met', 'Most Relevant Subsidiary / Brand', 'Recommended Approach', 'Why this brand / approach',
      'F1 Fit Score (/60)', 'Financial Capacity Score (/40)', 'Total Score (/100)', 'Rationale', 'Research Confidence', 'Sources & Dates',
      'Possible F1 link to verify', 'Preliminary?', 'Known subsidiaries / brands']
MW = [7, 30, 14, 26, 22, 12, 30, 22, 30, 26, 13, 45, 9, 9, 9, 60, 22, 60, 24, 10, 40]
def mrow(r, rk):
    return [rk, s(r['name']), s(r['hq_country']), r['sector_name'], r['website'], r['type_txt'], r['val_txt'], r['fund_txt'], r['qual'],
            r['brand_txt'], r['approach_txt'], r['why_txt'], r['fit'], r['capacity'], r['total'], r['rationale'], r['confidence'], r['sources_txt'],
            s(r['f1']) if r['f1_check'] else '', 'Yes' if r['preliminary'] else '', '; '.join(sorted(set(r['subs']) | set(r['children']))[:8])]
def mfill(r): return RED if r['f1_check'] else (AMB if r['preliminary'] else None)
# README
ws = wb.create_sheet('READ ME')
readme = [
 ['2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS', ''],
 ['Prepared for', 'SPORTFIVE Formula 1 sponsorship sales, 19 Oct 2026 (separate discovery exercise from the Clay prospect-ranking project)'],
 ['Qualification', 'Ultimate parent with valuation / market cap >= USD 1B OR cumulative funding >= USD 100M. Revenue is never used to qualify.'],
 ['Discovery sources', '40 knowledge-research category/region briefs; Apollo.io company search (total funding >= USD 100M, 3,000 records); Lusha company search (total funding >= USD 100M, 1,500 records). No paid enrichment beyond the approved search pages.'],
 ['Cross-reference', 'Every parent, alias, subsidiary and brand name and website checked against: Old Google Drive master files (all worksheets), previous prospect workbooks and CSVs (all worksheets, incl. the Wave 16 final ranking), and the Friday Clay exports (all CSVs).'],
 ['Categories', 'A = genuinely new parent (no parent, subsidiary or brand in any dataset) -> master ranking + industry tabs. B = corporate-group overlap (parent or at least one subsidiary/brand already in a dataset) -> EXISTING CORPORATE-GROUP OVERLAPS, ranked separately. C = identity or qualification uncertain -> MANUAL REVIEW.'],
 ['Scoring', 'F1 Fit /60 = audience overlap (20) + commercial synergies (20) + brand alignment (10) + international relevance (10). Financial Capacity /40 = revenue & scale (20) + valuation & funding (10) + other affordability indicators (10). Fit is scored by research judgement per parent; capacity from valuation, funding, Apollo revenue where available, ownership type, confidence and sponsorship record.'],
 ['Colour code', 'Amber row = preliminary (figures from memory or connector filter only). Red row = possible current F1 / F1-team link to verify before outreach. Confirmed current F1 sponsors are kept out of the ranking in the EXISTING F1 SPONSORS tab.'],
 ['Caveats', 'Valuations and funding are research-knowledge figures dated as shown (mostly late 2025 to mid 2026); "Verified" in Sources means re-checked against a public source on 19 Oct 2026. No figure has been invented: where unknown the cell is blank and the qualification rests on the database filter.'],
]
for rrow in readme: ws.append(rrow)
ws.column_dimensions['A'].width = 20; ws.column_dimensions['B'].width = 140
for row in ws.iter_rows():
    for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
ws['A1'].font = Font(bold=True, size=14)
# master
sheet('NEW PARENT COMPANIES (MASTER)', MH, [mrow(r, r['rank']) for _, r in A.iterrows()], MW, [mfill(r) for _, r in A.iterrows()])
# industry tabs
used = set()
for sec in NAMES:
    sub = A[A['sector_name'] == sec]
    if not len(sub): continue
    t = re.sub(r'[\[\]\*\?/\\:]', '-', sec)[:31]
    while t in used: t = t[:29] + '_2'
    used.add(t)
    sheet(t, MH, [mrow(r, r['rank']) for _, r in sub.iterrows()], MW, [mfill(r) for _, r in sub.iterrows()])
# overlaps
OH = ['Overlap Rank', 'Parent Company Name', 'HQ Country', 'Industry / Sector', 'Website', 'Existing Subsidiary / Brand(s) in datasets', 'Dataset(s)',
      'Parent itself listed?', 'Where parent is listed', 'Overlap type', 'Most Relevant Subsidiary / Brand', 'Recommended Approach', 'Why still worth approaching at parent level',
      'Valuation / Market Cap', 'Cumulative Funding', 'Qualification Criterion Met', 'F1 Fit (/60)', 'Financial Capacity (/40)', 'Total (/100)', 'Research Confidence', 'Sources & Dates', 'Possible F1 link to verify']
def otype(r):
    return 'Only in the unworked Friday Clay export (never approached)' if r['clay_only'] else 'In Old Google Drive / previous prospect workbooks (worked before)'
orows = [[r['rank'], s(r['name']), s(r['hq_country']), r['sector_name'], r['website'], s(r['existing_brands']) or ('parent itself' if r['parent_listed'] == 'yes' else ''), s(r['datasets']),
          r['parent_listed'], s(r['parent_where']), otype(r), r['brand_txt'], r['approach_txt'],
          (r['why_txt'] + ('; group-level deal not previously explored' if r['parent_listed'] == 'no' else '; parent already listed - revisit at group level with new sector/brand angle')).strip('; '),
          r['val_txt'], r['fund_txt'], r['qual'], r['fit'], r['capacity'], r['total'], r['confidence'], r['sources_txt'], s(r['f1']) if r['f1_check'] else ''] for _, r in B.iterrows()]
sheet('EXISTING CORPORATE-GROUP OVERLAPS', OH, orows, [7, 30, 14, 26, 22, 45, 30, 10, 45, 36, 26, 13, 55, 30, 22, 30, 8, 8, 8, 22, 60, 24], [mfill(r) for _, r in B.iterrows()])
# excluded
EH = ['Company', 'Website', 'Reason excluded', 'Source(s)']
erows = [[d.parent, d.domain, d.reason, d.sources] for d in dups.itertuples()] + [[e.parent, e.domain, e.reason, e.sources] for e in excl.itertuples()] + \
        [[s(r['name']), r['website'], 'does not meet the qualification (valuation < USD 1B and funding < USD 100M per research knowledge)' + (f"; {s(r['note'])}" if s(r.get('note')) else ''), ', '.join(r['sources'])] for _, r in XQ.iterrows()]
sheet('EXCLUDED DIRECT DUPLICATES', EH, erows, [32, 26, 80, 24])
# existing F1 sponsors
FH = ['Parent Company Name', 'HQ Country', 'Industry / Sector', 'Website', 'Current F1 link', 'Valuation / Market Cap', 'F1 Fit (/60)', 'Financial Capacity (/40)', 'Total (/100)', 'Sources & Dates']
sheet('EXISTING F1 SPONSORS', FH, [[s(r['name']), s(r['hq_country']), r['sector_name'], r['website'], s(r['f1']), r['val_txt'], r['fit'], r['capacity'], r['total'], r['sources_txt']] for _, r in F1.iterrows()],
      [30, 14, 26, 22, 40, 30, 8, 8, 8, 60], [RED] * len(F1))
# manual review
CH = ['Company (as found)', 'Website', 'HQ Country', 'Industry / Sector', 'Why it needs review', 'Evidence so far', 'Source(s)', 'Possible existing dataset match', 'Provisional Total (/100)']
def creason(r):
    if s(r['conf']) == 'U': return 'Company not recognised by research; identity and ultimate parent unconfirmed'
    if s(r['overlap_basis']).startswith('parent inferred'): return s(r['overlap_basis'])
    if not r['has_fin']: return 'No valuation or funding evidence found'
    if len(r['sn']) < 3: return 'Name too short to match reliably'
    return s(r['overlap_basis']) or 'Qualification or identity uncertain'
crows = [[s(r['name']), r['website'], s(r['hq_country']), r['sector_name'], creason(r), (r['val_txt'] or r['fund_txt'] or s(r['fin_basis'])), ', '.join(r['sources']),
          s(r['parent_where']) or s(r['existing_brands']), r['total']] for _, r in C.iterrows()]
sheet('MANUAL REVIEW', CH, crows, [32, 26, 14, 26, 60, 40, 24, 50, 10])
# summary
secs = A['sector_name'].value_counts()
SH = ['Metric', 'Value']
srows = [['Parents discovered (all sources, after merging duplicate records)', len(par) + len(dups)],
         ['Duplicate parent records merged', len(dups)], ['Excluded (non-prospects / not qualified)', len(excl) + len(XQ)],
         ['Confirmed current F1 sponsors set aside', len(F1)],
         ['Category A - genuinely new parents (master ranking)', len(A)],
         ['Category B - corporate-group overlaps', len(B)], ['   of which overlap only with the unworked Friday Clay export', int(B['clay_only'].sum())],
         ['   of which parent itself already listed', int((B['parent_listed'] == 'yes').sum())],
         ['Category C - manual review', len(C)], ['Preliminary rows in master ranking', int(A['preliminary'].sum())], ['', '']]
srows += [['New parents by sector: ' + k, int(v)] for k, v in secs.items()] + [['', '']]
srows += [[f'Top {i} new parent', f"{r['name']} ({r['hq_country']}) - {r['sector_name']} - total {r['total']}"] for i, (_, r) in enumerate(A.head(20).iterrows(), 1)]
sheet('SUMMARY', SH, srows, [70, 90], freeze='A2')
wb.move_sheet('SUMMARY', offset=-(len(wb.sheetnames) - 1))
wb.move_sheet('READ ME', offset=-(len(wb.sheetnames) - 1))
wb.save(OUT)
json.dump({'A': len(A), 'B': len(B), 'C': len(C), 'F1': len(F1), 'dups': len(dups), 'excluded': len(excl) + len(XQ), 'clay_only_B': int(B['clay_only'].sum()),
           'top20': A.head(20)[['name', 'hq_country', 'sector_name', 'total']].values.tolist(), 'by_sector': secs.to_dict()}, open(f'{P}/summary.json', 'w'), indent=1)
print('saved', OUT)
