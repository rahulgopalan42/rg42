"""Usage: consolidated.py <out.xlsx> [--record]
Every new brand in one workbook, in the format of the public-company master (22 columns, one tab per sector, rows by score):
the research of every batch under the revised methodology, plus the qualifying brands of the user's older 48-tab sheet that are not
on the master, re-scored under the same rubric (older.py). Tabs: All New Brands (the cross-sector ranking), one numbered tab per
sector (ranked), Verification Required (no financial route shown yet). Four columns are added at the right: Qualification Status
(so unresolved finances or ownership stand apart from fully qualified prospects), Where It Came From, Your Marking on the Older
Sheet and Template Already Built. A row whose brand already has a template on the user's trackers is filled green.
--record writes v2/delivered/older.json (the older-sheet brands delivered here count as delivered from then on)."""
import json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import build as B, score as S, older as O, public_format as P, templates as TP
from register import norm, loose
GREEN = PatternFill('solid', start_color='FF92D050', end_color='FF92D050'); TABGREEN = 'FF00B050'
STATUS_FILL = {'Fully qualified': PatternFill('solid', fgColor='C6EFCE'), 'Qualified: figure indicative': PatternFill('solid', fgColor='FFF2CC'),
               'Qualified: ownership to verify': PatternFill('solid', fgColor='FCE4D6'), 'Qualified: figure indicative and ownership to verify': PatternFill('solid', fgColor='FCE4D6'),
               'Not yet qualified: financial verification required': PatternFill('solid', fgColor='F8CBAD')}
EXTRA = ['Qualification Status', 'Where It Came From', 'Your Marking on the Older Sheet', 'Template Already Built? (Your Trackers)']
GONE = re.compile(r'(?i)\blisted\b|shares trade|closed|liquidat|absorbed|merged|defunct|bankrupt|insolven|ceased|not a separate company|f1 partner|current f1')
def status(d, watch=False):
    if watch: return 'Not yet qualified: financial verification required'
    ind = d['A']['conf'] != 'Confirmed capacity'; own = 'verification' in B.clean(d.get('ownership_type')).lower() or not B.clean(d.get('ownership_type'))
    return 'Qualified: figure indicative and ownership to verify' if ind and own else 'Qualified: ownership to verify' if own else 'Qualified: figure indicative' if ind else 'Fully qualified'
def research_cells(d, watch=False):
    c = P.cells(d, watch=watch); st = status(d, watch)
    if 'ownership to verify' in st: c[6] = 'Not listed on the pages read; owner to verify'
    names = [B.clean(d['name'])] + [B.clean(x) for x in (d.get('aliases') or []) if isinstance(x, str)]
    return c + [st, f"New research, batch {d['_batch'][1:].lstrip('0') or '1'} (found through: {d.get('_via') or 'Independent web research'})", O.marking(names, none='Not on your older sheet'), TP.note(B.clean(d['name']))]
def older_cells(d):
    a = d['A']; c = list(d['_cells']); f = d['_funding_usd_m']
    c[2] = a['tier_txt']; c[3] = a['priority']; c[19] = a['conf']; c[21] = a['total']
    note = (f"From your older sheet; re-scored under the new method on 28 Nov 2026. Qualifies on Crunchbase total funding of USD {f:,.0f}M" + (' (lower end of a Crunchbase range)' if d['_funding_range'] else '') +
            ', which can include debt and was not re-checked on a company page. F1 fit carried over from the 23 Nov assessment. ' + '; '.join(a['flags']))
    c[20] = note.strip() + ((' | ' + B.clean(c[20])) if B.clean(c[20]) else '')
    names = [d['_brand'], d['name']]; mk = 'x: template wanted' if d['_x'] else O.marking(names, d['_tab'])
    return c + ['Qualified: figure indicative', 'Your older sheet (tab: ' + O.sheet_tabs(names, d['_tab']) + '), re-scored', mk, TP.note(d['name']) or TP.note(d['_brand'])]
