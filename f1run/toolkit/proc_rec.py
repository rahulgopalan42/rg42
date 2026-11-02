# Usage: python3 proc_rec.py <workdir> <title=fileid> ...  -> downloads each Drive recording, samples 1 frame/s,
# finds the Crunchbase "Organization Name" column by OCR, reads names, writes <workdir>/names_<title>.json, deletes the video.
import subprocess, sys, os, json, re, glob, hashlib, csv, io, shutil, time
W=sys.argv[1]; os.makedirs(W,exist_ok=True)
def sh(*a,**k): return subprocess.run(a,capture_output=True,text=True,**k)
def header_box(img):
    t=sh('tesseract',img,'-','--psm','11','tsv').stdout
    rows=list(csv.DictReader(io.StringIO(t),delimiter='\t',quoting=csv.QUOTE_NONE))
    org=[r for r in rows if r.get('text','').lower().startswith('organiz') or r.get('text','').lower().endswith('nization')]
    if not org: return None
    o=org[0]; x=int(o['left']); y=int(o['top']); h=int(o['height'])
    nxt=[int(r['left']) for r in rows if r.get('text') and abs(int(r['top'])-y)<12 and int(r['left'])>x+90]
    right=min(nxt)-8 if nxt else x+260
    res=' '.join(r['text'] for r in rows if r.get('text') and ('result' in r['text'] or '$' in r['text'] or re.match(r'^\d[\d,]*$',r['text'])) and abs(int(r['top'])-(y-50))<40)
    return (x+24, y+h+6, right, res)
def fix(n):
    n=n.strip(' |.,;:-_~')
    n=re.sub(r'\bAl\b','AI',n); n=re.sub(r'\.Al\b','.AI',n)
    return n
for arg in sys.argv[2:]:
    title,fid=arg.split('=',1)
    out=f'{W}/names_{title}.json'
    if os.path.exists(out): print('skip',title,flush=True); continue
    vid=f'{W}/{title}.mov'; fr=f'{W}/fr_{title}'
    t0=time.time()
    r=sh('curl','-sS','-L','--retry','4','-o',vid,f'https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t')
    if r.returncode or not os.path.exists(vid): print('DLFAIL',title,r.stderr[:200],flush=True); continue
    dur=float(sh('ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',vid).stdout.strip() or 0)
    os.makedirs(fr,exist_ok=True)
    sh('ffmpeg','-v','error','-y','-i',vid,'-vf','fps=1','-q:v','3',f'{fr}/%05d.jpg')
    os.remove(vid)
    frames=sorted(glob.glob(f'{fr}/*.jpg'))
    print(f'{title}: {dur:.0f}s, {len(frames)} frames, dl+extract {time.time()-t0:.0f}s',flush=True)
    box=None; last=None; recs=[]; names=[]
    for i,f in enumerate(frames):
        if box is None or i%15==0:
            b=header_box(f)
            if b: box=b
        if box is None: continue
        x0,y0,x1,res=box
        crop=f'{fr}/c.png'
        sh('ffmpeg','-v','error','-y','-i',f,'-vf',f'crop={x1-x0}:{1080-y0}:{x0}:{y0},scale=iw*3:-1,format=gray',crop)
        hsh=hashlib.md5(open(crop,'rb').read()).hexdigest()
        if hsh==last: continue
        last=hsh
        txt=sh('tesseract',crop,'-','--psm','6').stdout
        lines=[fix(l) for l in txt.splitlines() if len(fix(l))>1]
        recs.append({'t':i,'header':res,'names':lines}); names+=lines
    seen=[]; [seen.append(n) for n in names if n not in seen]
    json.dump({'title':title,'duration':dur,'frames':len(frames),'records':recs,'names':seen},open(out,'w'),indent=1)
    shutil.rmtree(fr)
    print(f'{title}: {len(seen)} distinct names, total {time.time()-t0:.0f}s',flush=True)
print('ALL DONE',flush=True)
