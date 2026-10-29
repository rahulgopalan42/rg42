"""Rebuild the tennis and football rights-package slides from the Word docs.

Run against an unpacked deck in which add_slide.py has already created:
  slide55/56/57 (copies of slide37, tennis) and slide58/59 (copies of slide48, football).
"""
import copy
import sys
import uuid
from xml.sax.saxutils import escape

from lxml import etree

ROOT = sys.argv[1]
E = 914400
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
NSDECL = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items())

BLUE = "2A4CF9"
BLACK = "000000"
GREY = "595959"
WHITE = "FFFFFF"
LIGHT = "D9D9D9"
BODY_FONT = "Aptos Light"
HEAD_FONT = "+mj-lt"
BODY = 11  # pt, body copy on every package slide


def emu(v):
    return int(round(v * E))


def frag(xml):
    return etree.fromstring(f"<root {NSDECL}>{xml}</root>")[0]


# ---------------------------------------------------------------- text helpers
def color_xml(c, alpha=None):
    a = f'<a:alpha val="{alpha * 1000}"/>' if alpha is not None else ""
    if c in ("bg1", "tx1"):
        return f'<a:schemeClr val="{c}">{a}</a:schemeClr>'
    return f'<a:srgbClr val="{c}">{a}</a:srgbClr>'


def run(text, sz=BODY, b=False, i=False, color=BLACK, font=BODY_FONT, spc=None):
    spc_attr = f' spc="{spc}"' if spc is not None else ""
    sym = ""
    if font == "Segoe UI Symbol":
        sym = '<a:sym typeface="Segoe UI Symbol"/>'
    return (
        f'<a:r><a:rPr lang="en-GB" sz="{int(sz * 100)}" b="{int(b)}" i="{int(i)}"{spc_attr} dirty="0">'
        f'<a:solidFill>{color_xml(color)}</a:solidFill>'
        f'<a:latin typeface="{font}"/><a:cs typeface="{font}"/>{sym}</a:rPr>'
        f"<a:t>{escape(text)}</a:t></a:r>"
    )


def para(runs, algn="l", bullet=False, spc_bef=0, spc_aft=0, ln=100, end_sz=BODY):
    if bullet:
        ind = emu(0.17)
        pre = (
            f'<a:pPr marL="{ind}" indent="-{ind}" algn="{algn}">'
            f'<a:lnSpc><a:spcPct val="{ln * 1000}"/></a:lnSpc>'
            f'<a:spcBef><a:spcPts val="{int(spc_bef * 100)}"/></a:spcBef>'
            f'<a:spcAft><a:spcPts val="{int(spc_aft * 100)}"/></a:spcAft>'
            f'<a:buClr><a:srgbClr val="{BLUE}"/></a:buClr><a:buSzPct val="100000"/>'
            f'<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/></a:pPr>'
        )
    else:
        pre = (
            f'<a:pPr marL="0" indent="0" algn="{algn}">'
            f'<a:lnSpc><a:spcPct val="{ln * 1000}"/></a:lnSpc>'
            f'<a:spcBef><a:spcPts val="{int(spc_bef * 100)}"/></a:spcBef>'
            f'<a:spcAft><a:spcPts val="{int(spc_aft * 100)}"/></a:spcAft><a:buNone/></a:pPr>'
        )
    return f'<a:p>{pre}{"".join(runs)}<a:endParaRPr lang="en-GB" sz="{int(end_sz * 100)}" dirty="0"/></a:p>'


def body_pr(ins, anchor="t", wrap=True):
    l, t, r, b = (emu(v) for v in ins)
    w = "square" if wrap else "none"
    return (
        f'<a:bodyPr wrap="{w}" lIns="{l}" tIns="{t}" rIns="{r}" bIns="{b}" anchor="{anchor}" rtlCol="0">'
        f"<a:noAutofit/></a:bodyPr>"
    )


