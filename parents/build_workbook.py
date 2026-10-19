"""Parent-company prospects, step 3: score (60/40), categorise and write
'2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS.xlsx'. Input: parents.pkl, dups.pkl, excluded.pkl from consolidate.py."""
import collections, glob, json, math, os, re, sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs
R = inputs.REPO; S = inputs.S; P = inputs.P; OUT = f'{R}/reports/2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS.xlsx'
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
# web verification of top-ranked new parents (parents/verify_out, see verify_brief.md): verified figures override memory figures
VF = ['key', 'verdict', 'val_bn', 'val_basis', 'val_date', 'funding_m', 'revenue_m', 'f1_status', 'parent_ok', 'source', 'note', 'conf']
import glob as _glob
vrows = []
for f_ in sorted(_glob.glob(f'{R}/parents/verify_out/chunk_*.json')):
    try: vrows += [dict(zip(VF, r)) for r in json.load(open(f_)) if isinstance(r, list) and len(r) == 12]
    except Exception as e: print('bad verify file', f_, e)
par['web_verdict'] = ''; par['web_note'] = ''
for v in vrows:
    m = par['key'] == v['key']
    if not m.any(): continue
    par.loc[m, 'web_verdict'] = s(v['verdict']); par.loc[m, 'web_note'] = s(v['note'])
    if s(v['verdict']) in ('OK', 'CORRECTED'):
        # a memory-based "OK" must not replace a market cap taken from the 2026-10 listing; only a CORRECTED verdict or a row without a listing figure is overridden
        listed_fig = par.loc[m, 'verified_src'].astype(str).str.startswith('companiesmarketcap').any()
        if f(v['val_bn']) and (s(v['verdict']) == 'CORRECTED' or not listed_fig):
            par.loc[m, ['val_bn', 'val_basis', 'val_date']] = [f(v['val_bn']), s(v['val_basis']) or 'market cap', s(v['val_date']) or '2026-10']
        if f(v['funding_m']): par.loc[m, 'funding_m'] = f(v['funding_m'])
        if f(v['revenue_m']) and 'revenue_printed' in par: par.loc[m & par['revenue_printed'].isna(), 'revenue_printed'] = f"{f(v['revenue_m']):.0f}M"
        prev = s(par.loc[m, 'verified_src'].iloc[0])
        evidence = bool(re.search(r'homepage|wikipedia|\.', s(v['source']))) and s(v['source']).strip().lower() != 'memory'
        if evidence:      # only an actual public page counts as verification; a memory-only "OK" keeps the row preliminary
            par.loc[m, 'verified_src'] = (prev + '; ' if prev else '') + f"web check {s(v['source'])}"
            par.loc[m, 'conf'] = 'H' if s(v['conf']) == 'H' else 'M'
        else:
            par.loc[m, 'conf'] = par.loc[m, 'conf'].map(lambda c: 'M' if s(c) in ('', 'U') else s(c))
            par.loc[m, 'web_note'] = ('recalled, unconfirmed by a public source; ' + s(v['note'])).strip('; ')
    fs = s(v['f1_status'])
    if fs.startswith('current'): par.loc[m, 'f1'] = fs
    elif fs == '' and s(v['verdict']) in ('OK', 'CORRECTED'): par.loc[m, 'f1'] = par.loc[m, 'f1'].map(lambda x: '' if 'unsure' in s(x).lower() or 'verify' in s(x).lower() else s(x))
    if s(v['parent_ok']).startswith('N'): par.loc[m, 'note'] = ('owned by ' + s(v['parent_ok'])[2:].strip() + '; ' + s(par.loc[m, 'note'].iloc[0])).strip('; ')
print('web-verified rows applied', len(vrows))

# ---------------------------------------------------------------- qualification and F1 status
for c in ('a', 's', 'l', 'n'): par[c] = pd.to_numeric(par[c], errors='coerce')
par['val_bn'] = par['val_bn'].map(f); par['funding_m'] = par['funding_m'].map(f)
par['sector'] = pd.to_numeric(par['sector'], errors='coerce').fillna(48).astype(int)
par['scored'] = par['a'].notna()
for c in ('a', 's', 'l', 'n'): par[c] = par[c].fillna(1).clip(0, 4)
def rev_bn(x):
    x = s(x).upper().replace('$', '').replace(',', '')
    mm = re.match(r'([\d.]+)\s*([KMBT]?)', x)
    if not mm: return None
    v = float(mm.group(1)); return v * {'': 1e-9, 'K': 1e-6, 'M': 1e-3, 'B': 1, 'T': 1000}[mm.group(2)]
