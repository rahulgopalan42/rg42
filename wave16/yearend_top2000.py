"""Year-end close list: the 2,000 Wave 16 brands most likely to sign an F1 deal before 31 Dec 2026.
Starts from the final ranking (final_ranked.pkl, existing F1 sponsors already removed) and re-orders by a
CLOSE SCORE = 70% of the priority score + up to 30 points of 'can sign this quarter' signals.
Usage: python -I wave16/yearend_top2000.py reports/F1-Wave16-YearEnd-Top2000-2026-10.xlsx"""
import glob, json, os, re, sys
import numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font, PatternFill, Alignment
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
OUT = sys.argv[1]; N = 2000; CAP = 140          # at most 140 brands from any one sector (7%)
q = pd.read_pickle(f'{S}/final_ranked.pkl')
v2 = pd.read_pickle(f'{S}/work_maps.pkl')['v2']
ps = {}
idx = json.load(open(f'{R}/wave16/presort/index.json'))
for f in sorted(glob.glob(f'{R}/wave16/presort/out_*.json')):
    keys = idx.get(os.path.basename(f)[4:8], [])
    for r in json.load(open(f)):
        try: ps[keys[int(r[0])]] = {'scale': str(r[6]).upper()[:1], 'note': str(r[9] or '')}
        except Exception: pass

F1MKT = {'United States', 'United Kingdom', 'Germany', 'Italy', 'France', 'Netherlands', 'Spain', 'Belgium', 'Austria', 'Hungary', 'Monaco',
         'Switzerland', 'Japan', 'China', 'Singapore', 'Australia', 'Brazil', 'Mexico', 'Canada', 'Saudi Arabia', 'United Arab Emirates', 'Qatar',
         'Bahrain', 'Azerbaijan', 'Portugal', 'Sweden', 'Denmark', 'Norway', 'Ireland', 'South Korea', 'India', 'Hong Kong', 'Taiwan'}
SANCT = re.compile(r'sanction|russia|iran|belarus|syria|north korea|crimea|venezuela', re.I)
SANCT_C = {'Russia', 'Iran', 'Belarus', 'Syria', 'North Korea', 'Cuba', 'Venezuela', 'Myanmar', 'Afghanistan'}
FAST = {'Luxury, Jewellery & Watches', 'Travel, Hotels & Leisure', 'Airlines & Air Travel', 'Fashion, Apparel & Footwear', 'Beauty & Personal Care',
        'Alcoholic Drinks', 'Software, Internet & AI', 'Semiconductors & Electronics', 'Financial Services & Payments', 'Investment & Capital Markets',
        'Telecommunications', 'Automotive & Mobility', 'Video Games & Esports', 'Sports, Fitness & Events', 'Consumer Products', 'Food & Beverage',
        'Media, Entertainment & Publishing', 'Real Estate', 'Aerospace, Defence & Space', 'Gambling & Gaming Venues', 'Shipping, Maritime & Shipbuilding'}
SLOW = {'Healthcare Services', 'Education & Training', 'Staffing & HR', 'Security Services', 'Environmental & Waste Services',
        'Agriculture & Agribusiness', 'Packaging & Printing', 'Construction & Engineering', 'Building Products & Materials'}
# groups that own an F1 team or hold a current F1 / F1-team partnership: their subsidiaries are held back too
F1GROUPS = re.compile(r'\b(honda|toyota|audi|volkswagen|vw group|alphabet|google|msc|mediterranean shipping|shell|mercedes|daimler|ferrari|exor|renault|'
                      r'general motors|\bgm\b|ford motor|aramco|petronas|lvmh|heineken|red bull|amazon|salesforce|oracle|lenovo|deutsche post|dhl|rolex|'
                      r'qatar airways|emirates group|mastercard|santander|\bhp inc|hewlett|pepsico|visa inc|crypto\.com|pirelli|puma se|pvh|tommy hilfiger|'
                      r'allwyn|moet|liberty media|ineos|bwt|stake|kick streaming|bybit|globant|ibm|cisco|unilever|tag heuer|richemont|tata group|tata sons)\b', re.I)
SPON = re.compile(r'sponsor|partner(ship)?|ambassador|naming rights|official .* (supplier|partner)|campaign|marketing spend|advertis|sport|club|league|motorsport|racing', re.I)