def textbox(name, x, y, w, h, paras, anchor="t", ins=(0.1, 0.05, 0.1, 0.05)):
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="0" name="{escape(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        f'<p:txBody>{body_pr(ins, anchor)}<a:lstStyle/>{"".join(paras)}</p:txBody></p:sp>'
    )


def rounded(name, x, y, w, h, paras, fill=WHITE, alpha=60, radius=0.22, anchor="t",
            ins=(0.2, 0.13, 0.2, 0.1)):
    adj = min(50000, int(radius / min(w, h) * 100000))
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="0" name="{escape(name)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
        f'<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst></a:prstGeom>'
        f'<a:solidFill>{color_xml(fill, alpha if alpha < 100 else None)}</a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>'
        f'<p:txBody>{body_pr(ins, anchor)}<a:lstStyle/>{"".join(paras)}</p:txBody></p:sp>'
    )


# ---------------------------------------------------------------- slide parts
def title_block(line1, big, line3, x, y, line3_dx, line3_w, line3_align="l"):
    """The deck's stacked title: small white caps / big blue italic / small white caps."""
    return [
        textbox("Title line 1", x, y, 8.3, 0.37,
                [para([run(line1, 16, color="bg1")])]),
        textbox("Title", x + 0.29, y + 0.14, 6.2, 0.77,
                [para([run(big, 40, b=True, i=True, color=BLUE, font=HEAD_FONT)], end_sz=40)]),
        textbox("Title line 3", x + line3_dx, y + 0.80, line3_w, 0.37,
                [para([run(line3, 16, color="bg1")], algn=line3_align)]),
    ]


def item_paras(items):
    out = []
    for n, it in enumerate(items):
        label, desc = it[0], it[1]
        note = it[2] if len(it) > 2 else None
        runs = [run(label + " ", b=True), run(desc)]
        if note:
            runs.append(run(" " + note, i=True))
        out.append(para(runs, bullet=True, spc_aft=0 if n == len(items) - 1 else ITEM_GAP))
    return out


ITEM_GAP = 5  # pt between bullet items


def card(title, items, x, y, w, h, gap=None):
    global ITEM_GAP
    keep = ITEM_GAP
    if gap is not None:
        ITEM_GAP = gap
    paras = [para([run(title, 13, b=True, color=BLUE)], algn="ctr", spc_aft=4, end_sz=13)]
    paras += item_paras(items)
    ITEM_GAP = keep
    return rounded(f"Card - {title}", x, y, w, h, paras)


def callout(x, y, w, h, blocks):
    """Solid blue investment box; blocks = [(label, figure, caption), ...] laid side by side."""
    shapes = [rounded("Investment box", x, y, w, h, [para([run("")])], fill=BLUE, alpha=100, radius=0.2)]
    bw = w / len(blocks)
    for n, (label, figure, caption) in enumerate(blocks):
        paras = [
            para([run(label, 10, b=True, color=WHITE, spc=100)], algn="ctr", end_sz=10),
            para([run(figure, 26, b=True, color=WHITE, font=HEAD_FONT)], algn="ctr", end_sz=26),
            para([run(caption, 11, color=WHITE)], algn="ctr"),
        ]
        shapes.append(textbox(f"Investment - {label}", x + n * bw, y, bw, h, paras, anchor="ctr",
                              ins=(0.08, 0.04, 0.08, 0.04)))
    if len(blocks) > 1:
        for n in range(1, len(blocks)):
            lx = x + n * bw
            shapes.append(
                f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="0" name="Investment divider"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
                f'<p:spPr><a:xfrm><a:off x="{emu(lx)}" y="{emu(y + 0.22)}"/><a:ext cx="0" cy="{emu(h - 0.44)}"/></a:xfrm>'
                f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="9525"><a:solidFill>{color_xml(WHITE, 60)}</a:solidFill></a:ln></p:spPr></p:cxnSp>'
            )
    return shapes


def footnote(text, x=0.55, y=6.27, w=10.6):
    return textbox("Footnote", x, y, w, 0.3, [para([run(text, 9, i=True, color=LIGHT)], end_sz=9)],
                   anchor="ctr", ins=(0, 0, 0, 0))


