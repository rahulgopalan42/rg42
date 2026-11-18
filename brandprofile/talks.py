"""Watch list: unlisted companies reported to be in funding talks that would take them over USD 150M raised or a USD 1B valuation (17 Nov 2026).
Leads only: every line rests on a press report, not on a company announcement. Source files: newsec/talks/*.jsonl (main) and known_*.jsonl
(companies already on the sheet or in the new-brands workbook). Usage: talks.py [xlsx]"""
import glob, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b, newsectors as ns, allsector as a
OUT = os.path.join(b.R, 'reports', 'F1-FUNDING-TALKS-WATCH-LIST-v2-2026-11-18.xlsx')
STATUS = {'unconfirmed': 'Unconfirmed', 'since confirmed': 'Since confirmed', 'denied or fell through': 'Denied or fell through'}
RORD = {'Global': 0, 'International': 1, 'Regional': 2, 'Domestic': 3}
# read by hand: name -> reason it is left off the watch list
DROP = {}
# same name as a company on the sheet, but a different company
NOT_SAME = {'Emulate (AI lab)'}
# what kind of talks: default is a fundraising round
TEAM = {'New York Yankees (Yankee Global Enterprises)', 'Atlanta Falcons', 'Las Vegas Raiders', 'Cleveland Browns', 'Liverpool FC', 'New York Islanders', 'Everton FC', 'Crystal Palace FC', 'Cleveland Cavaliers'}
SALE = {'Cloudnine Hospitals (Kids Clinic India)', 'Adyar Ananda Bhavan (A2B)', 'AIG Hospitals', 'Parfums de Marly', 'Arthea (formerly PDC Brands)', 'LaserAway', 'Rawlings Sporting Goods', 'SuKarne', 'Custom Ink',
        'Orbicular Pharmaceutical Technologies', 'Brunt Workwear', 'Discovery Senior Living', 'Dose', 'Iconix International', 'Javvy', 'True Religion'}
KIND = {'raise': 'Fundraising round', 'sale': 'Owner selling the company or a stake', 'team': 'Sports team stake sale'}
KORD = {'raise': 0, 'sale': 1, 'team': 2}
# the report itself said "close to" or "hopes for" the figure
BORDER = {'Dose': 'reported as "close to" USD 1B, so it may fall just short', 'True Religion': 'reported as "close to" USD 1B, so it may fall just short',
          'Everton FC': 'the owner is reported to hope for GBP 1B; analysts quoted put it nearer GBP 500M'}
# since-confirmed lines that still do not meet a line
NOT_YET = {'Adyar Ananda Bhavan (A2B)': 'No: USD 180M for a majority stake at about USD 350M, below the valuation line; the split between new and existing shares was not disclosed, so money raised is not shown'}
GENERIC = ('https://www.axios.com/pro/climate-deals',)
# who owns the company, as the report read states it (18 Nov 2026: every row names the parent company, or says there is none)
PARENT = {'Parfums de Marly': 'None: owned by an investment firm (Advent)', 'Arthea (formerly PDC Brands)': 'None: owned by an investment firm (CVC funds)', 'LaserAway': 'None: backed by an investment firm (Ares)',
          'Rawlings Sporting Goods': 'None: owned by an investment firm (Seidler Equity, 75%)', 'True Religion': 'None: owned by an investment firm (ACON)',
          'Cloudnine Hospitals (Kids Clinic India)': 'None: founders and investment firms (Permira buying 25.71% from True North)', 'Liverpool FC': 'Fenway Sports Group', 'Everton FC': 'The Friedkin Group',
          'New York Yankees (Yankee Global Enterprises)': 'None (the Steinbrenner family controls Yankee Global Enterprises)', 'Las Vegas Raiders': 'None (controlled by Mark Davis)', 'Cleveland Browns': 'None (Haslam family)',
          'Atlanta Falcons': 'None (owner Arthur Blank)', 'Adyar Ananda Bhavan (A2B)': 'None: investment firm Bodhi Tree Systems agreed to buy a majority (Nov 2026)', 'Destinus': 'None (independent company)',
          'Orbicular Pharmaceutical Technologies': 'None: backed by an investment firm (Tata Capital Healthcare Fund)', 'AIG Hospitals': 'None (founder-controlled)'}
