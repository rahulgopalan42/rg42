"""Usage: simple.py <batch> <output.xlsx>
One plain sheet of the new ranked brands of a batch: no extra tabs, no colours, short text. For when the full workbook is too heavy to open."""
import os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
import build as B, batch2 as X2, score as S
def short(t, n):
    t = B.clean(t)
    return t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0] + '…'
def figure(d):
    M = d['A']['M']; k = next((k for k in ('revenue', 'aum', 'equity_funding', 'valuation', 'arr', 'ebitda', 'transaction_value') if k in M), None)
    if not k: return 'Not published: qualifies on other indicators of scale' if d['A']['route'] == 'C' else 'Not published'
    v = M[k]; bits = [b for b in (v[1], v[2]) if b]
    return f"{S.LABEL[k].capitalize()}: {B.money(v[0])}" + (' (' + ', '.join(bits) + ')' if bits else '')
def parent(d):
    p = B.clean(d.get('parent_immediate'))
    return '' if p.lower() in ('', 'none', 'n/a', 'na', '-', 'unknown') else p
def main(batch, path):
    D = B.load(batch); Q, W, I, tab = B.classify(D['recs']); X = B.classify.discovered
    if batch != 'b01':
        R, raw = X2.register(D, Q, W, I, X, batch); via = {r['name']: r['via'] for r in R.values()}
    else: via = {}
    cols = [('Rank', 7), ('Company', 34), ('Priority', 11), ('Score (0-100)', 9), ('Sector', 30), ('Headquarters', 28), ('Website', 26), ('What It Does', 60), ('Ownership', 24), ('Parent Company', 28),
            ('Key Figure', 36), ('Financial Confidence', 20), ('Estimated Annual Investment', 30), ('Why Formula 1', 70), ('Found Through', 24)]
    wb = Workbook(); ws = wb.active; ws.title = 'New Brands'
    ws.append([c for c, w in cols])
    for j, (c, w) in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(j)].width = w; ws.cell(row=1, column=j).font = Font(bold=True)
    for d in Q:
        a = d['A']; site = re.sub(r'^https?://(www\.)?', '', B.clean(d.get('website'))).rstrip('/')
        ws.append([d['rank_all'], B.clean(d['name']), a['priority'], a['total'], d['sector'], ', '.join(b for b in (B.clean(d.get('hq_city')), B.clean(d.get('hq_country'))) if b), site,
                   short(d.get('desc'), 220), B.clean(d.get('ownership_type')) or 'requires verification', parent(d), figure(d), a['conf'], a['tier_txt'], short(d.get('fit_rationale'), 300),
                   via.get(B.clean(d['name'])) or d.get('_via') or 'Independent web research'])
    ws.freeze_panes = 'C2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(cols))}{len(Q) + 1}'
    wb.save(path); print(path, len(Q), 'rows', round(os.path.getsize(path) / 1024), 'KB')
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