par['rev_bn'] = par['revenue_printed'].map(rev_bn) if 'revenue_printed' in par else None
par['qual'] = ''
par.loc[par['val_bn'].fillna(0) >= 1, 'qual'] = 'Valuation >= USD 1B'
m = (par['qual'] == '') & (par['funding_m'].fillna(0) >= 100); par.loc[m, 'qual'] = 'Cumulative funding >= USD 100M'
m = (par['qual'] == '') & par['apollo_funding'].notna(); par.loc[m, 'qual'] = 'Cumulative funding >= USD 100M (Apollo database filter; amount not disclosed)'
m = (par['qual'] == '') & par['sources'].map(lambda x: 'lusha' in x); par.loc[m, 'qual'] = 'Cumulative funding >= USD 100M (Lusha database filter; amount not disclosed)'
m = (par['qual'] == '') & (par['rev_bn'].fillna(0) >= 0.1); par.loc[m, 'qual'] = 'Annual revenue >= USD 100M (Apollo estimate ' + par.loc[m, 'revenue_printed'].astype(str) + ')'
m = (par['qual'] == '') & par.get('group_funding', pd.Series(False, index=par.index)).fillna(False).astype(bool)
par.loc[m, 'qual'] = 'Cumulative funding >= USD 100M at group level (subsidiary ' + par.loc[m, 'apollo_funded_child'].astype(str) + ' per Apollo filter; parent figure unverified)'
par['qualifies_k'] = par.get('qualifies_k', pd.Series('', index=par.index)).fillna('')
# knowledge says it clearly does not qualify, and no figure contradicts that -> excluded
not_q = ((par['qualifies_k'] == 'N') & (par['val_bn'].fillna(0) < 1) & (par['funding_m'].fillna(0) < 100)) | \
        ((par['qual'] == '') & par['val_bn'].notna())      # verified market cap now below USD 1B and no funding or revenue criterion
f1 = par['f1'].fillna('').astype(str)
UNSURE = re.compile(r'unsure|verify|unverified|former|past|\?|reported|possible|check|ended|expired|until 20', re.I)
par['f1_current'] = (f1.str.strip() != '') & ~f1.str.contains(UNSURE)
par['f1_check'] = (f1.str.strip() != '') & f1.str.contains(UNSURE)

# ---------------------------------------------------------------- scores
par['fit'] = (par['a'] * 5 + par['s'] * 5 + par['l'] * 2.5 + par['n'] * 2.5).round(1)
def capacity(r):
    v = r['val_bn'] if pd.notna(r['val_bn']) else 0; fu = r['funding_m'] if pd.notna(r['funding_m']) else 0; rv = r['rev_bn'] if pd.notna(r['rev_bn']) else 0
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
# ---------------------------------------------------------------- sponsorship signals (parents/signals_out, see signals_brief.md)
SG = ['key', 'headcount', 'fund_recency', 'pe_owned', 'brand_hires', 'competitor_f1', 'motorsport', 'expansion', 'race_footprint', 'founder', 'evidence', 'ceo_name', 'conf', 'flag']
sig = []
for f_ in sorted(glob.glob(f'{R}/parents/signals_out/chunk_*.json')):
    try: sig += [dict(zip(SG, r)) for r in json.load(open(f_)) if isinstance(r, list) and len(r) == 14]
    except Exception as e: print('bad signals file', f_, e)