# ---------------------------------------------------------------- comparison table
def tc(paras, fill=None, alpha=None, anchor="ctr", span=None, row_span=None, hmerge=False, vmerge=False,
       mar=(0.08, 0.02, 0.08, 0.02), lines=True):
    attrs = ""
    if span:
        attrs += f' gridSpan="{span}"'
    if row_span:
        attrs += f' rowSpan="{row_span}"'
    if hmerge:
        attrs += ' hMerge="1"'
    if vmerge:
        attrs += ' vMerge="1"'
    l, t, r, b = (emu(v) for v in mar)
    ln = ""
    for side in ("lnL", "lnR", "lnT", "lnB"):
        if lines:
            ln += f'<a:{side} w="9525"><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill></a:{side}>'
        else:
            ln += f'<a:{side} w="0"><a:noFill/></a:{side}>'
    fill_xml = f"<a:solidFill>{color_xml(fill, alpha)}</a:solidFill>" if fill else "<a:noFill/>"
    body = "".join(paras) if paras else '<a:p><a:endParaRPr lang="en-GB" dirty="0"/></a:p>'
    return (
        f"<a:tc{attrs}><a:txBody><a:bodyPr/><a:lstStyle/>{body}</a:txBody>"
        f'<a:tcPr marL="{l}" marR="{r}" marT="{t}" marB="{b}" anchor="{anchor}">{ln}{fill_xml}</a:tcPr></a:tc>'
    )


CHECK = "✓"


def mark(v):
    """Render one package cell: True = included, None = not included, str = specific entitlement."""
    if v is True:
        return [para([run(CHECK, BODY, b=True, color=BLUE, font="Segoe UI Symbol")], algn="ctr")]
    if v is None:
        return [para([run("Not included", BODY, i=True, color=GREY)], algn="ctr")]
    if isinstance(v, tuple):  # (check, "Lead asset")
        return [para([run(CHECK + "  ", BODY, b=True, color=BLUE, font="Segoe UI Symbol"),
                      run(v[1], BODY, b=True, color=BLUE)], algn="ctr")]
    return [para([run(v, BODY, b=True)], algn="ctr")]


def comparison_table(x, y, cols, head_h, row_h, groups):
    rows_xml = []
    # header row
    head = [
        tc([para([run("WHAT’S INCLUDED", 12, b=True, color=WHITE, spc=50)], end_sz=12)],
           anchor="b", span=2, mar=(0.02, 0.02, 0.08, 0.08), lines=False),
        tc(None, hmerge=True, lines=False),
    ]
    for code, name, price in (("PACKAGE A", "Premium umpire-chair position", "€600K – 1M p.a. / tournament"),
                              ("PACKAGE B", "Sidewall LED visibility", "€300K – 500K p.a. / tournament")):
        head.append(tc([
            para([run(code, 10, b=True, color=WHITE, spc=100)], algn="ctr", end_sz=10),
            para([run(name, 12, b=True, color=WHITE)], algn="ctr", end_sz=12),
            para([run(price, BODY, color=WHITE)], algn="ctr"),
        ], fill=BLUE, alpha=None, mar=(0.06, 0.04, 0.06, 0.04)))
    rows_xml.append(f'<a:tr h="{emu(head_h)}">{"".join(head)}</a:tr>')
    for cat, items in groups:
        for n, (label, a, b) in enumerate(items):
            cells = []
            if n == 0:
                cells.append(tc([para([run(cat, 10.5, b=True, color=BLUE, spc=50)], algn="ctr", end_sz=10.5)],
                                fill=WHITE, alpha=88, row_span=len(items) if len(items) > 1 else None))
            else:
                cells.append(tc(None, vmerge=True))
            cells.append(tc([para([run(label, BODY)])], fill=WHITE, alpha=70, mar=(0.12, 0.02, 0.08, 0.02)))
            cells.append(tc(mark(a), fill=WHITE, alpha=70))
            cells.append(tc(mark(b), fill=WHITE, alpha=70))
            rows_xml.append(f'<a:tr h="{emu(row_h)}">{"".join(cells)}</a:tr>')
    grid = "".join(f'<a:gridCol w="{emu(c)}"/>' for c in cols)
    total_h = head_h + row_h * sum(len(i) for _, i in groups)
    return (
        f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="0" name="Package comparison table"/>'
        f'<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
        f'<p:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(sum(cols))}" cy="{emu(total_h)}"/></p:xfrm>'
        f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
        f'<a:tbl><a:tblPr firstRow="1"/><a:tblGrid>{grid}</a:tblGrid>{"".join(rows_xml)}</a:tbl>'
        f"</a:graphicData></a:graphic></p:graphicFrame>"
    )


