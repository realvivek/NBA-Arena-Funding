"""Build the site's data from the committed ledgers.

    .venv/bin/python pipeline/build.py           # validate, compute, write site/src/generated/ and docs/fact-check.md
    .venv/bin/python pipeline/build.py --check   # same, but fail if any output differs from what is committed

Steps, each of which stops the build on a problem:
1. Frictionless validation of every CSV in data/ against data/datapackage.json.
2. The source registry: every URL cited in the data has an entry with an origin tag and dates.
3. DuckDB views over the CSVs (pipeline/views.sql), plus tables mapping every row's citations to source ids.
4. Every stat in pipeline/stats.yaml and dataset in pipeline/datasets.yaml, validated with Pydantic.
5. JSON for the site, and the fact-check ledger.
"""
import csv
import json
import os
import sys

import duckdb
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import registry  # noqa: E402
from fmt import display  # noqa: E402
from models import Dataset, DatasetSpec, Source, Stat, StatSpec, label_ok  # noqa: E402

OUT = os.path.join(ROOT, 'site', 'src', 'generated')
FACTCHECK = os.path.join(ROOT, 'docs', 'fact-check.md')


class BuildError(Exception):
    pass


def fail(msgs):
    raise BuildError('\n'.join(['build failed:'] + ['  ' + m for m in msgs]))


# ---------------------------------------------------------------- 1. tables
def validate_tables():
    from frictionless import Package
    pkg = Package(os.path.join(ROOT, 'data', 'datapackage.json'))
    report = pkg.validate()
    if not report.valid:
        msgs = []
        for task in report.tasks:
            for err in task.errors[:5]:
                msgs.append(f'{task.name}: {err.message}')
        fail(msgs or ['datapackage.json is not valid'])
    return len(pkg.resources)


# ---------------------------------------------------------------- 2. sources
def load_sources():
    entries = []
    for fn in ('sources.yaml', 'sources_extra.yaml'):
        with open(os.path.join(HERE, fn)) as f:
            entries += (yaml.safe_load(f) or {}).get('sources', [])
    problems = registry.check()
    srcs, by_url = {}, {}
    for e in entries:
        for k in ('date', 'checked'):  # YAML reads 2026-10-16 as a date and 2026 as a number
            if k in e and not isinstance(e[k], str):
                e[k] = e[k].isoformat() if hasattr(e[k], 'isoformat') else str(e[k])
        try:
            s = Source(**e)
        except Exception as ex:  # pydantic ValidationError
            problems.append(f"source {e.get('id')}: {ex}")
            continue
        if s.id in srcs:
            problems.append(f'duplicate source id {s.id}')
        if s.url in by_url:
            problems.append(f'duplicate source url {s.url} ({by_url[s.url]}, {s.id})')
        srcs[s.id] = s
        by_url[s.url] = s.id
    if problems:
        fail(problems)
    return srcs, by_url


def ids_for(text, by_url):
    out = []
    for url, _ in registry.segments(text):
        sid = by_url.get(url)
        if sid is None:
            raise BuildError(f'cited URL has no source entry: {url}')
        if sid not in out:
            out.append(sid)
    return out


def source_tables(by_url):
    """Rows mapping each cited row in the data to source ids, in citation order."""
    def read(fn):
        with open(os.path.join(ROOT, fn), newline='') as f:
            return list(csv.DictReader(f))
    t = {'item_sources': [], 'arena_sources': [], 'lease_sources': [], 'threat_sources': [], 'left_behind_sources': [],
         'coord_sources': []}
    for r in read('data/ledger/ledger_items.csv'):
        for role in ('cost', 'public'):
            for i, sid in enumerate(ids_for(r[f'{role}_source'], by_url)):
                t['item_sources'].append((r['item_id'], r['team'], role, sid, i))
    for r in read('data/ledger/arena_ledger.csv'):
        for k, v in r.items():
            if 'source' in k:
                for i, sid in enumerate(ids_for(v, by_url)):
                    t['arena_sources'].append((r['row_type'], r['team'], k, sid, i))
    for r in read('data/authorities/lease_clock.csv'):
        for i, sid in enumerate(ids_for(r['source'], by_url)):
            t['lease_sources'].append((r['team'], sid, i))
    for r in read('data/threats/threat_ledger.csv'):
        for i, sid in enumerate(ids_for(r['sources'], by_url)):
            t['threat_sources'].append((r['id'], sid, i))
    for r in read('data/threats/left_behind.csv'):
        for i, sid in enumerate(ids_for(r['sources'], by_url)):
            t['left_behind_sources'].append((r['city'], sid, i))
    for r in read('data/inputs/arena_coordinates.csv'):
        for i, sid in enumerate(ids_for(r['source'], by_url)):
            t['coord_sources'].append((r['team'], sid, i))
    return t


