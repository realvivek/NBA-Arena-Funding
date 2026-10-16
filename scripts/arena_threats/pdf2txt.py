import sys
import pypdfium2 as pdfium
src,dst=sys.argv[1],sys.argv[2]
pdf=pdfium.PdfDocument(src); out=[]
for i in range(len(pdf)):
    out.append('=====PAGE %d====='%(i+1)); out.append(pdf[i].get_textpage().get_text_range())
open(dst,'w').write('\n'.join(out)); print(len(pdf),'pages')