def parent_of(d, nm, kind, sr, hv):
    if clean(d.get('parent')): return clean(d.get('parent'))
    if nm in PARENT: return PARENT[nm]
    if hv is not None: return ns.parent_txt(hv)
    if sr is not None: return a.parent_txt(sr)
    return 'None (independent company)' if kind == 'raise' else 'Not stated in the report'
clean = b.clean
def num(v): return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
def known_label(d, nm, k, sheetname, sr=None):
    if sr is not None: return 'On your sheet' + (' as ' + sheetname if sheetname and b.loose(sheetname) != b.loose(nm) else '') + ' (' + clean(sr['r'].get('sector') or sr['sector']) + ')'
    sec = re.search(r'on the sheet \((.+?)(?:, (?:private|listed|unknown|subsidiary|state[^)]*))?\)', k[1]) if k else None
    if sheetname or (k and 'on the sheet' in k[1]):
        return 'On your sheet' + (' as ' + sheetname if sheetname and b.loose(sheetname) != b.loose(nm) else '') + (' (' + sec.group(1) + ')' if sec else '')
    t = re.sub(r'(?i)^(already known|possibly known)\s*[-:]\s*', '', clean(d.get('known_as')))
    t = re.sub(r'(?i)\s*[;(]\s*on_sheet printed.*$', '', t).strip(' ;(')
    m = re.search(r'(?i)^(.*?)\s*on the sheet(?: \((.+?)(?:, (?:private|listed|unknown|subsidiary)[^)]*)?\))?(?: as (.+))?', t)
    if m:
        as_ = (m.group(3) or m.group(1) or '').strip(' :;-')
        sec2 = m.group(2) if m.group(2) and not re.search(r'(?i)same c|possibly', m.group(2)) else ''
        return 'On your sheet' + (' as ' + as_ if as_ and b.loose(as_) != b.loose(nm) else '') + (' (' + sec2 + ')' if sec2 else '')
    return 'On your lists' + (': ' + t if t else '')
