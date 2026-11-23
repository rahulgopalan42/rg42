"""Refresh of 23 Nov 2026: reads newsec/refresh/events_*.jsonl and says where each company sits (new-brands list of 18 Nov, the 48-tab sheet, or neither).
Writes newsec/refresh/resolved.json for refresh_decide.py. Usage: refresh_resolve.py"""
import glob, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import bp_build as b, allsector as a
RD = os.path.join(H, 'newsec', 'refresh')
def main():
    A, rows, L = a.load()
    sheet = {}
    for x in rows:
        for n in (x['name'], x['r']['brand']):
            k = b.loose(n)
            if k and k not in sheet: sheet[k] = x
    inscope = {id(x) for x in L}
    f1 = {b.loose(d['name']): d['name'] for d in A['f1x']}
    snap = {b.loose(d['name']): d for d in json.load(open(os.path.join(RD, 'v3_snapshot.json'), encoding='utf-8'))}
    out = []
    for f in sorted(glob.glob(os.path.join(RD, 'events_*.jsonl'))):
        for i, l in enumerate(open(f, encoding='utf-8')):
            l = l.strip()
            if not l: continue
            d = json.loads(l); d['file'] = os.path.basename(f)[7:-6]; d['line'] = i
            names = [d.get('company') or '']
            m = re.search(r' as (.+?)(?:\s*[|;]|$)', d.get('known_as') or '')
            if m: names.append(m.group(1).strip())
            names += [re.sub(r'\s*\([^)]*\)', '', n) for n in list(names)]
            t = None
            for n in names:
                k = b.loose(n)
                if not k: continue
                if k in snap: t = ('new', snap[k]['name'], snap[k].get('tab', '')); break
                if k in sheet:
                    x = sheet[k]; t = ('sheet', x['name'], x['status'] + ('' if id(x) in inscope else ', out of scope') + ' | ' + x['r'].get('sector', '')); break
                if k in f1: t = ('f1', f1[k], 'current F1 partner'); break
            d['target'] = t or ('none', '', '')
            out.append(d)
    json.dump(out, open(os.path.join(RD, 'resolved.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return out
if __name__ == '__main__':
    out = main()
    from collections import Counter
    print(len(out), Counter(d['target'][0] for d in out))
