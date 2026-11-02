"""Fill copies of the six-card rights-package slide with the Haas, Ollie Bearman or
tennis-ambassador package.

Usage: python3 build_rights.py <unpacked_deck_dir> <slide.xml>:<package>:<source_image> [...]
  package is haas, bearman or tennis; source_image is a file in ppt/media used for the
  darkened background (e.g. slide60.xml:bearman:image181.png). Each slide must be a copy of a
  rights-package slide (made with add_slide.py). Safe to re-run on a filled slide.
"""
import re
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageStat

ROOT = sys.argv[1]
E = 914400
BG_W, BG_H = 12188825, 6757665          # background picture frame on slide39
TARGET_LUM = 30                          # mean luminance of the existing package backgrounds

PACKAGES = {
    "haas": dict(
        crop_y=0.5, out="rights_haas.jpeg",
        subtitle=("TGR HAAS F1 TEAM", "PARTNERSHIP"),
        cards=[
            ("Brand & IP Rights", ["Official Partner designation", "Associated IP and promotional rights"]),
            ("Car & Team Branding", ["Car branding, potentially 2 positions",
                                     "Driver, mechanic and team principal apparel",
                                     "Selected team assets"]),
            ("Activation", ["Driver and team appearances, in-market and virtual",
                            "Replica/show car usage", "Simulator usage"]),
            ("Digital & Social", ["Digital and social media support", "Co-branded content",
                                  "Partner presence on the team website"]),
            ("Hospitality", ["Paddock access", "Paddock Club tickets",
                             "Hospitality and paddock branding"]),
            ("Business Value", ["B2B introductions across the team’s partner network",
                                "Merchandise allocation", "Licensing opportunities"]),
        ]),
    "bearman": dict(
        crop_y=0.62, out="rights_bearman.jpeg",
        subtitle=("OLLIE BEARMAN", "ATHLETE PARTNERSHIP"),
        cards=[
            ("Brand & IP Rights", ["Official ambassador designation", "Territory: global"]),
            ("IP Usage", ["Digital and social media", "OOH and TVC", "POS and retail marketing"]),
            ("Helmet Branding", ["Five9 branding on Ollie’s helmet", "At all 24 Formula 1 races"]),
            ("Content & Social", ["Production time with Ollie", "Social media usage"]),
            ("Experiences", ["Meet & greets", "Signed merchandise",
                             "Formula 1 Paddock Club hospitality"]),
            ("Investment", ["Fee: $2–2.5M p.a."]),
        ]),
    "tennis": dict(
        crop_y=0.5, out="rights_tennis_ambassador.jpeg",
        subtitle=("TENNIS", "AMBASSADOR"),
        cards=[
            ("Brand & IP Rights", ["Official Ambassador designation", "Territory: global"]),
            ("IP Usage", ["Digital and social media", "OOH and TVC", "POS and retail marketing"]),
            ("Experiences", ["Meet & greets", "Signed merchandise"]),
            ("Content & Social", ["Production time", "Social media posts"]),
            ("Hospitality", ["Hospitality tailored to Five9’s needs"]),
            ("Investment", ["Djokovic: $2M", "Zverev: $1.5M", "Jódar: $1M", "Shelton: $1.5M"]),
        ]),
}

# Card text boxes on slide39, in reading order: row 1 left→right, then row 2.
BOXES = ["TextBox 91", "TextBox 93", "TextBox 99", "TextBox 95", "TextBox 97", "TextBox 101"]
COLS = [1278048, 4789404, 8300759]       # card x offsets (from the card groups)
ROWS = [2036621, 4032704]                # card group y offsets


