"""Research Summary and Key tabs of the brand workbook."""
from collections import Counter
WIDTHS = (44, 12, 9, 9, 9, 9, 10, 11, 10, 11, 10, 12, 12, 13)
KEY = [
 ('Where the brands come from', 'The 48 sector tabs of your sheet "F1-SCREEN-RECORDINGS-ALL-BRANDS-RANKED-2026-11-02-2" (read from Google Drive on 15 Nov 2026). The first tabs (Summary, Ranges check, Page check, All prospects, Already F1 sponsors) and the QC tab were left out, as you asked. Each brand stays on the tab where your sheet has it.'),
 ('Company Name', 'The company\'s proper name. Names cut short or misread in the recordings were completed only where the company was certain. The last columns show the name and tab exactly as in your sheet.'),
 ('Headquarters', 'City and country from the Crunchbase location on your sheet, with spelling and cut-off text repaired.'),
 ('F1 Investment Category', 'Estimated annual sponsorship capacity: Challenger USD 4-6M, Mid-level USD 6-12M, Large USD 12M+. "To Verify" = the evidence does not support a category.'),
 ('How the category is set', 'Listed brands found in the listed-company database: from published revenue, profit, cash and marketing spend, exactly as in the listed-company workbook. All other brands: 2% of total funding raised when the last round is within 24 months, 1% when it is 24-48 months old, nothing when older. So a recent USD 200M of funding gives Challenger, USD 300M Mid-level, USD 600M Large. No category is given to pre-revenue companies, single-project vehicles, funds, public bodies or closed companies, whatever they raised.'),
 ('Financial Capacity Confidence', 'Strong Evidence = listed and profitable, with published figures that support USD 4M+ a year. Plausible Capacity = supported by funding raised, or by published figures with a caveat (loss-making, cash-based, near-miss). Not Established = nothing in the sources supports USD 4M a year.'),
 ('Outreach Priority', 'High / Medium / Lower from the Priority Score: 60% strategic relevance (sector fit, company relevance to F1, geographic reach) and 40% financial capacity. High needs an assigned category. A low-confidence profile is capped at Medium. Closed companies and acquired companies with no category are Lower.'),
 ('Geographic Reach', 'Where the company\'s customers and operations are today. Domestic = essentially one country. Regional = several countries in one region. International = two or more world regions, not worldwide. Global = North America, Europe and Asia-Pacific at real scale. A company with no customers yet takes the reach of its operations.'),
 ('Revenue, market value, profit', 'Filled only for listed brands found in the listed-company database (SEC filings, companiesmarketcap.com, stockanalysis.com exchange lists, Nov 2026). Private companies do not publish these figures: the cells say "Not disclosed (private company)". No figure was estimated.'),
 ('Free Cash Flow / Liquidity', 'For private companies this shows the total funding raised and the date of the last round, as recorded from Crunchbase. Where the amount was shown in another currency, the USD range of the Crunchbase search it appeared in is given.'),
 ('Profile fields', 'Description, sector, reach, markets and rationale are desk assessments based on the Crunchbase facts and descriptions in your sheet and on general knowledge of each company. Brands you marked x and all High-priority brands were assessed twice, the second time against the company\'s Wikipedia summary. Most rows were not looked up one by one on the web; rows that were say so in the notes. "Profile Confidence" says how well the company is known: treat Low rows as unverified.'),
 ('Profile Confidence', 'High = well-known company, profile is reliable. Medium = partly known. Low = little is known beyond what Crunchbase shows; check before outreach.'),
 ('F1 exclusion', 'Brands that are current Formula 1 championship, team or Grand Prix partners, or the parent or subsidiary of one, are on the "Current F1 Partners" tab and not in the lists (2025-26 roster of 424 partners plus the partners found on 15 Nov 2026).'),
 ('Verification Notes', 'What to check before outreach: low-confidence profile, reach inferred, ownership not confirmed, a pending or unconfirmed corporate change, insolvency or closure, listed brand without matched figures, a link to an F1 partner. "None flagged" = no point to check was raised. The notes also carry plain information (owner, rename, same company on another row).'),
 ('Verification Required tab', 'High- and Medium-priority brands with at least one point to check. Lower-priority brands are not repeated there.'),
 ('Marked "x" in Your Sheet', 'The x you had put next to a brand in your sheet, carried over unchanged.'),
]
def lines(A, tabs):
    rows = A['rows']; B = A['B']; n = len(rows)
    out = [('Brand profiles in the listed-company format - research summary (2026-11-15)',),
           [f"{len(B):,} brands on the 48 sector tabs of your sheet. {n:,} are profiled here; {len(A['f1x'])} are current Formula 1 partners or their parents / subsidiaries and sit on their own tab."], [],
           ('Tab in your sheet', 'Brands', 'High', 'Medium', 'Lower', 'Large', 'Mid-level', 'Challenger', 'To Verify', 'Marked x', 'F1 partner', 'Low-confid.', 'Other sector', 'Check needed')]
    f1 = Counter(d['r']['sector'] for d in A['f1x']); tot = Counter()
    for t in tabs:
        L = [x for x in rows if x['r']['sector'] == t]
        v = [len(L)] + [sum(1 for x in L if x['priority'] == p) for p in ('High', 'Medium', 'Lower')] + [sum(1 for x in L if x['cat'] == c) for c in ('Large', 'Mid-level', 'Challenger', 'To Verify')] + \
            [sum(1 for x in L if x['r']['mark']), f1[t], sum(1 for x in L if x['conf'] == 'low'), sum(1 for x in L if x['sector'] != t), sum(1 for x in L if x['verify'])]
        out.append([t] + v)
        for i, a in enumerate(v): tot[i] += a
    out.append(('Total',) + tuple(tot[i] for i in range(13)))
    out.append([])
    out.append(('What kind of companies these are',))
    for k, lab in (('private', 'Private (independent, founder-, family-, PE- or VC-owned)'), ('listed', 'Listed on a stock exchange'), ('subsidiary', 'Owned by another company'), ('state-owned', 'State-owned'),
                   ('non-commercial', 'Public body, university or non-profit'), ('defunct', 'Reported closed or absorbed'), ('unknown', 'Not confirmed')):
        out.append([lab, sum(1 for x in rows if x['status'] == k)])
    out.append(['Listed brands with published figures filled in', sum(1 for x in rows if x['pub'])])
    out.append([])
    out.append(('Geographic reach',))
    for k in ('Global', 'International', 'Regional', 'Domestic'): out.append([k, sum(1 for x in rows if x['reach'] == k)])
    out.append(['of which stated in the source text', sum(1 for x in rows if x['basis'] == 'stated')])
    out.append(['of which known about the company', sum(1 for x in rows if x['basis'] == 'known')])
    out.append(['of which inferred, not confirmed (flagged)', sum(1 for x in rows if x['basis'] == 'inferred')])
    out.append([])
    out.append(('How accuracy was checked',))
    for ln in accuracy(A): out.append([ln])
    out.append([])
    out.append(('Limits to keep in mind',))
    for ln in limits(A): out.append([ln])
    return out
