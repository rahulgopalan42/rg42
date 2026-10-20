"""Wave 16 final step 2: dedupe the Friday Clay rows within themselves and against every old file (old_v2.pkl).
Fixes v1: shared hosting / social domains (facebook.com, linktr.ee, ...) and 2-level country suffixes (ind.br,
bank.in, ...) no longer merge different companies. Adds LinkedIn-page and research-alias matching.
Writes new_dedup_v2.pkl (one row per unique company), internal_v2.pkl (rows merged into another)."""
import collections, glob, json, os, re, sys, unicodedata
import pandas as pd
from rapidfuzz import process, fuzz
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
R = '/home/user/rg42'
GENERIC = {'facebook.com', 'linktr.ee', 'instagram.com', 'google.com', 'blogspot.com', 'youtube.com', 'wixsite.com',
           'business.site', 'wikipedia.org', 'wordpress.com', 'linkedin.com', 'wa.me', 'fiverr.com', 'alibaba.com',
           'twitter.com', 'x.com', 'tiktok.com', 'github.io', 'github.com', 'squarespace.com', 'weebly.com', 'wix.com',
           'godaddysites.com', 'myshopify.com', 'bit.ly', 'medium.com', 'sites.google.com', 'yolasite.com', 'jimdo.com',
           'webnode.com', 'carrd.co', 'notion.site', 'canva.site', 'about.me', 'tumblr.com', 'yelp.com', 'gmail.com',
           'outlook.com', 'hotmail.com', 'yahoo.com', 'amazon.com', 'apple.com', 'microsoft.com', 'bing.com', 'uk.com',
           'us.com', 'eu.com', 'cn.com', 'de.com', 'onlinecareer360.com', 'piton-global.com', 'glassdoor.com', 'indeed.com',
           'crunchbase.com', 'zoominfo.com', 'tripadvisor.com', 'booking.com', 'wechat.com', 'line.me', 't.me', 'vk.com'}
GENERIC_KEEP = {'amazon.com', 'apple.com', 'microsoft.com', 'google.com', 'alibaba.com', 'booking.com', 'linkedin.com',
                'github.com', 'fiverr.com', 'tripadvisor.com', 'yelp.com', 'glassdoor.com', 'indeed.com'}  # real firms: keep when the name says so

def regdom(d, name=''):
    d = str(d or '').lower().strip()
    d = re.sub(r'^(https?://)?(www\d?\.)?', '', d).split('/')[0].split(':')[0].strip('.')
    p = [x for x in d.split('.') if x]
    if len(p) < 2: return ''
    r = '.'.join(p[-3:]) if (len(p) >= 3 and len(p[-1]) == 2 and len(p[-2]) <= 4) else '.'.join(p[-2:])
    if r in GENERIC or '.'.join(p[-3:]) in GENERIC:
        base = r.split('.')[0]
        if r in GENERIC_KEEP and base in strict(name): return r
        return ''
    return r

SUF = r'\b(inc|incorporated|ltd|limited|plc|corp|corporation|co|company|group|holdings?|ag|sa|spa|se|nv|llc|lp|gmbh|as|the|sas|bv|ab|pte|pty|pvt|private|kg|kgaa|oy|oyj|asa|srl|sl|sarl|bhd|sdn|tbk|pt|jsc|ojsc|pjsc|cv|de|of|and)\b'
GEN = r'\b(international|global|worldwide|technologies|technology|tech|systems|solutions|services|industries|industrial|enterprises?|partners|brands|usa|us|uk|europe|america|americas|asia|india|china|japan|official)\b'
def _norm(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)', ' ', s).replace('&', ' and ')
    return re.sub(SUF, ' ', re.sub(r'[^a-z0-9 ]', ' ', s))
def strict(s): return re.sub(r'\s+', '', _norm(s))
def core(s): return re.sub(r'\s+', '', re.sub(GEN, ' ', _norm(s)))
def lislug(u):
    m = re.search(r'linkedin\.com/(?:company|school|showcase)/([^/?#\s]+)', str(u or '').lower())
    return m.group(1).strip() if m else ''