# ---------------------------------------------------------------- 3. database
def connect(by_url, srcs):
    con = duckdb.connect()
    with open(os.path.join(HERE, 'views.sql')) as f:
        con.execute(f.read().replace('{root}', ROOT))
    cols = {'item_sources': 'item_id VARCHAR, team VARCHAR, role VARCHAR, source_id VARCHAR, ord INTEGER',
            'arena_sources': 'row_type VARCHAR, team VARCHAR, field VARCHAR, source_id VARCHAR, ord INTEGER',
            'lease_sources': 'team VARCHAR, source_id VARCHAR, ord INTEGER',
            'threat_sources': 'id VARCHAR, source_id VARCHAR, ord INTEGER',
            'left_behind_sources': 'city VARCHAR, source_id VARCHAR, ord INTEGER',
            'coord_sources': 'team VARCHAR, source_id VARCHAR, ord INTEGER'}
    for name, rows in source_tables(by_url).items():
        con.execute(f'create table {name} ({cols[name]})')
        if rows:
            con.executemany(f"insert into {name} values ({', '.join('?' * len(rows[0]))})", rows)
    calc = json.load(open(os.path.join(ROOT, 'data', 'ledger', '_calc.json')))
    con.execute('create table cpi (year INTEGER, cpi DOUBLE, factor_2026 DOUBLE)')
    base = calc['CPI']['2026']
    con.executemany('insert into cpi values (?, ?, ?)', [(int(y), v, base / v) for y, v in calc['CPI'].items()])
    comp = json.load(open(os.path.join(ROOT, 'data', 'threats', 'comparison.json')))
    con.execute('create table comparison (k VARCHAR, v DOUBLE)')
    con.execute('create table comparison_ids (k VARCHAR, id VARCHAR)')
    con.execute('create table threat_lags (id VARCHAR, team VARCHAR, months DOUBLE)')
    flat, ids = [], []
    for k, v in comp.items():
        if isinstance(v, dict):
            flat += [(f'{k}.{k2}', float(v2)) for k2, v2 in v.items() if isinstance(v2, (int, float))]
        elif isinstance(v, (int, float)):
            flat.append((k, float(v)))
        elif isinstance(v, list) and k != 'deals':
            flat.append((f'{k}.n', float(len(v))))
            if k == 'lag_months':
                con.executemany('insert into threat_lags values (?, ?, ?)', [(d['id'], d['team'], d['months']) for d in v])
            else:
                ids += [(k, i) for i in v]
    con.executemany('insert into comparison values (?, ?)', flat)
    con.executemany('insert into comparison_ids values (?, ?)', ids)
    con.execute('create table threat_deals (id VARCHAR, deal VARCHAR, grp VARCHAR, flags VARCHAR, year INTEGER, '
                'public_m DOUBLE, public_m_2025 DOUBLE, total_m DOUBLE, share DOUBLE)')
    con.executemany('insert into threat_deals values (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    [(d['id'], d['deal'], d['group'], d['flags'], d['year'], d['public_m'], d['public_m_2025'], d['total_m'], d['share'])
                     for d in comp['deals']])
    con.execute('create table sources (id VARCHAR, origin VARCHAR, publisher VARCHAR, date VARCHAR, checked VARCHAR)')
    con.executemany('insert into sources values (?, ?, ?, ?, ?)', [(s.id, s.origin, s.publisher, s.date, s.checked) for s in srcs.values()])
    return con, calc, comp


def one(con, sql, what):
    try:
        res = con.execute(sql).fetchall()
    except duckdb.Error as ex:
        raise BuildError(f'{what}: {ex}')
    if len(res) != 1 or len(res[0]) != 1 or res[0][0] is None:
        raise BuildError(f'{what}: expected one value, got {res!r}')
    return res[0][0]


def column(con, sql, what):
    try:
        return [r[0] for r in con.execute(sql).fetchall() if r[0] is not None]
    except duckdb.Error as ex:
        raise BuildError(f'{what}: {ex}')


