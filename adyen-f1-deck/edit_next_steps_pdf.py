"""Replace the step list on the Next steps page of the exported final PDF.

Removes the old numbered steps (text, circles and connector; images and header untouched) and draws
the new, shorter list in the same style: green first and last circles, navy middle ones, a grey
connector, bold Calibri-metric headings and a green date line where there is one.

Usage: python3 edit_next_steps_pdf.py in.pdf out.pdf page_number
"""
import sys

import pymupdf

src, out, pno = sys.argv[1], sys.argv[2], int(sys.argv[3])
BOLD = "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"
STEPS = [("Meeting with the Chairman", "Week of 9 November 2026"),
         ("Revisit the rights package", None),
         ("Contracting", None),
         ("Launch in Milan", "February 2027")]
GREEN, NAVY, WHITE = (0.0392, 0.749, 0.325), (0.0, 0.0667, 0.173), (1, 1, 1)
DEEP, LINE = (0.0275, 0.6039, 0.2667), (0.835, 0.855, 0.878)

doc = pymupdf.open(src)
page = doc[pno - 1]
assert "Next steps" in page.get_text(), "not the Next steps page"
page.add_redact_annot(pymupdf.Rect(40, 130, 560, 476), fill=WHITE)
page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED)

font = pymupdf.Font(fontfile=BOLD)
cx, d, top, bottom = 63.4, 39.6, 140.8, 428.9
step = (bottom - top) / (len(STEPS) - 1)
centres = [top + d / 2 + i * step for i in range(len(STEPS))]
page.draw_line((cx, centres[0]), (cx, centres[-1]), color=LINE, width=2)
for i, ((head, sub), cy) in enumerate(zip(STEPS, centres)):
    edge = i in (0, len(STEPS) - 1)
    page.draw_circle((cx, cy), d / 2, color=WHITE, fill=GREEN if edge else NAVY, width=2)
    n = str(i + 1)
    page.insert_text((cx - font.text_length(n, fontsize=15.1) / 2, cy + 5.3), n, fontsize=15.1, fontname="CarlitoB",
                     fontfile=BOLD, color=NAVY if edge else WHITE)
    if sub:
        page.insert_text((100.8, cy - 1), head, fontsize=17.3, fontname="CarlitoB", fontfile=BOLD, color=NAVY)
        page.insert_text((100.8, cy + 15), sub, fontsize=12, fontname="CarlitoB", fontfile=BOLD, color=DEEP)
    else:
        page.insert_text((100.8, cy + 6), head, fontsize=17.3, fontname="CarlitoB", fontfile=BOLD, color=NAVY)
doc.save(out, garbage=3, deflate=True)
print("wrote", out)
