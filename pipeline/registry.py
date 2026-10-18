"""Source registry: every URL the site cites, with a stable id, origin tag, title, publisher and dates.

`python pipeline/registry.py seed [YYYY-MM-DD]` adds entries for URLs that are cited in the data but missing from
pipeline/sources.yaml, filling title, date and publisher by rule; the date, if given, is when the new sources were checked. It never changes an existing entry, so
curated fields survive. `python pipeline/registry.py check` fails if any cited URL has no entry.
"""
import csv, os, re, sys, json
from collections import OrderedDict
from urllib.parse import urlparse, unquote
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(ROOT, 'pipeline', 'sources.yaml')
EXTRA = os.path.join(ROOT, 'pipeline', 'sources_extra.yaml')  # sources cited by the site but not by URL in the data
DOMAINS = os.path.join(ROOT, 'pipeline', 'domains.yaml')
TITLES_CACHE = os.path.join(ROOT, 'raw', 'titles_cache.json')  # raw/ is not committed
URL_RE = re.compile(r'https?://[^\s;|,"\'\]]+')

# data files the site reads, and the columns that hold citations
CITED = {
    'data/ledger/ledger_items.csv': ['cost_source', 'public_source'],
    'data/ledger/arena_ledger.csv': None,  # every column whose name contains "source"
    'data/authorities/lease_clock.csv': ['source'],
    'data/threats/threat_ledger.csv': ['sources'],
    'data/threats/left_behind.csv': ['sources'],
    'data/inputs/arena_coordinates.csv': ['source'],
    'data/inputs/research_claims.csv': ['source'],
    'data/teams/team_values.csv': ['owner_source', 'price_source', 'value_source', 'deal_source'],
    'data/teams/investors.csv': ['source'],
    'data/teams/value_history.csv': ['source'],
    'data/teams/public_return.csv': ['sources'],
}
ORIGINS = ('government', 'court', 'team_or_league', 'independent')
GENERIC = {'download', 'document', 'file', 'content', 'show', 'view', 'index', 'detail', 'details', 'default', 'pdf', 'page',
           'archive', 'resource', 'files', 'attachments', 'documents', 'record', 'news', 'article', 'story', 'post', 'home'}


def norm_url(u):
    u = u.strip().rstrip('.').rstrip(']').rstrip(':')
    # a URL may contain parentheses ("..._(G1C)_Taxable.pdf"); drop only a closing one that has no opening one
    while u.endswith(')') and u.count(')') > u.count('('):
        u = u[:-1].rstrip('.')
    return u


def host_of(u):
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith('www.') else h


def segments(text):
    """Split a citation string into (url, description) pairs."""
    out = []
    for part in re.split(r'\s+[;|]\s+', text or ''):
        for m in URL_RE.finditer(part):
            url = norm_url(m.group(0))
            rest = part[m.end():].strip()
            desc = ''
            if rest.startswith('('):
                depth = 0
                for i, ch in enumerate(rest):
                    depth += ch == '('
                    depth -= ch == ')'
                    if depth == 0:
                        desc = rest[1:i]
                        break
                else:
                    desc = rest[1:]
            out.append((url, desc.strip()))
    return out


def citations():
    """Every (file, url, description) cited in the data the site reads."""
    found = []
    for fn, cols in CITED.items():
        with open(os.path.join(ROOT, fn), newline='') as f:
            for row in csv.DictReader(f):
                for k, v in row.items():
                    if cols is None and 'source' not in k:
                        continue
                    if cols is not None and k not in cols:
                        continue
                    for url, desc in segments(v):
                        found.append((fn, url, desc))
    return found


