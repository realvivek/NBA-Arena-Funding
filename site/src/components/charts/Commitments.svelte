<script>
  // Public payments under deals and laws already in force, one row each, from the year the deal or law took effect
  // to the year it ends, on one time axis; the part before 2026 lighter, the part still to come darker. A payment
  // with no end date runs to the right edge.
  import { WIDE, NARROW, FONT, textWidth, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const NOW = 2026;
  const t0 = 1980, t1 = 2060;
  const data = [...rows].sort((a, b) => (b.end ?? 9999) - (a.end ?? 9999) || a.start - b.start);
  const ml = 0, mr = narrow ? 4 : 8;
  const sx = (y) => ml + ((W - ml - mr) * (y - t0)) / (t1 - t0);
  const rowH = narrow ? 58 : 44;
  const mt = 26;
  const H = mt + data.length * rowH + 6;
  const ticks = narrow ? [1980, 2000, 2040, 2060] : [1980, 1990, 2000, 2010, 2040, 2050, 2060];
  const city = (t) => (t === 'NYK' ? 'New York' : TEAM_CITY[t]);
  // the end year goes after the bar when it fits there
  const fitsRight = (r) => sx(r.end ?? t1) + 6 + textWidth(`to ${r.end}`) <= W;
  const tip = (r) => `${city(r.team)}: ${r.what}, ${r.start}${r.end ? `-${r.end}` : ', no end date'}; ${r.amount}. Decided by: ${r.decided}`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each ticks as t}
      <line class="grid" x1={sx(t)} x2={sx(t)} y1={mt - 6} y2={H - 4} />
      <text class="tick t-muted" x={sx(t)} y={mt - 12} text-anchor={t === t0 ? 'start' : t === t1 ? 'end' : 'middle'} font-size={FONT}>{t}</text>
    {/each}
    <!-- now: a tick at the top and a mark across each bar, so the line never crosses the row text -->
    <text class="tick t-strong" x={sx(NOW)} y={mt - 12} text-anchor="middle" font-size={FONT}>{NOW}</text>
    {#each data as r, i}
      {@const top = mt + i * rowH}
      {@const by = top + (narrow ? 34 : 20)}
      {@const xe = sx(r.end ?? t1)}
      <g data-tip={tip(r)}>
        {#if narrow}
          <text class="t-strong halo" x="0" y={top + 13} font-size={FONT}>{city(r.team)}<tspan class="t-muted" font-weight="400" dx="6">{!r.end ? `${r.amount}, no end date` : fitsRight(r) ? r.amount : `${r.amount}, to ${r.end}`}</tspan></text>
          <text class="t-muted halo" x="0" y={top + 28} font-size={FONT}>{r.what}</text>
        {:else}
          <text class="t-strong halo" x="0" y={top + 12} font-size={FONT}>{city(r.team)}<tspan class="t-ink" font-weight="400" dx="6">{r.what}</tspan><tspan class="t-muted" font-weight="400" dx="8">{r.amount}</tspan></text>
        {/if}
        <!-- before now: lighter; still to come: darker -->
        <rect class="f-orange-soft" x={sx(r.start)} y={by} width={Math.max(sx(Math.min(NOW, r.end ?? t1)) - sx(r.start), 1)} height="10" rx="2" />
        {#if (r.end ?? t1) > NOW}
          <rect class="f-orange" x={sx(NOW)} y={by} width={xe - sx(NOW)} height="10" rx="2" />
        {/if}
        <line class="ann-line" x1={sx(NOW)} x2={sx(NOW)} y1={by - 4} y2={by + 14} />
        {#if r.end && fitsRight(r)}
          <text class="tick t-ink halo" x={xe + 6} y={by + 9} font-size={FONT}>to {r.end}</text>
        {:else if r.end && !narrow}
          <!-- on wide screens, above the bar's end when it does not fit after it; on phones the year joins the row's first line -->
          <text class="tick t-ink halo" x={xe} y={by - 4} text-anchor="end" font-size={FONT}>to {r.end}</text>
        {:else if !narrow}
          <text class="tick t-ink" x={sx(t1) - 2} y={by - 4} text-anchor="end" font-size={FONT}>no end date</text>
        {/if}
      </g>
    {/each}
  </svg>
</div>
