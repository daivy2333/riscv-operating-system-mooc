import os,re,argparse

SRC_EXT={'.c','.h','.S','.ld','Makefile'}
IGN={'.git','build','dist','__pycache__','.vscode'}
ARCH_MAP={'core':[],'mm':[],'driver':[],'fs':[],'user':[],'other':[]}

def classify(path):
    for k in ARCH_MAP:
        if f"/{k}/" in path: return k
    return 'other'

def strip_comments(s):
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
    s=re.sub(r'//.*','',s)
    return s

def minify_c(s):
    s=strip_comments(s)
    lines=[]
    buf=[]
    for l in s.splitlines():
        l=l.strip()
        if not l:continue
        if l.startswith('#'):
            if buf:lines.append(" ".join(buf));buf=[]
            lines.append(l)
        else:buf.append(l)
    if buf:lines.append(" ".join(buf))
    s="\n".join(lines)
    s=re.sub(r'\s*([=+\-*/%&|^!<>?:;,(){}\[\]])\s*',r'\1',s)
    return s

def parse_funcs(s):
    return re.findall(r'\b([a-zA-Z_][\w\s\*]+?)\s+([a-zA-Z_]\w*)\s*\(',s)

def parse_includes(s):
    return re.findall(r'#include\s+[<"](.+?)[>"]',s)

def main(root,out):
    index,includes,funcs,code=[],[],[],[]
    for r,ds,fs in os.walk(root):
        ds[:]=[d for d in ds if d not in IGN]
        for f in fs:
            if f.endswith(tuple(SRC_EXT)):
                p=os.path.join(r,f)
                rp=os.path.relpath(p,root)
                with open(p,'r',errors='ignore') as fd:
                    raw=fd.read()
                ARCH_MAP[classify(rp)].append(rp)
                inc=parse_includes(raw)
                if inc: includes.append(f"{rp}->{','.join(inc)}")
                fsig=parse_funcs(raw)
                for _,n in fsig: funcs.append(n)
                code.append((rp,minify_c(raw)))

    with open(out,'w') as o:
        o.write("[ARCH]\n")
        for k,v in ARCH_MAP.items():
            if v:o.write(f"{k}:{' '.join(v)}\n")

        o.write("\n[INCLUDE_GRAPH]\n")
        for i in includes:o.write(i+"\n")

        o.write("\n[SYMBOLS]\n")
        o.write(" ".join(sorted(set(funcs)))+"\n")

        o.write("\n[CODE]\n")
        for p,c in code:
            o.write(f"<{p}>\n{c}\n</{p}>\n")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("-o",default="os_context.txt")
    a=ap.parse_args()
    main(a.dir,a.o)
