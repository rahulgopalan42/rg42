# Usage: python3 proc_rec2.py <workdir> title=fileid ... -> rows_<title>.json with row-level OCR (every 3 s, 4 workers)
import subprocess,sys,os,json,glob,shutil,time
from multiprocessing import Pool
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.environ['OMP_THREAD_LIMIT']='1'
import rowocr
W=sys.argv[1]; os.makedirs(W,exist_ok=True)
def job(f):
    try:
        st,rows=rowocr.rows(f); return {'f':os.path.basename(f),'cols':st,'rows':rows}
    except Exception as e: return {'f':os.path.basename(f),'err':str(e)}
if __name__=='__main__':
    for arg in sys.argv[2:]:
        title,fid=arg.split('=',1); out=f'{W}/rows_{title}.json'
        if os.path.exists(out): continue
        t0=time.time(); vid=f'{W}/{title}.mov'; fr=f'{W}/fr_{title}'
        subprocess.run(['curl','-sS','-L','--retry','4','-o',vid,f'https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t'])
        os.makedirs(fr,exist_ok=True)
        subprocess.run(['ffmpeg','-v','error','-y','-i',vid,'-vf','fps=1/3','-q:v','2',f'{fr}/%05d.jpg']); os.remove(vid)
        frames=sorted(glob.glob(f'{fr}/*.jpg'))
        with Pool(4) as p: res=p.map(job,frames,chunksize=4)
        json.dump({'title':title,'frames':res},open(out,'w'))
        shutil.rmtree(fr)
        print(f'{title}: {len(frames)} frames, {sum(len(r.get("rows",[])) for r in res)} rows, {time.time()-t0:.0f}s',flush=True)
    print('ALL DONE',flush=True)
