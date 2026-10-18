"""Wave 16 step 1c: dedupe new Clay rows internally and against the old index.
Outputs (pickles in scratchpad): new_unique, excluded (dup vs old), review_dup (uncertain), stats."""
import re, unicodedata, collections
import pandas as pd
from rapidfuzz import process, fuzz
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
SL = {'co', 'com', 'net', 'org', 'gov', 'ac', 'edu', 'or', 'ne', 'go', 'gob', 'gouv'}

def regdom(d):
    d = str(d or '').lower().strip()
    d = re.sub(r'^(https?://)?(www\d?\.)?', '', d).split('/')[0].split(':')[0]
    p = d.split('.')
    if len(p) < 2: return ''
    if len(p) >= 3 and p[-2] in SL and len(p[-1]) == 2: return '.'.join(p[-3:])
    return '.'.join(p[-2:])

SUF = r'\b(inc|incorporated|ltd|limited|plc|corp|corporation|co|company|group|holdings?|ag|sa|spa|se|nv|llc|lp|gmbh|as|the|sas|bv|ab|pte|pty|pvt|private|kg|kgaa|oy|oyj|asa|srl|sl|sarl|bhd|sdn|tbk|pt|jsc|ojsc|pjsc|cv|de|of|and)\b'
GEN = r'\b(international|global|worldwide|technologies|technology|tech|systems|solutions|services|industries|industrial|enterprises?|partners|brands|usa|us|uk|europe|america|americas|asia|india|china|japan|official)\b'

def strict(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)', ' ', s).replace('&', ' and ')
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(SUF, ' ', s)
    return re.sub(r'\s+', '', s)

def core(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\(.*?\)', ' ', s).replace('&', ' and ')
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(SUF, ' ', s); s = re.sub(GEN, ' ', s)
    return re.sub(r'\s+', '', s)

new = pd.read_pickle(f'{S}/new_all.pkl')
old = pd.read_pickle(f'{S}/old_all.pkl')
new['rd'] = new['domain'].map(regdom); new['sn'] = new['name'].map(strict); new['cn'] = new['name'].map(core)
old['rd'] = old['domain'].map(regdom); old['sn'] = old['name'].map(strict); old['cn'] = old['name'].map(core)
n0 = len(new)
# --- internal dedupe: one row per registered domain (else per strict name); remember every source CSV
new['_k'] = new['rd'].where(new['rd'] != '', 'N:' + new['sn'])
new = new[new['_k'] != 'N:']
src = new.groupby('_k')['source_csv'].agg(lambda x: '; '.join(sorted(set(x))))
srch = new.groupby('_k')['clay_search'].agg(lambda x: ' || '.join(sorted(set(x))))
new = new.drop_duplicates('_k').copy()
new['source_csv'] = new['_k'].map(src); new['clay_search'] = new['_k'].map(srch)
n1 = len(new)
# a second pass on strict name (same brand on two domains) - keep first, list as internal dup
dupname = new[new['sn'].str.len() >= 4].duplicated('sn', keep='first')
internal = new[new['sn'].str.len() >= 4][dupname]
new = new.drop(internal.index)
# --- match against old
od = old[old['rd'] != ''].drop_duplicates('rd').set_index('rd')
on = old[old['sn'].str.len() >= 3].drop_duplicates('sn').set_index('sn')
oc = old[old['cn'].str.len() >= 5].drop_duplicates('cn').set_index('cn')
reason, status, match = [], [], []
for rd, sn, cn in zip(new['rd'], new['sn'], new['cn']):
    if rd and rd in od.index:
        o = od.loc[rd]; reason.append(f"same website ({rd}) as '{o['name']}'"); status.append('dup'); match.append(o['source'])
    elif len(sn) >= 3 and sn in on.index:
        o = on.loc[sn]; reason.append(f"same name as '{o['name']}'"); status.append('dup'); match.append(o['source'])
    elif len(cn) >= 5 and cn in oc.index:
        o = oc.loc[cn]; reason.append(f"name variation of '{o['name']}' ({o['domain'] or 'no domain'})"); status.append('maybe'); match.append(o['source'])
    else:
        reason.append(''); status.append('new'); match.append('')
new['dup_reason'] = reason; new['dup_status'] = status; new['matched_in'] = match
# --- fuzzy pass for remaining 'new' rows against old strict names (same first 3 chars)
oldsn = old.loc[old['sn'].str.len() >= 5, ['sn', 'name', 'source']].drop_duplicates('sn')
byp = collections.defaultdict(list)
for sn, nm, sc in oldsn.itertuples(index=False): byp[sn[:3]].append((sn, nm, sc))
m = new['dup_status'].eq('new') & new['sn'].str.len().ge(5)
for i in new.index[m]:
    sn = new.at[i, 'sn']; cand = byp.get(sn[:3])
    if not cand: continue
    best = process.extractOne(sn, [c[0] for c in cand], scorer=fuzz.ratio, score_cutoff=92)
    if best:
        c = cand[best[2]]
        new.at[i, 'dup_status'] = 'maybe'; new.at[i, 'dup_reason'] = f"close spelling of '{c[1]}' ({best[1]:.0f}% match)"; new.at[i, 'matched_in'] = c[2]
new.to_pickle(f'{S}/new_dedup.pkl'); internal.to_pickle(f'{S}/internal_dups.pkl')
c = new['dup_status'].value_counts().to_dict()
print(f'rows {n0} -> unique by website/name {n1} -> after same-name merge {len(new)} (internal dups {n0 - len(new)})')
print('vs old:', c)