sig = pd.DataFrame(sig, columns=SG).drop_duplicates('key')
for c in SG[1:10]: sig[c] = pd.to_numeric(sig[c], errors='coerce').fillna(0).clip(0, 4)
sig = sig.set_index('key')
par = par.join(sig.add_prefix('sg_'), on='key')
par['sg_scored'] = par['sg_headcount'].notna()
for c in SG[1:10]: par['sg_' + c] = par['sg_' + c].fillna(0)
for c in ('sg_evidence', 'sg_ceo_name', 'sg_flag', 'sg_conf'): par[c] = par[c].fillna('').astype(str)
print('signals applied to', int(par['sg_scored'].sum()), 'parents')
# capacity signals /20: headcount 6, funding recency 6, PE ownership 4, brand hires 4 (cheque size assumed USD 2.5M/yr)
par['cap_signals'] = (par['sg_headcount'] * 1.5 + par['sg_fund_recency'] * 1.5 + par['sg_pe_owned'] * 4 / 3 + par['sg_brand_hires'] * 4 / 3).round(1)
# financial evidence /20: the valuation / funding / revenue rubric compressed from 40 to 20 points
par['cap_financial'] = ((par['cap_scale'] + par['cap_val'] + par['cap_other']) / 2).round(1)
par['capacity'] = (par['cap_financial'] + par['cap_signals']).round(1)
# fit signals /20: competitor in F1 4.5, motorsport adjacency 4.5, expansion moment 4, race-market footprint 3.5, founder/CEO affinity 3.5
# race footprint: being headquartered in one host country (score 1) is not a signal; only multi-market presence (2-3) counts
par['fit_signals'] = (par['sg_competitor_f1'] * 1.5 + par['sg_motorsport'] * 1.5 + par['sg_expansion'] * 4 / 3 + (par['sg_race_footprint'] - 1).clip(lower=0) * 3.5 / 2 + par['sg_founder'] * 3.5 / 3).round(1)
par['fit_core'] = (par['fit'] * 40 / 60).round(1)
par['fit'] = (par['fit_core'] + par['fit_signals']).round(1)
par['total'] = (par['fit'] + par['capacity']).round(1)
par['preliminary'] = ((~par['scored']) | par['conf'].fillna('').isin(['L', 'U']) | (par['val_bn'].isna() & par['funding_m'].isna())) & ~par['verified_src'].astype(str).str.contains('web check')
par['confidence'] = par.apply(lambda r: 'Preliminary - not scored (connector record only)' if not r['scored'] else
                              (('Low (figures recalled, unconfirmed)' if s(r['conf']) == 'L' else 'Medium (figures recalled, unconfirmed)') if s(r['web_note']).startswith('recalled') and 'web check' not in s(r['verified_src']) else
                               {'H': 'High', 'M': 'Medium', 'L': 'Low (figures from memory)', 'U': 'Low - identity unconfirmed'}.get(s(r['conf']), 'Medium') + (' - web-verified 2026-10-19' if 'web check' in s(r['verified_src']) else '')), axis=1)
def rationale(r):
    bits = []
    if r['a'] >= 3: bits.append('strong F1 audience overlap')
    if r['s'] >= 3: bits.append('clear activation / hospitality or technology-showcase use')
    if r['l'] >= 3: bits.append('brand fits performance, innovation or premium positioning')
    if r['n'] >= 3: bits.append('active across F1 race markets')
    v = r['val_bn'] if pd.notna(r['val_bn']) else None; fu = r['funding_m'] if pd.notna(r['funding_m']) else None
    if v: bits.append(f"USD {v:,.1f}B {s(r['val_basis']) or 'valuation'}")
    elif fu: bits.append(f"USD {fu:,.0f}M raised")
    elif 'group level' in s(r['qual']): bits.append(f"group includes funded subsidiary {s(r.get('apollo_funded_child'))} (>= USD 100M raised); parent size unverified")
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
    if 'mcap' in r['sources']: src.append('Public market-cap listing (companiesmarketcap.com, 2026-10-19; market cap >= USD 1B)')
    if s(r.get('verified_src')): src.append(f"Verified: {r['verified_src']} ({TODAY})")
    return '; '.join(src)
