"""New-parameters run: which companies are candidates for the new list, and input files for the profile pass.
  np_select.py count            prints the candidate counts
  np_select.py enrich [per]     np/enrich/in_NN.jsonl for candidates with a sector and no profile yet (skips symbols already written)
  np_select.py extra [per]      np/extra/in_NN.jsonl for candidates profiled in the earlier pass (they lack the four new fields)"""
import glob, html, json, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build                      # first: a later import puts another folder with its own build.py at the front of the path
import np_common as nc
from np_common import H, SECTORS, financials, fm
def master_syms():
    A = build.assemble(); return {r['sym'] for r in A['rows']}
def candidates():
    U = nc.universe(); cls = nc.classes(); E = nc.profiles(); G = {d['sym']: d for d in nc.jl('gap/out_*.jsonl') if d.get('found')}
    inm = master_syms(); out = []; st = Counter(); FIN = nc.fin_pages(); SCR = nc.screen_scores()
    for sym, c in U.items():
        if sym in inm: st['on the 15 Nov master'] += 1; continue
        if c['country'] == 'Russia' or sym.endswith('.ME'): st['Russian market'] += 1; continue
        e = E.get(sym); code = cls.get(sym, '')
        s2 = str((e or {}).get('sector') or '')
        if s2 in ('FF', 'DD') or (s2 in SECTORS and not (s2 == '35' and c['country'] not in build.ASIA35)): code = s2
        if code in ('FF', 'DD'): st['fund, shell or duplicate line'] += 1; continue
        grp = SECTORS[code]['grp'] if code in SECTORS else 'ind'
        f = financials(c, grp, G.get(sym)); f.setdefault('growth_note', '')
        if sym in FIN: nc.apply_fin(f, c, FIN[sym])
        if not nc.entry(f): st['below the entry criteria'] += 1; continue
        sc = code if code in SECTORS else '50'
        gross = bool(f['rev'] and f['mcap'] and f['rev'] > 3 * f['mcap'] and (sc == '07' or grp == 'fin'))     # gross trading or investment value booked as revenue
        k = nc.estimate(dict(f, rev=None, mkt=None) if gross else f, sc); cat = nc.category(k['cap'])
        why = [] if cat else nc.exception_reasons(f, k, sc)
        scr = SCR.get(sym, '')
        if not cat and not why and scr in ('4', '5'): why = [f'company review found a clear commercial reason for F1 (score {scr} of 5)']
        elif not cat and not why and e and e.get('rel') in (4, 5): why = [f"company profile shows strong strategic fit (relevance {e['rel']} of 5)"]
        if code not in SECTORS: st['no sector yet'] += 1
        x = {'sym': sym, 'c': c, 'e': e, 'f': f, 'k': k, 'code': code, 'cat': cat, 'why': why, 'listed': bool(cat or why), 'scr': scr, 'gross': gross}
        st[('candidate: ' + (cat or 'exception')) if x['listed'] else 'below USD 3.5M with no stated reason'] += 1
        out.append(x)
    return out, st
def nxt(pattern):
    n = [int(re.search(r'_(\d+)\.', os.path.basename(f)).group(1)) for f in glob.glob(os.path.join(H, pattern))]
    return max(n) + 1 if n else 1
if __name__ == '__main__':
    cmd = sys.argv[1]; C, st = candidates()
    for k, v in sorted(st.items(), key=lambda x: -x[1]): print(f'{v:6d}  {k}')
    L = [x for x in C if x['listed']]
    print('candidates to list', len(L), '| with a sector', sum(1 for x in L if x['code'] in SECTORS), '| with a profile', sum(1 for x in L if x['e']), '| new-style profile', sum(1 for x in L if x['e'] and 'b2b' in x['e']))
    if cmd in ('enrich', 'extra'):
        per = int(sys.argv[2]) if len(sys.argv) > 2 else 110; sub = 'np/enrich' if cmd == 'enrich' else 'np/extra'; os.makedirs(os.path.join(H, sub), exist_ok=True)
        done = set()
        for f in glob.glob(os.path.join(H, sub, 'in_*.jsonl')):
            for l in open(f, encoding='utf-8'):
                try: done.add(json.loads(l)['sym'])
                except Exception: pass
        if cmd == 'enrich': todo = [x for x in L if x['code'] in SECTORS and not x['e'] and x['sym'] not in done]
        else: todo = [x for x in L if x['e'] and 'b2b' not in x['e'] and x['sym'] not in done]
        todo.sort(key=lambda x: (x['code'], -(x['f']['mcap'] or 0)))
        import random; random.Random(5).shuffle(todo)
        n0 = nxt(sub + '/in_*.jsonl')
        for i in range(0, len(todo), per):
            with open(os.path.join(H, sub, f'in_{n0 + i // per:03d}.jsonl'), 'w', encoding='utf-8') as fh:
                for x in todo[i:i + per]:
                    c = x['c']; sec = c.get('sec') or {}; sa = c.get('sa') or {}
                    hq = ', '.join(p for p in (str(sec.get('city') or '').title(), sec.get('state') or '') if p) or (c.get('clay') or {}).get('city', '')
                    hints = '; '.join(p for p in (','.join(c.get('cats') or []), str(sec.get('sicd') or '').title(), (c.get('clay') or {}).get('industry', ''), ('listed on ' + sa['exchange']) if sa else '') if p)
                    d = {'sym': x['sym'], 'name': re.sub(r'\s+', ' ', html.unescape(c['name'])).strip(), 'country': c['country'], 'sector': x['code'], 'hq_hint': hq, 'hints': hints,
                         'revenue': fm(x['f']['rev']) or 'n/a', 'market_cap': fm(x['f']['mcap']) or 'n/a'}
                    if cmd == 'extra': d['desc'] = x['e'].get('desc', '')
                    fh.write(json.dumps(d, ensure_ascii=False) + '\n')
        print(cmd, 'inputs:', len(todo), 'companies in', (len(todo) + per - 1) // per, 'files from', n0)
