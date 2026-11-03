"""Turn extract.py output into one row per company per results page, tagged with the funding-filter band and page.
Usage: parse.py <ocr.jsonl> [...]  -> writes <name>.rows.json next to each input and prints a band/page summary."""
import json, re, sys, os, difflib
from collections import defaultdict

FIELDS = ('name', 'ipo', 'total', 'date', 'ind', 'hq', 'desc')
CELL = {'org': 'name', 'ipo': 'ipo', 'total': 'total', 'date': 'date', 'ind': 'ind', 'hq': 'hq', 'desc': 'desc'}
def norm(t): return re.sub(r'\s+', ' ', t).strip()
def amount(t):
    """'$150M' / '$1.2B' / '150' -> USD millions (float)"""
    m = re.search(r'([\d][\d,\.]*)\s*([MBK])?', t.replace(' ', ''))
    if not m: return None
    try: v = float(m.group(1).replace(',', '').rstrip('.'))
    except ValueError: return None
    u = (m.group(2) or 'M').upper()
    return v * 1000 if u == 'B' else (v / 1000 if u == 'K' else v)

def top_meta(boxes):
    """band (lo, hi in USD M; hi None if only one end was read), page start/end and total results"""
    meta = {'band': None, 'start': None, 'end': None, 'results': None}
    txt = [(b[0], b[1], b[2], b[3], norm(b[4])) for b in boxes]
    for x0, y0, x1, y1, t in txt:
        m = re.search(r'of\s*([\d,]+)\s*result', t)
        if m and meta['results'] is None:
            meta['results'] = int(m.group(1).replace(',', ''))
            for a0, b0, a1, b1, u in [(x0, y0, x1, y1, t)] + [z for z in txt if abs(z[1] - y0) < 15 and z[0] < x0 + 10]:
                mm = re.search(r'(\d[\d,]*)\s*-\s*(\d[\d,]*)', u.replace(' ', ''))
                if mm: meta['start'], meta['end'] = int(mm.group(1).replace(',', '')), int(mm.group(2).replace(',', '')); break
    for x0, y0, x1, y1, t in txt:
        if 'Total Funding Amount:' in t or t.startswith('Financials'):
            chips = sorted([(a0, u) for a0, b0, a1, b1, u in txt if abs(b0 - y0) < 14 and a0 > x0 - 5 and re.search(r'[\$S]\s*[\d.,]+\s*[MBK]', u)])
            vals = []
            for _, u in chips:
                for mm in re.finditer(r'[\$S]\s*([\d.,]+)\s*([MBK])', u): vals.append(amount(mm.group(1) + mm.group(2)))
            if len(vals) >= 2: meta['band'] = (vals[0], vals[1]); break
            if len(vals) == 1: meta['band'] = (vals[0], None)
    return meta

def obs_of(r, t):
    o = {'t': t, 'still': r.get('still', False)}
    for k, (txt, cf) in r['cells'].items():
        if k not in CELL: continue
        txt = norm(txt)
        if k == 'org': txt = re.sub(r'^[^A-Za-z0-9一-鿿]+', '', txt)
        o[CELL[k]] = (txt, cf)
    return o if o.get('name') and len(o['name'][0]) > 1 else None

def key_of(o):
    tot = re.sub(r'[^0-9]', '', o.get('total', ('', 0))[0])
    hq = re.sub(r'[^a-z]', '', o.get('hq', ('', 0))[0].lower())[:10]
    return tot, hq

def sim(a, b): return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def nkey(n): return re.sub(r'[^a-z0-9]', '', re.sub(r'\.{2,}|\u2026', '', n.lower()))
def same_co(a, b, ka, kb, loose_=False):
    """two readings of one page are the same company: similar names, a cut-short name that prefixes the other, or a
    looser name match backed by the same total funding and HQ"""
    na, nb = nkey(a), nkey(b); s = sim(na, nb)
    if ka[0] and kb[0] and ka[0] != kb[0] and len(ka[0]) >= 6 and len(kb[0]) >= 6 and s < 0.9: return False   # different total funding
    if s >= (0.7 if loose_ else 0.8): return True
    if min(len(na), len(nb)) >= 5 and (na.startswith(nb) or nb.startswith(na)): return True
    same_amt = ka[0] and ka[0] == kb[0] and ka[1][:5] == kb[1][:5]
    return bool(same_amt and s >= (0.4 if loose_ else 0.5))

