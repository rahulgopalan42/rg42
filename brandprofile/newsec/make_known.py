"""Writes newsec/known.json: every name already on the 48-tab sheet, on the listed-company universe or on the F1 roster, keyed by a loose form of the name."""
import html, json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(H))
import bp_build as b, allsector as a
A, rows, L = a.load()
K = {}
def put(n, why):
    k = b.loose(n)
    if k and k not in K: K[k] = [n, why]
for d in A['f1x']: put(d['name'], 'current F1 partner')
for x in rows:
    w = 'on the sheet (' + x['sector'] + ', ' + x['status'] + ')'
    put(x['name'], w); put(x['r']['brand'], w)
PA = b.pb.assemble()
for c in PA['U'].values(): put(html.unescape(c['name']), 'listed on a stock exchange')
json.dump(K, open(os.path.join(H, 'known.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(K))
