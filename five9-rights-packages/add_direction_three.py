"""Turn a copy of the Direction two slide into Direction three (football), and make the
overview slide say "three potential directions".

Usage: python3 add_direction_three.py <unpacked_deck_dir> <new_slide.xml>
<new_slide.xml> must be a fresh copy of slide32.xml (Direction two) made with add_slide.py.
"""
import re
import sys

ROOT, SLIDE = sys.argv[1], sys.argv[2]
IMAGE = "image241.jpeg"   # football portrait already used on the Arsenal slide
TWO = ("Multi-assets platform: several partnerships with assets in your key markets, "
       "based on the same partnership structure")
THREE = ("Club partnership: one partnership with a leading European football club, "
         "giving access to the biggest audience in sport")

path = f"{ROOT}/ppt/slides/{SLIDE}"
xml = open(path, encoding="utf-8").read()
assert xml.count("<a:t>two</a:t>") == 1 and xml.count(TWO) == 1, "not a fresh Direction two copy"
xml = xml.replace("<a:t>two</a:t>", "<a:t>three</a:t>").replace(TWO, THREE)
# "three" is wider than "two": stop its box from wrapping
i = xml.index("<a:t>three</a:t>")
s = xml.rindex("<a:bodyPr", 0, i)
xml = xml[:s] + xml[s:i].replace('<a:bodyPr wrap="square"', '<a:bodyPr wrap="none"', 1) + xml[i:]
# portrait frame is 4873658 x 6134100; the 1010 x 1466 photo needs ~13% trimmed top + bottom
xml = re.sub(r'<a:srcRect t="5185"/>', '<a:srcRect t="3000" b="10300"/>', xml, count=1)
xml = xml.replace('descr="Image d’Épingle Story"', 'descr="Football player portrait"', 1)
open(path, "w", encoding="utf-8").write(xml)

rels_path = f"{ROOT}/ppt/slides/_rels/{SLIDE}.rels"
rels = open(rels_path, encoding="utf-8").read()
rels = rels.replace("../media/image182.jpeg", f"../media/{IMAGE}")
open(rels_path, "w", encoding="utf-8").write(rels)

overview = f"{ROOT}/ppt/slides/slide18.xml"
xml = open(overview, encoding="utf-8").read()
xml = xml.replace("<a:t>two potential directions</a:t>", "<a:t>three potential directions</a:t>")
open(overview, "w", encoding="utf-8").write(xml)
print("direction three ->", SLIDE)