def cluster(obs):
    """readings of one page from many frames -> one row per company; each field takes the reading with the highest
    summed confidence (readings on a still screen count 1.5x)"""
    groups = []
    for o in sorted(obs, key=lambda o: -o['name'][1]):
        k = key_of(o); nm = o['name'][0]
        g = next((g for g in groups if same_co(nm, g['name'], k, g['key'])), None)
        if g: g['obs'].append(o)
        else: groups.append({'key': k, 'name': nm, 'obs': [o]})
    multi = [g for g in groups if len(g['obs']) > 1]; keep = list(multi)
    for g in groups:                    # a company read only once (often a garbled read) joins a matching group
        if len(g['obs']) > 1: continue
        o = g['obs'][0]
        tgt = next((h for h in multi if same_co(o['name'][0], h['name'], g['key'], h['key'], True)), None)
        if tgt: tgt['obs'].append(o)
        else: keep.append(g)
    out = []
    for g in keep:
        row = {'seen': len(g['obs']), 't': min(o['t'] for o in g['obs'])}
        for fld in FIELDS:
            votes = defaultdict(float)
            for o in g['obs']:
                if fld in o:
                    txt, cf = o[fld]; w = cf ** 4 * (1.5 if o['still'] else 1.0)
                    if fld == 'name' and (txt.endswith('..') or len(txt) <= 3): w *= 0.5
                    votes[txt] += w
            if votes:
                best = max(votes, key=votes.get); row[fld] = best
                row[fld + '_conf'] = round(max(o[fld][1] for o in g['obs'] if o.get(fld, ('',))[0] == best), 3)
        if len(row.get('name', '')) <= 2 and row['seen'] < 2: continue
        out.append(row)
    return out

def parse_file(path):
    obs = defaultdict(list); pagemeta = {}
    cur = {'band': None, 'start': None, 'end': None, 'results': None}
    for line in open(path):
        fr = json.loads(line)
        if 'top' in fr:
            m = top_meta(fr['top'])
            b = m['band']
            cb = cur['band']
            if b and b[1] is not None: cur['band'] = b
            elif b and cb and cb[1] is not None and abs(b[0] - cb[1]) < 0.01 and m['results'] and cur['results'] and m['results'] != cur['results']:
                cur['band'] = (b[0], None)      # only a minimum ("Total Funding Amount: $9.8B"): open-ended top range
            elif b and cb and b[0] not in cb: cur['band'] = None
            cur.update({k: m[k] for k in ('start', 'end', 'results')})
        band = cur['band']
        # a start beyond the result count is a real Crunchbase view (page offset kept from the previous search, e.g.
        # "801-247 of 247"): its rows are kept; build.py leaves such pages out of the page-completeness check
        if cur['start'] is None or band is None or not cur['results']: continue
        key = (band, cur['start'])
        pagemeta.setdefault(key, {'band': band, 'start': cur['start'], 'end': cur['end'], 'results': cur['results'], 't': fr['t']})
        for r in fr.get('rows', []):
            o = obs_of(r, fr['t'])
            if o: obs[key].append(o)
    pages = {k: cluster(v) for k, v in obs.items()}
    return pages, pagemeta

if __name__ == '__main__':
    for path in sys.argv[1:]:
        pages, pm = parse_file(path)
        out = []
        for key, rows in pages.items():
            for r in rows: out.append(dict(r, band_lo=key[0][0], band_hi=key[0][1], page_start=key[1], results=pm[key]['results']))
        json.dump({'rows': out, 'pages': [dict(v, rows=len(pages.get(k, []))) for k, v in pm.items()]}, open(path.replace('.jsonl', '.rows.json'), 'w'))
        print(os.path.basename(path), 'rows', len(out))
        for key in sorted(pm, key=lambda k: (k[0][0], k[0][1] or 1e12, k[1])):
            m = pm[key]; n = len(pages.get(key, []))
            exp = min(50, (m['results'] or 0) - m['start'] + 1) if m['results'] else 50
            print(f"  band {m['band']} page {m['start']}-{m['end']} of {m['results']}: rows {n}/{exp}")
