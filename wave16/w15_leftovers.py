"""Wave 15 completion: brands from the Wave 15 unchecked database sweep that are NOT in the Friday Clay export
(so Wave 16 cannot reassess them) and NOT already in the Drive master files or a delivered prospect list.
They get the same preliminary 60/40 score from their database row. Writes w15_left.pkl."""
import sys
import openpyxl, pandas as pd
R = '/home/user/rg42'; S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
sys.path.insert(0, f'{R}/wave16')
from dedupe_v2 import regdom, strict, lislug
from sectors_v3 import sector_of_industry
import scoring_v3 as sc
nd = pd.read_pickle(f'{S}/new_dedup_v2.pkl'); allr = pd.read_pickle(f'{S}/new_all.pkl')
w16d = set(nd['rd']) | {regdom(d) for d in allr['domain']}; w16n = set(nd['sn']) | set(allr['name'].map(strict)); w16d.discard('')
old = pd.read_pickle(f'{S}/old_v2.pkl'); ex = old[old['category'].isin(['Old master files (Drive)', 'Earlier wave'])]
exd = {regdom(d) for d in ex['domain']} - {''}; exn = set(ex['name'].map(strict)) - {''}; exl = {lislug(u) for u in ex['linkedin']} - {''}
wb = openpyxl.load_workbook(f'{R}/reports/F1-Wave15-Database-Sweep-UNCHECKED-2026-10.xlsx', read_only=True)
rows = []
for ws in wb.worksheets:
    if ws.title.startswith(('00', '99')): continue
    it = ws.iter_rows(values_only=True); h = [str(x or '').strip().lower() for x in next(it)]
    for r in it:
        d = dict(zip(h, r))
        nm = str(d.get('company') or '').strip()
        if not nm: continue
        rd, sn, li = regdom(d.get('website')), strict(nm), lislug(d.get('linkedin'))
        if (rd and rd in w16d) or sn in w16n: continue                     # reassessed inside Wave 16
        if (rd and rd in exd) or (sn and sn in exn) or (li and li in exl): continue   # already delivered / in master
        rows.append({'name': nm, 'domain': d.get('website') or '', 'country': d.get('country') or '', 'w15_tab': ws.title,
                     'route': d.get('qualifying route') or '', 'band': str(d.get('revenue band (database)') or ''),
                     'size_n': d.get('staff'), 'type': d.get('ownership') or '', 'industry': d.get('database industry') or '',
                     'linkedin': d.get('linkedin') or '', 'flags': d.get('flags') or '', 'rd': rd, 'sn': sn})
w = pd.DataFrame(rows).drop_duplicates('sn')
def size_band(n):
    try: n = int(n)
    except Exception: return ''
    return '10,001+' if n > 10000 else '5,001-10,000' if n > 5000 else '1,001-5,000' if n > 1000 else '501-1,000' if n > 500 else '201-500'
w['size'] = w['size_n'].map(size_band); w['description'] = ''; w['sector'] = w['industry'].map(sector_of_industry)
a, s, l, i = sc.prog_fit_df(w)
fit = [[min(17, round(x * 20)), min(17, round(y * 20)), min(9, round(z * 10)), min(9, round(v * 10))] for x, y, z, v in zip(a, s, l, i)]
B = {'75M-200M': '75M-200M', '200M-500M': '200M-500M', '500M-1B': '500M-1B', '1B-10B': '1B-10B', '10B-100B': '10B-100B', '100B-1T': '100B-1T'}
fin = [sc.prog_fin(B.get(b, ''), 'raised' in str(rt).lower(), str(t).lower().startswith('public'), sz)
       for b, rt, t, sz in zip(w['band'], w['route'], w['type'], w['size'])]
w['fit60'] = [sum(f) for f in fit]; w['fin40'] = [sum(f) for f in fin]; w['priority'] = w['fit60'] + w['fin40']
w = w.sort_values(['priority', 'fit60'], ascending=False).reset_index(drop=True)
w.to_pickle(f'{S}/w15_left.pkl')
print('Wave 15 sweep brands outside the Friday export and not in master/delivered lists:', len(w))
