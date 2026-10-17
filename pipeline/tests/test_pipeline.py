"""Tests for the site pipeline: run with `.venv/bin/python -m pytest pipeline/tests`."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
ROOT = os.path.dirname(PIPE)
sys.path.insert(0, PIPE)

import build  # noqa: E402
import registry  # noqa: E402
from fmt import display  # noqa: E402
from models import StatSpec  # noqa: E402


@pytest.fixture(scope='module')
def built():
    srcs, by_url = build.load_sources()
    con, calc, comp = build.connect(by_url, srcs)
    stats = build.compute_stats(con, srcs)
    datasets = build.compute_datasets(con, srcs)
    return dict(srcs=srcs, con=con, calc=calc, comp=comp, stats=stats, datasets=datasets)


def test_tables_valid():
    assert build.validate_tables() >= 40


def test_registry_check():
    assert registry.check() == []


@pytest.mark.parametrize('stat,key', [
    ('core_public', 'core26'), ('total_spending', 'spend26'), ('construction_public', 'pub26'),
    ('purchase_public', 'acq26'), ('renovation_public', 'ren_pub26'), ('ongoing_public', 'og26'),
    ('pending_existing', 'pend26'),
])
def test_sql_matches_ledger_totals(built, stat, key):
    """The SQL over the normalized rows reproduces the ledger script's own totals."""
    assert built['stats'][stat].value == pytest.approx(built['calc']['agg'][key], abs=0.01)


def test_funding_streams_match_ledger(built):
    rows = {r['bucket']: r['public_2026_m'] for r in built['datasets']['who-pays'].rows}
    for b, v in built['calc']['bucket26'].items():
        assert rows[b] == pytest.approx(v, abs=0.01)
    shares = built['stats']['residents_share'].value + built['stats']['visitors_share'].value + built['stats']['other_share'].value
    assert shares == pytest.approx(100, abs=1e-6)


def test_expanded_total(built):
    s = built['stats']
    assert s['expanded_public'].value == pytest.approx(s['core_public'].value + s['tax_breaks_added'].value, abs=0.01)


def test_threat_stats_match_comparison(built):
    comp, s = built['comp'], built['stats']
    assert s['threats_counted'].value == comp['episodes_explicit_or_implied']
    assert s['threats_same_city'].value == len(comp['same_city_money'])
    assert s['lag_median'].value == pytest.approx(comp['lag_median'])
    assert s['p_share'].value == pytest.approx(comp['p_share'])


def test_every_stat_has_sources_and_label(built):
    for k, s in built['stats'].items():
        assert s.sources, k
        assert all(i in built['srcs'] for i in s.sources), k
        assert s.label, k


def test_rows_that_need_sources_have_them(built):
    with open(os.path.join(PIPE, 'datasets.yaml')) as f:
        import yaml
        specs = {d['id']: d for d in yaml.safe_load(f)['datasets']}
    for did, d in built['datasets'].items():
        spec = specs[did]
        if spec.get('require_row_sources'):
            col = spec['row_sources']
            assert all(r[col] for r in d.rows), did


def test_outputs_are_current():
    """The committed site data is what the pipeline produces now (CI runs the same check)."""
    build.main(['--check'])


@pytest.mark.parametrize('value,unit,digits,long,short', [
    (9304.75, 'usd_m', None, '$9.30 billion', '$9.30B'),
    (759.1, 'usd_m', None, '$759 million', '$759M'),
    (9.6, 'usd_m', None, '$9.6 million', '$9.6M'),
    (312.7, 'usd_m', 1, '$312.7 million', '$312.7M'),
    (34.23, 'pct', None, '34.2 percent', '34.2%'),
    (7, 'count', None, 'seven', '7'),
    (13, 'count', None, '13', '13'),
    (9098.63, 'usd', None, '$9,099', '$9,099'),
    (2.83, 'number', 1, '2.8', '2.8'),
])
def test_display(value, unit, digits, long, short):
    d = display(value, unit, digits)
    assert (d['long'], d['short']) == (long, short)


def test_count_must_be_whole():
    with pytest.raises(ValueError):
        display(2.5, 'count')


def test_spec_needs_evidence_for_hand_values():
    with pytest.raises(ValueError):
        StatSpec(key='x', title='x', unit='usd_m', value=1.0, label='b', sources=['ledger'])


def test_citation_parser_keeps_parentheses_in_urls():
    segs = registry.segments('https://a.gov/x_(G1C)_T.pdf (desc, p.2) ; https://b.org/y ; see (https://c.com/z)')
    assert segs == [('https://a.gov/x_(G1C)_T.pdf', 'desc, p.2'), ('https://b.org/y', ''), ('https://c.com/z', '')]


def test_labels_on_ledger_items_are_known(built):
    rows = built['con'].execute('select distinct public_label from items').fetchall()
    for (lbl,) in rows:
        assert all(part.strip() and set(part.strip()) <= set('abc/') for part in lbl.split(';')), lbl
