"""Put the pitch script into the deck's speaker notes.

Reads "Adyen x F1 - Pitch script.md": each "## N · Title" section becomes the SCRIPT part of slide N's
notes; the notes the build wrote (sources, caveats) are kept underneath. Sections without a slide
number (the Q&A) are skipped. Checks that every numbered section lands on a visible slide.

Usage: python3 add_script.py deck.pptx
"""
import re
import sys

from pptx import Presentation

deck = sys.argv[1]
md = open("Adyen x F1 - Pitch script.md", encoding="utf-8").read()
sections = {}
for m in re.finditer(r"^## (\d+) · ([^\n]*)\n(.*?)(?=^## |^---|\Z)", md, re.S | re.M):
    n, body = int(m.group(1)), m.group(3).strip()
    body = re.sub(r"\*\*(.+?)\*\*", r"\1", body)
    body = re.sub(r"\*(.+?)\*", r"[\1]", body)
    sections[n] = body

prs = Presentation(deck)
for n, body in sections.items():
    slide = prs.slides[n - 1]
    assert slide._element.get("show") != "0", f"script for hidden slide {n}"
    tf = slide.notes_slide.notes_text_frame
    old = tf.text.strip()
    tf.text = "SCRIPT\n" + body + ("\n\nSOURCES AND NOTES\n" + old if old else "")
prs.save(deck)

# python-pptx rewrites [Content_Types].xml from the parts it knows; make sure every media
# extension in the package still has a Default content type (pptxgenjs names photos .jpg).
import shutil, tempfile, zipfile
TYPES = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif", "svg": "image/svg+xml"}
with zipfile.ZipFile(deck) as z:
    names = z.namelist()
    ct = z.read("[Content_Types].xml").decode("utf-8")
exts = {n.rsplit(".", 1)[-1].lower() for n in names if n.startswith("ppt/media/") and "." in n}
missing = [e for e in sorted(exts) if e in TYPES and f'Extension="{e}"' not in ct]
if missing:
    add = "".join(f'<Default Extension="{e}" ContentType="{TYPES[e]}"/>' for e in missing)
    ct = ct.replace("<Default ", add + "<Default ", 1)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
    with zipfile.ZipFile(deck) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = ct.encode("utf-8") if item.filename == "[Content_Types].xml" else zin.read(item.filename)
            zout.writestr(item, data)
    shutil.move(tmp, deck)
print(f"script added to {len(sections)} slides; content types added: {missing or 'none'}")
