import sys
import re, os
X=os.environ.get('RAW_DIR','raw')+'/wiki_x/'
# args: file regex [maxchars] [maxhits] ... separated by ::
args=' '.join(sys.argv[1:]).split('::')
for a in args:
    p=a.strip().split(' ',1)
    if len(p)<2: continue
    fn,rx=p[0],p[1]
    mc,mh=900,6
    m=re.match(r'(.*?)\s+(\d+)\s+(\d+)$',rx)
    if m: rx,mc,mh=m.group(1),int(m.group(2)),int(m.group(3))
    try: txt=open(X+fn+'.txt').read().split('\n')
    except Exception as e: print('NOFILE',fn); continue
    hits=[l for l in txt if re.search(rx,l,re.I)]
    print('#### %s /%s/ (%d hits)'%(fn,rx,len(hits)))
    for l in hits[:mh]:
        # center on first match
        mm=re.search(rx,l,re.I); s=max(0,mm.start()-mc//3)
        print('-', l[s:s+mc])
