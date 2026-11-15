"""Workbook for the user's 'Private' selection sheet (8 tabs of brands picked from the 48-tab sheet), in the listed-company format.
International and Global brands stay on their sector tabs with full details; Regional and Domestic brands go on one separate tab.
Usage: sel_build.py [check|xlsx]      (run sel_prep.py first)"""
import json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b, summary
OUT = os.path.join(b.R, 'reports', f'F1-PRIVATE-SHEET-BRAND-PROFILES-{b.DATE}.xlsx')
LOCAL = ('Regional', 'Domestic'); RD = 'Regional & Domestic'
def assemble():
    S = json.load(open(os.path.join(H, 'data', 'selection.json'), encoding='utf-8')); A = b.assemble()
    sel = {r['id']: r for r in S}; tabs = []
    for r in S:
        if r['tab'] not in tabs: tabs.append(r['tab'])
    rows = [x for x in A['rows'] if x['r']['id'] in sel]; f1x = [d for d in A['f1x'] if d['r']['id'] in sel]
    seen = {}
    for x in rows:
        x['sel'] = sel[x['r']['id']]
        x['notes'] = [(t, n.replace(f"On the '{x['r']['sector']}' tab in your sheet", f"On the '{x['sel']['tab']}' tab in your sheet")) for t, n in x['notes'] if not n.startswith('Same company as')]
        seen.setdefault((re.sub(r'[^a-z0-9]', '', x['name'].lower()), x['r']['country']), []).append(x)
    for k, g in seen.items():
        if len(g) > 1 and k[0]:
            for x in g:
                o = [y for y in g if y is not x][0]; x['notes'].append(('info', f"Same company as '{o['sel']['brand']}' on the '{o['sel']['tab']}' tab of your sheet (row {o['sel']['row']})"))
    for d in f1x: d['sel'] = sel[d['r']['id']]
    found = {x['r']['id'] for x in rows} | {d['r']['id'] for d in f1x}
    return {'S': S, 'tabs': tabs, 'rows': rows, 'f1x': f1x, 'missing': [r for r in S if r['id'] not in found], 'stat': A['stat']}
def cells(x):
    c = b.cells(x); s = x['sel']; c[20] = '; '.join(t for _, t in x['notes']) or 'None flagged'; c[23] = s['mark']; c[24] = s['brand']; c[25] = s['tab']; return c