def dedupe(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


# ---------------------------------------------------------------- 4. stats and datasets
def check_evidence(spec):
    ev = spec.evidence
    with open(os.path.join(ROOT, ev.file), newline='') as f:
        rows = [r for r in csv.DictReader(f) if all(r.get(k) == v for k, v in ev.where.items())]
    if not rows:
        raise BuildError(f'{spec.key}: no row in {ev.file} matches {ev.where}')
    if not any(ev.contains in (r.get(ev.column) or '') for r in rows):
        raise BuildError(f'{spec.key}: {ev.contains!r} not found in {ev.file} {ev.column} for {ev.where}')


def compute_stats(con, srcs):
    with open(os.path.join(HERE, 'stats.yaml')) as f:
        specs = [StatSpec(**s) for s in yaml.safe_load(f)['stats']]
    stats, problems = {}, []
    for spec in specs:
        try:
            if spec.key in stats:
                raise BuildError(f'duplicate stat key {spec.key}')
            if spec.sql is not None:
                value = float(one(con, spec.sql, spec.key))
                method = ' '.join(spec.sql.split())
            else:
                check_evidence(spec)
                value = spec.value
                ev = spec.evidence
                method = f"Entered by hand; confirmed against {ev.file} ({', '.join(f'{k}={v}' for k, v in ev.where.items())}, column {ev.column}: \"{ev.contains}\")"
            if spec.check and one(con, spec.check, spec.key + ' check') is not True:
                raise BuildError(f'{spec.key}: check failed: {" ".join(spec.check.split())}')
            label = spec.label if spec.label is not None else str(one(con, spec.label_sql, spec.key + ' label'))
            if not label_ok(label):
                raise BuildError(f'{spec.key}: label {label!r} is not (a), (b), (c) or a combination')
            sources = list(spec.sources)
            if spec.sources_sql:
                sources += column(con, spec.sources_sql, spec.key + ' sources')
            sources = dedupe(sources)
            missing = [s for s in sources if s not in srcs]
            if missing:
                raise BuildError(f'{spec.key}: unknown source ids {missing}')
            if not sources:
                raise BuildError(f'{spec.key}: no sources (sources_sql returned nothing)')
            stats[spec.key] = Stat(key=spec.key, title=spec.title, value=round(value, 6), unit=spec.unit, basis=spec.basis,
                                   digits=spec.digits, label=label, sources=sources, display=display(value, spec.unit, spec.digits),
                                   note=spec.note, method=method)
        except (BuildError, ValueError) as ex:
            problems.append(f'{spec.key}: {ex}' if not str(ex).startswith(spec.key) else str(ex))
    if problems:
        fail(problems)
    return stats


def clean(v):
    if isinstance(v, float):
        return round(v, 6)
    if isinstance(v, list):
        return [clean(x) for x in v]
    if hasattr(v, 'isoformat'):
        return v.isoformat()
    return v


def compute_datasets(con, srcs):
    with open(os.path.join(HERE, 'datasets.yaml')) as f:
        specs = [DatasetSpec(**d) for d in yaml.safe_load(f)['datasets']]
    out, problems = {}, []
    for spec in specs:
        try:
            if spec.id in out:
                raise BuildError(f'duplicate dataset id {spec.id}')
            try:
                cur = con.execute(spec.sql)
            except duckdb.Error as ex:
                raise BuildError(f'{spec.id}: {ex}')
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, (clean(v) for v in r))) for r in cur.fetchall()]
            if not rows:
                raise BuildError(f'{spec.id}: no rows')
            sources = list(spec.sources)
            if spec.sources_sql:
                sources += column(con, spec.sources_sql, spec.id + ' sources')
            base = dedupe(sources)
            if spec.row_sources:
                for r in rows:
                    rs = r.get(spec.row_sources)
                    if not isinstance(rs, list):
                        raise BuildError(f'{spec.id}: column {spec.row_sources} is not a list of source ids')
                    r[spec.row_sources] = rs = dedupe(rs)
                    if spec.require_row_sources and not rs:
                        raise BuildError(f'{spec.id}: a row has no source: {dict(list(r.items())[:3])}')
                    sources += rs
            sources = dedupe(sources)
            missing = [s for s in sources if s not in srcs]
            if missing:
                raise BuildError(f'{spec.id}: unknown source ids {missing}')
            out[spec.id] = Dataset(id=spec.id, title=spec.title, sources=sources, base_sources=base, columns=cols, rows=rows, note=spec.note,
                                   method=' '.join(spec.sql.split()))
        except BuildError as ex:
            problems.append(str(ex))
    if problems:
        fail(problems)
    return out


