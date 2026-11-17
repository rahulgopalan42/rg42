"""Watch list: unlisted companies reported to be in funding talks that would take them over USD 150M raised or a USD 1B valuation (17 Nov 2026).
Leads only: every line rests on a press report, not on a company announcement. Source files: newsec/talks/*.jsonl (main) and known_*.jsonl
(companies already on the sheet or in the new-brands workbook). Usage: talks.py [xlsx]"""
import glob, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b, newsectors as ns
OUT = os.path.join(b.R, 'reports', 'F1-FUNDING-TALKS-WATCH-LIST-2026-11-17.xlsx')
STATUS = {'unconfirmed': 'Unconfirmed', 'since confirmed': 'Since confirmed', 'denied or fell through': 'Denied or fell through'}
RORD = {'Global': 0, 'International': 1, 'Regional': 2, 'Domestic': 3}
# read by hand: name -> reason it is left off the watch list
DROP = {}
clean = b.clean
def num(v): return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
def money(m):
    if m is None: return 'Not reported'
    return f'USD {m / 1000:,.1f}bn' if m >= 1000 else f'USD {m:,.0f}M'
def load():
    L, left, drop, onsheet, _ = ns.load()
    have = {ns.core(x['name']): x for x in L}
    K = json.load(open(os.path.join(H, 'newsec', 'known.json'), encoding='utf-8'))
    main, known, out, seen = [], [], [], set()
    for f in sorted(glob.glob(os.path.join(H, 'newsec', 'talks', '*.jsonl'))):
        isknown = os.path.basename(f).startswith('known_')
        for l in open(f, encoding='utf-8'):
            if not l.strip(): continue
            try: d = json.loads(l)
            except Exception: continue
            nm = clean(d.get('name')); ck = ns.core(nm)
            if not nm or ck in seen: continue
            if not clean(d.get('talks_url')).startswith('http') or not clean(d.get('talks')): out.append((nm, 'No report with a link')); continue
            if nm in DROP: out.append((nm, DROP[nm])); continue
            if b.f1_link(nm)[0]: out.append((nm, 'Current F1 partner: ' + b.f1_link(nm)[0])); continue
            seen.add(ck)
            st = STATUS.get(clean(d.get('status')).lower(), 'Unconfirmed')
            k = K.get(b.loose(nm)) or K.get(b.loose(ns.fold(nm)))
            where = ''
            if ck in have: where = 'In the new-brands workbook (' + have[ck]['tab'] + ')'
            elif b.loose(nm) in onsheet or b.loose(ns.fold(nm)) in onsheet or isknown: where = 'On your sheet' + (': ' + clean(d.get('known_as')) if clean(d.get('known_as')) else (' (' + k[1].replace('on the sheet (', '').rstrip(')') + ')' if k and k[1].startswith('on the sheet') else ''))
            rec = {'name': nm, 'hq': ns.hq_fix(d.get('hq')), 'sector': d.get('sector') if d.get('sector') in b.FIT else '', 'theme': clean(d.get('theme')), 'desc': clean(d.get('desc')),
                   'reach': clean(d.get('reach')).title() if clean(d.get('reach')).title() in RORD else '', 'markets': clean(d.get('markets')), 'talks': clean(d.get('talks')),
                   'round': num(d.get('talks_usd_m')), 'val': num(d.get('talks_valuation_usd_m')), 'date': clean(d.get('talks_date')), 'outlet': clean(d.get('talks_outlet')), 'url': clean(d.get('talks_url')),
                   'raised': clean(d.get('raised_so_far')), 'raised_m': num(d.get('raised_usd_m')), 'pass': clean(d.get('would_pass')), 'status': st, 'sdetail': clean(d.get('status_detail')),
                   'surl': clean(d.get('status_url')), 'rationale': clean(d.get('rationale')), 'rel': d.get('rel') if d.get('rel') in (1, 2, 3, 4, 5) else 2, 'conf': clean(d.get('conf')).lower() or 'medium', 'where': where}
            # which line would it cross, from the figures reported
            total = (rec['raised_m'] or 0) + (rec['round'] or 0)
            lines = [t for t, ok in (('USD 1B valuation', (rec['val'] or 0) >= 1000), ('USD 150M raised in total', total >= 150)) if ok]
            rec['lines'] = ' and '.join(lines) if lines else 'Not clear from the figures reported' + (f" (researcher: {rec['pass']})" if rec['pass'] else '')
            rec['tab'] = ns.tab_for(rec['theme'], '', rec['sector'] or 'Diversified & Other') if rec['sector'] or rec['theme'] else ''
            (known if where else main).append(rec)
    key = lambda x: ({'Since confirmed': 0, 'Unconfirmed': 1, 'Denied or fell through': 2}[x['status']], -(x['val'] or 0), -(x['round'] or 0), x['name'].lower())
    main.sort(key=key); known.sort(key=key)
    return main, known, out
COLS = ['Company Name', 'Headquarters – City and country', 'Status of the Talks', 'What Was Reported', 'Reported Round (USD)', 'Reported Valuation (USD)', 'Report Date', 'Reported By', 'Report Link',
        'Raised So Far (from pages read)', 'Line It Would Cross', 'What Has Happened Since', 'Follow-up Link', 'Company Description', 'Sector', 'Category Tab (New Brands Workbook)', 'Geographic Reach',
        'Main Customer Markets', 'F1 Sponsorship Rationale', 'Relevance to F1 (1-5)', 'Confidence in the Report', 'Already On Your Lists?']