def how(x): return 'web' if x['web'] else 'inferred' if x['basis'] == 'inferred' or x['conf'] == 'low' else 'twice'
def summary_lines(A):
    rows = A['rows']; n = len(rows); loc = [x for x in rows if x['reach'] in LOCAL]; wide = [x for x in rows if x['reach'] not in LOCAL]
    out = [(f'Brands from your "Private" sheet in the listed-company format - research summary ({b.DATE})',),
           [f"{len(A['S'])} brands on the {len(A['tabs'])} tabs of your sheet (read from Google Drive on 15 Nov 2026). {n} are profiled here; {len(A['f1x'])} are owned by current Formula 1 partners and sit on their own tab."],
           [f"{len(wide)} are International or Global and stay on their sector tab with full details. {len(loc)} are Regional or Domestic and are on the '{RD}' tab (also with full details). 'Master Brands' holds all {n}."], [],
           ('Tab in your sheet', 'Brands', 'Global', 'Internat.', 'Regional', 'Domestic', 'High', 'Medium', 'Lower', 'Large', 'Mid-level', 'Challenger', 'To Verify', 'F1 partner')]
    f1 = Counter(d['sel']['tab'] for d in A['f1x']); tot = Counter()
    for t in A['tabs']:
        L = [x for x in rows if x['sel']['tab'] == t]
        v = [len(L)] + [sum(1 for x in L if x['reach'] == k) for k in ('Global', 'International', 'Regional', 'Domestic')] + [sum(1 for x in L if x['priority'] == p) for p in ('High', 'Medium', 'Lower')] + \
            [sum(1 for x in L if x['cat'] == c) for c in ('Large', 'Mid-level', 'Challenger', 'To Verify')] + [f1[t]]
        out.append([t] + v)
        for i, a in enumerate(v): tot[i] += a
    out.append(('Total',) + tuple(tot[i] for i in range(13))); out.append([])
    out.append(('How the Regional / Domestic split was established',))
    hw = Counter((how(x), x['reach'] in LOCAL) for x in rows)
    out.append([f"Looked up on the web on 15 Nov 2026 (where the company has customers and offices): {hw[('web', True)] + hw[('web', False)]} brands, of which {hw[('web', True)]} are Regional / Domestic and {hw[('web', False)]} International / Global."])
    out.append([f"Assessed twice, the second time against the company's Wikipedia summary, with the reach known or stated: {hw[('twice', True)] + hw[('twice', False)]} brands, of which {hw[('twice', True)]} Regional / Domestic and {hw[('twice', False)]} International / Global."])
    out.append([f"Reach still inferred or profile low-confidence, not looked up on the web: {hw[('inferred', True)] + hw[('inferred', False)]} brands, of which {hw[('inferred', True)]} Regional / Domestic and {hw[('inferred', False)]} International / Global. Their Verification Notes say so."])
    for ln in A.get('accuracy', []): out.append([ln])
    out.append([])
    out.append(('What the four reach values mean',))
    out.append(['Domestic = essentially one country. Regional = several countries in one region (Europe; Gulf / Middle East; South-East Asia; Latin America; US + Canada). '
                'International = customers or operations in two or more world regions, not worldwide. Global = North America, Europe and Asia-Pacific at real scale. '
                'A company with no customers yet takes the reach of its operations. Selling software online does not by itself make a company Global.'])
    out.append([])
    out.append(('Limits to keep in mind',))
    for ln in ['Reach is a judgement on a four-step scale. A company one step from the line (Regional versus International) can reasonably be read either way: look at the "Main Customer Markets" column before discarding a Regional brand.',
               'Private companies publish no revenue or profit. Their investment category rests on funding raised and the date of the last round: it indicates capacity, it is not evidence of a marketing budget.',
               'Rows not looked up on the web rest on Crunchbase data recorded in Oct-Nov 2026, Wikipedia summaries and general knowledge: an acquisition, listing or closure during 2026 can be missing.',
               'Financial figures appear only for brands matched to a stock ticker. No figure was estimated for any private company.']: out.append([ln])
    return out
def key():
    K = [k for k in summary.KEY if k[0] not in ('Where the brands come from', 'Verification Required tab', 'Marked "x" in Your Sheet')]
    return [('Where the brands come from', 'The 8 tabs of your Google Sheet "Private" (read on 15 Nov 2026). Every brand was matched to the profile already written for it in the 48-tab brand workbook.'),
            ('Sector tabs', 'One tab per tab of your sheet, holding only the brands whose reach is International or Global, with full details, ranked by priority score.'),
            (f'{RD} tab', 'Every brand from any tab whose reach is Regional or Domestic, with the same full details, grouped by the tab it came from. The "Tab in Your Sheet" column says which.'),
            ('Master Brands tab', 'All brands together, whatever their reach.')] + K + \
           [('Verification Required tab', 'High- and Medium-priority brands with at least one point to check, whatever their reach.'), ('Marked "x" in Your Sheet', 'The mark next to the brand in your sheet, carried over unchanged.')]
def write(A, path):
    import write_xlsx as wx
    from openpyxl import Workbook
    from openpyxl.cell import WriteOnlyCell
    from openpyxl.utils import get_column_letter
    rows = A['rows']; data = {id(x): cells(x) for x in rows}; wb = Workbook(write_only=True); order = {t: i for i, t in enumerate(A['tabs'])}
    wx.sheet(wb, 'Master Brands', b.COLS, b.WIDTH, [data[id(x)] for x in rows])
    for t in A['tabs']: wx.sheet(wb, re.sub(r'[\\/*?:\[\]]', ' ', t), b.COLS, b.WIDTH, [data[id(x)] for x in rows if x['sel']['tab'] == t and x['reach'] not in LOCAL])
    wx.sheet(wb, RD, b.COLS, b.WIDTH, [data[id(x)] for x in sorted([x for x in rows if x['reach'] in LOCAL], key=lambda x: order[x['sel']['tab']])])
    wx.sheet(wb, 'Verification Required', b.COLS, b.WIDTH, [data[id(x)] for x in rows if x['verify']])
    ws = wb.create_sheet('Current F1 Partners')
    for j, w in enumerate((32, 30, 110, 12, 30), 1): ws.column_dimensions[get_column_letter(j)].width = w
    hdr = []
    for c in ['Brand', 'Tab in Your Sheet', 'Current Formula 1 Link (why it is not a prospect)', 'Marked "x" in Your Sheet', 'Brand Name in Your Sheet']:
        x = WriteOnlyCell(ws, value=c); x.font = wx.HFONT; x.fill = wx.HEAD; x.alignment = wx.HALIGN; hdr.append(x)
    ws.append(hdr)
    for d in sorted(A['f1x'], key=lambda d: (order[d['sel']['tab']], d['name'].lower())):
        out = []
        for v in (d['name'], d['sel']['tab'], d['why'], d['sel']['mark'], d['sel']['brand']):
            x = WriteOnlyCell(ws, value=v); x.alignment = wx.WRAP; out.append(x)
        ws.append(out)
    wx.text_sheet(wb, 'Research Summary', summary_lines(A), widths=(44, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 11, 10, 11))
    wx.text_sheet(wb, 'Key', key())
    wb.save(path)
