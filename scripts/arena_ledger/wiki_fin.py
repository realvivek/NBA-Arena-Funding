import sys
import re, json, glob, os
RAW=os.environ.get('RAW_DIR','raw')
files=sorted(glob.glob(RAW+'/wikiraw/*.txt'))+sorted(glob.glob(RAW+'/wiki/*.json'))
only=sys.argv[1:]
def clean(s):
    s=re.sub(r'<ref[^>]*/>','',s); s=re.sub(r'<ref[^>]*>.*?</ref>','',s,flags=re.S)
    s=re.sub(r'\{\{[Ii]nflation[^}]*\}\}','',s)
    s=re.sub(r'\{\{(?:US\$|USD)\|?([^}]*)\}\}',r'$\1',s)
    s=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',r'\1',s)
    s=re.sub(r'<br\s*/?>',' ; ',s)
    return s
kw=re.compile(r'(public|taxpayer|bond|tax|financ|fund|subsid|contribut|land|purchas|bought|paid|privately|cost)',re.I)
for f in files:
    name=os.path.basename(f).rsplit('.',1)[0]
    if only and not any(o.lower() in name.lower() for o in only): continue
    raw=open(f,encoding='utf-8',errors='ignore').read()
    if f.endswith('.json'):
        try: raw=json.loads(raw)['parse']['wikitext']['*']
        except Exception: continue
    if '<html' in raw[:500].lower(): continue
    lines=[l for l in clean(raw).split('\n') if not l.strip().startswith(('|','{|','!','*{{','{{Infobox'))]
    body=re.sub(r'\s+',' ',' '.join(lines))
    sents=re.split(r'(?<=[.!?])\s+(?=[A-Z])',body)
    out=[s for s in sents if re.search(r'(million|billion)',s) and kw.search(s) and not re.search(r'(tour|concert|gross|attendance)',s,re.I)]
    print('#####',name, len(out))
    for s in out[:int(os.environ.get('N','22'))]: print('  -',s[:380])