def close(r):
    v = v2.get(r.k) or {}; p = ps.get(r.k) or {}
    text = ' '.join(str(x) for x in (r.rationale, r.review_detail, p.get('note', ''), v.get('not_a_prospect', '')))
    # hard exclusions
    if r.f1_deal: return None, 'F1 link via parent'
    if F1GROUPS.search(str(r.parent or '')): return None, 'F1 link via parent'
    if r.sector in ('Tobacco & Nicotine', 'Government, Non-profit & Associations'): return None, 'category not sellable now'
    if r.country in SANCT_C or SANCT.search(text): return None, 'sanctions / country risk'
    if p.get('scale') == 'S' or str(r.tri_scale) == 'small': return None, 'probably below USD 75M revenue'
    if r.confidence.startswith('Very low'): return None, 'database-only record, no pre-sort'
    pts, why = 0.0, []
    st = str(r.status)
    if r.ranking_type.startswith('Verified'):
        if st == 'Verified': pts += 6; why.append('financials verified')
        elif st.startswith('Partially'): pts += 4; why.append('financials partly verified')
        else: pts += 1
    else:
        sc = p.get('scale') or {'large': 'L', 'mid': 'M'}.get(str(r.tri_scale), '')
        if sc == 'L': pts += 3; why.append('known large company')
        elif sc == 'M': pts += 2
    me = str(v.get('marketing_evidence') or '')
    if me and not re.match(r'^(unknown|none|n/a|no )', me, re.I) and SPON.search(me): pts += 6; why.append('sponsorship / marketing track record')
    elif SPON.search(p.get('note', '')): pts += 3; why.append('sports / sponsorship link')
    if r.fin40 >= 30: pts += 4; why.append('strong financial capacity')
    elif r.fin40 >= 25: pts += 2
    if r.funding_100m_apollo: pts += 2; why.append('USD 100M+ funding raised')
    if r.type == 'Public Company' or str(r.apollo_exchange or ''): pts += 1
    if r.country in F1MKT: pts += 3; why.append(f'HQ in an F1 race market ({r.country})')
    if r.sector in FAST: pts += 3; why.append('fast-activation category')
    if r.sector in SLOW: pts -= 5
    if r.kind == 'division': pts -= 4; why.append('needs parent sign-off')
    if r.confidence.startswith('Low'): pts -= 2
    return round(0.7 * r.priority + pts, 1), '; '.join(why)

res = [close(r) for r in q.itertuples()]
q['close_score'] = [a for a, b in res]; q['close_why'] = [b for a, b in res]
held = q[q['close_score'].isna() & (q['close_why'] == 'F1 link via parent')].head(300)
c = q[q['close_score'].notna()].sort_values(['close_score', 'priority', 'fit60'], ascending=False)
c = c[c.groupby('sector').cumcount() < CAP].head(N).reset_index(drop=True)
c['close_rank'] = c.index + 1
assert len(c) == N and (c['f1_deal'] == '').all() and not c['f1_src'].astype(str).str.len().gt(0).any()

def tier(r):
    if r.close_rank <= 200: return 'A - call this week'
    if r.close_rank <= 800: return 'B - outreach by mid-Nov'
    return 'C - pipeline for Dec / Q1 2027'
c['tier'] = [tier(r) for r in c.itertuples()]

wb = Workbook(write_only=True)
HB = Font(bold=True, color='FFFFFF'); HF = PatternFill('solid', fgColor='1F3864')
def sheet(title, header, rows, widths):
    ws = wb.create_sheet(title[:31]); ws.freeze_panes = 'D2'
    for i, w in enumerate(widths): ws.column_dimensions[chr(65 + i) if i < 26 else 'A' + chr(65 + i - 26)].width = w
    hdr = []
    for h in header:
        x = WriteOnlyCell(ws, value=h); x.font = HB; x.fill = HF; x.alignment = Alignment(wrap_text=True, vertical='top'); hdr.append(x)
    ws.append(hdr)
    for r in rows: ws.append(['' if (isinstance(x, float) and np.isnan(x)) else x for x in r])
