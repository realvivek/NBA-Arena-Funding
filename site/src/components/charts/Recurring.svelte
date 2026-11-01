<script>
  // The money that comes due every year under deals and laws already in place: yearly payments to teams and arena
  // operators, and property-tax breaks, one stacked column per year with a segment for each of the largest payers
  // and one for the rest, the last year labeled at the right.
  import { WIDE, NARROW, FONT, money, moneyTick, vbar, textWidth, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const GROUPS = [
    { key: 'NYK', name: 'Garden', long: "Garden's tax break", cls: 'f-public-soft' },
    { key: 'IND', name: 'Indianapolis', long: 'Indianapolis', cls: 'f-orange' },
    { key: 'MIA', name: 'Miami', long: 'Miami', cls: 'f-orange-soft' },
    { key: 'NOP', name: 'New Orleans', long: 'New Orleans', cls: 'f-other' },
    { key: 'other', name: 'Others', long: 'Others', cls: 'f-private' },
  ];
  const group = (t) => (GROUPS.some((g) => g.key === t) ? t : 'other');
  const first = Math.min(...rows.map((r) => r.year));
  const last = Math.max(...rows.map((r) => r.year));
  const years = Array.from({ length: last - first + 1 }, (_, i) => first + i);
  const cell = {};
  for (const r of rows) {
    const k = `${r.year}|${group(r.team)}`;
    (cell[k] ??= { v: 0, parts: [] });
    cell[k].v += r.public_2026_m;
    cell[k].parts.push(`${TEAM_CITY[r.team]}, ${r.description.charAt(0).toLowerCase()}${r.description.slice(1)} ${money(r.public_2026_m)}`);
  }
  const total = (y) => GROUPS.reduce((a, g) => a + (cell[`${y}|${g.key}`]?.v ?? 0), 0);
  const ymax = Math.max(...years.map(total));
  const yTop = Math.ceil(ymax / 25) * 25;
  const ml = narrow ? 40 : 48, mr = narrow ? 122 : 180, mt = 28, mb = 26;
  const H = narrow ? 290 : 330;
  const step = (W - ml - mr) / years.length;
  const bw = Math.max(step * 0.72, 2);
  const x = (y) => ml + (y - first) * step + (step - bw) / 2;
  const sy = (v) => H - mb - ((H - mb - mt) * v) / yTop;
  const segs = [];
  for (const y of years) {
    let base = 0;
    const list = GROUPS.map((g) => ({ g, c: cell[`${y}|${g.key}`] })).filter((d) => d.c && d.c.v > 0);
    list.forEach((d, i) => {
      segs.push({ year: y, g: d.g, y0: base, y1: base + d.c.v, top: i === list.length - 1, tip: `${y}: ${d.c.parts.join('; ')} (2026 dollars)` });
      base += d.c.v;
    });
  }
  const ticksY = Array.from({ length: yTop / 25 + 1 }, (_, i) => i * 25);
  const ticksX = narrow ? [1984, 2000, 2025] : [1984, 1990, 2000, 2010, 2020, 2025];
  // labels for the last column, spread so none overlap
  const lastSegs = segs.filter((s) => s.year === last);
  const labels = lastSegs.map((s) => ({ s, mid: (sy(s.y0) + sy(s.y1)) / 2 })).sort((a, b) => b.mid - a.mid);
  let floor = Infinity;
  for (const l of labels) {
    l.ly = Math.min(l.mid, floor);
    floor = l.ly - 16;
  }
  const xr = x(last) + bw;
  const jump = segs.find((s) => s.year === 2015 && s.g.key === 'NYK');
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each ticksY as t}
      <line class={t === 0 ? 'baseline' : 'grid'} x1={ml} x2={xr} y1={sy(t)} y2={sy(t)} />
      <text class="tick t-muted" x={ml - 6} y={sy(t)} dy="0.32em" text-anchor="end" font-size={FONT}>{moneyTick(t)}</text>
    {/each}
    {#each ticksX as t}
      <text class="tick t-muted" x={x(t) + bw / 2} y={H - mb + 19} text-anchor="middle" font-size={FONT}>{t}</text>
    {/each}
    {#each segs as s}
      {@const ya = sy(s.y0) - (s.y0 > 0 ? 1 : 0)}
      {@const yb = sy(s.y1)}
      {#if s.top}
        <path class={s.g.cls} d={vbar(x(s.year), bw, ya, Math.min(yb, ya - 0.75), 2)} data-tip={s.tip} />
      {:else}
        <rect class={s.g.cls} x={x(s.year)} y={yb} width={bw} height={Math.max(ya - yb, 0.75)} data-tip={s.tip} />
      {/if}
    {/each}
    <!-- the year after the Garden's renovation, when its value and the break rose -->
    {#if jump && !narrow}
      {@const top = sy(total(2015))}
      <path class="ann-line" d="M{x(2015) + bw / 2},{top - 4}V{top - 22}H{x(2015) - 6}" />
      <text class="ann-text halo" x={x(2015) - 10} y={top - 33} text-anchor="end" font-size={FONT}>2015: after a renovation, the Garden's</text>
      <text class="ann-sub halo" x={x(2015) - 10} y={top - 18} text-anchor="end" font-size={FONT}>value and its tax break jump</text>
    {/if}
    <text class="ann-text" x={xr + 11} y={Math.min(...labels.map((l) => l.ly)) - 24} font-size={FONT}>{money(total(last))} in {last}</text>
    {#each labels as l}
      <path class="ann-line" d="M{xr + 2},{l.mid}H{xr + 5}V{l.ly}H{xr + 8}" />
      <text class="t-ink" x={xr + 11} y={l.ly} dy="0.32em" font-size={FONT}>{narrow ? l.s.g.name : l.s.g.long}<tspan class="t-muted" dx="5">{money(l.s.y1 - l.s.y0)}</tspan></text>
    {/each}
  </svg>
</div>
