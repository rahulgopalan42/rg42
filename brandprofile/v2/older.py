"""The user's older 48-tab sheet: their own marks, and the conversion of its qualifying brands to the new method.
gap() yields the brands of the 23 Nov all-sector list that are not on the master, not delivered and not F1 partners.
record(row) turns one of them into a record that score.py can assess. Everything comes from the 23 Nov list: the capacity basis is the
Crunchbase total-funding figure on the user's sheet (it can include debt and was not re-checked on a company page), the F1 fit is the
23 Nov fit score carried over, and buying signals are the four 'Parameter 4' columns. Nothing is added from memory."""
import gzip, json, os, re, sys
from collections import defaultdict
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
LIST = os.path.join(H, '..', '..', 'reports', 'F1-NON-LISTED-PROSPECTS-ALL-SECTORS-v3-2026-11-23.xlsx')
# the user's own marks (their explanation of 28 Nov 2026): x = a template is wanted; blank on a tab that has x marks = a colleague already
# works the account (it is on Salesforce); a tab with no marks at all = the user has not gone through that tab yet
SHEET = json.load(gzip.open(os.path.join(H, '..', 'data', 'brands.json.gz'), 'rt', encoding='utf-8'))
MARKED_TABS = {d['tab'] for d in SHEET if d.get('mark')}; OCC = defaultdict(list)
for d in SHEET:
    for nm in {str(d.get('brand') or '').strip().lower(), str(d.get('orig_brand') or '').strip().lower()} - {''}: OCC[nm].append((d['tab'], bool(d.get('mark'))))
def sheet_tabs(names, tab=''):
    occ = [o for n in names for o in OCC.get(str(n or '').strip().lower(), [])]
    return '; '.join(sorted({t for t, m in occ})) or str(tab or '')
def marking(names, tab='', none=''):
    occ = [o for n in names for o in OCC.get(str(n or '').strip().lower(), [])] or ([(tab, False)] if tab else [])
    if not occ: return none
    if any(m for t, m in occ): return 'x: template wanted'
    if any(t in MARKED_TABS for t, m in occ): return 'Blank on a tab you have marked: with a colleague on Salesforce'
    return 'Tab not gone through yet: no marks on it'
