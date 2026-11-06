"""Use slides the team has written themselves, exactly as they wrote them.

Eleri rewrote the Max Verstappen slides (route 1: overview, business, rights, hospitality bundle) in the
reviewed deck. This swaps each of those slides into the built deck in place of the generated one: her
slide XML and images go in as they are, mapped onto this deck's layout of the same name. The built
slide's position, section and speaker notes (the script) are kept.

Usage: python3 use_reviewed_slides.py deck.pptx
"""
import posixpath
import re
import shutil
import sys
import tempfile
import zipfile

SOURCE = "reviewed/Adyen x F1 - Chairman deck 7 v2 (Eleri's Max slides).pptx"
# (slide in the reviewed deck, eyebrow it must carry; the built deck's slides are found by the same eyebrows, in order)
SLIDES = [(19, "ROUTE 1 · MAX VERSTAPPEN"), (20, "ROUTE 1 · BUSINESS OPPORTUNITY"),
          (21, "ROUTE 1 · RIGHTS PACKAGE"), (22, "ROUTE 1 · HOSPITALITY BUNDLE")]

deck = sys.argv[1]
src = zipfile.ZipFile(SOURCE)
dst = zipfile.ZipFile(deck)
files = {n: dst.read(n) for n in dst.namelist()}
infos = {i.filename: i for i in dst.infolist()}


def rels_path(part):
    d, f = posixpath.split(part)
    return posixpath.join(d, "_rels", f + ".rels")


def rels(xml):
    return [dict(re.findall(r'(\w+)="([^"]*)"', r)) for r in re.findall(r"<Relationship\s+([^>]*?)/?>", xml)]


def texts(xml):
    return [t for t in re.findall(r"<a:t>([^<]*)</a:t>", xml)]


def slide_order(z_read, names):
    pres = z_read("ppt/presentation.xml").decode("utf-8")
    prels = {r["Id"]: r["Target"] for r in rels(z_read("ppt/_rels/presentation.xml.rels").decode("utf-8"))}
    return ["ppt/" + prels[rid] for rid in re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"', pres)]


def layout_name(read, part):
    m = re.search(r'<p:cSld name="([^"]*)"', read(part).decode("utf-8"))
    return m.group(1)


dst_order = slide_order(lambda n: files[n], files)
src_order = slide_order(src.read, src.namelist())
dst_layouts = {layout_name(lambda n: files[n], n): n for n in files if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", n)}

# where the Max slides sit in the built deck: the first visible run that starts with the route 1 overview
start = next(i for i, p in enumerate(dst_order) if SLIDES[0][1] in texts(files[p].decode("utf-8")))
for k, (src_n, eyebrow) in enumerate(SLIDES):
    tgt = dst_order[start + k]
    sp = src_order[src_n - 1]
    sxml = src.read(sp).decode("utf-8")
    assert eyebrow in texts(sxml), f"reviewed slide {src_n} is not '{eyebrow}'"
    assert eyebrow in texts(files[tgt].decode("utf-8")), f"built slide {start + k + 1} is not '{eyebrow}'"
    old_rels = rels(files[rels_path(tgt)].decode("utf-8"))
    replaced_media = [posixpath.normpath(posixpath.join(posixpath.dirname(tgt), r["Target"])) for r in old_rels if r["Type"].endswith("/image")]
    notes = next((r for r in old_rels if r["Type"].endswith("/notesSlide")), None)
    out = []
    for r in rels(src.read(rels_path(sp)).decode("utf-8")):
        typ = r["Type"]
        abs_t = posixpath.normpath(posixpath.join(posixpath.dirname(sp), r["Target"]))
        if typ.endswith("/notesSlide"):
            if not notes:
                continue
            target = notes["Target"]
        elif typ.endswith("/slideLayout"):
            target = posixpath.relpath(dst_layouts[layout_name(src.read, abs_t)], posixpath.dirname(tgt))
        elif typ.endswith("/image"):
            media = posixpath.join("ppt/media", "team_" + posixpath.basename(abs_t))
            files[media] = src.read(abs_t)
            target = posixpath.relpath(media, posixpath.dirname(tgt))
        else:
            raise SystemExit(f"unexpected relationship on reviewed slide {src_n}: {typ}")
        out.append(f'<Relationship Id="{r["Id"]}" Type="{typ}" Target="{target}"/>')
    sxml = re.sub(r'(<p:sld\b[^>]*?)\sshow="[01]"', r"\1", sxml, count=1)
    files[tgt] = sxml.encode("utf-8")
    files[rels_path(tgt)] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(out) + "</Relationships>").encode("utf-8")
    # drop the generated slide's images if nothing else uses them
    for media in replaced_media:
        name = posixpath.basename(media)
        if not any(n.endswith(".rels") and name.encode() in d for n, d in files.items()):
            files.pop(media, None)
    print(f"slide {start + k + 1}: now reviewed slide {src_n} ({eyebrow})")

ct = files["[Content_Types].xml"].decode("utf-8")
for ext, typ in (("jpg", "image/jpeg"), ("jpeg", "image/jpeg"), ("png", "image/png")):
    if any(n.startswith("ppt/media/team_") and n.lower().endswith("." + ext) for n in files) and f'Extension="{ext}"' not in ct:
        ct = ct.replace("</Types>", f'<Default Extension="{ext}" ContentType="{typ}"/></Types>')
files["[Content_Types].xml"] = ct.encode("utf-8")

tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
    for n in [n for n in dst.namelist() if n in files] + [n for n in files if n not in dst.namelist()]:
        z.writestr(infos.get(n, n), files[n])
shutil.move(tmp, deck)
