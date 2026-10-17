<script>
  // Chart 10: when each current arena lease ends. Leases that end by 2036 are highlighted; open rings mark
  // arenas with public money pending.
  import { LayerCake, Svg } from 'layercake';
  import { scaleLinear, scaleBand } from 'd3-scale';
  import { WIDE, NARROW, FONT, money, textWidth, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '', cutoff = 2036 } = $props();
  const narrow = variant === 'narrow';
  const data = rows
    .filter((r) => r.term_end_year)
    .map((r) => ({ ...r, city: TEAM_CITY[r.team] }))
    .sort((a, b) => a.term_end_year - b.term_end_year || a.city.localeCompare(b.city));
  const W = narrow ? NARROW : WIDE;
  const lw = Math.ceil(Math.max(...data.map((d) => textWidth(d.city)))) + 12;
  const rowH = narrow ? 19 : 18, mt = 26;
  const H = mt + data.length * rowH + 8;
  const start = 2026, end = 2056;
  const ticks = narrow ? [2026, 2036, 2046, 2056] : [2026, 2031, 2036, 2041, 2046, 2051, 2056];
  const note = (d) =>
    d.pending_2026_m
      ? `${money(d.pending_2026_m)} pending`
      : d.new_arena_2026_m
        ? `${money(d.new_arena_2026_m)}${d.new_arena_pending_2026_m ? ` + ${money(d.new_arena_pending_2026_m)} pending` : ''} for a new arena`
        : '';
  const tip = (d) => `${d.arena}, ${d.city}: lease ends ${d.term_end_year}` + (note(d) ? `; ${note(d)}` : '');
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake
    ssr
    {data}
    x="term_end_year"
    y="team"
    xScale={scaleLinear()}
    xDomain={[start, end]}
    xRange={[lw, W - (narrow ? 64 : 210)]}
    yScale={scaleBand()}
    yDomain={data.map((d) => d.team)}
    yRange={[mt, mt + data.length * rowH]}
    containerWidth={W}
    containerHeight={H}
  >
    {#snippet children(k)}
      {@const x = k.xScale}
      {@const y = k.yScale}
      <Svg viewBox="0 0 {W} {H}" {label}>
        <rect x={x(start)} y={mt - 4} width={x(cutoff + 0.5) - x(start)} height={data.length * rowH + 8} fill="var(--public-wash)" />
        {#each ticks as t}
          <line class="grid" x1={x(t)} x2={x(t)} y1={mt - 4} y2={mt + data.length * rowH + 4} />
          <text class="tick t-muted" x={x(t)} y={mt - 10} text-anchor="middle" font-size={FONT}>{t}</text>
        {/each}
        {#each data as d}
          {@const cy = y(d.team) + rowH / 2}
          {@const soon = d.term_end_year <= cutoff}
          <text class={soon ? 't-strong' : 't-ink'} x={lw - 10} y={cy} dy="0.32em" text-anchor="end" font-size={FONT}>{d.city}</text>
          <line x1={x(start)} x2={x(d.term_end_year)} y1={cy} y2={cy} stroke={soon ? 'var(--public)' : 'var(--axis)'} stroke-width="2" />
          <circle class={soon ? 'f-public dot-ring' : 'f-other dot-ring'} cx={x(d.term_end_year)} cy={cy} r="5" data-tip={tip(d)} />
          <text class="tick t-muted" x={x(d.term_end_year) + 10} y={cy} dy="0.32em" font-size={FONT}>{d.term_end_year}{#if note(d) && !narrow}<tspan class="t-ink" dx="8">{note(d)}</tspan>{/if}</text>
        {/each}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
