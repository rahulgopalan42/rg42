import pdfplumber,sys
pdf=pdfplumber.open(sys.argv[1])
p=pdf.pages[int(sys.argv[2])]
for w in p.extract_words()[:120]:
    print(round(w['x0']),round(w['top']),w['text'])
