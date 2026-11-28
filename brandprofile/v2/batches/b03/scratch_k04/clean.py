import json,re
out=open('coface_clean.jsonl','w')
for l in open('coface_rows.jsonl'):
    r=json.loads(l)
    if r['rank']==0 or not r['name']: continue
    n=r['name'].replace('COMPANY NAME MAIN SECTOR','').replace('***','').replace('**','')
    n=re.sub(r'(\w)- (\w)',r'\1\2',n)
    n=re.sub(r'\s+',' ',n).strip()
    n=n.replace(' SP. O.O.',' SP. Z O.O.')
    short=re.sub(r'[\s,]*(\*|&)+\s*$','',n)
    short=re.sub(r'\s*\*\s*',' ',short)
    base=re.sub(r'[ ,]+(S\.A\.|SP\. Z O\.O\.( SP\.K\.)?|A\.S\.|A\. S\.|S\.R\.O\.|S\. R\. O\.|SRL|SA|ZRT\.?|KFT\.?|NYRT\.?|UAB|AB|AS|D\.O\.O\.|D\.D\.|JSC|EAD|AD|OOD|SE|K\.S\.|SPÓŁKA AKCYJNA|SP\.K\.|S\.K\.A\.|SP\. J\.|PLC)\.?\s*$','',short).strip(' ,*&')
    base=re.sub(r'[ ,]+(S\.A\.|SP\. Z O\.O\.|A\.S\.|SRL|SA|ZRT|KFT|UAB|AB|AS|D\.O\.O\.|EAD|AD)\s*$','',base).strip(' ,*&')
    nums=r['nums']
    r.update(name_clean=short.strip(),base=base,consolidated='*' in r['name'])
    if len(nums)>=2: r['t23'],r['t24']=nums[0],nums[1]
    if len(nums)>=9: r['np24']=nums[4]; r['emp24']=nums[7]
    out.write(json.dumps(r,ensure_ascii=False)+'\n')
