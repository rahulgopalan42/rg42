import json,subprocess,sys
P='/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python'
C='/home/user/rg42/brandprofile/v2/check.py'
def check(names):
    res={}
    for i in range(0,len(names),60):
        ch=names[i:i+60]
        o=subprocess.run([P,'-I',C]+ch,capture_output=True,text=True).stdout
        for line in o.splitlines():
            if ': ' in line:
                n,s=line.split(': ',1); res[n.strip()]=s.strip()
    return res
if __name__=='__main__':
    names=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    r=check(names); json.dump(r,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
    for n in names: print(n,'::',r.get(n.split('|')[0].strip(),'?')[:150])
