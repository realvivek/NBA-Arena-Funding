"""Write data/datapackage.json: a Frictionless table schema for every CSV in data/.

    .venv/bin/python pipeline/datapackage.py

Field types are inferred from each file; pipeline/schemas.yaml adds constraints (required fields, allowed values,
patterns, keys) for the files the site reads. pipeline/build.py validates every file against the package and stops
on the first error. Rerun this script after adding a CSV or a column.
"""
import json
import os

import yaml
from frictionless import describe

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')


def csv_files():
    out = []
    for d, _, files in os.walk(DATA):
        for f in files:
            if f.endswith('.csv'):
                out.append(os.path.relpath(os.path.join(d, f), DATA))
    return sorted(out)


def main():
    rules = yaml.safe_load(open(os.path.join(HERE, 'schemas.yaml')))
    resources, names = [], set()
    for rel in csv_files():
        res = describe(os.path.join(DATA, rel), stats=False)
        schema = res.schema.to_dict()
        rule = rules.get(rel, {})
        by_name = {f['name']: f for f in schema['fields']}
        for name, spec in rule.get('fields', {}).items():
            if name not in by_name:
                raise SystemExit(f'{rel}: schemas.yaml names a field that is not in the file: {name}')
            by_name[name].update(spec)
        if 'primaryKey' in rule:
            schema['primaryKey'] = rule['primaryKey']
        name = os.path.splitext(rel)[0].replace('/', '-').lower().replace('_', '-')
        name = ''.join(ch if ch.isalnum() or ch in '-._' else '-' for ch in name)
        assert name not in names, name
        names.add(name)
        resources.append({'name': name, 'type': 'table', 'path': rel, 'scheme': 'file', 'format': 'csv',
                          'mediatype': 'text/csv', 'encoding': 'utf-8', 'schema': schema})
    unknown = set(rules) - set(csv_files())
    if unknown:
        raise SystemExit(f'schemas.yaml names files that do not exist: {sorted(unknown)}')
    pkg = {'name': 'nba-arena-funding', 'title': 'NBA arena funding ledgers',
           'description': 'Every CSV in data/. Field types are inferred; constraints for the files the site reads come from pipeline/schemas.yaml.',
           'resources': resources}
    with open(os.path.join(DATA, 'datapackage.json'), 'w') as f:
        f.write(json.dumps(pkg, indent=1, ensure_ascii=False) + '\n')
    print(f'{len(resources)} tables written to data/datapackage.json')


if __name__ == '__main__':
    main()