MON = {m: i for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'], 1)}
def _date(s):
    m = re.search(r'(?:(\d{1,2}) )?([A-Za-z]{3})[a-z]* (20\d\d)', s or '')
    return f"{m.group(3)}-{MON[m.group(2).lower()]:02d}" if m and m.group(2).lower() in MON else ''
def _usd(s):
    """(lower bound in USD millions, is a range) from 'Total funding raised $181M ...' or '... USD 100M-500M (Crunchbase range)'"""
    m = re.search(r'(?:USD ?|\$)([\d][\d,\.]*)\s*([KMB])(?:\s*-\s*([\d][\d,\.]*)\s*([KMB]))?', s or '')
    if not m: return None, False
    v = float(m.group(1).replace(',', '')) * {'K': 0.001, 'M': 1, 'B': 1000}[m.group(2)]
    return v, bool(m.group(3))
def gap(with_status=False):
    from openpyxl import load_workbook
    import check as C
    ws = load_workbook(LIST, read_only=True)['Prospects - All Sectors']; rows = ws.iter_rows(values_only=True); h = list(next(rows)); seen = set()
    for r in rows:
        if not r[0]: continue
        nm = str(r[0]).strip()
        if nm.lower() in seen: continue
        seen.add(nm.lower()); s, disp, sr, hits = C.lookup(nm, batch='older')
        k = 'delivered' if s == 'dup' and sr.startswith('delivered') else {'dup': 'master', 'f1': 'f1'}.get(s, 'gap')
        if with_status: yield k, dict(zip(h, r))
        elif k == 'gap': yield dict(zip(h, r))
def record(v):
    """v: one row of the 23 Nov list as a dict -> a record in the new format (see brief_discovery.md section 4)"""
    import build as B
    g = lambda k: re.sub(r'\s+', ' ', str(v.get(k) or '')).strip()
    hq = g('Headquarters – City and country'); city, _, country = hq.rpartition(', ')
    sec_txt, _, sub = g('Sector / Industry').partition(':')
    usd, rng = _usd(g('Parameter 3: Capacity Basis')); last = _date(g('Free Cash Flow / Liquidity'))
    own_txt = g('Ownership Type'); parent = g('Parent Company')
    own = 'state-owned' if own_txt.lower().startswith('state') else 'subsidiary of listed group' if 'listed' in own_txt.lower() and own_txt.lower().startswith('subsidiary') else \
          'subsidiary of private group' if own_txt.lower().startswith('subsidiary') else 'private equity-backed' if 'investment firm' in own_txt.lower() else 'venture-backed'
    par = '' if parent.lower().startswith('none') else re.sub(r'\s*\((listed|private|state-owned)[^)]*\)\s*$', '', parent)
    sig = []
    p4a = g('Parameter 4a: Raised Money in Past 12 Months')
    if p4a.lower().startswith('confirmed') and last: sig.append({'category': 'capital', 'what': 'Funding round, ' + p4a.split(':', 1)[1].strip(), 'date': last, 'status': 'confirmed', 'source': 'Crunchbase record on your older sheet'})
    for k, cat in (('Parameter 4b: Preparing an IPO', 'capital'), ('Parameter 4c: Opening in New Regions', 'geographic'), ('Parameter 4d: Marketing Activity', 'marketing')):
        t = g(k)
        if not t.lower().startswith(('confirmed', 'lead only')): continue
        url = re.search(r'https?://[^\s\)]+', t); what = re.sub(r'\s*\([^()]*https?://[^()]*\)\s*$', '', t.split(':', 1)[1]).strip()
        sig.append({'category': cat, 'what': what, 'date': _date(t), 'status': 'confirmed' if t.lower().startswith('confirmed') else 'inferred', 'source': url.group(0) if url else ''})
    try: old_fit = float(g('Fit Score (0-100)'))
    except Exception: old_fit = 0.0
    fr = round(3 * max(0, min(100, old_fit)) / 100, 3)
    pre = g('Stage').lower().startswith('pre')
    return {'name': g('Company Name'), 'website': '', 'hq_city': city, 'hq_country': country or hq, 'sector': B.SECKEY.get(B.norm(sec_txt)) or 'Diversified & Other', 'subsector': sub.strip(),
            'desc': g('Company Description'), 'model': '', 'ownership_type': own, 'parent_immediate': par, 'parent_listed': 'listed' if 'listed' in parent.lower() else '',
            'reach': g('Geographic Reach'), 'markets': g('Main Customer Markets & International Expansion'), 'route': '',
            'fin': ([{'metric': 'equity_funding', 'value_orig': g('Parameter 3: Capacity Basis').split(' (Crunchbase, recorded')[0], 'usd_m': usd, 'period': (last[:4] if last else '2026'), 'kind': 'estimated' if rng else 'reported',
                      'source': 'Crunchbase record on your older sheet (Oct-Nov 2026)'}] if usd else []),
            'profitability': 'loss-making' if pre else 'unknown', 'profitability_basis': 'pre-revenue' if pre else '', 'signals': sig,
            'fit': {k: fr for k in ('b2b', 'ecosystem', 'technical', 'hospitality', 'geography', 'brand', 'consumer', 'category')}, 'fit_rationale': g('F1 Sponsorship Rationale'),
            'category_conflict': '', 'access': {}, 'outstanding': g('Verification Notes'), 'sources': [], 'conf': g('Profile Confidence').lower(),
            '_old_fit': old_fit, '_funding_usd_m': usd, '_funding_range': rng, '_last_round': last, '_tab': g('Tab in Your Sheet'), '_brand': g('Brand Name in Your Sheet'),
            '_x': g('Marked "x" in Your Sheet').lower() in ('x', 'yes', 'true'), '_cells': [v.get(k) for k in list(v)[:22]]}
