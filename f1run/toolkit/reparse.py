# Re-parses the tabs whose header the first parser missed (unlabelled mark column, header on row 1/2/5),
# then writes the full build plan: per-tab brand lists deduped in build order, exclusions applied.
import json, re, openpyxl, collections
norm = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
wb = openpyxl.load_workbook('dl_newlist/list_new.xlsx', read_only=True, data_only=True)
FIX = ['Software', 'Cloud and Data Centers', 'Mining', 'Consumer Goods', 'Semiconductors', 'MASTER',
       'Automotive and Mobility', 'Space', 'Software, Internet & AI', 'Existing Group Overlays', 'Asset Management']
reg = [r for r in json.load(open('build_register.json')) if r['tab'] not in FIX]
def col(hdr, *cands):
    for c in cands:
        for j, h in enumerate(hdr):
            if h and h.lower().startswith(c): return j
for tab in FIX:
    ws = wb[tab]; rows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if any(str(x).lower().startswith(('company name', 'parent company name')) for x in r if x))
    hdr = [str(x).strip() if x else '' for x in rows[hi]]
    ci = col(hdr, 'company name', 'parent company name'); si = col(hdr, 'most relevant brand', 'existing subsidiary')
    ki = col(hdr, 'hq country'); wi = col(hdr, 'website'); ni = col(hdr, 'why this brand', 'subsector', 'industry')
    n = 0
    for r in rows[hi + 1:]:
        v = [str(x).strip() if x is not None else '' for x in r]
        if not any(v): continue
        name = v[ci] if ci < len(v) else ''
        if not name or name.lower() in ('yes', 'no', 'x'): continue
        mark = next((x for x in v[:ci] if x.lower() in ('x', 'xx', 'yes', 'no', 'tbr', 'later', 'tes')), '')
        sub = v[si] if si is not None and si < len(v) else ''
        brand = name
        if sub and sub.lower() not in ('parent itself', 'n/a', '-', 'same') and tab != 'Existing Group Overlays':
            brand = re.sub(r'\s*\(.*$', '', sub).strip() or name     # "Ball Corporation (Ball..." -> "Ball Corporation"
        reg.append({'tab': tab, 'red': tab not in ('Space',), 'brand': brand, 'parent': name if brand != name else '',
                    'domain': v[wi] if wi is not None and wi < len(v) else '', 'country': v[ki] if ki is not None and ki < len(v) else '',
                    'note': (v[ni][:160] if ni is not None and ni < len(v) else ''), 'mark': mark, 'sub': sub[:80]})
        n += 1
    print(f'{tab:28s} hdr row {hi+1}: {n} rows; marks={dict(collections.Counter(x["mark"] for x in reg if x["tab"]==tab))}')
json.dump(reg, open('build_register2.json', 'w'), indent=0)
# ---- build plan ----
ORDER = ['AI Cloud & Data', 'SAAS', 'Machine Tools', 'Horizontal Saas', 'Chip Makers', 'AI DATA', 'Health & Wellness',
         'Cloud and Data Centers', 'Consumer Goods', 'Mining', 'Semiconductors', 'Software', 'Existing Group Overlays', 'MASTER',
         'Automotive and Mobility', 'Software, Internet & AI', 'ERP Finance', 'GRC Risk', 'Automation', 'Vertical Saas', 'Space']
excl = {norm(e) for e in json.load(open('exclusions.json'))} | {norm('H2 Green'), norm('MathWorks')}
done = set()
for f in ['pf_final_rows.json', 'am_final.json', 'fin_final.json', 'trd_final.json']:
    done |= {norm(r['brand']) for r in json.load(open(f))}
import glob
for f in glob.glob('agt_0?.json') + glob.glob('cyb_0?.json'):
    done |= {norm(x['brand']) for x in json.load(open(f))}
plan, dropped = {}, collections.Counter()
for tab in ORDER:
    out = []
    for r in [r for r in reg if r['tab'] == tab]:
        k = norm(r['brand'])
        if tab in ('Existing Group Overlays', 'MASTER') and r['mark'].lower() not in ('x', 'xx'): dropped['unmarked ' + tab] += 1; continue
        if k in excl or any(len(e) > 6 and e in k for e in excl): dropped['excluded'] += 1; print('  drop (excluded):', tab, '|', r['brand']); continue
        if k in done: dropped['dup'] += 1; continue
        done.add(k); out.append({'brand': r['brand'], 'domain': r['domain'], 'country': r['country'], 'note': r['note'], 'parent': r.get('parent', '')})
    plan[tab] = out
json.dump(plan, open('build_plan.json', 'w'), indent=0)
print('\nBUILD PLAN:', sum(len(v) for v in plan.values()), 'brands;', dict(dropped))
for t, v in plan.items(): print(f'  {t:28s} {len(v):4d}')