WIDTH = [30, 26, 16, 60, 16, 16, 12, 18, 44, 44, 26, 50, 40, 46, 26, 28, 14, 40, 46, 10, 12, 40]
def cells(x):
    return [x['name'], x['hq'], x['status'], x['talks'], x['round'] * 1e6 if x['round'] else 'Not reported', x['val'] * 1e6 if x['val'] else 'Not reported', x['date'], x['outlet'], x['url'],
            x['raised'] or 'Not found', x['lines'], x['sdetail'] or ('No announcement found as of 17 Nov 2026' if x['status'] == 'Unconfirmed' else ''), x['surl'], x['desc'], x['sector'], x['tab'], x['reach'],
            x['markets'], x['rationale'], x['rel'], x['conf'].title(), x['where'] or 'No']
def write(main, known, out, path):
    import write_xlsx as wx
    from openpyxl import Workbook
    wb = Workbook(write_only=True)
    sm = Counter(x['status'] for x in main); sk = Counter(x['status'] for x in known)
    un = [x for x in main if x['status'] == 'Unconfirmed']; cf = [x for x in main if x['status'] == 'Since confirmed']
    ctry = Counter(x['hq'].split(',')[-1].strip() for x in main if x['hq'] != 'Not recorded'); tabs = Counter(x['tab'] or 'Not classified' for x in main)
    S = [('Funding talks watch list (17 Nov 2026)',),
         ['Unlisted companies that the press has reported to be in talks to raise money since 1 May 2026, where the round would take them over one of your two lines: USD 150M raised in total, or a USD 1B valuation.'],
         ['These are leads, not qualified brands. Each line rests on a press report citing unnamed sources or otherwise not confirmed by the company. The outlet, date and link are given so the report can be read.'], [],
         ('Companies not on your lists',), [f"{len(main)} in total: {sm['Unconfirmed']} still unconfirmed, {sm['Since confirmed']} since confirmed by an announcement, {sm['Denied or fell through']} denied or fallen through."],
         [f"The {sm['Since confirmed']} since-confirmed companies now qualify outright and can move to the new-brands workbook: " + (', '.join(x['name'] for x in cf) or 'none') + '.'], [],
         ('Companies already on your sheet or in the new-brands workbook',), [f"{len(known)} have a new round reported ({sk['Unconfirmed']} unconfirmed, {sk['Since confirmed']} since confirmed). For these the talks are a buying signal, not a reason to add them."], [],
         ('Not-on-your-lists companies by category',), ['; '.join(f'{k} {v}' for k, v in tabs.most_common()) + '.'], [],
         ('By headquarters',), ['; '.join(f'{k} {v}' for k, v in ctry.most_common()) + '.'], [],
         ('How the list was made',),
         ['Web research on 17 Nov 2026 in four areas (AI; fintech, crypto and software; defence, space, energy and mobility; consumer, health and a sweep of non-US regions). Each company was checked against your sheet, the new-brands workbook and the F1 roster, and each report was checked for a later announcement.'],
         ['It is not complete: funding talks are reported unevenly, many reports sit behind paywalls, and each area was searched a limited number of times. Re-running it every two to four weeks would keep it current.'],
         ['Figures are those the outlet reported. "Raised So Far" is taken from pages read and may be incomplete; "Line It Would Cross" is worked out from those figures.']]
    wx.text_sheet(wb, 'Summary', S, widths=(170,))
    wx.sheet(wb, 'Talks - Unconfirmed', COLS, WIDTH, [cells(x) for x in un])
    wx.sheet(wb, 'Talks - Since Confirmed', COLS, WIDTH, [cells(x) for x in cf])
    rest = [x for x in main if x['status'] == 'Denied or fell through']
    if rest: wx.sheet(wb, 'Talks - Denied or Ended', COLS, WIDTH, [cells(x) for x in rest])
    wx.sheet(wb, 'Already On Your Lists', COLS, WIDTH, [cells(x) for x in known])
    K = [('What this is', 'A watch list of companies that do not yet qualify (or are not on your lists) but would if a reported funding round goes ahead. Nothing here is confirmed unless the Status column says so.'),
         ('Status of the Talks', 'Unconfirmed = no announcement found by 17 Nov 2026. Since confirmed = the round has been announced (details and link in the next columns). Denied or fell through = the company denied it or a later report says the talks ended.'),
         ('Reported Round / Reported Valuation', 'As the outlet reported them, in US dollars. "Not reported" where the report gave no figure.'),
         ('Line It Would Cross', 'USD 1B valuation if the reported valuation is at least USD 1B; USD 150M raised in total if the money raised so far plus the reported round reaches USD 150M.'),
         ('Category Tab', 'The tab the company would go on in the new-brands workbook if the round is confirmed.'),
         ('Already On Your Lists tab', 'Companies you already have, where a new round is being reported. Use it as a signal for timing an approach.'),
         ('What to do with it', 'Check the Unconfirmed tab every two to four weeks; when a round is announced, the company moves to the new-brands workbook with the announcement as its source.')]
    wx.text_sheet(wb, 'Key', K)
    wb.save(path)
if __name__ == '__main__':
    main, known, out = load()
    print(len(main), 'not on the lists', dict(Counter(x['status'] for x in main)), '|', len(known), 'already known', dict(Counter(x['status'] for x in known)), '| left off', out)
    print('lines:', dict(Counter(x['lines'] for x in main)))
    if len(sys.argv) > 1 and sys.argv[1] == 'xlsx': write(main, known, out, OUT); print(OUT)
