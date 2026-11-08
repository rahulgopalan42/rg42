"""Append the reviewers' remark slides to the deck as hidden before-and-after pairs.

For each round of remarks in reviewed/changes.json, copies every slide with a remark from the
reviewed deck exactly as it was left: same XML, images, charts, notes, and its own slide layouts,
master and theme (so nothing reflows onto this deck's layouts). Where the remark led to an updated
slide, a copy of that slide from this deck follows it, tagged "After". Each round gets its own
hidden section at the end.

Usage: python3 add_remark_slides.py deck.pptx
"""
import posixpath
import re
import shutil
import sys
import tempfile
import json
import uuid
import zipfile
from xml.sax.saxutils import escape

ROUNDS = json.load(open("reviewed/changes.json", encoding="utf-8"))
EMU = 914400

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NOTES_MASTER_TYPE = R_NS + "/notesMaster"
SLIDE_TYPE = R_NS + "/slide"
LAYOUT_TYPE = R_NS + "/slideLayout"

deck = sys.argv[1]
dst = zipfile.ZipFile(deck)
files = {n: dst.read(n) for n in dst.namelist()}
infos = {i.filename: i for i in dst.infolist()}
TARGET_CT = files["[Content_Types].xml"].decode("utf-8")

# this deck's slides in order, before anything is appended: position -> slide part
_pres = files["ppt/presentation.xml"].decode("utf-8")
_prels = dict(re.findall(r'Id="(rId\d+)"[^>]*?Target="([^"]*)"', files["ppt/_rels/presentation.xml.rels"].decode("utf-8")))
DECK_SLIDES = ["ppt/" + _prels[rid] for rid in re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"', _pres)]


def merge(rnd):
    global nid, prels, rid_n
    SOURCE, SECTION = rnd["source"], rnd["section"]
    SLIDES = [it["slide"] for it in rnd["items"]]
    src = zipfile.ZipFile(SOURCE)
    src_ct = src.read("[Content_Types].xml").decode("utf-8")
    def rels_path(part):
        d, f = posixpath.split(part)
        return posixpath.join(d, "_rels", f + ".rels")


    def parse_rels(xml):
        return re.findall(r'<Relationship\s+([^>]*?)/?>', xml)


    def attr(s, name):
        m = re.search(name + r'="([^"]*)"', s)
        return m.group(1) if m else None


    def next_name(prefix, ext):
        """First free 'ppt/<prefix>N.<ext>' in the target package."""
        n = 1
        while f"{prefix}{n}.{ext}" in files or f"{prefix}{n}.{ext}" in reserved:
            n += 1
        reserved.add(f"{prefix}{n}.{ext}")
        return f"{prefix}{n}.{ext}"


    reserved = set()
    mapping = {}       # source part -> target part
    overrides = {}     # target part -> content type
    NUMBERED = ("ppt/slides/slide", "ppt/slideLayouts/slideLayout", "ppt/slideMasters/slideMaster", "ppt/theme/theme",
                "ppt/notesSlides/notesSlide", "ppt/charts/chart", "ppt/drawings/drawing")


    def target_name(part):
        if part in mapping:
            return mapping[part]
        base, ext = part.rsplit(".", 1)
        for pre in NUMBERED:
            if base.startswith(pre) and base[len(pre):].isdigit():
                name = next_name(pre, ext)
                break
        else:  # media, embeddings: keep the file name with a prefix
            d, f = posixpath.split(part)
            name = posixpath.join(d, "rmk_" + f)
            while name in files:
                name = posixpath.join(d, "rmk_" + uuid.uuid4().hex[:6] + "_" + f)
        mapping[part] = name
        return name


    def content_type(part):
        m = re.search(r'<Override PartName="/' + re.escape(part) + r'" ContentType="([^"]*)"', src_ct)
        return m.group(1) if m else None


    new_slides = []
    layouts_used = set()
    master_part = None
    queue = []

    for n in SLIDES:
        part = f"ppt/slides/slide{n}.xml"
        target_name(part)
        new_slides.append(part)
        queue.append(part)

    done = set()
    while queue:
        part = queue.pop(0)
        if part in done:
            continue
        done.add(part)
        tgt = target_name(part)
        data = src.read(part)
        if part.endswith(".xml"):
            ct = content_type(part)
            if ct:
                overrides[tgt] = ct
        if part in new_slides:  # hide it
            xml = data.decode("utf-8")
            xml = re.sub(r"<p:sld\b([^>]*?)\sshow=\"[01]\"", r"<p:sld\1", xml, count=1)
            xml = re.sub(r"<p:sld\b", '<p:sld show="0"', xml, count=1)
            data = xml.encode("utf-8")
        rp = rels_path(part)
        if rp in src.namelist():
            rels = src.read(rp).decode("utf-8")
            out = []
            for rel in parse_rels(rels):
                rtype, rtarget, mode = attr(rel, "Type"), attr(rel, "Target"), attr(rel, "TargetMode")
                if mode == "External":
                    out.append(rel)
                    continue
                abs_t = posixpath.normpath(posixpath.join(posixpath.dirname(part), rtarget))
                if rtype == NOTES_MASTER_TYPE:
                    new_t = "ppt/notesMasters/notesMaster1.xml"
                elif rtype == SLIDE_TYPE and part.startswith("ppt/notesSlides/"):
                    new_t = target_name(abs_t)
                elif rtype == LAYOUT_TYPE and part.startswith("ppt/slideMasters/"):
                    if abs_t not in layouts_used:
                        continue  # prune layouts no copied slide uses
                    new_t = target_name(abs_t)
                elif rtype == SLIDE_TYPE:
                    if abs_t not in new_slides:
                        continue  # a link to a slide we don't copy
                    new_t = target_name(abs_t)
                else:
                    new_t = target_name(abs_t)
                    if rtype == LAYOUT_TYPE:
                        layouts_used.add(abs_t)
                    if part.startswith("ppt/slideLayouts/") and rtype.endswith("/slideMaster"):
                        assert master_part in (None, abs_t), "remark slides must share one master"
                        master_part = abs_t
                    queue.append(abs_t)
                rel_t = posixpath.relpath(new_t, posixpath.dirname(tgt))
                out.append(re.sub(r'Target="[^"]*"', f'Target="{rel_t}"', rel))
            kept_ids = {attr(r, "Id") for r in out}
            files[rels_path(tgt)] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + "".join(f"<Relationship {r}/>" for r in out) + "</Relationships>").encode("utf-8")
            if part.startswith("ppt/slideMasters/"):  # drop pruned layouts from the master's layout list
                xml = data.decode("utf-8")
                xml = re.sub(r'<p:sldLayoutId [^>]*r:id="([^"]*)"[^>]*/>',
                             lambda m: m.group(0) if m.group(1) in kept_ids else "", xml)
                data = xml.encode("utf-8")
        files[tgt] = data

    # the master is reached through a layout after the master was queued; make sure its layout list is final
    assert master_part, "no master found"

    # unique ids for the new master and its layouts
    pres = files["ppt/presentation.xml"].decode("utf-8")
    ids = [int(x) for x in re.findall(r'<p:sldMasterId id="(\d+)"', pres)]
    for name, data in files.items():
        if name.startswith("ppt/slideMasters/slideMaster") and name.endswith(".xml"):
            ids += [int(x) for x in re.findall(r'<p:sldLayoutId id="(\d+)"', data.decode("utf-8"))]
    nid = max(ids) + 1
    mtgt = mapping[master_part]
    mxml = files[mtgt].decode("utf-8")
    master_id = nid
    nid += 1


    def renum(m):
        global nid
        nid += 1
        return f'<p:sldLayoutId id="{nid - 1}"'


    mxml = re.sub(r'<p:sldLayoutId id="\d+"', renum, mxml)
    files[mtgt] = mxml.encode("utf-8")

    # presentation relationships and lists
    prels = files["ppt/_rels/presentation.xml.rels"].decode("utf-8")
    rid_n = max(int(x) for x in re.findall(r'Id="rId(\d+)"', prels)) + 1


    def add_rel(rtype, target):
        global prels, rid_n
        rid = f"rId{rid_n}"
        rid_n += 1
        prels = prels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="{R_NS}/{rtype}" Target="{target}"/></Relationships>')
        return rid


    mrid = add_rel("slideMaster", mtgt.replace("ppt/", "", 1))
    pres = pres.replace("</p:sldMasterIdLst>", f'<p:sldMasterId id="{master_id}" r:id="{mrid}"/></p:sldMasterIdLst>')
    def target_ct(part):
        m = re.search(r'<Override PartName="/' + re.escape(part) + r'" ContentType="([^"]*)"', TARGET_CT)
        return m.group(1)

    def duplicate(part, tag):
        """Hidden copy of one of this deck's slides with an 'After' tag; charts are copied, notes dropped."""
        new = next_name("ppt/slides/slide", "xml")
        xml = files[part].decode("utf-8")
        xml = re.sub(r"<p:sld\b([^>]*?)\sshow=\"[01]\"", r"<p:sld\1", xml, count=1)
        xml = re.sub(r"<p:sld\b", '<p:sld show="0"', xml, count=1)
        sid_max = max([int(x) for x in re.findall(r'<p:cNvPr[^>]*?\sid="(\d+)"', xml)] + [1])
        x, y, w, h = int(6.0 * EMU), int(0.05 * EMU), int(6.73 * EMU), int(0.3 * EMU)
        shape = (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid_max + 1}" name="After tag"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                 f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
                 '<a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="0ABF53"/></a:solidFill>'
                 '<a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="0" rIns="91440" bIns="0" anchor="ctr">'
                 '<a:normAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="r"/><a:r><a:rPr lang="en-GB" sz="900" b="1">'
                 '<a:solidFill><a:srgbClr val="00112C"/></a:solidFill><a:latin typeface="Inter"/></a:rPr>'
                 f'<a:t>{escape(tag)}</a:t></a:r></a:p></p:txBody></p:sp>')
        xml = xml.replace("</p:spTree>", shape + "</p:spTree>", 1)
        files[new] = xml.encode("utf-8")
        overrides[new] = target_ct(part)
        rels = files[rels_path(part)].decode("utf-8")
        out = []
        for rel in parse_rels(rels):
            rtype, rtarget = attr(rel, "Type"), attr(rel, "Target")
            if rtype.endswith("/notesSlide"):
                continue
            if rtype.endswith("/chart"):
                chart = posixpath.normpath(posixpath.join("ppt/slides", rtarget))
                nchart = next_name("ppt/charts/chart", "xml")
                files[nchart] = files[chart]
                overrides[nchart] = target_ct(chart)
                crels = files.get(rels_path(chart), b"").decode("utf-8")
                cout = []
                for crel in parse_rels(crels):
                    emb = posixpath.normpath(posixpath.join("ppt/charts", attr(crel, "Target")))
                    nemb = posixpath.join(posixpath.dirname(emb), "after_" + uuid.uuid4().hex[:8] + "_" + posixpath.basename(emb))
                    files[nemb] = files[emb]
                    cout.append(re.sub(r'Target="[^"]*"', f'Target="{posixpath.relpath(nemb, "ppt/charts")}"', crel))
                if crels:
                    files[rels_path(nchart)] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                        + "".join(f"<Relationship {r}/>" for r in cout) + "</Relationships>").encode("utf-8")
                rel = re.sub(r'Target="[^"]*"', f'Target="../charts/{posixpath.basename(nchart)}"', rel)
            out.append(rel)
        files[rels_path(new)] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f"<Relationship {r}/>" for r in out) + "</Relationships>").encode("utf-8")
        return new

    sid = max(int(x) for x in re.findall(r'<p:sldId id="(\d+)"', pres)) + 1
    new_ids = []
    pairs = 0
    for it in rnd["items"]:
        parts = [mapping[f"ppt/slides/slide{it['slide']}.xml"]]
        if it["after"]:
            parts.append(duplicate(DECK_SLIDES[it["after"] - 1],
                f"AFTER · Deck 11 slide {it['after']} · {it['change']}"))
            pairs += 1
        for part in parts:
            rid = add_rel("slide", part.replace("ppt/", "", 1))
            pres = pres.replace("</p:sldIdLst>", f'<p:sldId id="{sid}" r:id="{rid}"/></p:sldIdLst>')
            new_ids.append(sid)
            sid += 1
    section = (f'<p14:section name="{SECTION}" id="{{{uuid.uuid4()}}}"><p14:sldIdLst>'
               + "".join(f'<p14:sldId id="{i}"/>' for i in new_ids) + "</p14:sldIdLst></p14:section>")
    assert "</p14:sectionLst>" in pres
    pres = pres.replace("</p14:sectionLst>", section + "</p14:sectionLst>")
    files["ppt/presentation.xml"] = pres.encode("utf-8")
    files["ppt/_rels/presentation.xml.rels"] = prels.encode("utf-8")

    # content types
    ct = files["[Content_Types].xml"].decode("utf-8")
    for part, typ in overrides.items():
        if f'PartName="/{part}"' not in ct:
            ct = ct.replace("</Types>", f'<Override PartName="/{part}" ContentType="{typ}"/></Types>')
    for part in mapping.values():
        ext = part.rsplit(".", 1)[-1].lower()
        if ext != "xml" and f'Extension="{ext}"' not in ct:
            m = re.search(r'<Default Extension="' + ext + r'" ContentType="([^"]*)"', src_ct, re.I)
            ct = ct.replace("</Types>", f'<Default Extension="{ext}" ContentType="{m.group(1)}"/></Types>')
    files["[Content_Types].xml"] = ct.encode("utf-8")
    print(f"{rnd['label']}: added {len(new_slides)} hidden remark slides, {pairs} with an 'After' copy")


for rnd in ROUNDS:
    merge(rnd)

tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
    order = [n for n in dst.namelist() if n in files] + [n for n in files if n not in dst.namelist()]
    for n in order:
        z.writestr(infos.get(n, n), files[n])
shutil.move(tmp, deck)
