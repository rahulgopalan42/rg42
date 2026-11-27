"""Writes the revised-methodology workbook (called from build.py). Main tabs use the master's columns, widths, header style and frozen panes."""
import json, os, re, sys
from collections import Counter, defaultdict
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import build as B
import score as S
import backtest as BT
F = B.FMT
HEAD = PatternFill('solid', fgColor='1F3864'); HFONT = Font(bold=True, color='FFFFFF'); HALIGN = Alignment(wrap_text=True, vertical='center')
WRAP = Alignment(wrap_text=True, vertical='top'); TOP = Alignment(vertical='top'); BOLD = Font(bold=True)
FILL = {k: PatternFill('solid', fgColor=v) for k, v in {'High': 'C6EFCE', 'Medium': 'FFEB9C', 'Watchlist': 'FCE4D6', 'Low': 'EDEDED', 'To Verify': 'FCE4D6', 'Confirmed capacity': 'C6EFCE',
                                                         'Indicative capacity': 'FFEB9C', 'Unverified capacity': 'FCE4D6', 'Insufficient capacity': 'EDEDED'}.items()}
WRAPCOLS = {j + (3 if j > 7 else 0) for j in F['wrap_cols']}
def grid(wb, title, cols, widths, data, freeze='B2', height=None, wrap=None, tab=None):
    ws = wb.create_sheet(title[:31]); ws.freeze_panes = freeze
    if tab: ws.sheet_properties.tabColor = tab
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{max(len(data) + 1, 2)}'; ws.row_dimensions[1].height = F['header_height']; hdr = []
    for c in cols:
        x = WriteOnlyCell(ws, value=c); x.font = HFONT; x.fill = HEAD; x.alignment = HALIGN; hdr.append(x)
    ws.append(hdr)
    for i, r in enumerate(data, 2):
        if height: ws.row_dimensions[i].height = height
        out = []
        for j, v in enumerate(r, 1):
            x = WriteOnlyCell(ws, value=v); x.alignment = WRAP if (wrap is None or j in wrap) else TOP
            if isinstance(v, str) and v in FILL: x.fill = FILL[v]
            out.append(x)
        ws.append(out)
    return ws
def main_tab(wb, title, rows, tab=None): return grid(wb, title, B.COLS, B.WIDTH, rows, freeze=F['freeze'], height=F['row_height'], wrap=WRAPCOLS, tab=tab)
def text(wb, title, lines, width=150):
    ws = wb.create_sheet(title[:31]); ws.column_dimensions['A'].width = width
    for l in lines:
        if isinstance(l, tuple): x = WriteOnlyCell(ws, value=l[0]); x.font = BOLD; x.alignment = WRAP; ws.append([x])
        elif not l: ws.append([])
        else: x = WriteOnlyCell(ws, value=l[0] if isinstance(l, list) else l); x.alignment = WRAP; ws.append([x])
    return ws
REGION = {'North America': {'united states', 'usa', 'us', 'canada'}, 'Latin America': {'mexico', 'brazil', 'argentina', 'chile', 'colombia', 'peru', 'uruguay', 'panama', 'ecuador', 'guatemala', 'costa rica', 'dominican republic', 'venezuela', 'paraguay', 'bolivia', 'el salvador', 'honduras', 'puerto rico'},
          'Middle East': {'saudi arabia', 'united arab emirates', 'uae', 'qatar', 'kuwait', 'bahrain', 'oman', 'israel', 'turkey', 'türkiye', 'jordan', 'lebanon', 'iraq', 'egypt'},
          'Africa': {'south africa', 'nigeria', 'kenya', 'morocco', 'ghana', 'ethiopia', 'tanzania', 'mauritius', 'algeria', 'tunisia', 'angola', 'botswana', 'uganda', 'senegal', "côte d'ivoire", 'ivory coast', 'zambia', 'namibia'},
          'Asia-Pacific': {'japan', 'china', 'india', 'south korea', 'korea', 'singapore', 'australia', 'new zealand', 'indonesia', 'thailand', 'vietnam', 'malaysia', 'philippines', 'taiwan', 'hong kong', 'pakistan', 'bangladesh', 'sri lanka', 'kazakhstan', 'azerbaijan', 'uzbekistan', 'mongolia', 'cambodia', 'macau', 'brunei', 'nepal'}}