# ---------------------------------------------------------------- slide assembly
def load(name):
    path = f"{ROOT}/ppt/slides/{name}"
    return path, etree.parse(path)


def pieces(tree):
    """Pull the reusable parts of the source design out of a package slide."""
    sp_tree = tree.find(".//p:cSld/p:spTree", NS)
    bg = sp_tree.find("p:pic", NS)
    header = slide_no = None
    for sp in sp_tree.findall("p:sp", NS):
        txt = "".join(sp.itertext())
        name = sp.find(".//p:cNvPr", NS).get("name")
        if "Five9 x SPORTFIVE" in txt:
            header = sp
        if name.startswith("Slide Number"):
            slide_no = sp
    hatch = None
    for g in sp_tree.iter(f"{{{NS['p']}}}grpSp"):
        if g.find("p:nvGrpSpPr/p:cNvPr", NS).get("name") == "Group 133":
            hatch = g
            break
    return {k: copy.deepcopy(v) for k, v in
            dict(bg=bg, header=header, slide_no=slide_no, hatch=hatch).items()}


def hatch_at(src, cx, top):
    """The deck's '///////' motif, centred on cx, sitting on a card's top edge."""
    g = copy.deepcopy(src)
    w, h = 0.62, 0.13
    xfrm = g.find("p:grpSpPr/a:xfrm", NS)
    xfrm.find("a:off", NS).set("x", str(emu(cx - w / 2)))
    xfrm.find("a:off", NS).set("y", str(emu(top - 0.065)))
    xfrm.find("a:ext", NS).set("cx", str(emu(w)))
    xfrm.find("a:ext", NS).set("cy", str(emu(h)))
    g.find("p:nvGrpSpPr/p:cNvPr", NS).set("name", "Hatch motif")
    gsp = g.find("p:grpSpPr", NS)
    for f in gsp.findall("a:grpFill", NS) + gsp.findall("a:solidFill", NS):
        gsp.remove(f)
    gsp.append(frag(f"<a:solidFill>{color_xml(WHITE)}</a:solidFill>"))
    return g


def write_slide(name, parts, shapes):
    path, tree = load(name)
    sp_tree = tree.find(".//p:cSld/p:spTree", NS)
    for child in list(sp_tree):
        if etree.QName(child).localname not in ("nvGrpSpPr", "grpSpPr"):
            sp_tree.remove(child)
    sp_tree.append(parts["bg"])
    for s in shapes:
        sp_tree.append(s if isinstance(s, etree._Element) else frag(s))
    sp_tree.append(copy.deepcopy(parts["header"]))
    sp_tree.append(copy.deepcopy(parts["slide_no"]))
    # unique shape ids + fresh creation ids
    nid = 2
    for c in sp_tree.iter(f"{{{NS['p']}}}cNvPr"):
        if c.getparent().getparent() is sp_tree and etree.QName(c.getparent()).localname == "nvGrpSpPr":
            continue
        c.set("id", str(nid))
        nid += 1
        for ext in c.iter("{http://schemas.microsoft.com/office/drawing/2014/main}creationId"):
            ext.set("id", "{" + str(uuid.uuid4()).upper() + "}")
    tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)


def hide(name):
    path, tree = load(name)
    tree.getroot().set("show", "0")
    tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)


