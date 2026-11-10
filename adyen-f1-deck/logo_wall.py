"""Rebuild the F1 brand logo wall (slide 8) with Gucci and Stripe added, as a 6 x 5 grid.

Usage: python3 logo_wall.py assets/f1_logo_wall_v1.png assets/logo_gucci.png assets/logo_stripe.png assets/f1_logo_wall.png
Then swap the image on page 8 of the PDF: pymupdf Page.replace_image(xref, filename=assets/f1_logo_wall.png).
"""
import sys
import numpy as np
from PIL import Image

src, gucci_png, stripe_png, out = sys.argv[1:5]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(int)
BG = 247
d = np.abs(a - BG).sum(2)
ink = (d > 40) & ~(np.abs(a - 255).sum(2) < 20)

def runs(p, minlen=2):
    r, s = [], None
    for i, v in enumerate(p > 0):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s >= minlen: r.append([s, i])
            s = None
    if s is not None: r.append([s, len(p)])
    return r

def merge(rs, gap=50):
    out = [rs[0][:]]
    for s, e in rs[1:]:
        if s - out[-1][1] < gap: out[-1][1] = e
        else: out.append([s, e])
    return out

NAMES = [["Atlassian", "AMD", "IBM", "CrowdStrike", "Dell"],
         ["Intel", "HP", "ExxonMobil", "adidas", "Visa", "PwC"],
         ["bp", "Etihad", "Aramco", "Cisco", "PepsiCo", "Revolut"],
         ["American Express", "Oracle", "SAP", "DHL", "Petronas"],
         ["Anthropic", "Salesforce", "Nestle", "Disney", "Lenovo", "LVMH"]]
logos, row_centers = {}, []
for ri, (y0, y1) in enumerate(runs(ink.sum(1), 3)):
    groups = merge(runs(ink[y0:y1].sum(0)))
    assert len(groups) == len(NAMES[ri]), (ri, groups)
    cents = []
    for name, (x0, x1) in zip(NAMES[ri], groups):
        # full extent incl. light boxes (d > 6) inside the logo's column range
        thr = 6 if name == "American Express" else 30  # Amex sits on a light box; elsewhere ignore faint noise
        # search only inside this row's band, so nothing from the rows above or below is picked up
        sub = (np.abs(a[y0 - 2:y1 + 2, x0 - 6:x1 + 6] - BG).sum(2) > thr)
        ys, xs = np.where(sub)
        bx0, bx1 = x0 - 6 + xs.min(), x0 - 6 + xs.max() + 1
        by0, by1 = y0 - 2 + ys.min(), y0 - 2 + ys.max() + 1
        logos[name] = im.crop((bx0 - 2, by0, bx1 + 2, by1))
        cents.append((by0 + by1) / 2)
    row_centers.append(float(np.median(cents)))

def flat(png, h):
    """Logo PNG (transparent) flattened onto the panel grey, scaled to height h."""
    lg = Image.open(png).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    w = round(lg.width * h / lg.height)
    lg = lg.resize((w, h), Image.LANCZOS)
    base = Image.new("RGB", (w + 4, h + 4), (BG, BG, BG))
    base.paste(lg, (2, 2), lg)
    return base

logos["Stripe"] = flat(stripe_png, 58)
logos["Gucci"] = flat(gucci_png, 40)

LAYOUT = [["Atlassian", "AMD", "IBM", "CrowdStrike", "Dell", "HP"],
          ["Intel", "Anthropic", "ExxonMobil", "adidas", "Visa", "PwC"],
          ["bp", "Etihad", "Aramco", "Cisco", "PepsiCo", "Revolut"],
          ["American Express", "Stripe", "Oracle", "SAP", "DHL", "Petronas"],
          ["Salesforce", "Nestle", "Disney", "Lenovo", "LVMH", "Gucci"]]
# clean panel: every row's panel span (between its rounded edges) back to the panel grey
for y in range(a.shape[0]):
    cols = np.where(np.abs(a[y] - BG).sum(1) < 4)[0]
    if len(cols):
        a[y, cols.min() + 3:cols.max() - 2] = BG
canvas = Image.fromarray(a.astype("uint8"))
X0, X1 = 58, im.width - 58
for ri, row in enumerate(LAYOUT):
    ws = [logos[n].width for n in row]
    gap = (X1 - X0 - sum(ws)) / (len(row) - 1)
    x = X0
    for n in row:
        lg = logos[n]
        canvas.paste(lg, (round(x), round(row_centers[ri] - lg.height / 2)))
        x += lg.width + gap
canvas.save(out)
print("wrote", out, canvas.size, "rows at", [round(c) for c in row_centers])
