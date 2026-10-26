# Builds the four F1 Merge Master v7 docx files (B2B, B2B no reference, B2C, B2C no reference).
# Format matches the user's sent emails (13 Oct 2026 screenshot): Calibri 11, 1.5 line spacing,
# a blank line between every paragraph and bullet, bold designation in the hook, bold bullet labels,
# SPORTFIVE in bold in the signature. Merge fields match the Merge List column headers.
# Run with python3.13 (python-docx is installed there).
import os
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

SCRATCH = os.path.dirname(os.path.abspath(__file__))

TEXT = {
    'opener': 'Reaching out from SPORTFIVE - the authorized agency managing brands sponsorships for '
              'Formula 1 teams working closely with McLaren, Haas, Audi & Mercedes to name a few.',
    'hook_a': 'A few of our Formula 1 teams are looking for an ',
    'hook_b': ', and ',
    'hook_c': ' was identified as a potential fit ',   # Fit_reason is a "due to ..." clause ending in a full stop
    'close': 'Would you be open to a quick call?',
    'sig': ['Rahul', 'Major Motorsport Projects - Global Sales', 'SPORTFIVE'],
}
BULLETS = [('Your target audience: ', 'Target_audience'),
           ('Market Overlap: ', 'Market_overlap'),
           ('Market Reference: ', 'Market_reference'),
           ('Shared Values: ', 'Shared_values'),
           ('Formula 1 Audience: ', 'F1_Audience')]


def fmt(p):
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p


def add_field(paragraph, name, bold=False):
    """Append a MERGEFIELD showing «name» in Word; MERGEFORMAT keeps the placeholder's bold."""
    anchor = paragraph.add_run()
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), f' MERGEFIELD {name} \\* MERGEFORMAT ')
    r = OxmlElement('w:r')
    if bold:
        rpr = OxmlElement('w:rPr')
        rpr.append(OxmlElement('w:b'))
        r.append(rpr)
    t = OxmlElement('w:t')
    t.text = f'«{name}»'
    r.append(t)
    fld.append(r)
    anchor._r.addnext(fld)
    anchor._r.getparent().remove(anchor._r)


def blank(doc):
    fmt(doc.add_paragraph())


def build(variant, with_reference):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(12)
    p = fmt(doc.add_paragraph('Hi '))
    add_field(p, 'First_name')
    p.add_run(',')
    blank(doc)
    fmt(doc.add_paragraph(TEXT['opener']))
    blank(doc)
    p = fmt(doc.add_paragraph(TEXT['hook_a']))
    add_field(p, 'Partner_designation', bold=True)
    if variant == 'B2B':     # B2B: short lead-in, the reason lives in the bullets (25 Oct)
        p.add_run(', and ')
        add_field(p, 'Company')
        p.add_run(' was identified for the following reasons:')
    else:                    # B2C keeps the "identified as a potential fit due to ..." sentence
        p.add_run(TEXT['hook_b'])
        add_field(p, 'Company')
        p.add_run(TEXT['hook_c'])
        add_field(p, 'Fit_reason')
    for label, field in BULLETS:
        if field == 'Market_reference' and not with_reference:
            continue
        if field == 'F1_Audience' and variant == 'B2B':
            continue
        if field == 'Pipeline' and variant == 'B2C':
            continue
        blank(doc)
        p = fmt(doc.add_paragraph(style='List Bullet'))
        p.add_run(label).bold = True
        add_field(p, field)
    blank(doc)
    fmt(doc.add_paragraph(TEXT['close']))
    blank(doc)
    fmt(doc.add_paragraph(TEXT['sig'][0]))
    fmt(doc.add_paragraph(TEXT['sig'][1]))
    p = fmt(doc.add_paragraph())
    p.add_run(TEXT['sig'][2]).bold = True
    name = f'F1 Merge Master v7 - {variant}{"" if with_reference else " no reference"}.docx'
    doc.save(os.path.join(SCRATCH, name))
    return name


if __name__ == '__main__':
    for v in ('B2B', 'B2C'):
        for ref in (True, False):
            print('built', build(v, ref))