def card_with_hatch(parts, title, items, x, y, w, h, gap=None):
    return [card(title, items, x, y, w, h, gap), hatch_at(parts["hatch"], x + w / 2, y)]


# ---------------------------------------------------------------- content (from the Word docs)
IP_TENNIS = [("IP Rights & Category exclusivity:",
              "Use of tournament logo, marks and official name across Five9 marketing and advertising "
              "materials. Category designation to be mutually agreed.")]

ACTIVATION_TENNIS = [
    ("Player meet & greet:", "Exclusive guest experience hosted by players."),
    ("Entrance activation:", "Branded space near the main entrance for engagement, demonstrations and lead generation."),
    ("Coin Toss:", "Five9 lives the “Coin Toss Experience”, one of the tournament’s most iconic "
                   "on-court moments, with premium visibility on center court during the pre-match ceremony."),
    ("Clinics:", "A private, one-hour on-court tennis clinic during the tournament weeks, giving guests "
                 "exclusive access to the tournament environment through a premium tennis session."),
]

PACKAGES = {
    "A": dict(
        name="PREMIUM UMPIRE-CHAIR POSITION",
        price="€600K – 1M",
        visibility=[
            ("Premium branding:", "Five9 branding on the umpire chair or similar premium on-court positions, "
                                  "delivering prominent in-venue and broadcast exposure.",
             "Inventory may change for each tournament."),
            ("LED sidewall branding:", "Five9 branding on courtside LED inventory during games."),
            ("Big-screen spot:", "Five9 video shown on the main venue screens."),
            ("Practice courts:", "Static branding around selected outdoor practice courts."),
            ("Tournament website & App:", "Five9 banner and sponsor-directory presence on the official website & App."),
            ("Social media:", "Co-branded posts through the tournament’s official channels."),
        ],
        hospitality=[
            ("VIP boxes:", "Premium spaces on the main show court for hosting clients, prospects and partners."),
            ("VIP Club tables:", "Dedicated hospitality tables for networking and relationship-building."),
            ("Premium tickets per session:", "Flexible premium access for client entertainment and employee engagement."),
        ],
        note="*Subject to approval by each rights-holder.",
    ),
    "B": dict(
        name="SIDEWALL LED VISIBILITY",
        price="€300K – 500K",
        visibility=[
            ("LED sidewall branding:", "Five9 branding on courtside LED inventory during games, delivering "
                                       "prominent in-venue and broadcast exposure."),
            ("Practice courts:", "Static branding around selected outdoor practice courts."),
            ("Big-screen spot:", "Five9 video shown on the main venue screens."),
            ("Tournament website & App:", "Five9 banner and sponsor-directory presence on the official website & App."),
            ("Social media:", "Collaborative Five9 communications through the tournament’s official channels."),
        ],
        hospitality=[
            ("One VIP box:", "Premium space on the main show court for hosting clients and prospects."),
            ("One VIP Club table:", "Dedicated hospitality table for networking and relationship-building."),
            ("Ten premium tickets per session:", "Flexible premium access for guests and employee engagement."),
        ],
        note="*Subject to approval by each rights-holder. Umpire-chair / premium on-court branding is part of Package A only.",
    ),
}

COMPARISON = [
    ("IP RIGHTS", [("IP rights & category exclusivity", True, True)]),
    ("VISIBILITY", [
        ("Umpire-chair / premium on-court branding", (True, "Lead asset"), None),
        ("Courtside LED sidewall branding", True, (True, "Lead asset")),
        ("Big-screen video spot", True, True),
        ("Practice-court static branding", True, True),
        ("Tournament website & App presence", True, True),
        ("Social media (tournament channels)", "Co-branded posts", "Collaborative communications"),
    ]),
    ("HOSPITALITY", [
        ("VIP boxes on the main show court", "Multiple boxes", "One box"),
        ("VIP Club tables", "Multiple tables", "One table"),
        ("Premium tickets per session", "Flexible allocation", "Ten tickets"),
    ]),
    ("ACTIVATION", [
        ("Player meet & greet", True, True),
        ("Entrance activation space", True, True),
        ("Coin Toss Experience (center court)", True, True),
        ("Private Tennis Clinic", True, True),
    ]),
]

