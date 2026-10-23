"""ITEP's Who Pays? (7th edition, January 2024): state and local taxes as a share of family income for seven income
groups in each state, for the four lines the arena analysis uses. Reads ITEP's data workbook from $RAW_DIR/itep
(default ./raw/itep) and writes data/who_pays/itep_who_pays_7.csv (sources in data/who_pays/sources.csv). Needs
openpyxl.

Download: https://sfo2.digitaloceanspaces.com/itep/ITEP_WhoPays7_Data_Jan2024rev.xlsx (linked from
https://itep.org/whopays-7th-edition/ as "Data Available for Download").
"""
import csv, os
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.environ.get('RAW_DIR') or os.path.join(ROOT, 'raw')
# workbook tab -> what it measures (ITEP's own line names)
LINES = {
    'APP_A': 'All state and local taxes',
    'SE_GST': 'General sales taxes paid by individuals',
    'SE_EXCISE': 'Other sales and excise taxes paid by individuals',
    'PROP_TOTAL': 'Property taxes',
}
GROUPS = ['Lowest 20%', 'Second 20%', 'Middle 20%', 'Fourth 20%', 'Next 15%', 'Next 4%', 'Top 1%']

wb = openpyxl.load_workbook(os.path.join(RAW, 'itep', 'ITEP_WhoPays7_Data_Jan2024rev.xlsx'), read_only=True, data_only=True)
out = []
for tab, name in LINES.items():
    header = None
    for row in wb[tab].iter_rows(values_only=True):
        if row[0] == 'State':
            header = list(row[1:8])
            assert header == GROUPS, (tab, header)
            continue
        if header and isinstance(row[0], str) and isinstance(row[1], (int, float)):
            if row[0].startswith('Average'):
                continue
            for i, g in enumerate(GROUPS):
                out.append(dict(state=row[0], line=tab, line_name=name, grp=g, grp_order=i + 1,
                                share_of_income=round(float(row[1 + i]), 6), label='c'))
states = {r['state'] for r in out}
assert len(states) == 51, len(states)  # 50 states and the District of Columbia
path = os.path.join(ROOT, 'data', 'who_pays', 'itep_who_pays_7.csv')
with open(path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(out)
print(path, len(out), 'rows')