def load():
    L, left, drop, onsheet, _ = ns.load()
    have = {ns.core(x['name']): x for x in L}
    K = json.load(open(os.path.join(H, 'newsec', 'known.json'), encoding='utf-8'))
    main, known, nolink, out, seen = [], [], [], [], set()
    for f in sorted(glob.glob(os.path.join(H, 'newsec', 'talks', '*.jsonl'))):
        isknown = os.path.basename(f).startswith('known_')
        for l in open(f, encoding='utf-8'):
            if not l.strip(): continue
            try: d = json.loads(l)
            except Exception: continue
            nm = clean(d.get('name')); ck = ns.core(nm) if nm not in NOT_SAME else b.loose(nm)
            if not nm or ck in seen or not clean(d.get('talks')): continue
            if nm in DROP: out.append((nm, DROP[nm])); continue
            if b.f1_link(nm)[0]: out.append((nm, 'Current F1 partner: ' + b.f1_link(nm)[0])); continue
            st = STATUS.get(clean(d.get('status')).lower(), 'Unconfirmed')
            url = clean(d.get('talks_url')); surl = clean(d.get('status_url'))
            if not url.startswith('http') or url.rstrip('/') in GENERIC: url = ''
            if not surl.startswith('http'): surl = ''
            linked = bool(url) or (st == 'Since confirmed' and bool(surl))
            k = None if nm in NOT_SAME else K.get(b.loose(nm)) or K.get(b.loose(ns.fold(nm)))
            sheetname = '' if nm in NOT_SAME else onsheet.get(b.loose(nm)) or onsheet.get(b.loose(ns.fold(nm))) or ''
            where = added = ''
            if ck in have and have[ck]['key'] == 'talks_added': added = have[ck]['tab']
            elif ck in have: where = 'In the new-brands workbook (' + have[ck]['tab'] + ')'
            sr = None if nm in NOT_SAME else ns.load.sheetrow.get(b.loose(nm)) or ns.load.sheetrow.get(b.loose(ns.fold(nm)))
            if ck not in have and (sheetname or isknown): where = known_label(d, nm, k, sheetname, sr)
            kind = clean(d.get('kind')) if clean(d.get('kind')) in KIND else 'team' if nm in TEAM else 'sale' if nm in SALE else 'raise'
            rec = {'name': nm, 'hq': ns.hq_fix(d.get('hq')), 'sector': d.get('sector') if d.get('sector') in b.FIT else '', 'theme': clean(d.get('theme')), 'desc': clean(d.get('desc')),
                   'reach': clean(d.get('reach')).title() if clean(d.get('reach')).title() in RORD else '', 'markets': clean(d.get('markets')), 'talks': clean(d.get('talks')),
                   'round': num(d.get('talks_usd_m')), 'val': num(d.get('talks_valuation_usd_m')), 'date': clean(d.get('talks_date')), 'outlet': clean(d.get('talks_outlet')), 'url': url,
                   'raised': clean(d.get('raised_so_far')), 'raised_m': num(d.get('raised_usd_m')), 'pass': clean(d.get('would_pass')), 'status': st, 'sdetail': clean(d.get('status_detail')),
                   'surl': surl, 'rationale': clean(d.get('rationale')), 'rel': d.get('rel') if d.get('rel') in (1, 2, 3, 4, 5) else 2, 'conf': clean(d.get('conf')).lower() or 'medium', 'where': where,
                   'added': added, 'kind': kind, 'parent': parent_of(d, nm, kind, sr if where.startswith('On your') else None, have.get(ck))}
            if not linked:
                if not any(x['name'] == nm for x in nolink): nolink.append(rec)
                continue
            seen.add(ck)
            # which line would it cross, from the figures reported
            total = (rec['raised_m'] or 0) + (rec['round'] or 0 if kind == 'raise' else 0)
            lines = [t for t, ok in (('USD 1B valuation', (rec['val'] or 0) >= 1000), ('USD 150M raised in total', total >= 150)) if ok]
            rec['lines'] = ' and '.join(lines) if lines else 'Not clear from the figures reported'
            if nm in BORDER: rec['lines'] += ' (' + BORDER[nm] + ')'
            rec['tab'] = added or (ns.tab_for(rec['theme'], '', rec['sector'] or 'Diversified & Other') if rec['sector'] or rec['theme'] else '')
            if added: rec['now'] = 'Yes: added to the new-brands workbook (' + added + ')' + (' on money already raised' if st == 'Unconfirmed' else '')
            elif nm in NOT_YET: rec['now'] = NOT_YET[nm]
            elif st == 'Since confirmed': rec['now'] = 'To check: deal confirmed, figures not yet read from a source page'
            elif st == 'Denied or fell through': rec['now'] = 'No'
            else: rec['now'] = 'Not yet: only if the reported ' + ('round' if kind == 'raise' else 'sale') + ' goes ahead on these terms'
            (known if where else main).append(rec)
    nolink = [x for x in nolink if (ns.core(x['name']) if x['name'] not in NOT_SAME else b.loose(x['name'])) not in seen]
    key = lambda x: (KORD[x['kind']], -(x['val'] or 0), -(x['round'] or 0), x['name'].lower())
    main.sort(key=key); known.sort(key=lambda x: ({'Unconfirmed': 0, 'Since confirmed': 1, 'Denied or fell through': 2}[x['status']], -(x['val'] or 0), -(x['round'] or 0), x['name'].lower()))
    nolink.sort(key=lambda x: x['name'].lower())
    return main, known, nolink, out
COLS = ['Company Name', 'Headquarters – City and country', 'Parent Company', 'Type of Talks', 'Status of the Talks', 'What Was Reported', 'Reported Round (USD)', 'Reported Valuation (USD)', 'Report Date', 'Reported By', 'Report Link',
        'Raised So Far (from pages read)', 'Line It Would Cross', 'Qualifies Now?', 'What Has Happened Since', 'Follow-up Link', 'Company Description', 'Sector', 'Category Tab (New Brands Workbook)', 'Geographic Reach',
        'Main Customer Markets', 'F1 Sponsorship Rationale', 'Relevance to F1 (1-5)', 'Confidence in the Report']
WIDTH = [30, 26, 34, 22, 16, 60, 16, 16, 12, 22, 44, 44, 30, 40, 50, 40, 46, 26, 28, 14, 40, 46, 10, 12]
def usd(v): return v * 1e6 if v else 'Not reported'
def since(x): return x['sdetail'] or ('No announcement found as of 17 Nov 2026' if x['status'] == 'Unconfirmed' else '')
def cells(x):
    return [x['name'], x['hq'], x['parent'], KIND[x['kind']], x['status'], x['talks'], usd(x['round']), usd(x['val']), x['date'], x['outlet'], x['url'] or 'Not captured (see follow-up link)',
            x['raised'] or 'Not found', x['lines'], x['now'], since(x), x['surl'], x['desc'], x['sector'], x['tab'], x['reach'], x['markets'], x['rationale'], x['rel'], x['conf'].title()]