par['sources_txt'] = par.apply(sources, axis=1)
par['val_txt'] = par.apply(lambda r: f"USD {r['val_bn']:,.1f}B ({s(r['val_basis']) or 'valuation'}, {s(r['val_date']) or 'date n/a'})" if pd.notna(r['val_bn']) and r['val_bn'] else '', axis=1)
par['fund_txt'] = par.apply(lambda r: f"USD {r['funding_m']:,.0f}M" if pd.notna(r['funding_m']) and r['funding_m'] else ('>= USD 100M (database filter, amount not disclosed)' if 'database filter' in r['qual'] else ('>= USD 100M at group level via subsidiary (amount not disclosed)' if 'group level' in r['qual'] else '')), axis=1)
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
par.loc[par['web_verdict'] == 'NOT_A_PROSPECT', 'bucket'] = 'XQ'
par.loc[par['note'].fillna('').astype(str).str.startswith('owned by') & (par['bucket'] == 'A'), 'bucket'] = 'C'
# sports clubs, teams, leagues and franchise owners are sponsorship properties, not sponsors
CLUB = re.compile(r'\bFC\b|Football|Soccer|Club\b|Yankees|Warriors|Lakers|Cowboys|Dodgers|Knicks|Celtics|Patriots|Red Sox|Real Madrid|Manchester|Juventus|Saint-Germain|Bayern|Kroenke|Fenway Sports|Liberty Media|\bNBA\b|\bNFL\b|\bMLB\b|\bNHL\b|League\b|Racing\b|Motorsport|Circuit|Grand Prix|Speedway|Raceway|Autodrom|Formula', re.I)
is_club = (par['sector'] == 6) & par['name'].astype(str).str.contains(CLUB)
par.loc[is_club, 'bucket'] = 'XQ'; par.loc[is_club, 'note'] = 'sports property / team owner - a rights holder, not a sponsor'
fl = par['sg_flag'].str.lower()
par.loc[fl.str.startswith('current f1'), 'f1_current'] = True
par.loc[fl.str.startswith('current f1') & (par['f1'].fillna('') == ''), 'f1'] = par['sg_flag']
par.loc[fl.str.contains('sanction|defunct|bankrupt|dissolved'), 'bucket'] = 'XQ'
par.loc[par['f1_current'], 'bucket'] = 'F1'
def rank(df):
    df = df.sort_values(['total', 'fit', 'val_bn'], ascending=[False, False, False], na_position='last').reset_index(drop=True)
    df.insert(0, 'rank', range(1, len(df) + 1)); return df
DROPPED = re.compile(r'DROPPED|REJECT|AUTO-REMOVED|Unsorted|UNCHECKED|PENDING', re.I)
def otype(r):
    if r['parent_listed'] == 'no': return '1 - Group-level NEW: only a subsidiary/brand was listed, the parent never was'
    if r['clay_only']: return '2 - Only in the unworked Friday Clay export (never approached)'
    if DROPPED.search(s(r['parent_where'])) and not re.search(r'MASTER REFERENCE|FINAL|Top2000|Prospect-Book', s(r['parent_where'])): return '3 - Parent listed before but only in dropped / rejected / unchecked sheets - revisit'
    return '4 - Parent already in worked datasets'
par['otype'] = par.apply(otype, axis=1)
# connector records whose parent is already in the existing datasets and were not re-scored add nothing new: count them, do not list them
par.loc[(par['bucket'] == 'A') & ~par['scored'], 'bucket'] = 'C'      # connector record not yet researched -> manual review, not the ranking
unscored_B = (par['bucket'] == 'B') & ~par['scored'] & (par['parent_listed'] == 'yes')
par.loc[unscored_B, 'bucket'] = 'BU'
# ranked parents that have no sponsorship-signals row yet: export them to parents/signals_in/chunk_NNN.json for the signals agents
# (signals_brief.md); the next build picks the results up from parents/signals_out automatically
need = par[(par['bucket'].isin(['A', 'B'])) & ~par['sg_scored']].sort_values(['bucket', 'total'], ascending=[True, False])
if len(need):
    done = {r[0] for f_ in glob.glob(f'{R}/parents/signals_in/chunk_*.json') for r in json.load(open(f_))}
    need = need[~need['key'].isin(done)]
    nxt = max([int(re.search(r'chunk_(\d+)', f_).group(1)) for f_ in glob.glob(f'{R}/parents/signals_in/chunk_*.json')] or [0]) + 1
    rows = [[r['key'], s(r['name']), s(r['domain']), s(r['hq_country']), r['sector_name'], r['type_txt'], r['val_bn'] if pd.notna(r['val_bn']) else '',
             r['funding_m'] if pd.notna(r['funding_m']) else '', s(r.get('revenue_printed', '')), '', r['bucket']] for _, r in need.iterrows()]
    for i in range(0, len(rows), 200):
        json.dump(rows[i:i + 200], open(f'{R}/parents/signals_in/chunk_{nxt:03d}.json', 'w')); nxt += 1
    print('signals still needed for', len(rows), 'ranked parents -> new signals_in chunks written')
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
      'Possible F1 link to verify', 'Preliminary?', 'Known subsidiaries / brands',
      'Fit: core (/40)', 'Fit: signals (/20)', 'Capacity: financial (/20)', 'Capacity: signals (/20)',
      'Headcount band (0-4)', 'Funding recency (0-4)', 'PE ownership (0-3)', 'Brand hires (0-3)', 'Competitor in F1 (0-3)', 'Motorsport adjacency (0-3)',
      'Expansion moment (0-3)', 'Race-market footprint (0-3)', 'Founder/CEO affinity (0-3)', 'CEO / founder', 'Signal evidence', 'Signals confidence']