def region(d):
    c = B.clean(d.get('hq_country')).lower()
    for r, S_ in REGION.items():
        if c in S_: return r
    return 'Europe' if c else 'Not recorded'
def write(D, Q, W, I, tab, path, X=None):
    wb = Workbook(write_only=True); X = X or []
    bt = BT.run(); bs = BT.summary(bt)
    n = len(Q); pr = Counter(d['A']['priority'] for d in Q); cf = Counter(d['A']['conf'] for d in Q); tr = Counter(d['A']['tier_txt'] for d in Q); rt = Counter(d['A']['route'] for d in Q)
    own = Counter(B.clean(d.get('ownership_type')) or 'requires verification' for d in Q); reg = Counter(region(d) for d in Q); sec = Counter(d['sector'] for d in Q); reach = Counter(B.clean(d.get('reach')).title() or 'Not recorded' for d in Q)
    onsheet = [d for d in Q + W if d.get('_sheet')]; xsec = Counter(d['sector'] for d in X)
    exm = [e for e in D['excluded'] if e[1].startswith('Already on the master')]; exf = [e for e in D['excluded'] if e[1].startswith('Holds a current F1')]; exo = [e for e in D['excluded'] if e not in exm and e not in exf]
    dm = [x for x in D['dups'] if 'IN MASTER' in x[1] or x[1].startswith('master') or 'master:' in x[1]]
    checked = max(len(D['dups']) + D['raw'], sum(B.CHECKED.values()))
    clusters = sorted({d['_cluster'] for d in D['recs']} | set(D['notes']))
    done_sectors = sorted(sec, key=lambda s: -sec[s]); empty = [s for s in B.SECTORS if s not in sec]
    fmt = lambda c: '; '.join(f'{k} {v}' for k, v in c.most_common())
    SUM = [('Formula 1 prospects, non-public companies: revised methodology, research batch 1 (' + B.DATE + ')',),
           [f"{n:,} genuinely new qualified companies, ranked; {len(W):,} on the financial verification watchlist; and {len(X):,} more found on industry rankings that meet a financial threshold but have not yet been assessed one by one. "
            "None is on your master spreadsheet (PRIVATE NEW- 27_11): every line was checked against all of its tabs by name, alias and website before it was written and again when this file was built."],
           ['This is batch 1 of a larger programme. It covers fourteen sector clusters to a first depth, not every qualifying company in the world. The Research Record tab says what was covered and what is still to do.'], [],
           ('Deduplication',),
           ['Rule applied (your instruction of 27 Nov 2026): only companies on the master spreadsheet in the shared Drive folder count as duplicates. Brands on your older 48-tab sheet and names from earlier waves are not excluded.'],
           [f"Candidates checked against the master by the research: about {checked:,}. Left out because they are already on the master: {len(dm) + len(exm):,}. Left out because the brand holds a current F1 deal: {len({x[0] for x in D['dups'] if 'F1 PARTNER' in x[1]} | {e[0] for e in exf}):,}. "
            f"Left out at the build for another reason (Russian, or the name is a listed company): {len(exo)}. Found by two clusters and kept once: {len(D['xdup'])}. The Excluded tab lists them."],
           [f"{len(onsheet):,} of the delivered companies are also on your older 48-tab sheet. They are included because they are not on the master; the On Your Sheet? column says so, and column D carries your x where you had marked the brand there."], [],
           ('What is in this workbook',),
           ['Consolidated Ranking: every qualified new company, strongest outreach opportunity first, across all sectors.'],
           ['Sector tabs (your existing tab names): the same companies by sector, ranked from 1 within each tab. Domestic companies are on the Domestic tab, as in your earlier workbooks, ranked within their sector there.'],
           ['Verification Watchlist (the financial verification watchlist): attractive companies where no financial route could be shown yet, ranked on fit, timing and access, with what is still needed.'],
           ['Discovered - To Assess: companies read off a ranking page (mostly the ENR lists of US contractors and design firms, the UK top 100 contractors and a US insurance-broker ranking). Their revenue is sourced and meets a threshold, '
            'but nobody has yet confirmed that each is unlisted or written a company-specific Formula 1 case, so they are not scored or ranked. They are listed so nothing found is lost.'],
           ['Supporting Research: one row per company with ownership, every figure and its source, the route, confidence, tier, each score component, signals and sponsorships.'],
           ['Methodology, Backtest, Research Record, Excluded, Key.'], [],
           ('The new companies',),
           [f"By priority: {fmt(pr)}."], [f"By financial confidence: {fmt(cf)}."], [f"By qualification route: " + '; '.join(f'Route {k} {v}' for k, v in rt.most_common()) + '.'],
           [f"By estimated annual investment tier: {fmt(tr)}."], [f"By region of headquarters: {fmt(reg)}."], [f"By geographic reach: {fmt(reach)}."], [f"By ownership: {fmt(own)}."],
           [f"By sector ({len(sec)} sectors): {fmt(sec)}."],
           [f"Sectors with no new company yet in this batch: {', '.join(empty) or 'none'}."],
           [f"Discovered - To Assess, by sector: {fmt(xsec)}."], [],
           ('How to read the ranking',),
           ['Overall Score = financial capacity (35) + Formula 1 fit (30) + buying intent and timing (25) + decision-maker accessibility (10). 75 and above is High, 55 to 74 Medium, 35 to 54 Watchlist, below 35 Low.'],
           ['The score rewards evidence. Most companies have no dated buying signal on the pages read, so they score 0 of 25 on intent and sit in Medium or Watchlist. That is missing information, not a negative finding; a signal check on the top names would move them.'],
           ['Tiers 1 to 3 score almost the same on affordability, so the largest company is not automatically first.'], [],
           ('Limits of this batch',),
           ['Current F1 deals: every name was checked against the roster of championship and team partners. Grand Prix-level partners were then checked on the promoters\' own pages for 15 races '
            '(Abu Dhabi, Bahrain, Miami, Australia, Britain, Netherlands, Madrid, Austria, Belgium, Austin, Canada, Mexico, Monza, Japan and Singapore in part). That check removed ADNOC, Mubadala, Lunate and Miral '
            '(Yas Island), all on the Abu Dhabi promoter\'s partner page. The partner pages for Saudi Arabia, Qatar, Azerbaijan, China, Las Vegas, Brazil, Hungary, Barcelona and Monaco could not be read; '
            'searches found no race deal for the Saudi, Azerbaijani, Qatari, Chinese or Brazilian companies listed here, but confirm before approaching a state-owned company from a host country.'],
           ['MSC Mediterranean Shipping Company is kept, flagged and capped at Watchlist: its cruise division MSC Cruises is an F1 Global Partner. NEOM is kept and flagged: it backs McLaren\'s F1 Academy entry, which is not a championship, team or Grand Prix deal.'],
           ['No subscription database was used: PitchBook, Orbis, D&B Hoovers and Sales Navigator are not available to me; Crunchbase is out of allowance until 1 Dec 2026; Apollo was not used. Sources are public pages: rankings, registries, annual reports, company and owner sites, trade press.'],
           ['Web searches were limited to about 11 per cluster, so each cluster reached the best-documented companies first. Figures are as stated on the page cited; none was estimated by me.'],
           ['The investment tiers and the score weights inside each dimension are a first version. The Backtest tab shows how the routes perform on real sponsors and what I would adjust.']]
    text(wb, 'Summary', SUM)
    main_tab(wb, 'Consolidated Ranking', [B.row(d) for d in Q])
    for s in [s for s in B.SECTORS if s in tab]: main_tab(wb, re.sub(r'[\\/*?:\[\]]', ' ', s), [B.row(d) for d in tab[s]])
    if 'Domestic' in tab: main_tab(wb, 'Domestic', [B.row(d) for d in sorted(tab['Domestic'], key=lambda d: (d['sector'], d['rank_sector']))])
    main_tab(wb, 'Verification Watchlist', [B.row(d, watch=True) for d in W])
    def xrow(d):
        M = d['A']['M']; k = next((k for k in ('revenue', 'aum', 'ebitda', 'equity_funding', 'valuation', 'transaction_value', 'arr') if k in M), None)
        src = '; '.join(sorted(B.sources(d))[:2]) or 'No page recorded by the research'
        return [B.clean(d['name']), ', '.join(b for b in (B.clean(d.get('hq_city')), B.clean(d.get('hq_country'))) if b), d['sector'], B.clean(d.get('subsector')), B.clean(d.get('desc')),
                (S.LABEL[k].capitalize() + ': ' + B.figline(M, k)) if k else 'Not recorded', M[k][1] if k else '', src, B.clean(d.get('ownership_type')) or 'requires verification', B.clean(d.get('reach')).title(),
                'Confirm it is unlisted and who owns it; write the company-specific Formula 1 case; check sponsorships and signals' + ('; ' + B.clean(d['outstanding']) if B.clean(d.get('outstanding')) else ''), B.CLUSTER.get(d['_cluster'], d['_cluster'])]
    grid(wb, 'Discovered - To Assess', ['Company Name', 'Headquarters', 'Sector', 'Subsector', 'Company Description', 'Figure Found', 'Period', 'Source (ranking page)', 'Ownership', 'Geographic Reach (as recorded)',
                                        'Still Needed Before It Is Ranked', 'Research Cluster'], [34, 26, 28, 24, 50, 30, 10, 50, 22, 14, 60, 36], [xrow(d) for d in X], height=45)
    grid(wb, 'Supporting Research', B.SUPCOLS, B.SUPW, [B.suprow(d) for d in Q + W + I], freeze='B2', height=60)
    # ---- methodology
    ME = [('Revised methodology for non-public companies (governing reference: your master prompt of 27 Nov 2026)',),
          ['The full text of the master prompt is stored with the project and governs all later non-public prospecting. This tab states how it was turned into working rules.'], [],
          ('1. Three stages',), ['Discovery: any operating company whose own shares do not trade, in any sector, country or ownership form. Qualification: one financial route must be met. Prioritisation: a 100-point score ranks the qualified companies.'], [],
          ('2. Exclusions',), ['Already on the master spreadsheet (any tab); own shares publicly traded; closed or in liquidation; passive funds; single-project vehicles; the brand itself holds a current F1 championship, team or Grand Prix deal; Russian companies; sanctioned companies.'],
          ['Not excluded: sister brands and parents of F1 partners (the possible category conflict is flagged instead); operating asset managers and private equity firms; companies with no published accounts, no venture funding, no signal, or a domestic footprint.'], [],
          ('3. Qualification routes: any one is enough',),
          ['Route A (standard), any one of: total equity funding USD 100M+; annual revenue USD 150M+; ARR USD 50M+; annual EBITDA USD 20M+; valuation USD 1B+; acquisition or transaction value USD 1B+; assets under management USD 5B+; substantial paid sponsorship; documented parent or state financial backing with a commercial mandate.'],
          ['Route B (exceptional): equity funding USD 75M to below 100M, revenue USD 75M to below 150M, valuation USD 500M to below 1B, or a transaction below USD 1B, with documented supporting strength. Every exception is written in the Capacity Evidence column.'],
          ['Route C (alternative): no financials published, but at least two independent, sourced indicators of scale (for example 500+ employees, 3+ countries, 100+ stores, a credible revenue estimate of USD 150M+, paid sponsorships). Two indicators that restate one fact count once.'],
          ['No route met: the company goes to the Verification Watchlist tab, not the ranking.'], [],
          ('4. Financial confidence',),
          ['Confirmed capacity: a reported figure from the last three financial years (FY2023 or later), with its source, meets a standard threshold, and no serious strain was found.'],
          ['Indicative capacity: the route is met by an estimate, an older figure, Route B, Route C, sponsorship or backing rather than a recent reported figure.'],
          ['Unverified capacity: no route met on the pages found. Insufficient capacity: small on the figures found, loss-making and under strain. Missing information is never treated as negative evidence.'], [],
          ('5. Equity, debt and other capital',), ['Equity funding, debt, project finance, credit facilities, secondary sales, acquisition price, valuation, revenue, AUM and transaction volume are recorded as separate things. Only equity counts towards the equity threshold. Funding and valuation cap the investment tier at Tier 3, because money raised is not a marketing budget.'], [],
          ('6. Estimated annual partnership investment tier',),
          ['Tier 1 USD 20M+; Tier 2 USD 8M to below 20M; Tier 3 USD 3M to below 8M; Tier 4 USD 1M to below 3M; Tier 5 below USD 1M; Unverified. These are prospecting estimates of rights fees, not budgets or prices.'],
          ['The tier is read from the measure that suits the company type, not from one percentage of revenue. Lower bounds of Tiers 1, 2, 3, 4 in USD millions: ' + '; '.join(f"{k}: {v[0]:,} / {v[1]:,} / {v[2]:,} / {v[3]:,}" + (' of AUM' if 'asset' in k else ' of revenue' + (' or ARR' if 'software' in k else '')) for k, v in S.BANDS.items()) + '.'],
          ['Where revenue is unknown: EBITDA of 2,000 / 500 / 120 / 30; equity funding of 1,500 / 500 / 100 (Tier 3 at most); valuation or transaction value of 20,000 / 5,000 / 1,000 (Tier 3 at most).'],
          ['Adjustments: one tier lower if loss-making or under strain; one tier higher (Tier 2 at most) with documented parent or state backing; at least Tier 3 if it already pays for a top-tier sponsorship, at least Tier 4 for another paid sports sponsorship.'], [],
          ('7. The 100-point outreach score',)] + [[f'{a}: {b}'] if b else (a,) for a, b in S.RUBRIC] + [[],
          ('8. Where the earlier method (16 to 18 Nov) was inconsistent, and what changed',),
          ['Equity: the earlier test said "equity raised of USD 150M+" but, for brands on your 48-tab sheet, used the Crunchbase total-funding figure, which includes debt where Crunchbase counts it. Now only equity counts, and debt is recorded separately.'],
          ['Thresholds: equity 150M and revenue 300M became 100M and 150M, with ARR, EBITDA, AUM, backing, Route B and Route C added. The earlier test was already "any one of"; the gap was that companies with no published figure had nowhere to qualify.'],
          ['Subsidiaries: earlier a subsidiary had to pass on its own figure. Now documented parent or state backing with a commercial mandate also qualifies it, and immediate and ultimate parents are recorded.'],
          ['Funds: earlier, investment firms were removed as "funds". Now operating asset managers, wealth managers, private banks and private equity firms are eligible on AUM; passive funds and vehicles stay out.'],
          ['F1 groups: earlier, owners of F1 partners were removed. Now only the brand that holds the deal is removed; sister brands and parents stay, with the possible conflict flagged.'],
          ['Priority: earlier, priority was a count of confirmed reasons (2 = High, 1 = Medium) and fit only ordered rows inside a priority. Now one score combines capacity, fit, timing and access, and signals are no longer needed to qualify.'],
          ['Signals: the window is 24 months with more weight for the last 12; one senior marketing hire counts (five open roles are no longer required); sponsorship counts again, once as capacity and at half weight as intent.'], [],
          ('9. Sources actually used',), ['Public pages only. Not available to me: PitchBook, Moody\'s Orbis, D&B Hoovers, LinkedIn Sales Navigator. Crunchbase: allowance exhausted until 1 Dec 2026. Apollo: not used, at your request. Clay and Lusha were not used in this batch.']]
    text(wb, 'Methodology', ME)
    # ---- backtest
    P = [x for x in bt if x['private'] == 'yes']
    only_sp = sum(1 for x in P if x['revised_why'].strip() == 'existing substantial sponsorship')
    BL = [('Backtest: Formula 1 sponsors that were privately owned when they entered the sport',),
          [f"{bs['tested']} sponsors were examined; {bs['private']} were privately owned on the announcement date" + (f" (not private at entry and set aside: {', '.join(bs['not_private'])})" if bs['not_private'] else '') + '. Only figures dated before each announcement were used, and the sponsorship itself never counted as evidence. No sponsorship fee was estimated.'],
          [f"Original rules (16 to 18 Nov): captured {bs['orig_captured']} of {bs['private']}; {bs['orig_missed']} were below the thresholds on the figures found; {bs['orig_nofig']} could not be tested because no financial figure dated before the deal was found."],
          [f"Revised rules: captured {bs['rev_captured']} of {bs['private']} (" + ', '.join(f'{k.replace("Captured, ", "")} {v}' for k, v in bs['rev_routes'].items() if k.startswith('Captured')) + f"); {bs['rev_missed']} were below the thresholds; {bs['rev_nofig']} could not be tested."],
          [f"Captured only by the revised rules: {', '.join(bs['gained']) or 'none'}."], [f"Below the thresholds under both: {', '.join(bs['still_missed']) or 'none'}."],
          [f"Could not be tested: {', '.join(bs['nofig']) or 'none'}."], [],
          ('What the table shows',),
          [f"Earlier sponsorship is the commonest marker: {bs['with_prior_sponsorship']} of {bs['private']} already paid for another sports sponsorship, and for {only_sp} of them it is the only route they pass, because no financial figure was public before the deal. Counting sponsorship again was the right change."],
          [f"Timing shows up in most cases: {bs['with_signal']} of {bs['private']} had a dated funding round, expansion, senior hire, rebrand or IPO plan in the 24 months before the deal."],
          [f"Published figures are often missing: for {bs['rev_nofig']} of {bs['private']} no financial figure dated before the deal was on the pages read. Several are large family or partnership businesses (LEGO, Barilla, PwC, JCB, Bose) whose accounts exist in registries. Route C and registry filings are how to reach companies like these."],
          [f"Three entered below every threshold on the figures found ({', '.join(bs['still_missed'])}), with USD 10M to 60M of equity raised. They came in as team suppliers of kit or software, not as headline sponsors."],
          ['Size is not solvency: FTX passed every financial threshold and collapsed 14 months after its deal; Rich Energy and ROKiT had no verifiable figures and both title deals ended early. Thresholds find companies large enough to pay; they do not show that a company will keep paying.'], [],
          ('Proposed adjustments',),
          ['1. Keep the numeric thresholds as they are for now. No captured sponsor needed a lower threshold, and lowering them to catch the three small suppliers would admit thousands of companies of the same size.'],
          ['2. Check every candidate for existing sports sponsorships, not only where the research happens to find one. It is the best single marker in this sample.'],
          ['3. Add a "supplier-level" flag on the watchlist for technology companies below the thresholds whose product a team could use. That is how Castore, Keeper Security and Darktrace came in.'],
          ['4. Do not treat Unverified capacity as outreach-ready, however attractive the brand: that is the Rich Energy and ROKiT case. The watchlist already works this way.'],
          ['5. In the next batch, read registry filings for large family and partnership businesses, so fewer of them rest on Route C.'], [],
          ('Limits of this backtest',),
          ['About 50 sponsors, one research pass each, public pages only. No comparison group of similar companies that did not sponsor was built, so this shows who the rules would have found, not how many weak prospects they also let in. Several deal dates could not be fixed to the month. No sponsorship fee was estimated.'], []]
    text(wb, 'Backtest', BL)
    grid(wb, 'Backtest - Sponsors', ['Sponsor', 'F1 Property', 'Designation', 'Announced', 'Private at Entry?', 'Ownership at Entry', 'Country', 'Sector', 'Model', 'Figures Known Before the Deal', 'Sponsorships Before the Deal',
                                     'Signals in the 24 Months Before', 'Original Rules', 'Why', 'Revised Rules', 'Why', 'What Happened After', 'Notes', 'Announcement Source'],
         [28, 26, 22, 11, 10, 24, 16, 24, 8, 56, 40, 44, 16, 34, 18, 40, 36, 44, 40],
         [[x['sponsor'], x['property'], x['designation'], x['announced'], x['private'], x['ownership'], x['country'], x['sector'], x['model'], x['figures'], x['prior_sponsorships'], x['prior_signals'], x['original'], x['original_why'],
           x['revised'], x['revised_why'], x['after'], x['notes'], x['source']] for x in sorted(bt, key=lambda x: (x['private'] != 'yes', x['announced']))], height=60)
    # ---- research record
    per = defaultdict(lambda: Counter())
    for d in Q: per[d['_cluster']]['qualified'] += 1
    for d in X: per[d['_cluster']]['disc'] += 1
    for d in W: per[d['_cluster']]['watch'] += 1
    for x in D['dups']: per[x[2]]['dups'] += 1
    for e in D['excluded']: per[e[2]]['removed'] += 1
    RR = []
    for k in clusters:
        note = re.sub(r'\n{2,}', '\n', D['notes'].get(k, '').strip())
        RR.append([B.CLUSTER.get(k, k), B.CHECKED.get(k) or 'not reported', per[k]['qualified'], per[k]['watch'], per[k]['disc'], per[k]['dups'], per[k]['removed'], note[:6000] or 'No notes file was written.'])
    grid(wb, 'Research Record', ['Cluster Researched', 'Names Run Through the Duplicate Check (as reported)', 'Qualified New Companies', 'On the Verification Watchlist', 'Discovered - To Assess',
                                 'Candidates Left Out by the Research (already on the master, F1 partner or listed)', 'Lines Removed at the Build',
                                 "Researcher's Notes: pages used, regions covered, what was not reached"], [44, 14, 12, 12, 12, 18, 12, 150], RR, height=None)
    EX = [[x[0], 'Left out by the research', x[1], B.CLUSTER.get(x[2], x[2])] for x in D['dups'] if x[0]] + [[e[0], 'Removed at the build', e[1], B.CLUSTER.get(e[2], e[2])] for e in D['excluded']] + \
         [[x[0], 'Found by two clusters, kept once', 'Kept under: ' + B.CLUSTER.get(x[2], x[2]), B.CLUSTER.get(x[1], x[1])] for x in D['xdup']]
    grid(wb, 'Excluded', ['Company', 'Stage', 'Reason', 'Cluster'], [40, 26, 90, 50], sorted(EX, key=lambda r: (r[1], r[0].lower())), height=None)
    KEY = [('Key to the columns',),
           ['Columns keep the names and order of your master. Three were added after Outreach Priority: Outreach Rank (Sector), Outreach Rank (All Sectors) and Overall Score (0-100). Parent Company already existed.'],
           ['Columns B to D (template marks) are kept from the master and left empty for you; column D shows x only where you had marked the brand on your older 48-tab sheet.'],
           ['F1 Investment Category: the estimated annual partnership investment tier. Outreach Priority: High, Medium, Watchlist or Low from the overall score.'],
           ['Outreach Rank (Sector): 1 is the strongest new outreach opportunity on that tab. On the Domestic tab it is the rank among the domestic companies of the same sector. Outreach Rank (All Sectors): position in the Consolidated Ranking.'],
           ['Financial Capacity Confidence: Confirmed, Indicative, Unverified or Insufficient capacity (see Methodology). Verification Notes: why that confidence, the tier basis, conflicts to check and what is still to verify.'],
           ['Fit Score (0-100): the Formula 1 fit part of the score (30 points) shown out of 100.'],
           ['Parameter 3: Capacity Test Passed now shows the route (A, B or C) and what met it. Parameter 4a to 4d show capital, IPO, geographic and marketing or commercial signals: "Confirmed" has a date and a source from the past 24 months; "Lead only" does not.'],
           ['Parent Company: immediate parent, whether it is listed, the ultimate parent, any controlling investor, whether the brand runs its own marketing, and the backing evidence. "None (independent company)" where there is no parent.'],
           ['On Your Sheet?: "No (new brand)", or a note that the brand is on your older 48-tab sheet (allowed, because it is not on the master).'],
           ['Empty or "Not disclosed" means the page did not say. Nothing was estimated or filled in by me.']]
    text(wb, 'Key', KEY)
    wb.save(path)
