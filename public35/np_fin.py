"""New-parameters run: profit, cash and revenue growth for candidates whose source gave only revenue and market value.
One public page per company: the 'Financials Overview' page on stockanalysis.com (<company page>financials/).
  np_fin.py todo                 writes np/fin/todo.json (candidates to look up, most important first)
  np_fin.py fetch <raw dir> [part parts]   downloads the pages to <raw dir>/npfin/ (declared user agent, a pause after every request, stops on repeated
                                 refusals); part/parts splits the list so that a few downloads can run side by side
  np_fin.py parse <raw dir>      reads the saved pages and writes np/fin/out.jsonl (figures exactly as shown, in millions of the reporting currency)"""
import html, json, os, re, sys, time, urllib.request, urllib.error
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
UA = 'research-client/1.0 (listed-company research)'; TODO = os.path.join(H, 'np', 'fin', 'todo.json'); OUT = os.path.join(H, 'np', 'fin', 'out.jsonl')
def safe(sym): return re.sub(r'[^A-Za-z0-9._-]', '_', sym)
def todo():
    import build, np_common as nc, np_select as ns
    C, _ = ns.candidates(); U = nc.universe()
    suf = {}                                                        # ticker suffix -> exchange code, learned from the exchange-list records
    for c in U.values():
        m = re.search(r'\.([A-Z]+)$', c['sym'])
        if c.get('sa') and m and '/quote/' in c['sa']['url']: suf.setdefault(m.group(1), c['sa']['url'].split('/quote/')[1].split('/')[0])
    L = []
    for x in C:
        # listed candidates, plus companies below the threshold that the screen scored 3 (plausible): a growth figure can make them a Strategic Exception
        if not x['listed'] and x.get('scr') != '3': continue
        c = x['c']; f = x['f']
        if x['listed'] and f['pretax'] is not None and f['growth'] is not None: continue
        if not x['listed'] and f['growth'] is not None: continue
        if c.get('sa'): url = c['sa']['url']
        else:
            m = re.search(r'^(.*)\.([A-Z]+)$', c['sym'])
            if m and m.group(2) in suf: url = f"https://stockanalysis.com/quote/{suf[m.group(2)]}/{m.group(1)}/"
            elif not m and re.fullmatch(r'[A-Z.\-]{1,6}', c['sym']): url = f"https://stockanalysis.com/stocks/{c['sym'].lower().replace('-', '.')}/"
            else: continue
        rank = (0 if x['cat'] else 1 if x['listed'] else 2, 0 if f['pretax'] is None else 1, -(x['k']['cap'] or 0))
        L.append((rank, {'sym': x['sym'], 'url': url + 'financials/', 'exact': bool(c.get('sa'))}))
    L.sort(key=lambda t: t[0]); os.makedirs(os.path.dirname(TODO), exist_ok=True)
    T = json.load(open(TODO)) if os.path.exists(TODO) else []; have = {d['sym'] for d in T}          # earlier entries stay: pages already saved are still parsed
    add = [d for _, d in L if d['sym'] not in have]; json.dump(T + add, open(TODO, 'w'), indent=0)
    print(len(T), 'pages already on the list;', len(add), 'added;', sum(1 for d in add if d['exact']), 'of them with the exact page address')
