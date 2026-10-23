"""Which paying governments in data/ledger/households.csv each ZIP code lies in, for the ZIP lookup on the site.

Reads the Census Bureau's 2020 ZIP Code Tabulation Area relationship files from $RAW_DIR/census (default
./raw/census) and writes data/who_pays/zip_jurisdictions.csv (sources in data/who_pays/sources.csv): one row per ZIP code area and paying government, with
the share of the ZIP code area's land inside that government. Rows below 5% of the land are left out. Rerun after
write_totals.py when the governments in households.csv change.

Downloads: https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt
           https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_place20_natl.txt
"""
import collections, csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.environ.get('RAW_DIR') or os.path.join(ROOT, 'raw')
MIN_SHARE = 0.05

geos = {r['geo_id'] for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'ledger', 'households.csv')))}
land = {}                                  # ZCTA -> land area
part = collections.defaultdict(float)      # (ZCTA, geo_id) -> land area inside
for fn, kind in (('tab20_zcta520_county20_natl.txt', 'county'), ('tab20_zcta520_place20_natl.txt', 'place')):
    with open(os.path.join(RAW, 'census', fn), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f, delimiter='|'):
            z = r['GEOID_ZCTA5_20']
            if not z:
                continue
            land[z] = int(r['AREALAND_ZCTA5_20'] or 0)
            a = int(r['AREALAND_PART'] or 0)
            if kind == 'county':
                g = r['GEOID_COUNTY_20']
                for geo in ('05000US' + g, '04000US' + g[:2]):
                    if geo in geos:
                        part[(z, geo)] += a
            elif r['GEOID_PLACE_20'] and '16000US' + r['GEOID_PLACE_20'] in geos:
                geo = '16000US' + r['GEOID_PLACE_20']
                part[(z, geo)] += a
rows = []
for (z, geo), a in sorted(part.items()):
    if land.get(z) and a / land[z] >= MIN_SHARE:
        rows.append(dict(zip=z, geo_id=geo, land_share=round(a / land[z], 3)))
missing = geos - {r['geo_id'] for r in rows}
assert not missing, missing
path = os.path.join(ROOT, 'data', 'who_pays', 'zip_jurisdictions.csv')
with open(path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(path, len(rows), 'rows,', len({r['zip'] for r in rows}), 'ZIP code areas,', len(geos), 'governments')
