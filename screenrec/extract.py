"""Read Crunchbase Advanced Search result tables from a screen recording (OCR), fast enough for ~2 hours of video on
4 CPUs.

How it works
- Frames are sampled at 6 fps (1920x1080).
- The table's column-header row is located on every frame by template matching (cheap). The band of screen just
  above it (filter chips, "< Prev 951-993 Next > of 993 results") and the header itself are OCR'd (detection +
  recognition) only when those pixels change or the header moves; the header gives each column's x position.
- Table rows below the header are found from the text-line profile of the name / amount columns. Each fully visible
  row gets a cheap pixel signature; a row whose signature has not been seen on the current page is new, and only its
  cells are recognised (no detection pass). A row read on a moving frame with low confidence is read again once the
  screen is still.
Output: one JSON line per frame that produced anything:
  {t, key: [page range, results, band chips], rows: [{y, still, cells: {org|ipo|total|date|ind|hq|desc: [text, conf]}}],
   top: [[x0, y0, x1, y1, text, conf], ...] (only when the band above the header was re-read)}

Usage: extract.py <video> <out.jsonl> [ffmpeg input args, e.g. -ss 40 -t 20]"""
import json, os, re, subprocess, sys, time
import numpy as np
import cv2
from rapidocr_onnxruntime import RapidOCR
import imageio_ffmpeg

video, out, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
W, H, FPS, RIGHT, INK = 1920, 1080, 6, 1300, 150
ABOVE, BELOW = 130, 24                          # top band read around the header row: [hy - ABOVE, hy + BELOW]
HEAD = {'org': 'Organization Name', 'ipo': 'IPO Status', 'last': 'Last Funding Amount', 'total': 'Total Funding Amount',
        'date': 'Last Funding Date', 'stage': 'Stage', 'ind': 'Industries', 'hq': 'Headquarters Location',
        'desc': 'Description', 'rank': 'CB Rank'}