def slug(s, n=48):
    s = unquote(s).lower()
    s = re.sub(r'\.(pdf|html?|aspx|php|txt|json|htm)$', '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s[:n].strip('-')


def make_id(url, taken):
    p = urlparse(url)
    host = host_of(url)
    parts = [x for x in p.path.split('/') if x]
    if host == 'en.wikipedia.org' and parts:
        base = 'wiki-' + slug(parts[-1])
    elif host == 'sec.gov':
        base = 'sec-' + slug(parts[-1] if parts else 'filing')
    else:
        prefix = slug(host.split('.')[0] if host.split('.')[0] not in ('app', 'docs', 'api', 'data', 'news', 'apps', 'maps2', 'www2', 'audit', 'cd', 'web') else host.split('.')[1])
        seg = ''
        for cand in reversed(parts):
            c = slug(cand)
            if c and c not in GENERIC and not re.fullmatch(r'[0-9a-f-]{16,}', c) and not re.fullmatch(r'[0-9]+', c):
                seg = c
                break
        if not seg and p.query:
            seg = slug(p.query)
        base = prefix + ('-' + seg if seg else '')
    base = base[:60].strip('-')
    i, cand = 1, base
    while cand in taken and taken[cand] != url:
        i += 1
        cand = f'{base}-{i}'
    return cand


def guess_date(url, descs):
    for text in [url] + descs:
        m = re.search(r'(19|20)\d{2}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])', text)
        if m:
            return m.group(0).replace('/', '-')
        m = re.search(r'/((?:19|20)\d{2})/(0[1-9]|1[0-2])/', text)
        if m:
            return f'{m.group(1)}-{m.group(2)}'
    return 'n.d.'


def guess_title(url, descs, cache):
    for d in descs:
        t = re.split(r':| p\.\d| pdf p\.| printed p\.| s\.\d|; ', d)[0].strip(' ,')
        t = re.sub(r'\s+\($', '', t)
        if len(t) >= 12:
            return t, 'ledger description'
    c = cache.get(url) or {}
    t = (c.get('og_title') or c.get('title') or '').strip()
    if t and len(t) > 5 and not re.search(r'access denied|just a moment|forbidden|not found|attention required', t, re.I):
        return t, 'page title'
    p = urlparse(url)
    parts = [x for x in p.path.split('/') if x]
    last = unquote(parts[-1]) if parts else host_of(url)
    last = re.sub(r'\.(pdf|html?|aspx|php)$', '', last, flags=re.I)
    return re.sub(r'[-_]+', ' ', last).strip().capitalize(), 'url'


def load(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return yaml.safe_load(f) or default
    return default


def save_sources(entries):
    entries = sorted(entries, key=lambda e: e['id'])
    with open(SOURCES, 'w') as f:
        f.write('# Bibliography for the site. One entry per URL. origin: government | court | team_or_league | independent.\n')
        f.write('# date: document date (YYYY, YYYY-MM, YYYY-MM-DD or n.d.). checked: date the cited figures were last checked against it.\n')
        f.write('# title_from says how the title was set: ledger description, page title, url (needs a better title) or curated.\n')
        yaml.safe_dump({'sources': entries}, f, sort_keys=False, allow_unicode=True, width=1000)


def seed(checked_new='2026-10-16', checked_old='2026-10-11', old_urls=frozenset(), recheck_urls=frozenset()):
    domains = load(DOMAINS, {})
    cache = load(TITLES_CACHE, {}) if TITLES_CACHE.endswith('.yaml') else (json.load(open(TITLES_CACHE)) if os.path.exists(TITLES_CACHE) else {})
    reg = load(SOURCES, {'sources': []})['sources']
    extra = load(EXTRA, {'sources': []})['sources']
    by_url = {e['url']: e for e in reg + extra}
    taken = {e['id']: e['url'] for e in reg + extra}
    descs = OrderedDict()
    for fn, url, desc in citations():
        descs.setdefault(url, [])
        if desc and desc not in descs[url]:
            descs[url].append(desc)
    added = 0
    for url, ds in descs.items():
        if url in by_url:
            continue
        host = host_of(url)
        dom = domains.get(host) or domains.get('.'.join(host.split('.')[-2:])) or {}
        title, tfrom = guess_title(url, ds, cache)
        e = dict(id=make_id(url, taken), url=url, title=title, title_from=tfrom,
                        publisher=dom.get('publisher', host), origin=dom.get('origin', 'independent'),
                        date=guess_date(url, ds),
                        checked=checked_new if (url not in old_urls or url in recheck_urls) else checked_old)
        if not dom:
            e['review'] = 'domain not in domains.yaml'
        taken[e['id']] = url
        reg.append(e)
        by_url[url] = e
        added += 1
    save_sources(reg)
    return added, len(reg)


def check():
    reg = load(SOURCES, {'sources': []})['sources']
    extra = load(EXTRA, {'sources': []})['sources']
    urls = {e['url'] for e in reg + extra}
    ids = [e['id'] for e in reg + extra]
    problems = []
    if len(ids) != len(set(ids)):
        problems.append('duplicate ids')
    if len(urls) != len(reg) + len(extra):
        problems.append('duplicate urls (sources.yaml and sources_extra.yaml together)')
    cited = {url for _, url, _ in citations()}
    for e in reg:
        if e['url'] not in cited:
            problems.append(f"{e['id']}: in sources.yaml but no longer cited in the data; remove it or move it to sources_extra.yaml")
    for e in reg:
        for k in ('id', 'url', 'title', 'publisher', 'origin', 'date', 'checked'):
            if not e.get(k):
                problems.append(f"{e.get('id')}: missing {k}")
        if e.get('origin') not in ORIGINS:
            problems.append(f"{e['id']}: origin {e.get('origin')!r} not one of {ORIGINS}")
        if not re.fullmatch(r'\d{4}(-\d{2}(-\d{2})?)?|n\.d\.', str(e.get('date', ''))):
            problems.append(f"{e['id']}: date {e.get('date')!r}")
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(e.get('checked', ''))):
            problems.append(f"{e['id']}: checked {e.get('checked')!r}")
    for fn, url, desc in citations():
        if url not in urls:
            problems.append(f'{fn}: cited URL not in sources.yaml: {url}')
    return problems


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if cmd == 'seed':
        import subprocess
        old = set()
        for fn in CITED:
            try:
                txt = subprocess.run(['git', '-C', ROOT, 'show', f'main:{fn}'], capture_output=True, text=True, check=True).stdout
            except subprocess.CalledProcessError:
                continue
            old |= {norm_url(u) for u in URL_RE.findall(txt)}
        recheck = set()
        notes_dir = os.environ.get('RESEARCH_NOTES')
        if notes_dir and os.path.isdir(notes_dir):
            for n in os.listdir(notes_dir):
                if n.endswith('.md'):
                    recheck |= {norm_url(u) for u in URL_RE.findall(open(os.path.join(notes_dir, n)).read())}
        when = sys.argv[2] if len(sys.argv) > 2 else '2026-10-16'
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', when):
            sys.exit(f'seed: checked date {when!r} is not YYYY-MM-DD')
        print('added %d, total %d' % seed(checked_new=when, old_urls=old, recheck_urls=recheck))
    probs = check()
    for p in probs:
        print('PROBLEM', p)
    sys.exit(1 if probs else 0)