readme = [['F1 Wave 16 - YEAR-END CLOSE LIST: top 2,000 brands to approach for a deal signed before 31 Dec 2026'], [''],
 ['Source: F1-Wave16-FINAL-2026-10.xlsx Master Ranking (existing F1 sponsors already removed there).'],
 ['CLOSE SCORE = 70% of the Sponsorship Priority Score (F1 fit 60 + financial capacity 40) + up to 30 points of "can sign this quarter" signals:'],
 ['  +6 financials verified (+4 partly) / +3 known large company (pre-sort); +6 sponsorship or marketing track record (+3 sports link);'],
 ['  +4 strong financial capacity (30+/40; +2 for 25+); +2 USD 100M+ funding raised; +1 listed; +3 HQ in an F1 race market;'],
 ['  +3 fast-activation category (luxury, travel, airlines, fashion, beauty, drinks, tech, payments, telecom, auto, gaming, sport, media, Gulf real estate);'],
 ['  -5 slow-buying category (healthcare services, education, staffing, security, construction, building products ...); -4 division needing parent sign-off;'],
 ['  -2 low-confidence preliminary score.'],
 ['EXCLUDED: every existing F1 sponsor/partner (direct, and brands whose parent already sponsors - group deal conflicts slow a close),'],
 ['  tobacco/nicotine (F1 advertising limits), public bodies, sanctioned or high-risk countries, brands the pre-sort believes are below USD 75M,'],
 ['  and database-only records with no pre-sort. At most 140 brands per sector so the list is not one industry.'],
 ['TIERS: A (1-200) call this week; B (201-800) outreach by mid-November; C (801-2,000) December / Q1 2027 pipeline.'],
 ['Rows marked "Preliminary ranking" were not individually researched: confirm revenue and decision-maker before pitching.'],
 ['No paid Clay / Apollo / Lusha enrichment used. No outreach emails generated.']]
ws = wb.create_sheet('00 READ ME'); ws.column_dimensions['A'].width = 150
for l in readme: ws.append(l)
H = ['close rank', 'tier', 'brand', 'sector', 'website', 'country', 'CLOSE SCORE', 'PRIORITY SCORE (0-100)', 'F1 fit (0-60)', 'financial capacity (0-40)',
     'why it can close this quarter', 'ranking type', 'research confidence', 'annual revenue', 'financial criterion', 'parent company',
     'master overall rank', 'company-specific rationale', 'supporting sources']
sheet('01 Top 2000', H, ([r.close_rank, r.tier, r.name, r.sector, r.domain, r.country, r.close_score, int(r.priority), int(r.fit60), int(r.fin40),
                         r.close_why, r.ranking_type, r.confidence, r.revenue, r.criterion, r.parent, r.overall_rank, str(r.rationale)[:300], r.sources]
                        for r in c.itertuples()),
      [7, 22, 32, 26, 24, 14, 9, 9, 8, 9, 50, 18, 18, 26, 28, 24, 9, 70, 40])
sm = c.groupby('sector').agg(brands=('name', 'size'), tier_A=('tier', lambda x: (x.str.startswith('A')).sum()),
                             avg_close=('close_score', 'mean'), best=('name', 'first')).sort_values('brands', ascending=False)
sheet('02 By Sector', ['sector', 'brands in top 2000', 'tier A', 'average close score', 'top brand'],
      [[s, int(a), int(b_), round(float(d), 1), e] for s, (a, b_, d, e) in sm.iterrows()], [34, 12, 8, 12, 40])
sheet('03 Held back - F1 parent', ['master overall rank', 'brand', 'sector', 'website', 'PRIORITY SCORE', 'F1 link via parent / owner'],
      ([r.overall_rank, r.name, r.sector, r.domain, int(r.priority), r.f1_deal] for r in held.itertuples()), [9, 32, 26, 24, 9, 90])
wb.save(OUT)
c.to_pickle(f'{S}/yearend_top2000.pkl')
print('top', len(c), 'tiers', c['tier'].value_counts().to_dict(), 'verified', int(c['ranking_type'].str.startswith('Verified').sum()))
print('sectors', c['sector'].nunique(), 'countries in F1 markets', int(c['country'].isin(F1MKT).sum()))
print(c.head(30)[['close_rank', 'name', 'sector', 'country', 'close_score', 'priority']].to_string())
