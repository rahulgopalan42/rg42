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
 ('Profile fields', 'Description, sector, reach, markets and rationale are desk assessments based on the Crunchbase facts and descriptions in your sheet and on general knowledge of each company. They were not looked up one by one on the web. "Profile Confidence" says how well the company is known: treat Low rows as unverified.'),
 ('Profile Confidence', 'High = well-known company, profile is reliable. Medium = partly known. Low = little is known beyond what Crunchbase shows; check before outreach.'),
 ('F1 exclusion', 'Brands that are current Formula 1 championship, team or Grand Prix partners, or the parent or subsidiary of one, are on the "Current F1 Partners" tab and not in the lists (2025-26 roster of 424 partners plus the partners found on 15 Nov 2026).'),
 ('Verification Notes', 'What to check before outreach: low-confidence profile, reach not confirmed, reported acquisition or closure, listed brand without matched figures, a link to an F1 partner.'),
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
    out.append(('Accuracy checks',))
    import bp_review
    for ln in bp_review.ACCURACY: out.append([ln])
    out.append([])
    out.append(('Limits to keep in mind',))
    for ln in bp_review.LIMITS: out.append([ln])
    return out