def main(path, record=False):
    D = B.load(None); Q, W, I, tab = B.classify(D['recs'])
    keys = set()
    for d in Q + W + I: keys |= {norm(B.clean(d['name'])), loose(B.clean(d['name']))}
    gone = {norm(n) for n, why, cl, b in D['dups'] if GONE.search(why or '')} | {norm(e[0]) for e in D['excluded'] if GONE.search(e[1] or '')}
    PT = B.patches(); old = []; skip = Counter()
    for v in O.gap():
        d = O.record(v); k = norm(d['name'])
        if k in keys or loose(d['name']) in keys: skip['also in the new research (kept there)'] += 1; continue
        if k in gone: skip['left out: the new research found it listed, closed, absorbed or an F1 partner'] += 1; continue
        for x in PT.get(k, []): B.apply_patch(d, x)
        if B.clean(d.get('f1_deal')): skip['left out: holds a current F1 deal'] += 1; continue
        old.append(d)
    B.neutral_intent(D['recs'], old)
    for d in Q + W + I: d['A'] = S.assess(d)
    for d in old: d['A'] = S.assess(d)
    Q, W, I, tab = B.classify(D['recs'])                     # ranks again with the final scores
    rows = [(d['A']['total'], d['sector'], research_cells(d), d) for d in Q] + [(d['A']['total'], d['sector'], older_cells(d), d) for d in old]
    rows.sort(key=lambda t: (-t[0], -t[3]['A']['fin'], -t[3]['A']['fit'], str(t[2][0]).lower()))
    wl = [research_cells(d, watch=True) for d in W]             # before the extra columns are added to the writer's header
    P.COLS = P.COLS + EXTRA; P.WIDTH = P.WIDTH + [26, 34, 30, 46]; n22 = len(P.COLS) - len(EXTRA)
    def paint(ws, L):
        g = 0
        for i, c in enumerate(L, 2):
            ws.cell(i, n22 + 1).fill = STATUS_FILL.get(c[n22], STATUS_FILL['Fully qualified'])
            if str(c[n22 + 3]).startswith('Yes'):
                g += 1
                for j in range(1, len(P.COLS) + 1): ws.cell(i, j).fill = GREEN
            if c[n22 + 3]: ws.cell(i, n22 + 4).alignment = P.WRAP
        if g: ws.sheet_properties.tabColor = TABGREEN
        return g
    wb = Workbook(); allr = [t[2] for t in rows]; paint(P.sheet(wb, 'All New Brands', allr, first=True), allr)
    n = 0; made = []
    for s in B.SECTORS:
        L = [t[2] for t in rows if t[1] == s]
        if not L: continue
        n += 1; t = f'{n:02d} {P.SHORT.get(s, s)}'; paint(P.sheet(wb, t, L), L); made.append((t[:31], len(L)))
    paint(P.sheet(wb, 'Verification Required', wl), wl)
    wb.save(path)
    if record: json.dump([[d['name'], ''] for d in old], open(os.path.join(H, 'delivered', 'older.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    pr = Counter(t[2][3] for t in rows); st = Counter(t[2][n22] for t in rows); src = Counter(('older sheet' if '_cells' in t[3] else 'batch ' + t[3]['_batch']) for t in rows)
    print(path, round(os.path.getsize(path) / 1e6, 2), 'MB |', len(rows), 'qualified brands |', len(made), 'sector tabs |', len(W), 'to verify')
    print('priority', dict(pr)); print('status', dict(st)); print('source', dict(src)); print('older sheet skipped', dict(skip)); print('neutral intent', S.NEUTRAL_INTENT)
    print('templates built (green):', sum(1 for t in rows if str(t[2][n22 + 3]).startswith('Yes')), '| insufficient', len(I))
    return rows, W, made
if __name__ == '__main__':
    rows, W, made = main(sys.argv[1], '--record' in sys.argv)
    for t, k in made: print(f'  {t}: {k}')