def fetch(raw, part=0, parts=1):
    D = os.path.join(raw, 'npfin'); os.makedirs(D, exist_ok=True); T = json.load(open(TODO)); fails = 0; n = 0
    for d in T[part::parts]:
        p = os.path.join(D, safe(d['sym']) + '.html'); miss = p[:-5] + '.404'
        if (os.path.exists(p) and os.path.getsize(p) > 20000) or os.path.exists(miss): continue
        try:
            req = urllib.request.Request(d['url'], headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r: t = r.read().decode('utf-8', 'replace')
            open(p, 'w', encoding='utf-8').write(t); fails = 0; n += 1
        except urllib.error.HTTPError as e:
            if e.code == 404: open(miss, 'w').write(d['url']); fails = 0
            else:
                fails += 1; print('refused', e.code, d['sym'], flush=True)
                if e.code in (403, 429): time.sleep(90)
        except Exception as e: fails += 1; print('failed', d['sym'], str(e)[:80], flush=True)
        if fails >= 4: print('stopping: repeated refusals', flush=True); break
        if n % 100 == 0 and n: print(n, 'pages', flush=True)
        time.sleep(1.1)
    print('done', n, 'new pages', flush=True)
def num(s):
    s = str(s).replace(',', '').strip()
    if s in ('', '-', 'n/a'): return None
    try: return float(s.rstrip('%'))
    except ValueError: return None
def parse(raw):
    D = os.path.join(raw, 'npfin'); T = json.load(open(TODO)); n = ok = 0
    with open(OUT, 'w', encoding='utf-8') as fh:
        for d in T:
            p = os.path.join(D, safe(d['sym']) + '.html')
            if not os.path.exists(p): continue
            n += 1; t = open(p, encoding='utf-8').read(); o = {'sym': d['sym'], 'found': False, 'source_url': d['url']}
            title = html.unescape((re.findall(r'<title>(.*?)</title>', t) or [''])[0]); o['title'] = title
            m = re.search(r'[Mm]illions ([A-Z]{3})\. Fiscal year is ([A-Za-z]+ - [A-Za-z]+)', t)
            unit = 'millions'
            if not m:
                m = re.search(r'(?i)in (millions|thousands|billions) ([A-Z]{3})', t)
                if m: unit = m.group(1).lower(); cur = m.group(2)
                else: cur = ''
            else: cur = m.group(1)
            rows = {}; hdr = None; per = None
            for r in re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.S):
                c = [html.unescape(re.sub(r'<[^>]+>', ' ', x)).strip() for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
                if len(c) < 2: continue
                lab = re.sub(r'\s+', ' ', c[0]); lab = re.sub(r'^(.*?) \1 Growth$', r'\1', lab); lab = re.split(r'  +', c[0])[0].strip() if '  ' in c[0] else lab
                if lab == 'Fiscal Year': hdr = c[1:]; continue
                if lab == 'Period Ending': per = c[1:]; continue
                if lab not in rows and hdr: rows[lab] = (hdr, per, c[1:])
            def get(lab, col):
                if lab not in rows: return None
                h, _, v = rows[lab]
                for i, x in enumerate(h):
                    if (col == 'ttm' and x in ('TTM', 'Current')) or (col == 'fy' and x.startswith('FY')): return num(v[i]) if i < len(v) else None
                return None
            def period(lab, col):
                if lab not in rows: return ''
                h, pe, _ = rows[lab]
                for i, x in enumerate(h):
                    if (col == 'ttm' and x in ('TTM', 'Current')) or (col == 'fy' and x.startswith('FY')):
                        mm = re.search(r'([A-Z][a-z]{2} \d{1,2}, \d{4})', pe[i]) if pe and i < len(pe) else None
                        return (x + ' ' if x.startswith('FY') else '') + (mm.group(1) if mm else '')
                return ''
            if 'Revenue' in rows and cur:
                o.update({'found': True, 'currency': cur, 'unit': unit, 'ttm_to': period('Revenue', 'ttm'), 'fy': period('Revenue', 'fy'),
                          'revenue_ttm': get('Revenue', 'ttm'), 'revenue_fy': get('Revenue', 'fy'), 'growth_ttm_pct': get('Revenue Growth', 'ttm'), 'growth_fy_pct': get('Revenue Growth', 'fy'),
                          'opinc_ttm': get('Operating Income', 'ttm'), 'opinc_fy': get('Operating Income', 'fy'), 'netinc_ttm': get('Net Income', 'ttm'), 'netinc_fy': get('Net Income', 'fy'),
                          'pretax_margin_ttm_pct': get('Pretax Margin', 'ttm'), 'pretax_margin_fy_pct': get('Pretax Margin', 'fy'),
                          'cash': get('Cash & Investments', 'ttm'), 'debt': get('Total Debt', 'ttm'), 'fcf_ttm': get('Free Cash Flow', 'ttm'), 'fcf_fy': get('Free Cash Flow', 'fy')})
                ok += 1
            fh.write(json.dumps(o, ensure_ascii=False) + '\n')
    print(n, 'pages read;', ok, 'with figures')
if __name__ == '__main__':
    if sys.argv[1] == 'todo': todo()
    elif sys.argv[1] == 'fetch': fetch(sys.argv[2], *(int(x) for x in sys.argv[3:5]))
    else: parse(sys.argv[2])
