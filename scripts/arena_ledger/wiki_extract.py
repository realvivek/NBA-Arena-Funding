import sys
import re, json, glob, os
RAW=os.environ.get('RAW_DIR','raw')
files=sorted(glob.glob(RAW+'/wikiraw/*.txt'))+sorted(glob.glob(RAW+'/wiki/*.json'))
only=sys.argv[1:] 
def clean(s):
    s=re.sub(r'<ref[^>]*/>','',s); s=re.sub(r'<ref[^>]*>.*?</ref>','',s,flags=re.S)
    s=re.sub(r'\{\{[Ii]nflation[^}]*\}\}','[infl]',s)
    s=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',s)
    s=re.sub(r'<br\s*/?>',' ; ',s)
    return re.sub(r'\s+',' ',s).strip()
for f in files:
    name=os.path.basename(f).rsplit('.',1)[0]
    if only and not any(o.lower() in name.lower() for o in only): continue
    raw=open(f,encoding='utf-8',errors='ignore').read()
    if f.endswith('.json'):
        try: raw=json.loads(raw)['parse']['wikitext']['*']
        except Exception: continue
    if '<html' in raw[:500].lower(): continue
    print('#####',name)
    for fld in ['opened','built','owner','cost','construction_cost','project_manager','general_contractor','renovated','expanded','closed','operator','broke_ground','public_funding','private_funding']:
        m=re.search(r'\n\s*\|\s*'+fld+r'\s*=\s*(.*?)(?=\n\s*\|\s*\w+\s*=|\n\}\})',raw,flags=re.S)
        if m: print(f'  {fld}: {clean(m.group(1))[:300]}')
    body=clean(raw)
    sents=re.split(r'(?<=[.!?])\s+',body)
    kw=re.compile(r'(public|taxpayer|bond|tax|city|county|state|financ|fund|subsid|paid|contribut|land)',re.I)
    out=[s for s in sents if '$' in s and kw.search(s)]
    for s in out[:40]: print('   -',s[:420])
