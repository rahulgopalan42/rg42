"""Apply quick-triage results: junk rows become a stage-1 drop (out_NNNN.json); keep rows are re-packed into
new screening batches. Only touches batches that have a triage file and no out file.
Usage: python3 -I wave15/triage_apply.py"""
import glob, json, os
W = '/home/user/rg42/wave15/screen'
keep = []; nj = 0
for t in sorted(glob.glob(f'{W}/triage_*.json')):
    b = t[-9:-5]
    if os.path.exists(f'{W}/out_{b}.json') or os.path.exists(f'{W}/triaged_{b}.done'):
        continue
    ins = json.load(open(f'{W}/in_{b}.json'))
    tr = {r['id']: r for r in json.load(open(t))}
    if len(tr) < len(ins):
        print('incomplete triage', b); continue
    junk = []
    for r in ins:
        x = tr.get(r['id'], {})
        if x.get('t') == 'junk':
            junk.append(dict(id=r['id'], company=r['company'], keep=False, reason='quick triage: ' + (x.get('r') or 'junk'),
                             real_name='', parent='', status='unknown', scale_route='below', scale_evidence='',
                             staff_est='', f1_tie='', sector='', fit=0, verdict_guess='No', note=''))
        else:
            keep.append(r)
    json.dump(junk, open(f'{W}/out_{b}.json', 'w'), indent=0, ensure_ascii=False)
    open(f'{W}/triaged_{b}.done', 'w').write(str(len(junk)))
    nj += len(junk)
start = max(int(f[-9:-5]) for f in glob.glob(f'{W}/in_*.json'))
for i in range(0, len(keep), 60):
    json.dump(keep[i:i + 60], open(f'{W}/in_{start + i // 60 + 1:04d}.json', 'w'), indent=0, ensure_ascii=False)
print('junk', nj, 'kept for screening', len(keep), 'new batches', start + 1, '-', start + (len(keep) + 59) // 60)
