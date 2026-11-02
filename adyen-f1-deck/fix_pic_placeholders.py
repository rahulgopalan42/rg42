"""Give pptxgenjs image placeholders their picture type.

pptxgenjs 3.12 drops type="pic" when it writes an image placeholder, so PowerPoint
treats it as a generic content box. Every untyped, indexed <p:ph> in this deck is a
photo placeholder; stamp type="pic" on it in layouts and slides. Rewrites in place.
"""
import re
import shutil
import sys
import tempfile
import zipfile

src = sys.argv[1]
PH = re.compile(r"<p:ph\s[^>]*?/>", re.S)


def fix(xml):
    def one(m):
        tag = m.group(0)
        if "type=" in tag or 'idx="4294967295"' in tag or "idx=" not in tag:
            return tag
        return tag.replace("<p:ph", '<p:ph type="pic"', 1)
    return PH.sub(one, xml)


tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
changed = 0
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if re.match(r"ppt/(slides/slide|slideLayouts/slideLayout)\d+\.xml$", item.filename):
            text = data.decode("utf-8")
            new = fix(text)
            if new != text:
                changed += 1
                data = new.encode("utf-8")
        zout.writestr(item, data)
shutil.move(tmp, src)
print(f"picture placeholders typed in {changed} parts")
