"""Add an "INVESTMENT / <price> / <caption>" callout to the top right of a rights-package slide.

Usage: python3 add_price_callout.py <unpacked_deck_dir> <slide.xml> "<price>" ["<caption>"]
Right-aligned to the card grid, beside the "Rights package" title. Safe to re-run: an
existing callout is replaced. The title and price are pinned to Aptos Display (the deck's
heading font) so they match whichever slide master the slide sits on.
"""
import re
import sys
from xml.sax.saxutils import escape

ROOT, SLIDE, PRICE = sys.argv[1], sys.argv[2], sys.argv[3]
CAPTION = sys.argv[4] if len(sys.argv) > 4 else ""
E = 914400
RIGHT = 10756348                 # right edge of the card grid
W = round(2.2 * E)
WHITE, BLUE = '<a:schemeClr val="bg1"/>', '<a:srgbClr val="2A4CF9"/>'
HEAD_FONT = "Aptos Display"


def box(shape_id, name, y, h, text, sz, bold, italic, color, font, anchor):
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{RIGHT - W}" y="{y}"/><a:ext cx="{W}" cy="{h}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="{anchor}"><a:noAutofit/></a:bodyPr>'
        f'<a:lstStyle/><a:p><a:pPr algn="r"/><a:r><a:rPr lang="en-US" sz="{sz}" b="{int(bold)}" i="{int(italic)}" dirty="0">'
        f'<a:solidFill>{color}</a:solidFill><a:latin typeface="{font}"/></a:rPr>'
        f'<a:t>{escape(text)}</a:t></a:r></a:p></p:txBody></p:sp>'
    )


path = f"{ROOT}/ppt/slides/{SLIDE}"
xml = open(path, encoding="utf-8").read()
xml = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="\d+" name="Price (Label|Value|Caption)"/>.*?</p:sp>', "", xml, flags=re.S)
t = xml.index("<a:t>Rights package")
r = xml.rindex("<a:r>", 0, t)
xml = xml[:r] + xml[r:t].replace('<a:latin typeface="+mj-lt"/>', f'<a:latin typeface="{HEAD_FONT}"/>') + xml[t:]
next_id = max(int(i) for i in re.findall(r'<p:cNvPr id="(\d+)"', xml)) + 1
callout = (
    box(next_id, "Price Label", round(0.83 * E), round(0.30 * E), "INVESTMENT", 1600, False, False,
        WHITE, "Aptos Light", "b")
    + box(next_id + 1, "Price Value", round(1.15 * E), round(0.56 * E), PRICE,
          3200 if len(PRICE) <= 7 else 2800, True, True, BLUE, HEAD_FONT, "b")
)
if CAPTION:
    callout += box(next_id + 2, "Price Caption", round(1.74 * E), round(0.25 * E), CAPTION, 1200, False, False,
                   WHITE, "Aptos Light", "t")
i = xml.rindex("</p:spTree>")
xml = xml[:i] + callout + xml[i:]
open(path, "w", encoding="utf-8").write(xml)
print("price callout on", SLIDE, "->", PRICE, "/", CAPTION)
