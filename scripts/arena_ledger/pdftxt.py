import sys
import pymupdf
src,dst=sys.argv[1],sys.argv[2]
doc=pymupdf.open(src)
with open(dst,'w') as f:
    for i,p in enumerate(doc):
        f.write(f'\n=== PAGE {i+1} ===\n'+p.get_text())
print(dst, len(doc))
