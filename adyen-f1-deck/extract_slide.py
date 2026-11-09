"""Save one slide of a deck as its own PowerPoint file (speaker notes included).

Usage: python3 extract_slide.py deck.pptx slide_number out.pptx
"""
import sys

from pptx import Presentation

src, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
prs = Presentation(src)
ids = prs.slides._sldIdLst
for i, sld in reversed(list(enumerate(list(ids), 1))):
    if i != n:
        prs.part.drop_rel(sld.rId)
        ids.remove(sld)
# drop the section list: it would point at slides that are no longer there
for ext in prs.part._element.findall(".//{http://schemas.openxmlformats.org/presentationml/2006/main}extLst"):
    ext.getparent().remove(ext)
slide = prs.slides[0]
slide._element.attrib.pop("show", None)
prs.save(out)

# python-pptx rewrites [Content_Types].xml from the parts it knows; make sure image extensions are declared
import shutil, tempfile, zipfile
TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}
with zipfile.ZipFile(out) as z:
    items = [(i, z.read(i.filename)) for i in z.infolist()]
ct = next(d for i, d in items if i.filename == "[Content_Types].xml").decode("utf-8")
exts = {i.filename.rsplit(".", 1)[-1].lower() for i, _ in items if i.filename.startswith("ppt/media/")}
for e in sorted(exts):
    if e in TYPES and f'Extension="{e}"' not in ct:
        ct = ct.replace("</Types>", f'<Default Extension="{e}" ContentType="{TYPES[e]}"/></Types>')
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
    for i, d in items:
        z.writestr(i, ct.encode("utf-8") if i.filename == "[Content_Types].xml" else d)
shutil.move(tmp, out)
print("wrote", out)