if __name__ == '__main__':
    new = pd.read_pickle(f'{S}/new_all.pkl')
    old = pd.read_pickle(f'{S}/old_v2.pkl')
    n0 = len(new)
    new['rd'] = [regdom(d, n) for d, n in zip(new['domain'], new['name'])]
    new['sn'] = new['name'].map(strict); new['cn'] = new['name'].map(core); new['li'] = new['linkedin_url'].map(lislug)
    old['rd'] = [regdom(d, n) for d, n in zip(old['domain'], old['name'])]
    old['sn'] = old['name'].map(strict); old['cn'] = old['name'].map(core); old['li'] = old['linkedin'].map(lislug)
    blank = new[(new['rd'] == '') & (new['sn'] == '') & (new['li'] == '')]
    new = new.drop(blank.index)

    # ---- internal dedupe (within the 13 Friday CSVs): website, then LinkedIn page, then name
    merged = []   # (dropped index, kept index, reason)
    def collapse(df, key, reason):
        g = df[df[key] != ''].groupby(key).groups
        keep = {}
        for k, idx in g.items():
            idx = list(idx)
            for j in idx[1:]: merged.append((j, idx[0], reason))
        drop = [j for k, idx in g.items() for j in list(idx)[1:]]
        return df.drop(drop)
    new['_srcs'] = new['source_csv']; new['_srch'] = new['clay_search']
    new = collapse(new, 'rd', 'same website')
    new = collapse(new, 'li', 'same LinkedIn page')
    # same strict name: merge when the name is distinctive (8+ chars) or the country matches, else leave both
    new['_nk'] = [sn if len(sn) >= 8 else (sn + '|' + str(c) if len(sn) >= 4 else '') for sn, c in zip(new['sn'], new['country'])]
    new = collapse(new, '_nk', 'same company name')
    allrows = pd.read_pickle(f'{S}/new_all.pkl')
    mg = pd.DataFrame(merged, columns=['drop', 'keep', 'reason'])
    # carry every source CSV onto the kept row (follow chains)
    parent = dict(zip(mg['drop'], mg['keep']))
    def root(i):
        while i in parent: i = parent[i]
        return i
    mg['root'] = mg['drop'].map(root)
    srcs = collections.defaultdict(set); srch = collections.defaultdict(set)
    for i in new.index: srcs[i].add(allrows.at[i, 'source_csv']); srch[i].add(allrows.at[i, 'clay_search'])
    for d, r in zip(mg['drop'], mg['root']): srcs[r].add(allrows.at[d, 'source_csv']); srch[r].add(allrows.at[d, 'clay_search'])
    new['source_csv'] = [('; '.join(sorted(srcs[i]))) for i in new.index]
    new['clay_search'] = [(' || '.join(sorted(srch[i]))) for i in new.index]
    new['n_source_files'] = [len(srcs[i]) for i in new.index]
    internal = allrows.loc[mg['drop']].copy()
    internal['kept_as'] = [new.at[r, 'name'] for r in mg['root']]
    internal['kept_website'] = [new.at[r, 'domain'] for r in mg['root']]
    internal['reason'] = mg['reason'].values
    n1 = len(new)

    # ---- aliases from research (agents' proper company names) and Wave 15 screening (real_name)
    alias = {}
    for sub in ('verify2', 'verify'):
        for f in glob.glob(f'{R}/wave16/{sub}/out_*.json'):
            fi = f.replace('/out_', '/in_'); ins = json.load(open(fi)) if os.path.exists(fi) else []
            for i, r in enumerate(json.load(open(f))):
                nm = r.get('company') or ''
                src = ins[i] if i < len(ins) else {}
                k = r.get('id') or ('n:' + str(src.get('company', '')))
                if nm and strict(nm) and strict(nm) != strict(src.get('company', nm)): alias[k] = nm
    new['_k1'] = [d if d else 'n:' + str(n) for d, n in zip([regdom(x) if regdom(x) not in GENERIC else '' for x in new['domain']], new['name'])]
    new['alias'] = new['_k1'].map(alias).fillna('')
    new['an'] = new['alias'].map(strict)

    # ---- match against old files; best category wins, every matched file is recorded
    CATS = ['Old master files (Drive)', 'Earlier wave', 'Earlier wave - dropped/rejected list',
            'Wave 15 database sweep (unchecked)', 'Wave 15 database sweep - auto-removed']
    rank = {c: i for i, c in enumerate(CATS)}
    idx = {}
    for key in ('rd', 'li', 'sn', 'cn'):
        d = collections.defaultdict(list)
        sub = old[old[key].str.len() >= (5 if key == 'cn' else 3 if key == 'sn' else 1)]
        for v, nm, dm, src, cat in zip(sub[key], sub['name'], sub['domain'], sub['source'], sub['category']):
            d[v].append((rank[cat], cat, src, nm, dm))
        idx[key] = d
    # Only the Drive master files and earlier delivered prospect lists make a brand 'not new' (user decision, option 3).
    # Wave 15 DROPPED / unchecked-sweep matches are reassessed under the current criteria and only flagged.
    EXCL = {'Old master files (Drive)', 'Earlier wave'}
    out, seen = [], []
    for r in new.itertuples():
        hits = []   # (status, cat_rank, cat, reason, src)
        def add(key, val, status, why):
            for cr, cat, src, nm, dm in idx[key].get(val, []):
                hits.append((status, cr, cat, why(nm, dm), src))
        if r.rd: add('rd', r.rd, 'dup', lambda nm, dm: f"same website ({r.rd}) as '{nm or dm}'")
        if r.li: add('li', r.li, 'dup', lambda nm, dm: f"same LinkedIn page ({r.li}) as '{nm}'")
        if len(r.sn) >= 3: add('sn', r.sn, 'dup', lambda nm, dm: f"same name as '{nm}'")
        if len(r.an) >= 3: add('sn', r.an, 'dup', lambda nm, dm: f"researched name '{r.alias}' matches '{nm}'")
        ex = [h for h in hits if h[2] in EXCL]
        if not ex and len(r.cn) >= 5:
            for cr, cat, src, nm, dm in idx['cn'].get(r.cn, []):
                if cat in EXCL: ex.append(('maybe', cr, cat, f"name variation of '{nm}' ({dm or 'no website'})", src))
        oth = sorted([h for h in hits if h[2] not in EXCL], key=lambda h: h[1])
        seen.append((oth[0][2] + ': ' + oth[0][4]) if oth else '')
        if ex:
            ex.sort(key=lambda h: (h[0] != 'dup', h[1]))
            st, cr, cat, why, src = ex[0]
            files = []
            for h in ex:
                fl = h[4].split(' | ')[0]
                if fl not in files: files.append(fl)
            out.append((st, cat, why, src, '; '.join(files[:6]), len(files)))
        else:
            out.append(('new', '', '', '', '', 0))
    new['seen_in_w15'] = seen
    new[['dup_status', 'dup_category', 'dup_reason', 'matched_in', 'matched_files', 'n_matched_files']] = pd.DataFrame(out, index=new.index)
    # fuzzy spelling pass for the rest (same first 3 letters, ratio >= 92) -> manual review
    oldsn = old.loc[(old['sn'].str.len() >= 5) & old['category'].isin(EXCL), ['sn', 'name', 'source', 'category']].drop_duplicates('sn')
    byp = collections.defaultdict(list)
    for sn, nm, sc, cat in oldsn.itertuples(index=False): byp[sn[:3]].append((sn, nm, sc, cat))
    m = new['dup_status'].eq('new') & new['sn'].str.len().ge(5)
    for i in new.index[m]:
        sn = new.at[i, 'sn']; cand = byp.get(sn[:3])
        if not cand: continue
        best = process.extractOne(sn, [c[0] for c in cand], scorer=fuzz.ratio, score_cutoff=92)
        if best:
            c = cand[best[2]]
            new.loc[i, ['dup_status', 'dup_category', 'dup_reason', 'matched_in', 'matched_files', 'n_matched_files']] = \
                ['maybe', c[3], f"close spelling of '{c[1]}' ({best[1]:.0f}% match)", c[2], c[2].split(' | ')[0], 1]
    new.drop(columns=['_srcs', '_srch', '_nk', '_k1']).to_pickle(f'{S}/new_dedup_v2.pkl')
    mg[['drop', 'root']].to_pickle(f'{S}/merge_map_v2.pkl')
    internal.to_pickle(f'{S}/internal_v2.pkl'); blank.to_pickle(f'{S}/blank_v2.pkl')
    print(f'rows {n0}; blank (no name/website/LinkedIn) {len(blank)}; unique companies {n1}; merged within new files {len(internal)}')
    print(pd.crosstab(new['dup_status'], new['dup_category']).to_string())
    print('new brands also seen in W15 dropped/unchecked lists:', ((new.dup_status == 'new') & (new.seen_in_w15 != '')).sum())