KCOLS = ['Company Name', 'Where It Is On Your Lists', 'Parent Company', 'Status of the Talks', 'What Was Reported', 'Reported Round (USD)', 'Reported Valuation (USD)', 'Report Date', 'Reported By', 'Report Link',
         'What Has Happened Since', 'Follow-up Link']
KWIDTH = [30, 44, 36, 16, 64, 16, 16, 12, 24, 46, 54, 44]
def kcells(x):
    return [x['name'], x['where'], x['parent'], x['status'], x['talks'], usd(x['round']), usd(x['val']), x['date'], x['outlet'], x['url'] or 'Not captured (see follow-up link)', since(x), x['surl']]
NCOLS = ['Company Name', 'On Your Lists?', 'Parent Company', 'Status (as noted by the researcher)', 'What Was Reported', 'Reported Round (USD)', 'Reported Valuation (USD)', 'Report Date', 'Reported By', 'Researcher Note']
NWIDTH = [30, 44, 36, 18, 64, 16, 16, 12, 26, 60]
def ncells(x): return [x['name'], x['where'] or 'No', x['parent'], x['status'], x['talks'], usd(x['round']), usd(x['val']), x['date'], x['outlet'], x['sdetail']]
def write(main, known, nolink, out, path):
    import write_xlsx as wx
    from openpyxl import Workbook
    wb = Workbook(write_only=True)
    sm = Counter(x['status'] for x in main); sk = Counter(x['status'] for x in known)
    un = [x for x in main if x['status'] == 'Unconfirmed']; cf = [x for x in main if x['status'] == 'Since confirmed']
    kn = Counter(x['kind'] for x in un); added = [x for x in main if x['added']]
    ctry = Counter(x['hq'].split(',')[-1].strip() for x in main if x['hq'] != 'Not recorded'); tabs = Counter(x['tab'] or 'Not classified' for x in main)
    subs = [x for x in main + known if not x['parent'].startswith(('None', 'Not stated', 'Not confirmed', 'Parent not named'))]
    S = [('Funding talks watch list (research of 17 Nov 2026; subsidiaries included and parent companies named on 18 Nov 2026)',),
         ['Unlisted companies that the press has reported, since 1 May 2026, to be in talks to raise money or to be sold, where the deal would take them over one of your two lines: USD 150M raised in total, or a USD 1B valuation.'],
         ['These are leads, not qualified brands. Each line rests on a press report citing unnamed sources or otherwise not confirmed by the company. The outlet, date and link are given so the report can be read.'], [],
         ('Companies not on your lists',), [f"{len(main)} in total: {sm['Unconfirmed']} still unconfirmed and {sm['Since confirmed']} where the deal has since been announced."],
         [f"The {sm['Unconfirmed']} unconfirmed are {kn['raise']} fundraising rounds, {kn['sale']} companies whose owners are reported to be selling the company or a stake, and {kn['team']} sports team stake sales."],
         [f"{len(added)} now qualify outright and have been added to the new-brands workbook (now v3): " + ', '.join(x['name'] for x in added) + '.'],
         ['Two more companies found during the research, whose rounds had already been announced, were added as well: Rox (USD 100M at USD 1.3B, November 2026) and Venice AI (USD 65M at USD 1B, July 2026).'],
         ['A sale changes the owner, not the result: since 18 Nov a company bought by another group stays in as a subsidiary, with its new parent named. Sports teams pass on valuation, but a team sells sponsorship itself, so their relevance scores are low.'], [],
         ('Subsidiaries and parent companies (18 Nov 2026)',),
         [f"Subsidiaries are now included, and every row has a Parent Company column. {len(subs)} companies on this list have a parent company: " + '; '.join(f"{x['name']} ({x['parent'].split('.')[0]})" for x in subs) + '.'],
         ['Isomorphic Labs was left off on 17 Nov because its parent Alphabet owns Google, a McLaren partner. It is now on the Already On Your Lists tab, with that link stated. Companies that hold an F1 deal themselves stay off.'],
         ['For independent companies the column reads "None"; where the report names an investment firm or a family as owner, it says so.'], [],
         ('Companies already on your sheet or in the new-brands workbook',), [f"{len(known)} have a new round or sale reported ({sk['Unconfirmed']} unconfirmed, {sk['Since confirmed']} since announced). For these the talks are a buying signal and a timing cue, not a reason to add them."], [],
         ('Reported, but no link captured',), [f"{len(nolink)} more reports were seen only as a search summary or headline, so there is no link to read. They are listed on their own tab with the outlet and date, and should be looked up before use."], [],
         ('Not-on-your-lists companies by category',), ['; '.join(f'{k} {v}' for k, v in tabs.most_common()) + '.'], [],
         ('By headquarters',), ['; '.join(f'{k} {v}' for k, v in ctry.most_common()) + '.'], [],
         ('How the list was made',),
         ['Web research on 17 Nov 2026 in four areas (AI; fintech, crypto and software; defence, space, energy and mobility; consumer, health and a sweep of non-US regions). Each company was checked against your sheet, the new-brands workbook and the F1 roster, and each report was checked for a later announcement.'],
         ['It is not complete: funding talks are reported unevenly, many reports sit behind paywalls, and each area was searched a limited number of times. Re-running it every two to four weeks would keep it current.'],
         ['Figures are those the outlet reported. "Raised So Far" is taken from pages read and may be incomplete; "Line It Would Cross" is worked out from those figures. Currency conversions are approximate and stated in the text.']]
    wx.text_sheet(wb, 'Summary', S, widths=(170,))
    wx.sheet(wb, 'Talks - Unconfirmed', COLS, WIDTH, [cells(x) for x in un])
    wx.sheet(wb, 'Talks - Since Confirmed', COLS, WIDTH, [cells(x) for x in cf])
    rest = [x for x in main if x['status'] == 'Denied or fell through']
    if rest: wx.sheet(wb, 'Talks - Denied or Ended', COLS, WIDTH, [cells(x) for x in rest])
    wx.sheet(wb, 'Already On Your Lists', KCOLS, KWIDTH, [kcells(x) for x in known])
    wx.sheet(wb, 'No Link Captured', NCOLS, NWIDTH, [ncells(x) for x in nolink])
    K = [('What this is', 'A watch list of companies that do not yet qualify (or are not on your lists) but would if a reported funding round or sale goes ahead. Nothing here is confirmed unless the Status column says so.'),
         ('Parent Company', 'The company that owns it, where there is one, with any F1 link in that group. "None" = independent, or owned by an investment firm, a family or individuals (named where the report names them). "Not stated in the report" = the report read does not say who owns it.'),
         ('Type of Talks', 'Fundraising round = the company is raising new money. Owner selling the company or a stake = existing owners are reported to be exploring a sale; no new money may go in, so it can only pass on valuation. Sports team stake sale = a minority stake in a club or franchise.'),
         ('Status of the Talks', 'Unconfirmed = no announcement found by 17 Nov 2026. Since confirmed = the round or sale has been announced (details and link in the next columns). Denied or fell through = the company denied it or a later report says the talks ended.'),
         ('Reported Round / Reported Valuation', 'As the outlet reported them, in US dollars. "Not reported" where the report gave no figure.'),
         ('Line It Would Cross', 'USD 1B valuation if the reported valuation is at least USD 1B; USD 150M raised in total if the money raised so far plus the reported round reaches USD 150M.'),
         ('Qualifies Now?', 'Yes = the figures have been read from a source page and the company has been added to the new-brands workbook. Not yet = it depends on the reported deal going ahead.'),
         ('Category Tab', 'The tab the company is on, or would go on, in the new-brands workbook.'),
         ('Already On Your Lists tab', 'Companies you already have, where a new round or sale is being reported. Use it as a signal for timing an approach.'),
         ('No Link Captured tab', 'Reports seen only in a search summary or headline. The outlet and date are given; the report itself was not read.'),
         ('What to do with it', 'Check the Unconfirmed tab every two to four weeks; when a deal is announced, the company moves to the new-brands workbook with the announcement as its source.')]
    wx.text_sheet(wb, 'Key', K)
    wb.save(path)
if __name__ == '__main__':
    main, known, nolink, out = load()
    print(len(main), 'not on the lists', dict(Counter(x['status'] for x in main)), dict(Counter(x['kind'] for x in main)), '|', len(known), 'already known', dict(Counter(x['status'] for x in known)), '| no link', len(nolink), '| left off', out)
    print('lines:', dict(Counter(x['lines'] for x in main)))
    print('added:', [x['name'] for x in main if x['added']])
    if len(sys.argv) > 1 and sys.argv[1] == 'xlsx': write(main, known, nolink, out, OUT); print(OUT)