def flagged(x): return x['conf'] == 'low' or x['basis'] == 'inferred' or x['status'] == 'unknown'
def accuracy(A):
    rows = A['rows']; st = A['stat']; n2 = st['2x']; pct = lambda a, b: f'{100 * a / b:.0f}%' if b else '-'
    same = n2 - st['2x reach one step'] - st['2x reach differs']
    mk = [x for x in rows if x['r']['mark'] or x['r']['user_added']]; hi = [x for x in rows if x['priority'] == 'High']
    L = ['1. First pass: every brand was profiled from the Crunchbase facts on your sheet and what is known about the company, under a rule never to invent a product, owner, ticker, country or deal. '
         'Each profile carries a confidence level and says whether the reach is stated, known or inferred.',
         f"2. Second, independent pass on {n2:,} brands: every brand you marked x or added ({sum(1 for x in mk if x['checked']):,} of {len(mk):,} in the lists) and every brand that reached High priority "
         f"({sum(1 for x in hi if x['checked']):,} of {len(hi):,}). A stronger model redid the profile with the English Wikipedia summary of the company attached where one exists (used for {st['2x wiki used']:,}). "
         'Where the two passes differ, the second is used.',
         f"   Agreement between the two passes: reach identical for {same:,} ({pct(same, n2)}), one step apart for {st['2x reach one step']:,} ({pct(st['2x reach one step'], n2)}), further apart for "
         f"{st['2x reach differs']:,} ({pct(st['2x reach differs'], n2)}); ownership / listing status different for {st['2x status differs']:,} ({pct(st['2x status differs'], n2)}); "
         f"headquarters country different for {st['2x hq country differs']:,} ({pct(st['2x hq country differs'], n2)}).",
         '3. Blind web check of a random sample: 75 brands (25 High, 25 Medium, 25 Lower priority) were looked up on the web on 15 Nov 2026 without sight of the profile, then compared.',
         '   High priority (all checked twice), 25 brands: ownership / listing right for 25; reach identical for 22 and one step apart for 3; headquarters country right for 23 '
         '(the other two: a legal domicile abroad, and one company whose sources disagree).',
         '   Medium and Lower rows with no flag, 36 brands: ownership / listing right for 33; reach identical for 31 of 35, one step apart for 2, further apart for 2.',
         '   Rows carrying a flag (low confidence, reach inferred, or ownership not confirmed), 14 brands: ownership / listing right for 6 (6 of the other 8 said "not confirmed" rather than something wrong); '
         'reach identical for 4, one step apart for 3, further apart for 7.',
         '   Reading: rows without a flag are right about nine times in ten; flagged rows are unreliable on reach and ownership, and the Verification Notes say which rows those are. '
         f"The web findings were written into the {sum(1 for x in rows if x['web']):,} sampled rows they cover.",
         f"4. Formula 1 exclusion: names, parents and brands matched against the 2025-26 roster of 424 partners, then every match and every link reported by the two passes was reviewed by hand; "
         f"{len(A['f1x'])} brands were moved to the Current F1 Partners tab. Recent deals were confirmed on the web (Indra / IndraMind with Alpine, ServiceNow's purchase of Armis, Tata Motors' takeover of Iveco).",
         f"5. Financial figures: revenue, market value and profit are shown only for the {sum(1 for x in rows if x['pub']):,} brands matched to a stock ticker in the listed-company database. No figure was estimated for any private company.",
         '6. The finished workbook passes 14 automatic checks (every brand of your 48 tabs present exactly once, x marks carried over, allowed values only, no roster name in the lists, a category only where there is evidence).']
    if st['web']: L.insert(8, f"   Web verification of the uncertain rows: {st['web']:,} brands found on the web; it changed the reach for {st['web changed reach']:,} and the ownership / listing status for {st['web changed status']:,}.")
    return L
