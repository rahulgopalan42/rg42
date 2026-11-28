import pdfplumber,json,re
pdf=pdfplumber.open('coface.pdf')
rows={}
for pi,p in enumerate(pdf.pages):
    ws=p.extract_words()
    anchors=[w for w in ws if w['x0']<50 and re.fullmatch(r'\d{1,3}',w['text']) and w['top']>60]
    cc=[w for w in ws if 70<w['x0']<92 and re.fullmatch(r'[A-Z]{2}',w['text'])]
    if len(anchors)<5 or len(cc)<5: continue
    for a in anchors:
        t=a['top']
        def near(x0,x1,tol=4):
            return [w for w in ws if x0<=w['x0']<x1 and abs(w['top']-t)<tol]
        def nearest_anchor(w):
            return min(anchors,key=lambda b:abs(b['top']-w['top']))
        name=[w for w in ws if 90<=w['x0']<220 and abs(w['top']-t)<14 and nearest_anchor(w) is a]
        name.sort(key=lambda w:(round(w['top']),w['x0']))
        sect=[w for w in ws if 220<=w['x0']<322 and abs(w['top']-t)<14 and nearest_anchor(w) is a and len(w['text'])>2]
        c=near(70,92)
        t23=near(320,350);t24=near(352,385);np24=near(440,470);e24=near(525,550)
        r=int(a['text'])
        rows[r]={'rank':r,'country':c[0]['text'] if c else '','name':' '.join(w['text'] for w in name),
          'sector':' '.join(w['text'] for w in sorted(sect,key=lambda w:(round(w['top']),w['x0']))),
          'turnover_2023_eur_m':t23[0]['text'] if t23 else '','turnover_2024_eur_m':t24[0]['text'] if t24 else '',
          'net_profit_2024_eur_m':np24[0]['text'] if np24 else '','employees_2024':e24[0]['text'] if e24 else '','page':pi+1}
with open('coface_rows.jsonl','w') as f:
    for r in sorted(rows): f.write(json.dumps(rows[r],ensure_ascii=False)+'\n')
print(len(rows))