SKIP = {'stage', 'rank', 'last'}                # "Track Stages" (always "Not Started"), CB Rank, last round size: not needed
DEBUG = bool(os.environ.get('XDEBUG'))
FF = imageio_ffmpeg.get_ffmpeg_exe()
proc = subprocess.Popen([FF, '-hide_banner', '-loglevel', 'error', '-threads', '1', *extra, '-i', video, '-vf', f'fps={FPS},scale={W}:{H},format=gray',
                         '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
ocr = RapidOCR(intra_op_num_threads=1, inter_op_num_threads=1, det_limit_type='max', det_limit_side_len=2000)
rgb = lambda a: np.ascontiguousarray(np.stack([a] * 3, -1))

def ocr_boxes(img, dy):
    res, _ = ocr(rgb(img), use_cls=False)
    return [[int(min(p[0] for p in b)), int(min(p[1] for p in b)) + dy, int(max(p[0] for p in b)), int(max(p[1] for p in b)) + dy, t, round(float(c), 3)]
            for b, t, c in (res or [])]

LABELS = [('org', 'Organization'), ('ipo', 'IPO Stat'), ('last', 'Last Funding A'), ('total', 'Total Funding'), ('date', 'Last Funding D'),
          ('ind', 'Industries'), ('hq', 'Headquarter'), ('desc', 'Description'), ('rank', 'CB Rank'), ('stage', 'Stage')]
def header_of(bx, prev=None):
    """header y, header bottom and column x-starts from OCR boxes (labels the OCR missed are taken from the previous
    header when the table has not moved sideways), or None"""
    hdr = [b for b in bx if 'Organization' in b[4]]
    if not hdr: return None
    hy = hdr[0][1]; row = [b for b in bx if abs(b[1] - hy) < 12]
    cols = {}
    for x0, y0, x1, y1, t, c in row:
        t2 = t.replace('Track Stages', '#' * 12)
        for k, lab in LABELS:
            i = t2.find(lab)
            if i >= 0 and k not in cols: cols[k] = int(x0 + (x1 - x0) * i / max(len(t), 1))
    if prev and abs(prev.get('org', -99) - cols['org']) <= 6:
        for k, x in prev.items(): cols.setdefault(k, x)
    if 'total' not in cols: return None
    return hy, max(b[3] for b in row) + 2, cols

def lines(prof, minh, gap=1):
    """runs of y where the ink profile is > 0 -> [(start, end)]"""
    on = np.flatnonzero(prof > 0); res = []
    if not len(on): return res
    s = p = on[0]
    for y in on[1:]:
        if y - p > gap + 1:
            if p - s + 1 >= minh: res.append((s, p))
            s = y
        p = y
    if p - s + 1 >= minh: res.append((s, p))
    return res

def blocks(a):                  # 4x4 block means: robust to video-compression noise, still sees a changed digit
    a = a[:a.shape[0] // 4 * 4, :a.shape[1] // 4 * 4].astype(np.float32)
    return a.reshape(a.shape[0] // 4, 4, a.shape[1] // 4, 4).mean((1, 3))

def sig(f, c, x0=76):
    """column ink profile of the name and funding cells (x0 .. x0+470) at full resolution: different companies differ
    in name length and letter shapes, the same row read on another frame gives the same profile"""
    return (f[c - 9:c + 10, x0:x0 + 470] < INK).sum(0).astype(np.float32)

def same(a, b):
    sa, sb = a.sum(), b.sum()
    if sa < 5 or abs(sa - sb) > 0.12 * max(sa, sb): return False
    na, nb = np.flatnonzero(a[:150]), np.flatnonzero(b[:150])          # where the name text ends
    if len(na) and len(nb) and abs(int(na[-1]) - int(nb[-1])) > 3: return False
    a = a - a.mean(); b = b - b.mean(); n = np.sqrt((a * a).sum() * (b * b).sum())
    return n > 0 and (a * b).sum() / n > 0.9

fo = open(out, 'w')
tmpl = None                     # header-row template (x 20..700)
top = None                      # (boxes, hy, hb, cols, page key)
topimg = None; tophy = None; lastcols = None; lastfail = -99; pages = {}; page = None; prevsmall = None; lastsearch = (-99, None)
n = nrows = nrec = ntop = nsearch = 0; t0 = time.time()
while True:
    buf = proc.stdout.read(W * H)
    if len(buf) < W * H: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W); n += 1; t = round((n - 1) / FPS, 2)
    sm = f[150:1076:4, 20:RIGHT:4].astype(np.int16)
    still = prevsmall is not None and np.abs(sm - prevsmall).mean() < 0.5; prevsmall = sm
    # 1. locate the header row
    hy = None
    if tmpl is not None:
        r = cv2.matchTemplate(f[140:1000, 20:700], tmpl, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(r)
        if mx > 0.75: hy = loc[1] + 140 + 2
    if hy is None:              # full search (expensive): only on a changed screen and at most every 2 s
        if n - lastsearch[0] < 2 * FPS or (lastsearch[1] is not None and np.abs(sm - lastsearch[1]).mean() < 1.0): continue
        lastsearch = (n, sm); nsearch += 1
        bx = ocr_boxes(f[140:1080, :RIGHT], 140); h = header_of(bx)
        if DEBUG: print('search', t, h is not None, flush=True)
        if h is None: continue
        hy = h[0]; tmpl = f[hy - 2:hy + 20, 20:700].copy(); top = None
    # 2. (re)read the band above the header when it changed
    ya = max(140, hy - ABOVE); yb = hy + BELOW
    newtop = False
    cur = blocks(f[ya:yb, :RIGHT])
    moved = tophy is None or abs(hy - tophy) > 2 or cur.shape != topimg.shape
    changed = moved or (np.abs(cur - topimg) > 25).sum() > 2
    if top is None and n - lastfail < 3: continue      # a failed read of the header band is retried every 0.5 s
    if changed and not moved and top is not None and page:
        # a cursor over the pagination also changes these pixels: only re-read if the table shows rows not seen on this page
        tb, _, hb, cols, key = top
        reg = f[hb + hy - tophy + 2:1078, cols['org'] + 16:cols['org'] + 450] < INK
        cs = [(s + e) // 2 + hb + hy - tophy + 2 for s, e in lines(reg.sum(1), 8) if s > 2 and e < reg.shape[0] - 3 and e - s < 26]
        cs = [c for c in cs if c + 21 <= 1078]
        unseen = sum(1 for c in cs if not any(same(r['sig'], sig(f, c, max(cols['org'] + 25, 73))) for r in page))
        if unseen < 3: changed = False; topimg = cur
    if changed:
        bx = ocr_boxes(f[ya:yb, :RIGHT], ya); h = header_of(bx, lastcols); ntop += 1
        if DEBUG: print('top', t, hy, h is not None, flush=True)
        if h is None:
            top = None; tophy = None; lastfail = n; continue
        txt = ' '.join(b[4] for b in bx if b[3] <= h[1] + 2).replace(' ', '')
        m1 = re.search(r'(\d[\d,]*)-(\d[\d,]*)', txt); m2 = re.search(r'of([\d,]+)result', txt)
        key = (m1.group(0) if m1 else '', m2.group(1) if m2 else '', ' '.join(re.findall(r'\$[\d.,]+[MBK]', txt)))
        top = ([b for b in bx if b[3] <= h[1] + 2], h[0], h[1], h[2], key); lastcols = h[2]
        tophy = hy; topimg = cur; newtop = True
        page = pages.setdefault(key, [])
    tb, _, hb, cols, key = top
    hb = hb + hy - tophy
    order = sorted((x, k) for k, x in cols.items())
    xs = [x for x, _ in order] + [RIGHT]
    span = {k: (xs[i], xs[i + 1]) for i, (_, k) in enumerate(order)}
    a0, a1 = cols['org'] + 16, span['total'][1] - 6
    namex = max(cols['org'] + 25, 73)
    y0 = hb + 2
    if y0 > 1040: continue
    # 3. rows
    reg = f[y0:1078, a0:a1] < INK
    rows = [(s + y0, e + y0) for s, e in lines(reg.sum(1), 8) if s > 2 and e < reg.shape[0] - 3 and e - s < 26]
    if DEBUG: print('lines', t, [(s + y0, e + y0) for s, e in lines(reg.sum(1), 8)], flush=True)
    crops, meta, rowsout = [], [], []
    for s, e in rows:
        c = (s + e) // 2
        if c - 21 < y0 or c + 21 > 1078: continue
        g = sig(f, c, namex)
        hit = next((r for r in page if same(r['sig'], g)), None)
        if DEBUG: print('row', t, c, 'match' if hit is not None else 'new', hit.get('name', '') if hit else '', flush=True)
        if hit is not None and (hit['conf'] >= 0.8 or not still or hit['reread']): continue
        if hit is not None: hit['reread'] = True
        else:
            hit = {'sig': g, 'conf': 1.0, 'reread': still}; page.append(hit)
        cells = []
        for k, (x0, x1) in span.items():
            if k in SKIP or x0 >= RIGHT - 20: continue
            if k == 'org': x0 = namex + 2                # name text starts at a fixed x; the logo sits left of it
            if k == 'desc':                             # two text lines per row
                pr = (f[c - 18:c + 21, x0:min(x1, RIGHT) - 4] < INK).sum(1)
                for ls, le in lines(pr, 4):
                    if -13 <= c - 18 + (ls + le) / 2 - c <= 15 and le - ls < 18:     # this row's lines only
                        cells.append((k, x0, c - 18 + ls - 3, min(x1, RIGHT) - 4, c - 18 + le + 4))
                continue
            cells.append((k, x0 - 2, s - 3, x1 - 6, e + 4))
        for k, x0, ya2, x1, yb2 in cells:
            m = f[ya2:yb2, x0:x1] < INK                                       # tighten to the text, like a detector box
            ink = np.flatnonzero(m.any(0)); iy = np.flatnonzero(m.any(1))
            if not len(ink): continue
            x0, x1 = max(x0, x0 + int(ink[0]) - 5), min(x1, x0 + int(ink[-1]) + 6)
            ya2, yb2 = ya2 + max(0, int(iy[0]) - 3), ya2 + int(iy[-1]) + 4
            if x1 - x0 < 8: continue
            crops.append(rgb(f[ya2:yb2, x0:x1])); meta.append((hit, len(rowsout), k))
        rowsout.append({'y': int(c), 'still': bool(still), 'cells': {}})
        nrows += 1
    if crops:
        rec, _ = ocr.text_rec(crops, False); nrec += len(crops)
        for (hit, ri, k), r in zip(meta, rec):
            txt, cf = r[0].strip(), float(r[1])
            if not txt: continue
            hit['conf'] = min(hit['conf'], cf)
            if k == 'org' and 'name' not in hit: hit['name'] = txt
            cl = rowsout[ri]['cells']
            if k in cl: cl[k] = [cl[k][0] + ' ' + txt, round(min(cl[k][1], cf), 3)]
            else: cl[k] = [txt, round(cf, 3)]
    rowsout = [r for r in rowsout if 'org' in r['cells']]
    if rowsout or newtop:
        rec_ = {'t': t, 'key': list(key), 'rows': rowsout}
        if newtop: rec_['top'] = tb
        fo.write(json.dumps(rec_) + '\n'); fo.flush()
print(f'{video}: frames {n}, header searches {nsearch}, top reads {ntop}, rows read {nrows}, crops {nrec}, pages {len(pages)}, {time.time() - t0:.0f}s', flush=True)
