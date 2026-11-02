"""Fill the three Alpine slides (34-36) of the Adyen x SPORTFIVE F1 deck.

Content comes from "Adyen and Alpine Formula One Team - Provisional Rights
Overview 2027-2029". Layout mirrors the Max Verstappen section (slides 28-30):
  34 ALPINE OVERVIEW              <- like 28: narrative + key facts
  35 ALPINE: BUSINESS OPPORTUNITY <- like 29: subtitle + 4-column table
  36 ALPINE: RIGHTS OVERVIEW      <- like 30: rights package summary

Text boxes and the table are copied from the Max slides so fonts, sizes and
table style match. Every other slide is left untouched.

Usage: python3 add_alpine_slides.py <in.pptx> <out.pptx> <engine_cover.jpg> <halo.jpg>
"""
import copy
import sys
import uuid

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt
from lxml import etree

SRC, OUT, IMG_ENGINE, IMG_HALO = sys.argv[1:5]

RED = RGBColor(0xC0, 0x00, 0x00)
BLACK = RGBColor(0x00, 0x00, 0x00)
GREY = RGBColor(0x59, 0x59, 0x59)
FONT = "Aptos"
A16 = "http://schemas.microsoft.com/office/drawing/2014/main"

SOURCE = ("Source: Alpine Formula One Team, Adyen x Alpine Formula One Team Provisional "
          "Rights Overview 2027–2029. Provisional, subject to change and not legally binding.")

prs = Presentation(SRC)
slides = prs.slides


def title(slide):
    for sh in slide.shapes:
        if sh.has_text_frame and sh.name == "Textfeld 8":
            return sh.text_frame.text.strip()
    return None


max_over, max_biz = slides[27], slides[28]
alp_over, alp_biz, alp_rights = slides[33], slides[34], slides[35]
assert title(max_over) == "ADYEN POWERS MAX VERSTAPPEN", title(max_over)
assert title(max_biz) == "POWERING A HIGH PERFORMANCE ECOSYSTEM", title(max_biz)
assert title(alp_over) == "ALPINE OVERVIEW", title(alp_over)
assert title(alp_biz) == "ALPINE: BUSINESS OPPORTUNITY", title(alp_biz)
assert title(alp_rights) == "ALPINE: RIGHTS OVERVIEW", title(alp_rights)
for s in (alp_over, alp_biz, alp_rights):
    assert len(s.shapes) == 2, "Alpine slide is no longer empty; refusing to overwrite"


