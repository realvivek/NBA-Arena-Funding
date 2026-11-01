"""Madison Square Garden's property-tax exemption, fiscal year by fiscal year.

The Independent Budget Office's July 2023 report states the forgone tax for fiscal 1984-2023 only as a total, "more
than $946.7 million" in 2023 dollars, and draws it year by year in a bar chart ("Madison Square Garden Tax
Expenditure Cost to the City Over Time", report p.10). This reads the 40 bars' heights from the PDF's vector drawing,
checks them against the report's own figures (the total; fiscal 1984, $10.7 million, endnote 3; fiscal 2023, $42.4
million, p.9) and scales them to the stated total, so the series adds up to the figure the ledger uses. Fiscal
2024-2026 are the Department of Finance's tax-expenditure values, entered in ledger_inputs.py.

Reads the report from $RAW_DIR/ibo_msg (default ./raw/ibo_msg) and writes data/property_tax/msg_exemption_by_year.csv.
Needs PyMuPDF.

Download: https://www.ibo.nyc.gov/assets/ibo/downloads/pdf/taxes-and-other-revenues/2023/2023-july-an-examination-of-the-madison-square-garden-property-tax-exemption.pdf
"""
import csv, os, sys
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.environ.get('RAW_DIR') or os.path.join(ROOT, 'raw')
sys.path.insert(0, HERE)
from ledger_inputs import TEAMS, U  # noqa: E402

PDF = os.path.join(RAW, 'ibo_msg', '2023-july-msg-exemption-full.pdf')
URL = ('https://www.ibo.nyc.gov/assets/ibo/downloads/pdf/taxes-and-other-revenues/2023/'
       '2023-july-an-examination-of-the-madison-square-garden-property-tax-exemption.pdf')
CHART = 'Madison Square Garden Tax Expenditure Cost to the City Over Time'
TOTAL, FIRST, LAST = 946.7, 10.7, 42.4  # the report's own figures, 2023 dollars

doc = pymupdf.open(PDF)
page = next(p for p in doc if CHART in p.get_text())
words = page.get_text('words')
# the y axis runs $0 to $60 million; its labels are evenly spaced like the gridlines, so they give the scale
axis = {w[4]: (w[1] + w[3]) / 2 for w in words if w[4] in ('$0', '$60')}
per_m = (axis['$0'] - axis['$60']) / 60
# the bars: filled rectangles of one color standing on one baseline
bars = []
for g in page.get_drawings():
    if g.get('type') != 'f' or not g.get('fill'):
        continue
    for it in g['items']:
        if it[0] == 're' and it[1].width < 10 and it[1].height > 1:
            bars.append(it[1])
base = max(r.y1 for r in bars)
bars = sorted((r for r in bars if abs(r.y1 - base) < 0.1), key=lambda r: r.x0)
# the fiscal-year labels under the bars, matched to the nearest bar
labels = [((w[0] + w[2]) / 2, int(w[4])) for w in words
          if w[4].isdigit() and len(w[4]) == 4 and 1984 <= int(w[4]) <= 2023 and (w[1] + w[3]) / 2 > base]
read = {}
for r in bars:
    cx = (r.x0 + r.x1) / 2
    year = min(labels, key=lambda t: abs(t[0] - cx))[1]
    read[year] = (base - r.y0) / per_m

years = sorted(read)
assert years == list(range(1984, 2024)), f'expected one bar for each fiscal year 1984-2023, got {years}'
total = sum(read.values())
assert abs(total - TOTAL) / TOTAL < 0.005, f'bars add up to {total:.1f}, the report says {TOTAL}'
assert abs(read[1984] - FIRST) < 0.15, f'fiscal 1984 reads {read[1984]:.2f}, the report says {FIRST}'
assert abs(read[2023] - LAST) < 0.15, f'fiscal 2023 reads {read[2023]:.2f}, the report says {LAST}'
scale = TOTAL / total

nyk = next(t for t in TEAMS if t['team'] == 'NYK')['taxbreak']
dof = nyk['after']
out = os.path.join(ROOT, 'data', 'property_tax', 'msg_exemption_by_year.csv')
with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['fiscal_year', 'forgone_m', 'dollars', 'bar_reading_m', 'label', 'source'])
    for y in years:
        w.writerow([y, f'{read[y] * scale:.3f}', '2023', f'{read[y]:.3f}', 'a', URL])
    for y, v in dof:
        w.writerow([y, f'{v:.1f}', 'nominal', '', 'b', U['dof_ter'].split(' ')[0]])
print(f'{out}: {len(years)} bars read ({total:.1f}, scaled by {scale:.4f} to {TOTAL}) and {len(dof)} DOF years')