# ---------------------------------------------------------------- 5. outputs
def dumps(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False) + '\n'


def factcheck_md(stats, datasets, srcs, calc):
    L = ['# Fact-check ledger', '',
         'Generated by `pipeline/build.py`; do not edit. Every number the site computes is listed here with its value, how it is',
         'shown, its label and its sources. Labels: (a) computed, (b) primary document, (c) press or secondary; a combination such as',
         'b/a means a primary figure converted or combined by computation. Dollars are 2026 dollars (BLS CPI-U, not seasonally',
         f"adjusted, 2026 base {calc['CPI']['2026']:.3f}) unless the basis says otherwise. The site's fact-check page also lists every number typed",
         'in the copy (years, names) with the sources of the paragraph it appears in.', '',
         f'{len(stats)} figures, {len(datasets)} datasets, {len(srcs)} sources. Ledger as of {calc["as_of"]}.', '',
         '## Figures', '']
    for s in stats.values():
        L.append(f'### `{s.key}`: {s.title}')
        L.append('')
        L.append(f'- Shown as: {s.display["long"]} ({s.display["short"]})')
        L.append(f'- Value: {s.value:,.6g} {s.unit}' + (f', {s.basis}' if s.basis else ''))
        L.append(f'- Label: ({s.label})')
        L.append('- Sources: ' + '; '.join(f'[{srcs[i].title}]({srcs[i].url}) ({srcs[i].origin.replace("_", " ")})' for i in s.sources))
        if s.note:
            L.append(f'- Note: {s.note}')
        L.append(f'- Method: `{s.method}`')
        L.append('')
    L += ['## Datasets behind the charts and tables', '']
    for d in datasets.values():
        L.append(f'- `{d.id}`: {d.title}. {len(d.rows)} rows; {len(d.sources)} sources.' + (f' {d.note}' if d.note else ''))
    L.append('')
    return '\n'.join(L)


def write(path, text, check, stale):
    old = open(path).read() if os.path.exists(path) else None
    if old == text:
        return
    if check:
        stale.append(os.path.relpath(path, ROOT))
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(text)


def main(argv):
    check = '--check' in argv
    n_tables = validate_tables()
    srcs, by_url = load_sources()
    con, calc, comp = connect(by_url, srcs)
    stats = compute_stats(con, srcs)
    datasets = compute_datasets(con, srcs)
    stale = []
    used = dedupe([i for s in stats.values() for i in s.sources] + [i for d in datasets.values() for i in d.sources])
    meta = {'as_of': calc['as_of'], 'cpi_2026': calc['CPI']['2026'], 'n_sources': len(srcs), 'n_sources_used': len(used)}
    write(os.path.join(OUT, 'meta.json'), dumps(meta), check, stale)
    write(os.path.join(OUT, 'sources.json'), dumps([s.model_dump(exclude_none=True) for s in sorted(srcs.values(), key=lambda s: s.id)]), check, stale)
    write(os.path.join(OUT, 'stats.json'), dumps({k: s.model_dump() for k, s in stats.items()}), check, stale)
    for d in datasets.values():
        write(os.path.join(OUT, 'datasets', f'{d.id}.json'), dumps(d.model_dump()), check, stale)
    have = {f[:-5] for f in os.listdir(os.path.join(OUT, 'datasets'))} if os.path.isdir(os.path.join(OUT, 'datasets')) else set()
    extra = sorted(have - set(datasets))
    if extra and check:
        stale += [f'site/src/generated/datasets/{e}.json (no longer produced)' for e in extra]
    elif extra:
        for e in extra:
            os.remove(os.path.join(OUT, 'datasets', f'{e}.json'))
    write(FACTCHECK, factcheck_md(stats, datasets, srcs, calc), check, stale)
    # the corrections log and the list of unreachable sites, shown on the site's fact-check page
    with open(os.path.join(ROOT, 'notes', 'verification.md')) as f:
        write(os.path.join(OUT, 'verification.md'), f.read(), check, stale)
    if stale:
        fail(['outputs differ from the committed files; run pipeline/build.py and commit:'] + stale)
    print(f'{n_tables} tables valid; {len(srcs)} sources; {len(stats)} stats; {len(datasets)} datasets'
          + ('; outputs match the committed files' if check else '; written'))


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except BuildError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