MW = [7, 30, 14, 26, 22, 12, 30, 22, 30, 26, 13, 45, 9, 9, 9, 60, 22, 60, 24, 10, 40, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 22, 60, 9]
def mrow(r, rk):
    return [rk, s(r['name']), s(r['hq_country']), r['sector_name'], r['website'], r['type_txt'], r['val_txt'], r['fund_txt'], r['qual'],
            r['brand_txt'], r['approach_txt'], r['why_txt'], r['fit'], r['capacity'], r['total'], r['rationale'], r['confidence'], r['sources_txt'],
            s(r['f1']) if r['f1_check'] else '', 'Yes' if r['preliminary'] else '', '; '.join(sorted(set(r['subs']) | set(r['children']))[:8]),
            r['fit_core'], r['fit_signals'], r['cap_financial'], r['cap_signals'],
            int(r['sg_headcount']), int(r['sg_fund_recency']), int(r['sg_pe_owned']), int(r['sg_brand_hires']), int(r['sg_competitor_f1']), int(r['sg_motorsport']),
            int(r['sg_expansion']), int(r['sg_race_footprint']), int(r['sg_founder']), s(r['sg_ceo_name']), s(r['sg_evidence']), s(r['sg_conf']) if r['sg_scored'] else 'not yet scored']
def mfill(r): return RED if r['f1_check'] else (AMB if r['preliminary'] else None)
# README
ws = wb.create_sheet('READ ME')
readme = [
 ['2,000 F1 SPONSORSHIP PARENT COMPANY PROSPECTS', ''],
 ['Prepared for', 'SPORTFIVE Formula 1 sponsorship sales, 19 Oct 2026 (separate discovery exercise from the Clay prospect-ranking project)'],
 ['Qualification', 'Ultimate parent meeting ANY ONE of: valuation / market cap >= USD 1B, cumulative funding >= USD 100M, or annual revenue >= USD 100M (revenue test added 19 Oct 2026 on request; revenue figures are Apollo estimates). No restriction by ownership type or industry.'],
 ['Drive CSV brands tab', 'Brands from the Friday Clay export CSVs on Google Drive that meet the same valuation / funding parameters (revenue not counted), with their Wave 16 60/40 scores. These are existing-dataset brands, listed separately on request; they are not part of the parent-level master ranking.'],
 ['Apollo matches tab', 'Every Apollo/Lusha record that matched a company already in your files but was not re-scored, with the sheet it matched. Nothing from the pulls is hidden.'],
 ['Discovery sources', '40 knowledge-research category/region briefs; Apollo.io company search (total funding >= USD 100M, 3,000 records); Lusha company search (total funding >= USD 100M, 1,500 records). No paid enrichment beyond the approved search pages.'],
 ['Cross-reference', 'Every parent, alias, subsidiary and brand name and website checked against: Old Google Drive master files (all worksheets), previous prospect workbooks and CSVs (all worksheets, incl. the Wave 16 final ranking), and the Friday Clay exports (all CSVs).'],
 ['Categories', 'A = genuinely new parent (no parent, subsidiary or brand in any dataset) -> master ranking + industry tabs. B = corporate-group overlap (parent or at least one subsidiary/brand already in a dataset) -> EXISTING CORPORATE-GROUP OVERLAPS, ranked separately. C = identity or qualification uncertain -> MANUAL REVIEW.'],
 ['Scoring', 'F1 Fit /60 = core fit 40 (audience overlap, commercial synergies, brand alignment, international relevance; research judgement) + fit signals 20 (competitor already in F1 4.5, motorsport adjacency 4.5, expansion moment 4, race-market footprint 3.5, founder/CEO affinity 3.5). Financial Capacity /40 = financial evidence 20 (valuation / funding / revenue bands) + capacity signals 20 (headcount band 6 with 100+ staff as the floor, funding recency and investor quality 6, PE ownership 4, brand-building hires 4). Cheque size assumed: about USD 2.5M per year. Rows are ranked by Total, never by size alone.'],
 ['Signals', 'Signals stand in for the missing financials of private companies (agreed 19 Oct 2026). Deliberately NOT used: prior sponsorship spend, operating proxies (store counts etc.), debt ratings, B2B showcase story. Founder/CEO affinity: 3 documented participant (team stake, races, paddock / Drive to Survive, car collector), 2 reported interest, 1 plausible through company culture, 0 nothing known; the Signal evidence column names the facts. Signals are research knowledge, not verified records.'],
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
# new brands this round: master parents absent from the earlier 2026-10-19 delivery (parents/baseline_master.json)
_bl = json.load(open(f'{R}/parents/baseline_master.json')) if os.path.exists(f'{R}/parents/baseline_master.json') else {'names': [], 'websites': []}
_bn, _bw = set(_bl['names']), set(_bl['websites'])
_norm = lambda x: re.sub(r'[^a-z0-9]', '', str(x).lower())
NEWR = A[~A['name'].map(_norm).isin(_bn) & ~A['website'].astype(str).str.lower().isin(_bw)]
sheet('NEW BRANDS THIS ROUND', MH, [mrow(r, r['rank']) for _, r in NEWR.iterrows()], MW, [mfill(r) for _, r in NEWR.iterrows()])
print('new brands this round', len(NEWR))
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
      'Valuation / Market Cap', 'Cumulative Funding', 'Qualification Criterion Met', 'F1 Fit (/60)', 'Financial Capacity (/40)', 'Total (/100)', 'Research Confidence', 'Sources & Dates', 'Possible F1 link to verify',
      'Fit: signals (/20)', 'Capacity: signals (/20)', 'Founder/CEO affinity (0-3)', 'Competitor in F1 (0-3)', 'CEO / founder', 'Signal evidence']