def card_rect(i):
    """Rounded rectangle of card i, from its group transform on slide39."""
    gx, gy = COLS[i % 3], ROWS[i // 3]
    sy = 1681556 / 1369647
    return gx, gy + round((3481512 - 3428999) * sy), 2455589, round(1317134 * sy)


def make_background(src, cy_frac, out):
    im = Image.open(f"{ROOT}/ppt/media/{src}").convert("RGB")
    w, h = im.size
    aspect = BG_W / BG_H
    if w / h > aspect:                     # too wide: crop the sides
        nw = round(h * aspect)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:                                  # too tall: crop a band around cy_frac
        nh = round(w / aspect)
        top = min(max(round(h * cy_frac - nh / 2), 0), h - nh)
        im = im.crop((0, top, w, top + nh))
    if im.width > 2400:
        im = im.resize((2400, round(2400 / aspect)), Image.LANCZOS)
    lum = ImageStat.Stat(im.convert("L")).mean[0]
    im = im.point(lambda v: min(255, round(v * TARGET_LUM / lum)))
    im.save(f"{ROOT}/ppt/media/{out}", quality=88)


def para_heading(text):
    return ('<a:p><a:pPr algn="ctr" defTabSz="817839"/><a:r><a:rPr lang="en-GB" sz="1252" b="1">'
            '<a:solidFill><a:srgbClr val="2A4CF9"/></a:solidFill>'
            '<a:latin typeface="Aptos Light" panose="020B0004020202020204" pitchFamily="34" charset="0"/>'
            f'</a:rPr><a:t>{escape(text)}</a:t></a:r></a:p>')


def para_bullet(text):
    return ('<a:p><a:pPr marL="255575" indent="-255575" defTabSz="817839">'
            '<a:buFont typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/>'
            '<a:buChar char="&#8226;"/></a:pPr><a:r><a:rPr lang="en-GB" sz="1252">'
            '<a:solidFill><a:prstClr val="black"/></a:solidFill>'
            '<a:latin typeface="Aptos Light" panose="020B0004020202020204" pitchFamily="34" charset="0"/>'
            f'</a:rPr><a:t>{escape(text)}</a:t></a:r></a:p>')


def fill_card(xml, name, i, heading, bullets):
    start = xml.index(f'name="{name}"')
    s = xml.rindex("<p:sp>", 0, start)
    e = xml.index("</p:sp>", start) + len("</p:sp>")
    sp = xml[s:e]
    x, y, w, h = card_rect(i)
    pad_x, pad_top, pad_bot = round(0.10 * E), round(0.16 * E), round(0.10 * E)
    sp = re.sub(r'<a:xfrm><a:off [^>]*/><a:ext [^>]*/></a:xfrm>',
                f'<a:xfrm><a:off x="{x + pad_x}" y="{y + pad_top}"/>'
                f'<a:ext cx="{w - 2 * pad_x}" cy="{h - pad_top - pad_bot}"/></a:xfrm>', sp, count=1)
    body = ('<p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="ctr"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            + para_heading(heading) + "".join(para_bullet(b) for b in bullets) + "</p:txBody>")
    sp = re.sub(r"<p:txBody>.*</p:txBody>", lambda m: body, sp, flags=re.S)
    return xml[:s] + sp + xml[e:]


def set_subtitle(xml, lines):
    g = xml.index('name="Groupe 4"')
    start = xml.index('name="ZoneTexte 13"', g)
    s = xml.index("<a:r>", start)
    e = xml.index("<a:endParaRPr", s)
    run = xml[s:xml.index("</a:r>", s) + len("</a:r>")]
    rpr = re.search(r"<a:rPr.*?</a:rPr>", run, re.S).group(0)
    new = f'<a:br>{rpr.replace("<a:rPr", "<a:rPr", 1)}</a:br>'.join(
        f"<a:r>{rpr}<a:t>{escape(t)}</a:t></a:r>" for t in lines)
    return xml[:s] + new + xml[e:]


def set_background(slide, out):
    path = f"{ROOT}/ppt/slides/{slide}"
    xml = open(path, encoding="utf-8").read()
    pic_s = xml.index("<p:pic>")
    pic_e = xml.index("</p:pic>", pic_s)
    pic = xml[pic_s:pic_e]
    rid = re.search(r'<a:blip r:embed="([^"]+)"', pic).group(1)
    pic = re.sub(r"<a:extLst><a:ext uri=\"\{BEBA8EAE[^\"]*\}\">.*?</a:ext></a:extLst>", "", pic, flags=re.S)
    pic = re.sub(r"<a:srcRect [^>]*/>", "<a:srcRect/>", pic)
    xml = xml[:pic_s] + pic + xml[pic_e:]
    open(path, "w", encoding="utf-8").write(xml)

    rels_path = f"{ROOT}/ppt/slides/_rels/{slide}.rels"
    rels = open(rels_path, encoding="utf-8").read()
    rels = re.sub(r'<Relationship [^>]*/>',
                  lambda m: re.sub(r'Target="[^"]+"', f'Target="../media/{out}"', m.group(0))
                  if f'Id="{rid}"' in m.group(0) else m.group(0), rels)
    rels = re.sub(r'<Relationship [^>]*hdphoto[^>]*/>', "", rels)
    open(rels_path, "w", encoding="utf-8").write(rels)


for arg in sys.argv[2:]:
    slide, key, source = arg.split(":")
    cfg = PACKAGES[key]
    make_background(source, cfg["crop_y"], cfg["out"])
    set_background(slide, cfg["out"])
    path = f"{ROOT}/ppt/slides/{slide}"
    xml = open(path, encoding="utf-8").read()
    xml = set_subtitle(xml, cfg["subtitle"])
    for i, (name, (heading, bullets)) in enumerate(zip(BOXES, cfg["cards"])):
        xml = fill_card(xml, name, i, heading, bullets)
    open(path, "w", encoding="utf-8").write(xml)
    print("filled", slide, "with", key)