FOOTBALL_1 = [
    ("IP Rights & Designation", [
        ("IP Rights:", "Use of Club logo, marks and official name across Five9 marketing and advertising materials."),
        ("Group Player Image Rights:", "Collective use of Club players within Five9’s marketing and content "
                                       "platforms (minimum of 3 players required)."),
        ("Category Exclusivity:", "To be mutually agreed between Five9 and the Club."),
        ("Partnership Announcement:", "Official partnership announcement across the Club’s official channels "
                                      "and media outlets."),
    ]),
    ("Digital & CRM", [
        ("Club Website & App:", "Five9 integrated into the partners section of the Club’s official digital channels."),
        ("Club E-Newsletter:", "Five9 featured in the Club’s corporate e-newsletter, distributed to business "
                               "audiences and corporate fans, to drive traffic to the Five9 platform."),
    ]),
    ("In-Arena Signage", [
        ("LED Advertising:", "One (1) to three (3) minutes per game for all regular-season home games."),
        ("Other Premium Gameday Signage:", "Ribbon LED, 3D carpets, scoreboards and Entitlement VIP Lounge "
                                           "can also be included."),
    ]),
    ("Merchandising", [
        ("Unsigned Jerseys:", "Official First Team unsigned jerseys."),
        ("Signed Jerseys:", "Official First Team signed jerseys."),
    ]),
]

FOOTBALL_2 = [
    ("Social Media & Content", [
        ("Access to Players:", "Access to team players for a dedicated Five9 photo/video shoot, meet & greet, "
                               "or client engagement session."),
        ("Evergreen Content Piece (presented by Five9):", "Five9 presents an evergreen content piece on the "
                                                          "Club’s official social channels, jointly agreed by the Club and Five9."),
        ("Bespoke Branded Content:", "Two (2) to three (3) branded content campaigns per year on the Club’s "
                                     "LinkedIn channel, enabling Five9 to reach and engage enterprise audiences."),
        ("Paid Media Campaigns:", "Branded content advertising campaigns on LinkedIn to amplify the overall "
                                  "reach of the partnership."),
        ("Image & Video Database:", "Full access to the Club’s photo and video bank."),
    ]),
    ("Hospitality & Experiences", [
        ("VIP Gameday Experiences:", "For regular-season home games: VIP tickets, meet & greets with legends, "
                                     "photo opportunities with players, pitch warm-up experiences and more."),
        ("Training Sessions:", "Opportunity to attend first-team training sessions at the Club’s facilities."),
        ("Stadium Event:", "Opportunity to host a Five9 industry or networking event at the Club’s stadium."),
        ("VIP Annual Ticket Fund / Private Suite:", "VIP tickets or a private suite for every home game played "
                                                    "at the Club’s stadium."),
        ("Legends Access:", "A Club legend attends a Five9 corporate event or a meet & greet with clients."),
    ]),
]

# ---------------------------------------------------------------- geometry
L, R = 0.55, 12.78            # content left / right edge (in)
TOP, BOTTOM = 2.17, 6.17      # card band
GAP = 0.3
CALL_W, CALL_H, CALL_Y = 3.5, 1.28, 0.6


def detail_title(line1, big, line3):
    return title_block(line1, big, line3, x=L - 0.1, y=0.6, line3_dx=0.29, line3_w=7.0)