orows = [[r['rank'], s(r['name']), s(r['hq_country']), r['sector_name'], r['website'], s(r['existing_brands']) or ('parent itself' if r['parent_listed'] == 'yes' else ''), s(r['datasets']),
          r['parent_listed'], s(r['parent_where']), otype(r), r['brand_txt'], r['approach_txt'],
          (r['why_txt'] + ('; group-level deal not previously explored' if r['parent_listed'] == 'no' else '; parent already listed - revisit at group level with new sector/brand angle')).strip('; '),
          r['val_txt'], r['fund_txt'], r['qual'], r['fit'], r['capacity'], r['total'], r['confidence'], r['sources_txt'], s(r['f1']) if r['f1_check'] else '',
          r['fit_signals'], r['cap_signals'], int(r['sg_founder']), int(r['sg_competitor_f1']), s(r['sg_ceo_name']), s(r['sg_evidence'])] for _, r in B.iterrows()]
sheet('EXISTING GROUP OVERLAPS', OH, orows, [7, 30, 14, 26, 22, 45, 30, 10, 45, 36, 26, 13, 55, 30, 22, 30, 8, 8, 8, 22, 60, 24, 8, 8, 8, 8, 22, 60], [mfill(r) for _, r in B.iterrows()])
# excluded
EH = ['Company', 'Website', 'Reason excluded', 'Source(s)']
erows = [[d.parent, d.domain, d.reason, d.sources] for d in dups.itertuples()] + [[e.parent, e.domain, e.reason, e.sources] for e in excl.itertuples()] + \
        [[s(r['name']), r['website'], ('web check: not a prospect - ' + s(r['web_note']) if r['web_verdict'] == 'NOT_A_PROSPECT' else 'sports property / team owner - a rights holder, not a sponsor' if is_club.get(r.name, False) else 'market cap now below USD 1B (' + r['val_txt'] + ') and no funding criterion' if r['qual'] == '' else 'does not meet the qualification (valuation < USD 1B and funding < USD 100M per research knowledge)') + (f"; {s(r['note'])}" if s(r.get('note')) else ''), ', '.join(r['sources'])] for _, r in XQ.iterrows()]
