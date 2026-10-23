"""Bexar County's November 4, 2025 vote on Proposition B (the county venue tax for a new Spurs arena), precinct by
precinct, with each precinct's households and median household income estimated from Census block groups.

Reads from $RAW_DIR (default ./raw):
  votes/bexar_20251104_precinct.pdf   Bexar County Elections, Official Precinct Report
  votes/precincts24g.zip              Texas Legislative Council, 2024 general election precincts (the precincts the
                                      county used in November 2025: the same 776 numbers)
  census/cb_2024_48_bg_500k.zip       Census Bureau cartographic block groups, Texas, 2024
  census/acs2024_5yr_bg_bexar.json    ACS 2020-2024 5-year B19013 and B11001 for Bexar block groups (Census Reporter)
Writes data/who_pays/bexar_2025_prop_b_precincts.csv and data/who_pays/bexar_county_outline.json (sources in
data/who_pays/sources.csv).
Needs PyMuPDF, pyshp, shapely and pyproj.

Method: a block group's households are spread over the precincts it overlaps in proportion to area; a precinct's
median income is the household-weighted mean of its block groups' medians (an approximation of the median).
"""
import collections, csv, io, json, os, re, zipfile
import pymupdf, shapefile
from pyproj import CRS, Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.environ.get('RAW_DIR') or os.path.join(ROOT, 'raw')
OUT = os.path.join(ROOT, 'data', 'who_pays')


def shapes(zpath, keep):
    z = zipfile.ZipFile(zpath)
    base = [n[:-4] for n in z.namelist() if n.lower().endswith('.shp')][0]
    prj = z.read(base + '.prj').decode()
    r = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), dbf=io.BytesIO(z.read(base + '.dbf')),
                         shx=io.BytesIO(z.read(base + '.shx')))
    names = [f[0] for f in r.fields[1:]]
    out = []
    for sr in r.iterShapeRecords():
        rec = dict(zip(names, sr.record))
        if keep(rec):
            out.append((rec, shape(sr.shape.__geo_interface__)))
    return prj, out


# 1. votes: every block of the report starts with the precinct number and ballot style ("1001 BS 1")
votes = collections.defaultdict(collections.Counter)
cur = None
for page in pymupdf.open(os.path.join(RAW, 'votes', 'bexar_20251104_precinct.pdf')):
    L = [x.strip() for x in page.get_text().split('\n')]
    for i, line in enumerate(L):
        m = re.match(r'^(\d{4}) BS \d+$', line)
        if m:
            cur = m.group(1)
        elif line == 'Registered Voters - Total':
            votes[cur]['registered'] += int(L[i + 1].replace(',', ''))
        elif line == 'Ballots Cast - Total':
            votes[cur]['ballots'] += int(L[i + 1].replace(',', ''))
        elif line == 'BEXAR COUNTY PROPOSITION - B':
            j = L.index('For', i)
            k = L.index('Against', j)
            votes[cur]['yes'] += int(L[j + 1].replace(',', ''))
            votes[cur]['no'] += int(L[k + 1].replace(',', ''))
yes, no = sum(v['yes'] for v in votes.values()), sum(v['no'] for v in votes.values())
assert (yes, no) == (128786, 118192), (yes, no)  # the county's Official Summary Report

# 2. precincts in the Texas Legislative Council's Lambert projection (meters); Bexar is county 29
prj, prec = shapes(os.path.join(RAW, 'votes', 'precincts24g.zip'), lambda r: int(r['CNTY']) == 29)
lam = CRS.from_wkt(prj)
to_ll = Transformer.from_crs(lam, 'EPSG:4326', always_xy=True).transform
from_bg = Transformer.from_crs('EPSG:4269', lam, always_xy=True).transform
P = {r['PREC']: g.buffer(0) for r, g in prec}
assert len(P) == 776, len(P)
missing = [p for p, v in votes.items() if v['yes'] + v['no'] > 0 and p not in P]
assert not missing, missing

# 3. block groups and their households and median incomes
_, bgs = shapes(os.path.join(RAW, 'census', 'cb_2024_48_bg_500k.zip'), lambda r: r['COUNTYFP'] == '029')
acs = json.load(open(os.path.join(RAW, 'census', 'acs2024_5yr_bg_bexar.json')))
assert acs['release']['id'] == 'acs2024_5yr'
BG = []
for rec, g in bgs:
    d = acs['data']['15000US' + rec['GEOID']]
    BG.append((transform(from_bg, g).buffer(0), d['B11001']['estimate']['B11001001'] or 0, d['B19013']['estimate']['B19013001']))
tree = STRtree([b[0] for b in BG])

rows = []
for p in sorted(P):
    g = P[p]
    hh = w = wi = 0.0
    for j in tree.query(g):
        bg, n, med = BG[j]
        a = g.intersection(bg).area
        if a <= 0:
            continue
        h = n * a / bg.area
        hh += h
        if med is not None and h > 0:
            w += h
            wi += h * med
    c = to_ll(*g.representative_point().coords[0]) if not g.contains(g.centroid) else to_ll(g.centroid.x, g.centroid.y)
    v = votes.get(p, collections.Counter())
    rows.append(dict(precinct=p, registered=v['registered'], ballots=v['ballots'], yes_votes=v['yes'], no_votes=v['no'],
                     households_est=round(hh), median_income_est=int(round(wi / w, -2)) if w else '',
                     lon=round(c[0], 4), lat=round(c[1], 4), label='b/a'))
with open(os.path.join(OUT, 'bexar_2025_prop_b_precincts.csv'), 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
    wr.writeheader()
    wr.writerows(rows)

# 4. the county outline for the map, simplified to about 200 m
outline = transform(to_ll, unary_union(list(P.values())).buffer(50).buffer(-50).simplify(200))
geom = mapping(outline)
def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 4), round(c[1], 4)]
geom = {'type': geom['type'], 'coordinates': rnd(geom['coordinates'])}
with open(os.path.join(OUT, 'bexar_county_outline.json'), 'w') as f:
    json.dump({'geometry': geom}, f, separators=(',', ':'))
    f.write('\n')
print(len(rows), 'precincts;', sum(1 for r in rows if r['yes_votes'] + r['no_votes']), 'with votes; yes', yes, 'no', no)
