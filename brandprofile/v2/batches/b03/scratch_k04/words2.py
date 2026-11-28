import pdfplumber,sys
pdf=pdfplumber.open(sys.argv[1])
p=pdf.pages[int(sys.argv[2])]
print(p.width,p.height)
for w in p.extract_words():
    if 280<w['top']<420: print(round(w['x0']),round(w['top']),w['text'])