def build():
    _, t37 = load("slide37.xml")
    tennis = pieces(t37)
    _, t48 = load("slide48.xml")
    football = pieces(t48)

    # --- Tennis overview: A vs B at a glance (takes the original slide's title position)
    shapes = title_block("EXEMPLARY", "Rights packages", "ATP 1000 & 500 TOURNAMENTS",
                         x=4.06, y=0.6, line3_dx=0.29 + 1.1, line3_w=4.0, line3_align="r")
    cols = [1.55, 4.05, 2.85, 2.85]
    x0 = (13.33 - sum(cols)) / 2
    shapes.append(comparison_table(x0, 2.05, cols, 0.74, 0.243, COMPARISON))
    shapes.append(footnote("*All rights subject to approval by each rights-holder. Pricing is per tournament, "
                           "per year. Premium on-court inventory may change for each tournament.", x=x0))
    write_slide("slide55.xml", tennis, shapes)

    # --- Tennis Package A / B detail
    w1, w2 = 4.21, 3.91
    w3 = R - L - 2 * GAP - w1 - w2
    for slide, key in (("slide56.xml", "A"), ("slide57.xml", "B")):
        pk = PACKAGES[key]
        shapes = detail_title("EXEMPLARY RIGHTS PACKAGE · ATP 1000 & 500 TOURNAMENTS", f"Package {key}", pk["name"])
        shapes += callout(R - CALL_W, CALL_Y, CALL_W, CALL_H, [("INVESTMENT", pk["price"], "per annum, per tournament")])
        x1, x2, x3 = L, L + w1 + GAP, L + w1 + w2 + 2 * GAP
        ip_h = 1.45
        shapes += card_with_hatch(tennis, "IP Rights", IP_TENNIS, x1, TOP, w1, ip_h)
        shapes += card_with_hatch(tennis, "Hospitality", pk["hospitality"], x1, TOP + ip_h + GAP,
                                  w1, BOTTOM - TOP - ip_h - GAP)
        shapes += card_with_hatch(tennis, "Visibility", pk["visibility"], x2, TOP, w2, BOTTOM - TOP)
        shapes += card_with_hatch(tennis, "Activation", ACTIVATION_TENNIS, x3, TOP, w3, BOTTOM - TOP)
        shapes.append(footnote(pk["note"]))
        write_slide(slide, tennis, shapes)

    # --- Football detail (two slides)
    deal = [("INVESTMENT", "€2M+", "per year, per club"), ("TERM", "3 years", "partnership term")]
    note = "*Subject to approval by each rights-holder. Package applies per club (Arsenal FC or FC Bayern Munich)."
    half = (R - L - GAP) / 2

    shapes = detail_title("EXEMPLARY RIGHTS PACKAGE", "Global football club",
                          "ARSENAL FC  /  FC BAYERN MUNICH  ·  1 OF 2")
    shapes += callout(R - CALL_W, CALL_Y, CALL_W, CALL_H, deal)
    row1 = 2.3
    (t1, i1), (t2, i2), (t3, i3), (t4, i4) = FOOTBALL_1
    shapes += card_with_hatch(football, t1, i1, L, TOP, half, row1)
    shapes += card_with_hatch(football, t2, i2, L + half + GAP, TOP, half, row1)
    shapes += card_with_hatch(football, t3, i3, L, TOP + row1 + GAP, half, BOTTOM - TOP - row1 - GAP)
    shapes += card_with_hatch(football, t4, i4, L + half + GAP, TOP + row1 + GAP, half, BOTTOM - TOP - row1 - GAP)
    shapes.append(footnote(note))
    write_slide("slide58.xml", football, shapes)

    shapes = detail_title("EXEMPLARY RIGHTS PACKAGE", "Global football club",
                          "ARSENAL FC  /  FC BAYERN MUNICH  ·  2 OF 2")
    shapes += callout(R - CALL_W, CALL_Y, CALL_W, CALL_H, deal)
    (t1, i1), (t2, i2) = FOOTBALL_2
    shapes += card_with_hatch(football, t1, i1, L, TOP, half, BOTTOM - TOP, gap=17)
    shapes += card_with_hatch(football, t2, i2, L + half + GAP, TOP, half, BOTTOM - TOP, gap=17)
    shapes.append(footnote(note))
    write_slide("slide59.xml", football, shapes)

    # the old generic versions stay in the deck, hidden
    hide("slide37.xml")
    hide("slide48.xml")


build()