def shape_by_name(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    raise KeyError(name)


def next_id(slide):
    return max(int(e.get("id")) for e in slide.shapes._spTree.iter(qn("p:cNvPr"))) + 1


def clone_into(slide, shape, name):
    """Deep-copy a shape's XML onto another slide with a fresh id and creationId."""
    el = copy.deepcopy(shape._element)
    cnv = el.find(".//" + qn("p:cNvPr"))
    cnv.set("id", str(next_id(slide)))
    cnv.set("name", name)
    for cid in el.iter("{%s}creationId" % A16):
        cid.set("id", "{%s}" % str(uuid.uuid4()).upper())
    slide.shapes._spTree.append(el)
    return el


def set_xfrm(el, x, y, w, h):
    xfrm = el.find(".//" + qn("a:xfrm"))
    if xfrm is None:
        xfrm = el.find(".//" + qn("p:xfrm"))
    xfrm.find(qn("a:off")).set("x", str(x))
    xfrm.find(qn("a:off")).set("y", str(y))
    xfrm.find(qn("a:ext")).set("cx", str(w))
    xfrm.find(qn("a:ext")).set("cy", str(h))


def set_para_text(p_el, text):
    """Keep the paragraph's pPr and first run's rPr; replace runs with one run of text."""
    runs = p_el.findall(qn("a:r"))
    rpr = copy.deepcopy(runs[0].find(qn("a:rPr"))) if runs else None
    if rpr is None:
        end = p_el.find(qn("a:endParaRPr"))
        rpr = etree.Element(qn("a:rPr"))
        if end is not None:
            rpr = copy.deepcopy(end)
            rpr.tag = qn("a:rPr")
    for r in runs:
        p_el.remove(r)
    r = etree.Element(qn("a:r"))
    r.append(rpr)
    t = etree.SubElement(r, qn("a:t"))
    t.text = text
    end = p_el.find(qn("a:endParaRPr"))
    if end is not None:
        end.addprevious(r)
    else:
        p_el.append(r)


def style_run(run, size, bold=False, italic=False, color=BLACK):
    f = run.font
    f.name = FONT
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = color


def add_textbox(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tb


def add_source(slide, y=6420000):
    tb = add_textbox(slide, 432288, y, 11300000, 200000)
    run = tb.text_frame.paragraphs[0].add_run()
    run.text = SOURCE
    style_run(run, 7, color=GREY)


# ---------------------------------------------------------------- slide 34
NARRATIVE = (
    "Alpine proposes a three-year partnership (2027–2029) built around one theme: Performance "
    "in Every Transaction, from checkout to chequered flag. Every Formula 1 result depends on "
    "thousands of complex processes working together with speed, precision and resilience. Adyen "
    "delivers the same for enterprise commerce, connecting payments, data and financial products "
    "on one global platform. Adyen becomes the Team's exclusive Financial Technology Platform "
    "Partner and powers its new ecommerce platform, so every fan purchase is a live proof point. "
    "Content, race-week experiences and C-level hospitality then turn that proof into senior "
    "customer conversations, and the Team's partner network opens doors to new business."
)
OBJECTIVES = [
    "Prove Adyen's enterprise platform through a measurable ecommerce integration and a "
    "client-facing case study",
    "Deepen relationships with priority customers through C-level hospitality and F1 experiences",
    "Generate qualified new business through the Team's international partner network",
]

left = clone_into(alp_over, shape_by_name(max_over, "TextBox 7"), "Alpine narrative")
paras = left.findall(".//" + qn("a:p"))
narr_p, bullet_tpl = paras[0], paras[1]
set_para_text(narr_p, NARRATIVE)
txbody = narr_p.getparent()
txbody.remove(bullet_tpl)
blank = copy.deepcopy(narr_p)
for r in blank.findall(qn("a:r")):
    blank.remove(r)
txbody.append(blank)
lead = copy.deepcopy(narr_p)
set_para_text(lead, "What the partnership is built to achieve:")
txbody.append(lead)
for text in OBJECTIVES:
    p = copy.deepcopy(bullet_tpl)
    rpr = copy.deepcopy(narr_p.find(qn("a:r")).find(qn("a:rPr")))
    r = etree.Element(qn("a:r"))
    r.append(rpr)
    etree.SubElement(r, qn("a:t")).text = text
    p.find(qn("a:endParaRPr")).addprevious(r)
    txbody.append(p)

KEY_FACTS = [
    ("plain", "Partnership: Financial Technology Platform Partner (exclusive)"),
    ("plain", "Tier: Premium Partner (non-exclusive)"),
    ("plain", "Term: 3 years, 2027–2029"),
    ("plain", "Territory: Global"),
    ("plain", "Fee: £10.0M in 2027, rising 5% a year"),
    ("blank", ""),
    ("plain", "Alpine fan audience vs. average internet user:"),
    ("bullet", "10.0M senior decision-makers (2.22x)"),
    ("bullet", "23.6M business decision-makers (1.88x)"),
    ("bullet", "5.6M company owners and founders (1.98x)"),
    ("bullet", "4.5M technology early adopters (3.02x)"),
    ("bullet", "24.3M Google Pay users (1.83x)"),
    ("bullet", "7.2M Apple Pay users (1.59x)"),
    ("blank", ""),
    ("note", "Audience: GWI Core, Q3 2025 to Q2 2026, all internet users. "
             "Apple Pay covers selected markets only."),
]
right = clone_into(alp_over, shape_by_name(max_over, "TextBox 1"), "Alpine key facts")
rparas = right.findall(".//" + qn("a:p"))
plain_tpl, blank_tpl, bullet_tpl2 = rparas[0], rparas[3], rparas[5]
rbody = plain_tpl.getparent()
for p in rparas:
    rbody.remove(p)
for kind, text in KEY_FACTS:
    if kind == "blank":
        rbody.append(copy.deepcopy(blank_tpl))
        continue
    p = copy.deepcopy(bullet_tpl2 if kind == "bullet" else plain_tpl)
    set_para_text(p, text)
    if kind == "note":
        rpr = p.find(qn("a:r")).find(qn("a:rPr"))
        rpr.set("sz", "800")
        fill = etree.SubElement(rpr, qn("a:solidFill"))
        etree.SubElement(fill, qn("a:srgbClr")).set("val", "595959")
    rbody.append(p)

# Branding mock-ups from the proposal, stacked on the right.
img_x, img_w = 8350000, 3400000
img_h = int(img_w * 710 / 1262)
y = 1386307
for path, caption in ((IMG_ENGINE, "Engine cover (middle lower)"),
                      (IMG_HALO, "Halo top back (one side)")):
    alp_over.shapes.add_picture(path, Emu(img_x), Emu(y), Emu(img_w), Emu(img_h))
    cap = add_textbox(alp_over, img_x, y + img_h + 50000, img_w, 180000)
    run = cap.text_frame.paragraphs[0].add_run()
    run.text = caption + " – Alpine mock-up of Adyen branding"
    style_run(run, 8, color=GREY)
    y += img_h + 380000
add_source(alp_over)

# ---------------------------------------------------------------- slide 35
sub = clone_into(alp_biz, shape_by_name(max_biz, "TextBox 2"), "Alpine subtitle")
set_xfrm(sub, 432288, 1330000, 10900000, 200000)
set_para_text(sub.find(".//" + qn("a:p")),
              "Performance in Every Transaction: Adyen powers the Team's commerce, then turns that "
              "proof into content, live experiences and enterprise relationships")

HEADER = ["Alpine's business", "Activation", "What Adyen does", "Outcome for Adyen"]
ROWS = [
    ["Team ecommerce store (new platform)", "The Integrated Commerce Garage",
     "Powers agreed parts of the Team's ecommerce environment, giving fans a dependable, "
     "locally relevant purchase journey",
     "Measurable proof: checkout completion, payment performance, operational efficiency, "
     "customer experience"],
    ["Fan rewards", "Checkout to Chequered Flag Rewards",
     "Eligible online purchases unlock selected Team rewards, merchandise or experiences "
     "(subject to promotional and regulatory controls)",
     "Engagement, conversion and repeat purchase"],
    ["Content and storytelling", "The Performance Proof Series",
     "Documentary films, technical features and executive interviews on the integration, plus "
     "short-form assets for digital, social and account-based marketing",
     "Flagship case study, thought leadership and sales enablement"],
    ["Enstone factory (UK)", "Commerce Under Pressure Live Lab",
     "Immersive session for customers and prospects: practical commerce scenarios, Team insights "
     "and expert discussion",
     "Credibility with customers and prospects"],
    ["Grand Prix host city, with an Adyen customer", "Race Week, One Platform",
     "Turns a flagship retail, hospitality, travel or entertainment venue into a race-week "
     "experience: advance booking, mobile ordering, venue payments, merchandise and private "
     "hospitality",
     "Live product demo and a three-party case study"],
    ["Grand Prix hospitality", "Adyen Commerce Club",
     "C-level programme at selected Grands Prix: Team hospitality with private discussions, "
     "garage tours, Team appearances and near-track events",
     "Stronger relationships and progress with priority accounts"],
    ["Team partner network", "One Platform Partner Forum",
     "Recurring forum connecting Team partners with Adyen experts, customers and invited "
     "enterprise leaders",
     "Qualified introductions and new business (no guaranteed procurement outcomes)"],
]
COL_W = [1500000, 1450000, 2650000, 1800000]
ROW_H = 330000

frame = clone_into(alp_biz, shape_by_name(max_biz, "Table 1"), "Alpine business table")
tbl = frame.find(".//" + qn("a:tbl"))
for gc, w in zip(tbl.find(qn("a:tblGrid")).findall(qn("a:gridCol")), COL_W):
    gc.set("w", str(w))
trs = tbl.findall(qn("a:tr"))
row_tpl = copy.deepcopy(trs[1])
for tr in trs:
    tbl.remove(tr)


def fill_cell(tc, text, bold):
    body = tc.find(qn("a:txBody"))
    for p in body.findall(qn("a:p")):
        body.remove(p)
    p = etree.SubElement(body, qn("a:p"))
    ppr = etree.SubElement(p, qn("a:pPr"), marL="0", marR="0", fontAlgn="ctr")
    etree.SubElement(ppr, qn("a:buNone"))
    r = etree.SubElement(p, qn("a:r"))
    rpr = etree.SubElement(r, qn("a:rPr"), lang="en-GB", sz="800")
    if bold:
        rpr.set("b", "1")
    etree.SubElement(rpr, qn("a:effectLst"))
    etree.SubElement(rpr, qn("a:latin"), typeface=FONT)
    etree.SubElement(r, qn("a:t")).text = text
    end = etree.SubElement(p, qn("a:endParaRPr"), lang="en-GB", sz="800")
    etree.SubElement(end, qn("a:latin"), typeface=FONT)
    tcpr = tc.find(qn("a:tcPr"))
    for k, v in (("marL", "54864"), ("marR", "54864"), ("marT", "27432"), ("marB", "27432")):
        tcpr.set(k, v)


for i, cells in enumerate([HEADER] + ROWS):
    tr = copy.deepcopy(row_tpl)
    tr.set("h", str(220000 if i == 0 else ROW_H))
    for ext in tr.iter("{%s}rowId" % A16):
        ext.set("val", str(uuid.uuid4().int % 4000000000))
    for tc, text in zip(tr.findall(qn("a:tc")), cells):
        fill_cell(tc, text, bold=(i == 0))
    tbl.append(tr)
set_xfrm(frame, 432288, 1640000, sum(COL_W), 220000 + ROW_H * len(ROWS))

# Integrate -> Prove -> Experience -> Convert, beside the table.
steps = add_textbox(alp_biz, 8150000, 1640000, 3600000, 3800000)
tf = steps.text_frame
p = tf.paragraphs[0]
run = p.add_run()
run.text = "INTEGRATE → PROVE → EXPERIENCE → CONVERT"
style_run(run, 10.5, bold=True, color=RED)
STEPS = [
    ("1  Integrate", "Adyen powers the Team's ecommerce journey and takes a genuine operational "
                     "role in the partnership."),
    ("2  Prove", "The collaboration generates validated insights, a flagship case study and "
                 "reusable enterprise content."),
    ("3  Experience", "Adyen brings connected commerce to life through physical customer "
                      "environments, fan experiences and immersive demonstrations."),
    ("4  Convert", "Hospitality, executive forums and the Team's partner ecosystem turn the "
                   "partnership into customer engagement and commercial opportunity."),
]
for head, body in STEPS:
    p = tf.add_paragraph()
    p.space_before = Pt(9)
    r = p.add_run()
    r.text = head
    style_run(r, 10.5, bold=True)
    p = tf.add_paragraph()
    r = p.add_run()
    r.text = body
    style_run(r, 10.5)
add_source(alp_biz)

# ---------------------------------------------------------------- slide 36
intro = add_textbox(alp_rights, 432288, 1330000, 11300000, 220000)
p = intro.text_frame.paragraphs[0]
r = p.add_run()
r.text = "ALPINE FORMULA ONE TEAM X ADYEN, 2027–2029. "
style_run(r, 10.5, bold=True)
r = p.add_run()
r.text = "Alpine's provisional offer: subject to change and not legally binding."
style_run(r, 10.5, bold=True, color=RED)

COLS = [
    [
        ("h", "DURATION: 2027–2029 (3 YEARS)"),
        ("h", "COMMERCIAL TERMS"),
        ("kv", "Category: ", "Financial Technology Platform"),
        ("kv", "Designation: ", "Financial Technology Platform Partner (exclusive); "
                                "Premium Partner (non-exclusive)"),
        ("kv", "Territory: ", "Global"),
        ("kv", "Fee: ", "£10.0M (2027), £10.5M (2028), £11.025M (2029); 5% annual escalator"),
        ("kv", "Payment: ", "40% on signing (by 15 Feb in later years), 30% by 15 Sep, "
                            "30% by 15 Dec"),
        ("kv", "Championship bonus: ", "25% (1st), 12.5% (2nd), 6.5% (3rd); maximum 150% "
                                       "should both Drivers' and Constructors' bonuses be achieved"),
        ("kv", "Contracting entity: ", "Alpine Racing Ltd."),
        ("h", "BRANDING (ALL SEASON)"),
        ("kv", "Race car: ", "engine cover (middle lower); halo top back (one side)"),
        ("kv", "Showcar and virtual car: ", "all showcars in use; car branding replicated in "
                                            "the official F1 game (EA)"),
        ("kv", "Drivers: ", "suit and undersuit, collar middle*; helmet, chin"),
        ("kv", "Mechanics: ", "suit, collar middle*; helmet, chin"),
        ("kv", "Team kit: ", "collar, one side**"),
        ("kv", "Partner stack: ", "HQ reception, transporters, motorhome (European races), "
                                  "hospitality, press releases, media backdrop, garage wall "
                                  "panelling, Team website partner page"),
        ("note", "*Race kit as soon as feasible in 2027. **Driver and management polos in 2027; "
                 "full team kit from 2028."),
    ],
    [
        ("h", "IP RIGHTS"),
        ("b", "Use of Team property, imagery and footage on marketing materials, subject to "
              "approval"),
        ("h", "DRIVER AND PERSONNEL APPEARANCES"),
        ("kv", "F1 race drivers: ", "3 × 1-hour race-weekend off-track; 2 × 4-hour marketing "
                                    "off-track"),
        ("kv", "Reserve driver: ", "2 × 1-hour race-weekend off-track; 1 × 4-hour marketing "
                                   "off-track"),
        ("kv", "Senior team member: ", "2 × 1-hour race-weekend; 2 × 4-hour marketing; "
                                       "1 × 6-hour conference"),
        ("h", "ADYEN BUSINESS INTEGRATION"),
        ("b", "Product integration (product + department)"),
        ("b", "In-market activation (market + idea titles)"),
        ("b", "Ideas in Alpine's marketing appendix: see Business Opportunity slide"),
        ("h", "CONTENT"),
        ("b", "Partner content capture day (e.g. ad reads, social assets, product placements)"),
        ("b", "2 social media campaigns"),
        ("b", "Case studies (B2B case study, whitepaper, photo or video, testimonial, news "
              "release), distributed via trade and earned media"),
        ("h", "FAN ENGAGEMENT"),
        ("b", "4 integrated content blocks in race preview and debrief newsletters"),
        ("b", "2 solus CRM emails to an agreed audience"),
        ("h", "LAUNCH AND ACCOUNT MANAGEMENT"),
        ("b", "Coordinated launch with press release and social media post"),
        ("b", "Dedicated account manager; media exposure reports (Nielsen, Blinkfire)"),
    ],
    [
        ("h", "HOSPITALITY"),
        ("kv", "Paddock Club tickets: ", "24 at selected races (excl. Monaco, Singapore, Austin, "
                                         "Miami, Las Vegas, Abu Dhabi); 16 at Monaco, Singapore, "
                                         "Austin or Abu Dhabi; 8 at Miami; 8 at Las Vegas; more "
                                         "at partner rate"),
        ("kv", "Grandstand tickets: ", "right to purchase at partner rate"),
        ("kv", "Paddock passes: ", "one-day passes on request, subject to availability"),
        ("kv", "U.S. near-track dinners: ", "2, for up to 15 guests"),
        ("h", "OFF-TRACK EXPERIENCES"),
        ("kv", "Enstone factory: ", "2 VIP tours (12 guests each) and 1 factory event (60 guests), "
                                    "at Alpine's cost"),
        ("kv", "Showcar and Trak Racer simulators: ", "14 days' hire each, at Adyen's cost"),
        ("kv", "Driving: ", "1 motorsport driving day for 24 guests, at Alpine's cost; right to "
                            "buy more, e.g. Lapland Ice Driving"),
        ("kv", "Partner ecosystem: ", "networking with Alpine's partners; 6 car-launch tickets"),
        ("h", "MERCHANDISE"),
        ("b", "Team polos and caps: 40 signed and 80 unsigned of each"),
        ("b", "2 replica driver helmets, 50 mini helmets, 2 replica driver sets"),
        ("b", "Team and co-branded merchandise at partner rate"),
        ("note", "All benefits are per year of the term unless stated otherwise."),
    ],
]
COL_X = [432288, 4250000, 8070000]
COL_WIDTH = [3600000, 3600000, 3700000]
for items, x, w in zip(COLS, COL_X, COL_WIDTH):
    tf = add_textbox(alp_rights, x, 1700000, w, 4600000).text_frame
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        kind = item[0]
        if kind == "h":
            if not first:
                p.space_before = Pt(7)
            r = p.add_run()
            r.text = item[1]
            style_run(r, 8.5, bold=True, color=RED)
        elif kind == "kv":
            p.space_before = Pt(2)
            r = p.add_run()
            r.text = item[1]
            style_run(r, 8, bold=True)
            r = p.add_run()
            r.text = item[2]
            style_run(r, 8)
        elif kind == "b":
            p.space_before = Pt(2)
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", "114300")
            pPr.set("indent", "-114300")
            buclr = etree.SubElement(pPr, qn("a:buClr"))
            etree.SubElement(buclr, qn("a:srgbClr")).set("val", "C00000")
            etree.SubElement(pPr, qn("a:buFont"), typeface="Arial")
            etree.SubElement(pPr, qn("a:buChar"), char="•")
            r = p.add_run()
            r.text = item[1]
            style_run(r, 8)
        elif kind == "note":
            p.space_before = Pt(4)
            r = p.add_run()
            r.text = item[1]
            style_run(r, 7, italic=True, color=GREY)
        first = False
add_source(alp_rights)

prs.save(OUT)
print("saved", OUT)
