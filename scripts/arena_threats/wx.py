import sys
import re, os, glob
D=os.environ.get('RAW_DIR','raw')+'/wiki'
O=D+'_x'; os.makedirs(O, exist_ok=True)
def cite(m):
    s=m.group(0)
    def g(k):
        mm=re.search(r'\|\s*'+k+r'\s*=\s*([^|}]*)', s); return mm.group(1).strip() if mm else ''
    t=g('title'); d=g('date') or g('access-date'); u=g('url'); w=g('work') or g('newspaper') or g('website') or g('publisher')
    if not (t or u): return ''
    return ' [REF: %s | %s | %s | %s]'%(t[:90],w[:40],d,u)
for fn in glob.glob(D+'/*.txt'):
    s=open(fn,encoding='utf-8',errors='ignore').read()
    if s.startswith('<!DOCTYPE') or len(s)<500: continue
    s=re.sub(r'<ref[^>/]*/>','',s)
    s=re.sub(r'<ref[^>]*>.*?</ref>', cite, s, flags=re.S)
    s=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', s)
    s=re.sub(r"'''?",'',s)
    s=re.sub(r'\{\{(?:cvt|convert)\|([^|}]*)\|([^|}]*)[^}]*\}\}', r'\1 \2', s)
    out=[]
    for para in s.split('\n'):
        if not re.search(r'relocat|threat|move|leave|left|Seattle|Las Vegas|Kansas City|Louisville|Anaheim|Virginia|Austin|Broward|referend|voter|council|legislat|public|tax|bond|subsid|debt|\$\s?[0-9]|million', para, re.I): continue
        out.append(para.strip())
    open(O+'/'+os.path.basename(fn),'w').write('\n'.join(out))
print(len(glob.glob(O+'/*.txt')))