sheet('EXCLUDED DIRECT DUPLICATES', EH, erows, [32, 26, 80, 24])
# existing F1 sponsors
FH = ['Parent Company Name', 'HQ Country', 'Industry / Sector', 'Website', 'Current F1 link', 'Valuation / Market Cap', 'F1 Fit (/60)', 'Financial Capacity (/40)', 'Total (/100)', 'Sources & Dates']
sheet('EXISTING F1 SPONSORS', FH, [[s(r['name']), s(r['hq_country']), r['sector_name'], r['website'], s(r['f1']), r['val_txt'], r['fit'], r['capacity'], r['total'], r['sources_txt']] for _, r in F1.iterrows()],
      [30, 14, 26, 22, 40, 30, 8, 8, 8, 60], [RED] * len(F1))
# manual review
CH = ['Company (as found)', 'Website', 'HQ Country', 'Industry / Sector', 'Why it needs review', 'Evidence so far', 'Source(s)', 'Possible existing dataset match', 'Provisional Total (/100)']
def creason(r):
    if s(r['conf']) == 'U': return 'Company not recognised by research; identity and ultimate parent unconfirmed'
    if not r['scored']: return 'Connector record (Apollo/Lusha funding filter) not yet researched: confirm parent, qualification and fit'
    if s(r.get('note')).startswith('owned by'): return 'Web check indicates it is not the ultimate parent: ' + s(r['note'])
    if s(r['overlap_basis']).startswith('parent inferred'): return s(r['overlap_basis'])
    if not r['has_fin']: return 'No valuation or funding evidence found'
    if len(r['sn']) < 3: return 'Name too short to match reliably'
    return s(r['overlap_basis']) or 'Qualification or identity uncertain'
crows = [[s(r['name']), r['website'], s(r['hq_country']), r['sector_name'], creason(r), (r['val_txt'] or r['fund_txt'] or s(r['fin_basis'])), ', '.join(r['sources']),
          s(r['parent_where']) or s(r['existing_brands']), r['total']] for _, r in C.iterrows()]
sheet('MANUAL REVIEW', CH, crows, [32, 26, 14, 26, 60, 40, 24, 50, 10])
# Drive CSV brands (Friday Clay export, scored in Wave 16) that meet the parent-company parameters: valuation >= USD 1B or
# funding >= USD 100M (revenue does not count), no current F1 sponsors. Kept on their own tab so they do not mix with parents.
w16 = inputs.wave16_ranking()
crit = w16['criterion'].fillna('')
qual_b = (w16['funding_100m_apollo'] == True) | crit.str.contains('Valuation|Funding', regex=True)
nof1 = w16['f1_deal'].fillna('').astype(str).str.strip() == ''
D = w16[qual_b & nof1].copy()
def dcrit(r):
    bits = []
    v = s(r['valuation']); fu = s(r['funding'])
    if 'Valuation' in s(r['criterion']) and v and not v.lower().startswith('unknown'): bits.append(f"Valuation: {v}")
    if 'Funding' in s(r['criterion']) and fu and not fu.lower().startswith(('unknown', 'n/a')): bits.append(f"Funding: {fu}")
    if r['funding_100m_apollo'] == True: bits.append('Funding >= USD 100M (Apollo database filter)')
    return '; '.join(bits) or s(r['criterion'])
D['crit_txt'] = D.apply(dcrit, axis=1)
D = D.sort_values(['priority', 'fit60'], ascending=[False, False]).reset_index(drop=True)
D.insert(0, 'drank', range(1, len(D) + 1))
# does the brand's parent sit in this workbook's rankings?
pmap = {}
for df_, tag in ((A, 'master ranking'), (B, 'overlaps tab'), (F1, 'existing F1 sponsors')):
    for n_ in df_['name']: pmap[str(n_).lower().strip()] = tag
D['parent_in'] = D['parent'].fillna('').astype(str).str.lower().str.strip().map(pmap).fillna('')
DH = ['Rank', 'Brand', 'Ultimate Parent (Wave 16)', 'HQ Country', 'Industry / Sector', 'Website', 'Qualification Criterion Met', 'Wave 16 F1 Fit (/60)',
      'Wave 16 Financial Capacity (/40)', 'Wave 16 Total (/100)', 'Rationale (Wave 16)', 'Research Confidence', 'Source CSV(s) on Drive', 'Parent appears in this workbook']
