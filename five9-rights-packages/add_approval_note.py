"""Mark every rights-package slide "Rights package*" and add a "*Subject to approval" footnote.

Usage: python3 add_approval_note.py <unpacked_deck_dir> slideN.xml [slideM.xml ...]
The footnote sits under the left card column, level with the slide number. Safe to re-run.
"""
import re
import sys

ROOT = sys.argv[1]
NOTE = "*Subject to approval"
X = 1278048                      # left edge of the card grid
Y, CX, CY = 5800721, 3657600, 251460   # vertically centred on the slide-number placeholder


def footnote(shape_id):
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="Footnote Approval"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{X}" y="{Y}"/><a:ext cx="{CX}" cy="{CY}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        '<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="ctr"><a:noAutofit/></a:bodyPr>'
        '<a:lstStyle/><a:p><a:pPr algn="l"/><a:r><a:rPr lang="en-GB" sz="900" dirty="0">'
        '<a:solidFill><a:schemeClr val="bg1"/></a:solidFill>'
        '<a:latin typeface="Aptos Light" panose="020B0004020202020204" pitchFamily="34" charset="0"/></a:rPr>'
        f'<a:t>{NOTE}</a:t></a:r></a:p></p:txBody></p:sp>'
    )


for slide in sys.argv[2:]:
    path = f"{ROOT}/ppt/slides/{slide}"
    xml = open(path, encoding="utf-8").read()
    if 'name="Footnote Approval"' not in xml:
        next_id = max(int(i) for i in re.findall(r'<p:cNvPr id="(\d+)"', xml)) + 1
        i = xml.rindex("</p:spTree>")
        xml = xml[:i] + footnote(next_id) + xml[i:]
    xml = xml.replace("<a:t>Rights package</a:t>", "<a:t>Rights package*</a:t>", 1)
    open(path, "w", encoding="utf-8").write(xml)
    print("noted", slide)
