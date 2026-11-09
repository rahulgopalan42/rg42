"""Renumber the slide numbers in an exported deck PDF so they run 1..N by page.

Finds the small grey number at the bottom right of each page, removes it (text only; images and
background untouched) and writes the page's position in its place, right-aligned to the same edge,
in a Calibri-metric font at the same size and colour.
"""
import re
import sys

import pymupdf

src, out = sys.argv[1], sys.argv[2]
FONT = "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf"
font = pymupdf.Font(fontfile=FONT)
doc = pymupdf.open(src)
changes = []
for i, page in enumerate(doc, 1):
    spans = [sp for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for sp in l["spans"]
             if sp["bbox"][1] > 495 and sp["bbox"][0] > 850 and re.fullmatch(r"\d{1,2}", sp["text"].strip())]
    if not spans:
        continue
    sp = spans[0]
    old, new = sp["text"].strip(), str(i)
    if old == new:
        continue
    x0, y0, x1, y1 = sp["bbox"]
    page.add_redact_annot(pymupdf.Rect(x0 - 0.5, y0, x1 + 0.5, y1), fill=False)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    size, c = sp["size"], sp["color"]
    color = ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)
    width = font.text_length(new, fontsize=size)
    page.insert_text((x1 - width, sp["origin"][1]), new, fontsize=size, fontname="Carlito", fontfile=FONT, color=color)
    changes.append((i, old, new))
doc.save(out, garbage=3, deflate=True)
print("renumbered:", ", ".join(f"p{i}: {o}->{n}" for i, o, n in changes))
