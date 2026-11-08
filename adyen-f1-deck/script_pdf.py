"""Render the pitch script (Markdown) as a branded PDF for the presenter.

Writes "<script name>.html" next to the PDF, then prints it with the pre-installed Chromium (Playwright).
Handles only what the script uses: headings, paragraphs, **bold**, *italic* and '---' rules.

Usage: python3 script_pdf.py "Adyen x F1 - Pitch script.md" "Adyen x F1 - Pitch script (Deck 9).pdf"
"""
import html
import re
import subprocess
import sys

src, out = sys.argv[1], sys.argv[2]
eyebrow = sys.argv[3] if len(sys.argv) > 3 else "Talking script"
md = open(src, encoding="utf-8").read()


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*(.+?)\*", r'<em class="cue">\1</em>', t)
    return t


parts, star = [], "★"
title = ""
for block in re.split(r"\n\s*\n", md.strip()):
    b = block.strip()
    if b.startswith("# "):
        title = b[2:]
        parts.append(f'<header><div class="eyebrow">{html.escape(eyebrow)}</div><h1>{inline(title)}</h1></header>')
    elif b.startswith("## "):
        h = b[3:]
        m = re.match(r"([\d–]+) · (.*)", h)
        if m:
            n, name = m.groups()
            key = star in name
            name = name.replace(star, "").strip()
            parts.append(f'<h2><span class="num">{n}</span>{inline(name)}{"<span class=key>Key slide</span>" if key else ""}</h2>')
        else:
            parts.append(f'<h2 class="plain">{inline(h)}</h2>')
    elif b == "---":
        parts.append("<hr>")
    else:
        lines = b.split("\n")
        if len(lines) == 2 and lines[0].startswith("**\""):  # Q&A: question line + answer line
            parts.append(f'<div class="qa"><p class="q">{inline(lines[0])}</p><p>{inline(lines[1])}</p></div>')
        elif any(re.match(r"\d+\. ", l) for l in lines[1:]):  # lead-in paragraph followed by a numbered list
            lead = [l for l in lines if not re.match(r"\d+\. ", l)]
            items = [re.sub(r"^\d+\. ", "", l) for l in lines if re.match(r"\d+\. ", l)]
            parts.append(f"<p>{inline(' '.join(lead))}</p><ol>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ol>")
        else:
            text = " ".join(lines)
            cls = ""
            if b.startswith("*") and b.endswith("*") and not b.startswith("**"):
                cls = "cueline"
            for key, c in (("**Ask Mark:**", "ask"), ("**Insight:**", "insight"), ("**Land it:**", "land"), ("**Where it's from:**", "insight"), ("**Remember:**", "land")):
                if b.startswith(key):
                    cls = c
            parts.append(f'<p class="{cls}">{inline(text)}</p>' if cls else f"<p>{inline(text)}</p>")

doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
@page {{ size: A4; margin: 18mm 18mm 20mm 18mm; }}
body {{ font-family: Inter, sans-serif; color: #00112C; font-size: 11pt; line-height: 1.55; }}
header {{ border-bottom: 3px solid #0ABF53; padding-bottom: 10px; margin-bottom: 18px; }}
.eyebrow {{ color: #079A44; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; font-size: 9pt; }}
h1 {{ font-size: 22pt; margin: 4px 0 0; font-weight: 700; }}
h2 {{ font-size: 13.5pt; margin: 22px 0 6px; padding-top: 10px; border-top: 1px solid #D5DAE0; break-after: avoid; display: flex; align-items: center; gap: 10px; }}
h2.plain {{ display: block; color: #079A44; }}
.num {{ display: inline-block; min-width: 26px; height: 26px; line-height: 26px; text-align: center; border-radius: 13px;
  background: #00112C; color: #fff; font-size: 10pt; }}
.key {{ margin-left: auto; font-size: 8pt; font-weight: 700; color: #079A44; background: #E6F8ED; border-radius: 10px; padding: 2px 8px;
  letter-spacing: .06em; text-transform: uppercase; }}
p {{ margin: 0 0 8px; orphans: 3; widows: 3; }}
strong {{ font-weight: 700; }}
em.cue {{ color: #079A44; font-style: italic; }}
p.cueline {{ color: #079A44; }}
hr {{ border: 0; border-top: 3px solid #0ABF53; margin: 22px 0; }}
.qa {{ break-inside: avoid; margin-bottom: 10px; }}
p.land {{ font-size: 12pt; font-weight: 600; }}
p.land strong {{ color: #079A44; }}
p.insight {{ border-left: 3px solid #0ABF53; padding: 2px 0 2px 10px; }}
p.ask {{ background: #E6F8ED; border-radius: 6px; padding: 7px 10px; break-inside: avoid; }}
p.ask strong {{ color: #079A44; }}
ol {{ margin: 0 0 10px 18px; padding: 0; }} li {{ margin-bottom: 4px; }}
.qa .q {{ margin-bottom: 2px; }}
</style></head><body>{''.join(parts)}</body></html>"""

html_path = out.rsplit(".", 1)[0] + ".html"
open(html_path, "w", encoding="utf-8").write(doc)
js = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[1]);
  await p.pdf({ path: process.argv[2], format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-family:Inter,sans-serif;font-size:8px;color:#8F97A3;width:100%;padding:0 18mm;display:flex;justify-content:space-between"><span>Adyen × F1 · talking script · SPORTFIVE</span><span><span class=pageNumber></span> / <span class=totalPages></span></span></div>',
    margin: { top: '18mm', bottom: '20mm', left: '18mm', right: '18mm' } });
  await b.close();
})();
"""
import os
subprocess.run(["node", "-e", js, os.path.abspath(html_path), os.path.abspath(out)], check=True)
os.remove(html_path)
print("wrote", out)