drows = [[r['drank'], s(r['name']), s(r['parent']), s(r['country']), s(r['sector']), clean_domain(r['domain']), r['crit_txt'], r['fit60'], r['fin40'], r['priority'],
          s(r['rationale'])[:300], s(r['confidence']), s(r['source_csv']), r['parent_in']] for _, r in D.iterrows()]
sheet('DRIVE CSV BRANDS (QUALIFIED)', DH, drows, [7, 30, 28, 14, 26, 22, 45, 9, 9, 9, 60, 14, 24, 22])
print('drive csv brands qualified', len(D))
# Apollo/Lusha records whose parent is already in the existing datasets (not re-scored): listed for traceability
BU = par[par['bucket'] == 'BU'].sort_values('name')
BH = ['Company (as in Apollo/Lusha)', 'Website', 'HQ Country', 'Apollo revenue (est.)', 'Exchange', 'Owner per Apollo', 'Connector criterion', 'Matched in dataset(s)', 'Where the parent is listed', 'Existing subsidiary / brand found']
brows = [[s(r['name']), r['website'], s(r['hq_country']), s(r.get('revenue_printed')), s(r.get('exchange')), '; '.join(sorted(r['children']))[:120] if r['children'] else '', r['qual'],
          s(r['datasets']), s(r['parent_where']), s(r['existing_brands'])] for _, r in BU.iterrows()]
sheet('APOLLO MATCHES IN YOUR FILES', BH, brows, [32, 26, 14, 14, 10, 40, 40, 30, 60, 50])
# summary
secs = A['sector_name'].value_counts()
SH = ['Metric', 'Value']
srows = [['Parents discovered (all sources, after merging duplicate records)', len(par) + len(dups)],
         ['Duplicate parent records merged', len(dups)], ['Excluded (non-prospects / not qualified)', len(excl) + len(XQ)],
         ['Confirmed current F1 sponsors set aside', len(F1)],
         ['Category A - genuinely new parents (master ranking)', len(A)],
         ['Category B - corporate-group overlaps', len(B)], ['   of which overlap only with the unworked Friday Clay export', int(B['clay_only'].sum())],
         ['   of which parent itself already listed', int((B['parent_listed'] == 'yes').sum())]] + \
        [['   Overlap type ' + k, int(v)] for k, v in B['otype'].value_counts().sort_index().items()] + [
         ['Headline: share of all qualified parents already present in existing datasets', f"{len(B) / max(1, len(A) + len(B)):.0%}"],
         ['Category C - manual review', len(C)], ['Drive CSV brands meeting valuation/funding parameters (separate tab)', len(D)], ['Apollo/Lusha records whose parent is already in existing datasets (not re-scored; listed on APOLLO MATCHES IN YOUR FILES)', int(unscored_B.sum())], ['Preliminary rows in master ranking', int(A['preliminary'].sum())], ['New parents added this round (not in the earlier 2026-10-19 sheet; NEW BRANDS THIS ROUND tab)', len(NEWR)], ['', '']]
srows += [['New parents by sector: ' + k, int(v)] for k, v in secs.items()] + [['', '']]
srows += [[f'Top {i} new parent', f"{r['name']} ({r['hq_country']}) - {r['sector_name']} - total {r['total']}"] for i, (_, r) in enumerate(A.head(20).iterrows(), 1)]
sheet('SUMMARY', SH, srows, [70, 90], freeze='A2')
for t in ('DRIVE CSV BRANDS (QUALIFIED)', 'EXISTING GROUP OVERLAPS', 'NEW BRANDS THIS ROUND'):
    wb.move_sheet(t, offset=-(wb.sheetnames.index(t) - wb.sheetnames.index('NEW PARENT COMPANIES (MASTER)') - 1))
wb.move_sheet('SUMMARY', offset=-(len(wb.sheetnames) - 1))
wb.move_sheet('READ ME', offset=-(len(wb.sheetnames) - 1))
wb.save(OUT)
json.dump({'A': len(A), 'B': len(B), 'C': len(C), 'F1': len(F1), 'dups': len(dups), 'excluded': len(excl) + len(XQ), 'clay_only_B': int(B['clay_only'].sum()),
           'top20': A.head(20)[['name', 'hq_country', 'sector_name', 'total']].values.tolist(), 'by_sector': secs.to_dict()}, open(f'{P}/summary.json', 'w'), indent=1)
print('saved', OUT)
