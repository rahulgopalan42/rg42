"""Backtest of the original (16-18 Nov) and revised (27 Nov) qualification rules on F1 sponsors that were privately owned at entry.
Usage: backtest.py     Reads v2/backtest/bt_*.jsonl, writes v2/backtest/results.json. Only figures dated before the announcement are used;
the sponsorship being tested never counts as evidence."""
import glob, json, os, re, sys
from collections import Counter
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import score as S
def clean(v): return re.sub(r'\s+', ' ', str(v)).strip() if v not in (None, '') else ''
def run():
    rows = []
    for p in sorted(glob.glob(os.path.join(H, 'backtest', 'bt_*.jsonl'))):
        for l in open(p, encoding='utf-8'):
            try: d = json.loads(l)
            except Exception: continue
            if not isinstance(d, dict) or not clean(d.get('sponsor')): continue
            d['_file'] = os.path.basename(p)[3:-6]; rows.append(d)
    out = []
    for d in rows:
        priv = clean(d.get('private_at_entry')).lower()
        M = {}
        for f in d.get('pre') or []:
            if isinstance(f, dict) and clean(f.get('metric')) and S.num(f.get('usd_m')) is not None:
                k = clean(f['metric']).lower(); v = S.num(f['usd_m'])
                if k not in M or (S.year(f.get('as_of')) or 0) >= (S.year(M[k][1]) or 0): M[k] = (v, clean(f.get('as_of')), clean(f.get('kind')), clean(f.get('source')))
        own = clean(d.get('ownership_at_entry')).lower(); spons = clean(d.get('prior_sponsorships')); sig = clean(d.get('prior_signals')) or clean(d.get('last_round_before'))
        g = lambda k: M[k][0] if k in M else None
        money = [k for k in ('equity_funding', 'revenue', 'arr', 'ebitda', 'valuation', 'transaction_value', 'aum') if k in M]
        # original rules (16-18 Nov 2026): any one of equity USD 150M+, revenue USD 300M+, valued or bought at USD 1B+, a top-tier sponsorship, a state fund building the brand
        o = []
        if (g('equity_funding') or 0) >= 150: o.append('equity funding USD 150M+')
        if (g('revenue') or 0) >= 300: o.append('revenue USD 300M+')
        if max(g('valuation') or 0, g('transaction_value') or 0) >= 1000: o.append('valued or bought at USD 1B+')
        if spons and S.TOP_SPONSOR.search(spons): o.append('existing top-tier sponsorship')
        if own in ('state-owned', 'sovereign fund-backed'): o.append('state ownership')
        # revised rules: Routes A, B and C
        r = []; route = 'none'
        for k, th in S.STD.items():
            if (g(k) or 0) >= th: r.append(f'{S.LABEL[k]} USD {th:,}M+')
        if spons and S.TOP_SPONSOR.search(spons): r.append('existing substantial sponsorship')
        if own in ('state-owned', 'sovereign fund-backed'): r.append('state backing')
        if r: route = 'A'
        else:
            for k, (lo, hi) in S.EXC.items():
                if g(k) is not None and lo <= g(k) < hi: r.append(f'{S.LABEL[k]} in the exceptional band'); route = 'B'
            if not r:
                alt = []
                if (g('employees') or 0) >= 500: alt.append(f"{g('employees'):,.0f} employees")
                if (g('countries') or 0) >= 3: alt.append(f"{g('countries'):,.0f} countries")
                if (g('stores') or 0) >= 100: alt.append(f"{g('stores'):,.0f} stores")
                if spons: alt.append('paid sponsorships already')
                if (g('marketing_spend') or 0) > 0: alt.append('disclosed marketing spend')
                if len(alt) >= 2: r = alt; route = 'C'
                elif alt: r = alt + ['(one indicator only)']
        nofig = not money                      # no financial figure dated before the deal was found: the thresholds cannot be tested either way
        out.append({'sponsor': clean(d['sponsor']), 'property': clean(d.get('f1_property')), 'designation': clean(d.get('designation')), 'announced': clean(d.get('announced')), 'private': priv,
                    'ownership': clean(d.get('ownership_at_entry')), 'country': clean(d.get('hq_country')), 'sector': clean(d.get('sector')), 'model': clean(d.get('model')), 'group': d['_file'],
                    'figures': '; '.join(f"{S.LABEL.get(k, k)}: USD {v[0]:,.0f}M ({v[1]}, {v[2]})" if k in S.LABEL else f"{k}: {v[0]:,.0f} ({v[1]})" for k, v in M.items()) or 'None found dated before the deal',
                    'prior_sponsorships': spons, 'prior_signals': sig, 'original': 'Captured' if o else ('Not testable: no pre-deal financial figure found' if nofig else 'Below the thresholds on the figures found'), 'original_why': '; '.join(o),
                    'revised': ('Captured, Route ' + route) if route != 'none' else ('Not testable: no pre-deal financial figure found' if nofig else 'Below the thresholds on the figures found'), 'revised_why': '; '.join(r), 'had_signal': 'Yes' if sig else 'None found',
                    'after': clean(d.get('what_happened_after')), 'notes': clean(d.get('notes')), 'source': clean(d.get('announce_source')), 'conf': clean(d.get('conf'))})
    json.dump(out, open(os.path.join(H, 'backtest', 'results.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return out
def summary(out):
    P = [x for x in out if x['private'] == 'yes']; n = len(P)
    c = lambda k, v: sum(1 for x in P if x[k].startswith(v))
    return {'tested': len(out), 'private': n, 'not_private': [x['sponsor'] for x in out if x['private'] != 'yes'],
            'orig_captured': c('original', 'Captured'), 'orig_missed': c('original', 'Below'), 'orig_nofig': c('original', 'Not testable'),
            'rev_captured': c('revised', 'Captured'), 'rev_missed': c('revised', 'Below'), 'rev_nofig': c('revised', 'Not testable'),
            'rev_routes': dict(Counter(x['revised'] for x in P)), 'gained': [x['sponsor'] for x in P if x['revised'].startswith('Captured') and not x['original'].startswith('Captured')],
            'still_missed': [x['sponsor'] for x in P if x['revised'].startswith('Below')], 'nofig': [x['sponsor'] for x in P if x['revised'].startswith('Not testable')],
            'with_signal': sum(1 for x in P if x['had_signal'] == 'Yes'), 'with_prior_sponsorship': sum(1 for x in P if x['prior_sponsorships']),
            'by_ownership': dict(Counter(x['ownership'] or 'unclear' for x in P))}
if __name__ == '__main__':
    out = run(); s = summary(out)
    for k, v in s.items(): print(k, ':', v)