def limits(A):
    rows = A['rows']; fl = [x for x in rows if flagged(x) and not x['web']]
    by = {p: sum(1 for x in fl if x['priority'] == p) for p in ('High', 'Medium', 'Lower')}
    return [f"{len(fl):,} rows carry a flag (low confidence, reach inferred, or ownership not confirmed) and have not been looked up on the web: {by['High']} High, {by['Medium']:,} Medium, {by['Lower']:,} Lower priority. "
            'Treat their reach, ownership and description as unverified until checked. A web check of the flagged High and Medium rows and of the flagged brands you marked is prepared but could not be run in this session '
            '(the session allows a limited number of web searches).',
            'Rows not looked up on the web rest on Crunchbase data recorded in Oct-Nov 2026, Wikipedia summaries and general knowledge: an acquisition, listing or closure during 2026 can be missing.',
            'Private companies publish no revenue or profit. Their investment category rests on funding raised and the date of the last round (rule in the Key): it indicates capacity, it is not evidence of a marketing budget.',
            'Geographic reach is a judgement on a four-step scale. One-step differences between two careful assessments are normal (about one row in seven).',
            'The Crunchbase facts came from screen recordings: funding amounts and dates are as recorded, and some names were cut off or misread (flagged in the notes).',
            f"{sum(1 for x in rows if any('Same company as' in t for _, t in x['notes'])):,} rows are the same company entered twice on your sheet (old and new name, or two tabs). Both rows are kept and point to each other.",
            'Your x marks were carried over unchanged and played no part in the ranking.']
