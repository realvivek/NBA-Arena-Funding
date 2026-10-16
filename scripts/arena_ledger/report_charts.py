# Draws the two charts embedded in report/who-paid-for-nba-arenas.md from the built ledger.
# Run after build_ledger.py. Needs matplotlib (3.10); fonts fall back to DejaVu Sans if Inter is missing.
import csv, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = ROOT + '/data'
OUT = ROOT + '/report/charts'
plt.rcParams.update({'font.family': ['Inter', 'DejaVu Sans'], 'font.size': 11, 'text.parse_math': False, 'svg.hashsalt': 'arena', 'savefig.dpi': 150})
PUB, PRIV, VIS = '#2b7bd9', '#c4c4b8', '#1fb27a'
INK, MUTED = '#1a1a1a', '#555555'

CITY = {'ORL': 'Orlando', 'WAS': 'Washington', 'IND': 'Indiana', 'CHA': 'Charlotte', 'MEM': 'Memphis', 'UTA': 'Utah', 'HOU': 'Houston',
        'BKN': 'Brooklyn', 'SAS': 'San Antonio', 'DET': 'Detroit', 'CLE': 'Cleveland', 'NOP': 'New Orleans', 'MIL': 'Milwaukee', 'MIA': 'Miami',
        'ATL': 'Atlanta', 'SAC': 'Sacramento', 'PHX': 'Phoenix', 'OKC': 'Oklahoma City', 'MIN': 'Minnesota', 'DAL': 'Dallas', 'POR': 'Portland',
        'DEN': 'Denver', 'LAL': 'LA Lakers', 'LAC': 'LA Clippers', 'GSW': 'Golden State', 'CHI': 'Chicago', 'BOS': 'Boston', 'NYK': 'New York',
        'PHI': 'Philadelphia', 'TOR': 'Toronto'}

def money(m):
    return f'${m/1000:.2f}B' if m >= 1000 else f'${m:,.0f}M'

def arenas():
    rows = [r for r in csv.DictReader(open(DATA + '/ledger/arena_ledger.csv')) if r['row_type'] == 'current_arena']
    rows = [(r['team'], float(r['PUBLIC_TOTAL_2026_m'] or 0), float(r['total_arena_spending_2026_m'] or 0)) for r in rows]
    rows.sort(key=lambda x: (-x[1], -x[2]))
    pub = sum(p for _, p, _ in rows); tot = sum(t for _, _, t in rows); top10 = sum(p for _, p, _ in rows[:10])
    fig, ax = plt.subplots(figsize=(8.9, 8.9))
    fig.subplots_adjust(left=0.15, right=0.99, top=0.885, bottom=0.01)
    for i, (t, p, s) in enumerate(rows):
        ax.barh(i, s, color=PRIV, height=0.7)
        ax.barh(i, p, color=PUB, height=0.7)
        ax.text(s + 25, i, f'{money(p) if p else "$0"} of {money(s)}', va='center', ha='left', color=MUTED, fontsize=10.5)
    ax.axhline(9.5, color=MUTED, lw=1, ls=(0, (3, 3)))
    ax.text(max(s for _, _, s in rows) * 1.18, 9.38, f'Above the line: {100*top10/pub:.0f}% of all public money', ha='right', va='bottom', color=MUTED, fontsize=10.5)
    ax.set_yticks(range(len(rows)), [CITY[t] for t, _, _ in rows], fontsize=11, color=INK)
    ax.invert_yaxis(); ax.set_xticks([]); ax.set_xlim(0, max(s for _, _, s in rows) * 1.18)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(axis='y', length=0)
    fig.text(0.005, 0.975, f'Ten arenas hold {100*top10/pub:.0f}% of the public money in NBA arenas', fontsize=15, weight='bold', color=INK, va='top')
    fig.text(0.005, 0.94, f'{money(pub)} public of {money(tot)} spent on the 30 current arenas, 2026 dollars.', fontsize=11, color=MUTED, va='top')
    fig.patches.extend([plt.Rectangle((0.005, 0.902), 0.014, 0.014, color=PUB, transform=fig.transFigure, figure=fig),
                        plt.Rectangle((0.15, 0.902), 0.014, 0.014, color=PRIV, transform=fig.transFigure, figure=fig)])
    fig.text(0.025, 0.909, 'Public money', fontsize=11, color=INK, va='center'); fig.text(0.17, 0.909, 'Private money', fontsize=11, color=INK, va='center')
    fig.savefig(OUT + '/public-vs-private-by-arena.png', metadata={'Software': None})
    plt.close(fig)

def streams():
    C = json.load(open(DATA + '/ledger/_calc.json'))
    b = C['bucket26']; tot = sum(b.values())
    resident = ['general', 'sales', 'tif', 'leaserev', 'sin']; visitor = ['tourist']
    name = {'tourist': 'Hotel, car-rental, food and ticket taxes', 'general': 'General taxes, bonds and state grants', 'sales': 'Dedicated sales tax',
            'tif': 'Captured property and income taxes', 'mixed': 'Public, stream not documented', 'leaserev': 'Lease-revenue bonds (general fund, parking)',
            'sin': 'Alcohol and cigarette taxes', 'infra': 'Infrastructure and site work', 'land': 'Land given or sold below value'}
    res = sum(b.get(k, 0) for k in resident); vis = sum(b.get(k, 0) for k in visitor); oth = tot - res - vis
    order = sorted((k for k in b if b[k]), key=lambda k: -b[k])
    color = lambda k: PUB if k in resident else (VIS if k in visitor else PRIV)
    fig = plt.figure(figsize=(8.9, 4.6))
    fig.text(0.005, 0.975, f'Residents paid {100*res/tot:.0f}% of the public arena money; visitors paid {100*vis/tot:.0f}%', fontsize=15, weight='bold', color=INK, va='top')
    fig.text(0.005, 0.915, f'{money(tot)} of public capital for the 30 arenas, 2026 dollars, by who mostly pays (bar) and by funding stream (below).', fontsize=10.5, color=MUTED, va='top')
    top = fig.add_axes([0.0, 0.79, 1.0, 0.055]); x = 0
    for v, c in [(res, PUB), (vis, VIS), (oth, PRIV)]:
        top.barh(0, v, left=x, color=c, height=1); x += v
    top.set_xlim(0, tot); top.axis('off')
    fig.text(0.005, 0.755, f'Paid mostly by residents: {100*res/tot:.0f}%', fontsize=11, color=INK, va='top')
    fig.text(res / tot + 0.003, 0.755, f'Paid mostly by visitors: {100*vis/tot:.0f}%', fontsize=11, color=INK, va='top')
    fig.text(0.995, 0.755, f'In kind or not documented: {100*oth/tot:.0f}%', fontsize=11, color=INK, va='top', ha='right')
    ax = fig.add_axes([0.40, 0.02, 0.58, 0.63])
    for i, k in enumerate(order):
        ax.barh(i, b[k], color=color(k), height=0.62)
        ax.text(b[k] + tot * 0.006, i, f'${b[k]/1000:.2f}B ({100*b[k]/tot:.0f}%)', va='center', color=MUTED, fontsize=10.5)
    ax.set_yticks(range(len(order)), [name[k] for k in order], fontsize=11, color=INK)
    ax.invert_yaxis(); ax.set_xticks([]); ax.set_xlim(0, max(b.values()) * 1.25)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(axis='y', length=0)
    fig.savefig(OUT + '/public-capital-by-stream.png', metadata={'Software': None})
    plt.close(fig)

if __name__ == '__main__':
    arenas(); streams(); print('charts written to', OUT)
