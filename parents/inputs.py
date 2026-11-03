"""Input loaders for the parent-company pipeline: use the session scratchpad pickles when they exist, otherwise the
compact checkpoints committed under parents/checkpoints/ (so a fresh session can resume without the old scratchpad)."""
import glob, html, os, re, sys
import pandas as pd
R = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(R); C = f'{R}/checkpoints'
S = os.environ.get('F1_SCRATCH', '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad')
W16 = f'{S}/w16'; P = f'{S}/parents'; os.makedirs(P, exist_ok=True)
sys.path.insert(0, R)          # dedupe_v2 / sectors_v3 are copied next to this file
def _pkl_or_csv(pkl, csv):
    if os.path.exists(pkl): return pd.read_pickle(pkl)
    return pd.read_csv(csv, dtype=str, keep_default_na=False)
def old_datasets():
    """Old Google Drive master files + previous prospect workbooks (all worksheets): name, domain, category, source"""
    return _pkl_or_csv(f'{W16}/old_v2.pkl', f'{C}/existing_old_drive_and_workbooks.csv.gz')
def clay_export():
    """Friday Clay export CSVs: name, domain, source_csv"""
    return _pkl_or_csv(f'{W16}/new_all.pkl', f'{C}/existing_friday_clay_export.csv.gz')
def wave16_ranking():
    df = _pkl_or_csv(f'{W16}/final_ranked.pkl', f'{C}/wave16_brand_ranking.csv.gz')
    if 'funding_100m_apollo' in df and df['funding_100m_apollo'].dtype == object:
        df['funding_100m_apollo'] = df['funding_100m_apollo'].isin(['True', 'true', '1'])
        for c in ('fit60', 'fin40', 'priority'): df[c] = pd.to_numeric(df[c], errors='coerce')
    return df
def market_cap_rows():
    """[{name, code, val_bn, country}] from the companiesmarketcap.com pages fetched 2026-10-19"""
    pages = glob.glob(f'{S}/mcap/p*.html')
    if not pages: return pd.read_csv(f'{C}/market_cap_listing_2026-10-19.csv.gz', dtype={'code': str}, keep_default_na=False).to_dict('records')
    rows = []
    for f in pages:
        h = open(f, errors='ignore').read()
        for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S):
            nm = re.search(r'company-name">([^<]*)', tr)
            if not nm: continue
            tds = [re.sub('<[^>]+>', '', t).strip() for t in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
            code = tds[2][len(nm.group(1).strip()):].strip() if len(tds) > 2 else ''
            mc = next((t for t in tds if re.match(r'^\$[\d.]+ ?[TBM]$', t)), '')
            if not mc: continue
            v = float(mc[1:-1]) * {'T': 1000, 'B': 1, 'M': 0.001}[mc[-1]]
            rows.append({'name': html.unescape(nm.group(1).strip()), 'code': code, 'val_bn': round(v, 1), 'country': tds[-1].split()[-1] if tds else ''})
    return rows
