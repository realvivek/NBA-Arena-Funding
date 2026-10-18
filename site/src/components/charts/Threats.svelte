<script>
  // Chart 9: from a relocation threat to public money in the same city (dumbbells), and how deals after a threat
  // compare with deals without one (public share). On phones each strip's name and median sit above it.
  import { LayerCake, Svg } from 'layercake';
  import { scaleLinear, scaleBand } from 'd3-scale';
  import { WIDE, NARROW, FONT, TEAM_CITY, textWidth } from '../../lib/chart';
  import { STATS } from '../../lib/copy';

  let { rows, deals = [], variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const CITY = { ...TEAM_CITY, NOH: 'New Orleans', SEA: 'Seattle', VAN: 'Vancouver', NJ: 'New Jersey' };
  const frac = (iso) => {
    const d = new Date(iso + 'T00:00:00Z');
    return d.getUTCFullYear() + (d.getUTCMonth() + d.getUTCDate() / 31) / 12;
  };
  const lags = rows
    .filter((r) => r.lag_months != null && r.threat_date && r.approval_date)
    .map((r) => ({ ...r, city: CITY[r.team.split(' ')[0]] ?? r.team, t0: frac(r.threat_date), t1: frac(r.approval_date) }))
    .sort((a, b) => a.t0 - b.t0);
  const W = narrow ? NARROW : WIDE;
  const lw = Math.ceil(Math.max(...lags.map((d) => textWidth(`${d.city} ${d.threat_date.slice(0, 4)}`)))) + 12;
  const rowH = 22, mt = 8;
  const dumbH = mt + lags.length * rowH + 26;
  const compH = narrow ? 144 : 128;
  const H = dumbH + compH;
  const x0 = 1993, x1 = 2027;
  const ticks = narrow ? [1995, 2010, 2025] : [1995, 2000, 2005, 2010, 2015, 2020, 2025];
  const months = (m) => `${m.toFixed(1)} months`;
  const tip = (d) => `${d.city}: threat ${d.threat_date}, public money approved ${d.approval_date} (${months(d.lag_months)})`;

  // comparison strips
  // medians come from the comparison the stats use (compare.py), not recomputed here
  const groups = [
    { key: 'threat', name: 'After a threat', med: STATS.threat_median_share.value },
    { key: 'no_threat', name: 'No threat', med: STATS.nothreat_median_share.value },
  ].map((g) => ({ ...g, deals: deals.filter((d) => d.grp === g.key && d.share_pct != null) }));
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake
    ssr
    data={lags}
    xScale={scaleLinear()}
    xDomain={[x0, x1]}
    xRange={[lw, W - (narrow ? 70 : 90)]}
    yScale={scaleBand()}
    yDomain={lags.map((d) => d.id)}
    yRange={[mt, mt + lags.length * rowH]}
    containerWidth={W}
    containerHeight={H}
  >
    {#snippet children(k)}
      {@const x = k.xScale}
      {@const y = k.yScale}
      <Svg viewBox="0 0 {W} {H}" {label}>
        {#each ticks as t}
          <line class="grid" x1={x(t)} x2={x(t)} y1={mt} y2={mt + lags.length * rowH} />
          <text class="tick t-muted" x={x(t)} y={mt + lags.length * rowH + 18} text-anchor="middle" font-size={FONT}>{t}</text>
        {/each}
        {#each lags as d}
          {@const cy = y(d.id) + rowH / 2}
          <text class="t-ink" x={lw - 10} y={cy} dy="0.32em" text-anchor="end" font-size={FONT}>{d.city} <tspan class="t-muted">{d.threat_date.slice(0, 4)}</tspan></text>
          <g data-tip={tip(d)}>
            <line x1={x(d.t0)} x2={x(d.t1)} y1={cy} y2={cy} stroke="var(--axis)" stroke-width="2" />
            <circle class="f-public dot-ring" cx={x(d.t1)} cy={cy} r="5" />
            <circle class="f-orange dot-ring" cx={x(d.t0)} cy={cy} r="4" />
            <rect x={x(d.t0) - 8} y={cy - 9} width={x(d.t1) - x(d.t0) + 16} height="18" fill="transparent" />
          </g>
          <text class="tick t-muted" x={x(d.t1) + 10} y={cy} dy="0.32em" font-size={FONT}>{narrow ? `${Math.round(d.lag_months)} mo.` : months(d.lag_months)}</text>
        {/each}
        {#if narrow}
          {@const top = dumbH + 14}
          {@const sx = scaleLinear().domain([0, 100]).range([6, W - 6])}
          <line class="baseline" x1="0" x2={W} y1={top - 10} y2={top - 10} />
          <text class="t-strong" x="0" y={top + 10} font-size={FONT}>Public share of each deal</text>
          {#each groups as g, i}
            {@const cy = top + 52 + i * 44}
            <text class="t-ink" x="0" y={cy - 18} font-size={FONT}>{g.name}</text>
            <text class="tick t-ink" x={W} y={cy - 18} text-anchor="end" font-size={FONT}>median {Math.round(g.med)}%</text>
            <line class="grid" x1={sx(0)} x2={sx(100)} y1={cy} y2={cy} />
            <line x1={sx(g.med)} x2={sx(g.med)} y1={cy - 11} y2={cy + 11} stroke="var(--ink)" stroke-width="2" />
            {#each g.deals as d}
              <circle class={g.key === 'threat' ? 'f-orange dot-ring' : 'f-public dot-ring'} cx={sx(d.share_pct)} cy={cy} r="5" data-tip={`${d.deal} (${d.year}): ${Math.round(d.share_pct)}% public`} />
            {/each}
          {/each}
          {#each [0, 25, 50, 75, 100] as t, j}
            <text class="tick t-muted" x={sx(t)} y={top + 52 + 44 + 26} text-anchor={j === 0 ? 'start' : j === 4 ? 'end' : 'middle'} font-size={FONT}>{t}%</text>
          {/each}
        {:else}
          {@const top = dumbH + 14}
          {@const sx = scaleLinear().domain([0, 100]).range([lw, W - 118])}
          <line class="baseline" x1="0" x2={W} y1={top - 10} y2={top - 10} />
          <text class="t-strong" x="0" y={top + 10} font-size={FONT}>Public share of each deal</text>
          {#each groups as g, i}
            {@const cy = top + 36 + i * 30}
            <text class="t-ink" x={lw - 10} y={cy} dy="0.32em" text-anchor="end" font-size={FONT}>{g.name}</text>
            <line class="grid" x1={sx(0)} x2={sx(100)} y1={cy} y2={cy} />
            <line x1={sx(g.med)} x2={sx(g.med)} y1={cy - 11} y2={cy + 11} stroke="var(--ink)" stroke-width="2" />
            {#each g.deals as d}
              <circle class={g.key === 'threat' ? 'f-orange dot-ring' : 'f-public dot-ring'} cx={sx(d.share_pct)} cy={cy} r="5" data-tip={`${d.deal} (${d.year}): ${Math.round(d.share_pct)}% public`} />
            {/each}
            <text class="tick t-ink" x={W} y={cy} dy="0.32em" text-anchor="end" font-size={FONT}>median {Math.round(g.med)}%</text>
          {/each}
          {#each [0, 25, 50, 75, 100] as t}
            <text class="tick t-muted" x={sx(t)} y={top + 36 + 2 * 30 + 4} text-anchor="middle" font-size={FONT}>{t}%</text>
          {/each}
        {/if}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