def qc(A, path):
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True); res = []
    def check(name, ok, detail=''): res.append(ok); print(('PASS ' if ok else 'FAIL ') + name + (' | ' + str(detail) if detail else ''))
    def read(t):
        it = wb[t].iter_rows(values_only=True); h = list(next(it)); return h, [list(r) for r in it if r and r[0]]
    want = ['Master Brands'] + A['tabs'] + [RD, 'Verification Required', 'Current F1 Partners', 'Research Summary', 'Key']
    check('1 tabs present and in order', wb.sheetnames == want, wb.sheetnames)
    M = read('Master Brands')[1]; F = read('Current F1 Partners')[1]; sec = {t: read(t)[1] for t in A['tabs']}; L = read(RD)[1]; key = lambda n, t: (str(n), str(t))
    check('2 same 26 columns on every data tab', all(read(t)[0] == b.COLS for t in ['Master Brands', RD, 'Verification Required'] + A['tabs']))
    got = Counter(key(r[24], r[25]) for r in M) + Counter(key(r[4], r[1]) for r in F); exp = Counter(key(r['brand'], r['tab']) for r in A['S'])
    check('3 every brand of your sheet is in the workbook exactly once (Master + F1 partners tab)', got == exp, f"yours {sum(exp.values())}, workbook {sum(got.values())}, missing {list((exp - got).items())[:4]}")
    check('4 sector tabs hold only International / Global brands of that tab', all(all(r[13] in ('International', 'Global') and r[25] == t for r in v) for t, v in sec.items()))
    check(f'5 the {RD} tab holds only Regional / Domestic brands', all(r[13] in LOCAL for r in L), dict(Counter(r[13] for r in L)))
    check(f'6 sector tabs + {RD} tab = Master, no brand on two tabs', Counter(key(r[24], r[25]) for v in sec.values() for r in v) + Counter(key(r[24], r[25]) for r in L) == Counter(key(r[24], r[25]) for r in M),
          f"sector tabs {sum(len(v) for v in sec.values())} + {RD} {len(L)} = master {len(M)}")
    check('7 no blank cell in the 22 profile columns; descriptions 10-20 words', not [1 for r in M for j in range(22) if r[j] in (None, '')] and all(10 <= len(str(r[4]).split()) <= 20 for r in M))
    check('8 your marks are carried over', Counter(str(r[23] or '') for r in M) + Counter(str(r[3] or '') for r in F) == Counter(r['mark'] for r in A['S']))
    check('9 figures only for brands matched to a stock ticker', all(not isinstance(r[7], (int, float)) or (r[6] and 'Private' not in str(r[6])) for r in M))
    print(f'{sum(res)}/{len(res)} checks passed')
if __name__ == '__main__':
    A = assemble(); rows = A['rows']
    print(len(A['S']), 'brands |', len(rows), 'profiled |', len(A['f1x']), 'F1-linked |', len(A['missing']), 'not matched')
    print('reach', dict(Counter(x['reach'] for x in rows)), '| how', dict(Counter(how(x) for x in rows)), '| priority', dict(Counter(x['priority'] for x in rows)))
    if len(sys.argv) > 1 and sys.argv[1] == 'xlsx': write(A, OUT); print(OUT); qc(A, OUT)
