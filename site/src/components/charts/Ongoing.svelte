<script>
  // Chart 8: yearly public payments to teams or arena operators, one row per team, on shared scales. Each row
  // labels its largest year, so the heights can be read: above the bar on wide screens, beside the city on phones.
  import { LayerCake, Svg } from 'layercake';
  import { scaleBand, scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, money, vbar, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const byTeam = {};
  for (const r of rows) {
    const t = (byTeam[r.team] ??= { team: r.team, city: TEAM_CITY[r.team], total: 0, years: {} });
    t.total += r.public_2026_m;
    const y = (t.years[r.year] ??= { year: r.year, v: 0, parts: [] });
    y.v += r.public_2026_m;
    y.parts.push(`${r.description} ${money(r.public_2026_m)}`);
  }
  const teams = Object.values(byTeam).sort((a, b) => b.total - a.total);
  for (const t of teams) t.peak = Object.values(t.years).sort((a, b) => b.v - a.v || a.year - b.year)[0];
  const first = Math.min(...rows.map((r) => r.year));
  const last = Math.max(...rows.map((r) => r.year));
  const years = Array.from({ length: last - first + 1 }, (_, i) => first + i);
  const vmax = Math.max(...teams.flatMap((t) => Object.values(t.years).map((y) => y.v)));
  const W = narrow ? NARROW : WIDE;
  const lw = narrow ? 0 : 150;
  const rowH = narrow ? 64 : 50;
  const plotH = narrow ? 32 : 34;
  const mt = 4, mb = 22;
  const H = mt + teams.length * rowH + mb;
  const ticks = narrow ? [first, 2010, last] : [first, 2005, 2010, 2015, 2020, last];
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake
    ssr
    data={teams}
    xScale={scaleBand().paddingInner(0.25)}
    xDomain={years}
    xRange={[lw, W - 4]}
    yScale={scaleLinear()}
    yDomain={[0, vmax]}
    yRange={[plotH, 0]}
    containerWidth={W}
    containerHeight={H}
  >
    {#snippet children(k)}
      {@const x = k.xScale}
      {@const y = k.yScale}
      {@const bw = Math.min(x.bandwidth(), 12)}
      <Svg viewBox="0 0 {W} {H}" {label}>
        {#each teams as t, i}
          {@const top = mt + i * rowH + (narrow ? 22 : 10)}
          {#if narrow}
            <text class="t-ink" x="0" y={mt + i * rowH + 13} font-size={FONT} font-weight="600">{t.city}<tspan class="t-muted" font-weight="400" dx="8">{money(t.total)} in all</tspan></text>
            <text class="tick t-muted" x={W - 4} y={mt + i * rowH + 13} text-anchor="end" font-size={FONT}>peak {money(t.peak.v)}, {t.peak.year}</text>
          {:else}
            <text class="t-ink" x="0" y={top + plotH - 16} font-size={FONT} font-weight="600">{t.city}</text>
            <text class="t-muted" x="0" y={top + plotH} font-size={FONT}>{money(t.total)} in all</text>
          {/if}
          <line class="baseline" x1={lw} x2={W - 4} y1={top + plotH + 0.5} y2={top + plotH + 0.5} />
          {#each Object.values(t.years) as yr}
            <path class="f-public" d={vbar(x(yr.year) + (x.bandwidth() - bw) / 2, bw, top + plotH, top + y(yr.v))} data-tip={narrow ? undefined : `${t.city}, ${yr.year}: ${money(yr.v)}`} />
          {/each}
          {#if !narrow}
            {@const px = x(t.peak.year) + x.bandwidth() / 2}
            <text class="tick t-ink" x={px > W - 40 ? px + bw / 2 : px} y={top + y(t.peak.v) - 4} text-anchor={px > W - 40 ? 'end' : 'middle'} font-size={FONT}>{money(t.peak.v)}</text>
          {/if}
        {/each}
        {#each ticks as t}
          <text class="tick t-muted" x={t === first ? x(t) : t === last ? x(t) + x.bandwidth() : x(t) + x.bandwidth() / 2} y={H - 6} text-anchor={t === first ? "start" : t === last ? "end" : "middle"} font-size={FONT}>{t}</text>
        {/each}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
