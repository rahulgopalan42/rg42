import re,html,json,subprocess,time,sys
UA="Mozilla/5.0 (compatible; research-bot/1.0)"
idx=open('scratch_k03_idx.html',encoding='utf-8').read()
inds=sorted(set(re.findall(r'/toplists/sweden/largest-companies-by-turnover/industry/([a-z0-9-]+)',idx)))
skip={'sewerage','libraries-archives-museums-and-other-cultural-activities','residential-care-activities','veterinary-activities','activities-of-membership-organisations','social-work-activities-without-accommodation','repair-of-computers-and-personal-and-household-goods','water-collection-treatment-and-supply','fishing-and-aquaculture','forestry-and-logging','education','other-personal-service-activities','legal-and-accounting-activities','human-health-activities','services-to-buildings-and-landscape-activities'}
inds=[i for i in inds if i not in skip]
out=open('scratch_k03_lc_rows_'+sys.argv[1]+'.jsonl','a')
done=set()
import os
if os.path.exists('scratch_k03_lc_rows.jsonl'):
  done={(json.loads(l)['country'],json.loads(l)['industry']) for l in open('scratch_k03_lc_rows.jsonl')}
for c in sys.argv[1:]:
  for ind in ['']+inds:
    if (c,ind or "all") in done: continue
    path=f"/toplists/{c}/largest-companies-by-turnover"+(f"/industry/{ind}" if ind else "")
    url="https://www.largestcompanies.com"+path
    try:
      s=subprocess.run(['curl','-s','-m','30','-A',UA,url],capture_output=True,text=True).stdout
    except Exception as e: print('ERR',url); continue
    cur=re.search(r'Turnover \(×1000\)\s*(?:<[^>]+>\s*)*([A-Z]{3})',s)
    rows=re.findall(r'href="(/company/[^"]+)"[^>]*>([^<]+)</a>.*?([0-9][0-9 \xa0]{2,})\s*<',s,flags=re.S)
    n=0
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
    for href,name,val in re.findall(r'href="(/company/[^"]+)"[^>]*>\s*([^<]+?)\s*</a>(.*?)(?=href="/company/|$)',t,flags=re.S):
      m=re.search(r'>\s*(-?[0-9][0-9 \xa0]*)\s*<',val)
      v=m.group(1).replace(' ','').replace('\xa0','') if m else ''
      out.write(json.dumps({'country':c,'industry':ind or 'all','name':html.unescape(name),'turnover_k':v,'cur':cur.group(1) if cur else '','href':href,'source':url},ensure_ascii=False)+'\n'); n+=1
    out.flush(); print(c,ind,n,flush=True)
    time.sleep(1.5)
