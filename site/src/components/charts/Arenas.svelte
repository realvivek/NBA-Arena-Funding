<script>
  // Chart 2: every arena, public money (plus tax breaks) and private money, sorted by public money.
  import { LayerCake, Svg } from 'layercake';
  import { scaleBand, scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, money, moneyTick, hbar, textWidth, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();

  const data = rows.map((r) => ({
    ...r,
    name: TEAM_CITY[r.team],
    total: r.public_2026_m + r.tax_breaks_2026_m + r.private_2026_m,
  }));
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const ml = Math.ceil(Math.max(...data.map((d) => textWidth(d.name)))) + 12;
  const mr = narrow ? 44 : 60;
  const rowH = narrow ? 17 : 18;
  const mt = 30;
  const H = mt + data.length * rowH + 6;
  const xmax = Math.ceil(Math.max(...data.map((d) => d.total)) / 500) * 500;
  const ticks = narrow ? [0, 1000, 2000, 3000] : [0, 500, 1000, 1500, 2000, 2500, 3000, 3500];
  const x0 = scaleLinear().domain([0, xmax]).range([ml, W - mr]);
  const tip = (d) =>
    `${d.arena}, ${d.name}: ${money(d.public_2026_m)} public` +
    (d.tax_breaks_2026_m ? ` plus ${money(d.tax_breaks_2026_m)} in tax breaks` : '') +
    `, ${money(d.private_2026_m)} private (${Math.round(d.public_share_pct)}% public)`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake
    ssr
    {data}
    x="total"
    y="team"
    xScale={scaleLinear()}
    xDomain={[0, xmax]}
    xRange={[ml, W - mr]}
    yScale={scaleBand().paddingInner(0.3)}
    yDomain={data.map((d) => d.team)}
    yRange={[mt, H - 6]}
    containerWidth={W}
    containerHeight={H}
  >
    {#snippet children(k)}
      {@const x = k.xScale}
      {@const y = k.yScale}
      {@const bh = Math.min(y.bandwidth(), 12)}
      <Svg viewBox="0 0 {W} {H}" {label}>
        {#each ticks.filter((t) => t <= xmax && x0(t) < W - mr - 14) as t}
          <line class={t === 0 ? 'baseline' : 'grid'} x1={x(t)} x2={x(t)} y1={mt - 6} y2={H - 6} />
          <text class="tick t-muted" x={x(t)} y={mt - 12} text-anchor={t === 0 ? 'start' : 'middle'} font-size={FONT}>{moneyTick(t)}</text>
        {/each}
        <text class="t-muted" x={W} y={mt - 12} text-anchor="end" font-size={FONT}>Public share</text>
        {#each data as d}
          {@const y0 = y(d.team) + (y.bandwidth() - bh) / 2}
          {@const xp = x(d.public_2026_m)}
          {@const xt = x(d.public_2026_m + d.tax_breaks_2026_m)}
          {@const xe = x(d.total)}
          <text class="t-ink" x={ml - 8} y={y0 + bh / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{d.name}</text>
          <g data-tip={narrow ? undefined : tip(d)}>
            {#if d.public_2026_m > 0}
              <rect class="f-public" x={ml} y={y0} width={Math.max(xp - ml, 1)} height={bh} />
            {/if}
            {#if d.tax_breaks_2026_m > 0}
              <rect class="f-public-soft" x={xp + (d.public_2026_m > 0 ? 2 : 0)} y={y0} width={Math.max(xt - xp - 2, 1)} height={bh} />
            {/if}
            {#if d.private_2026_m > 0}
              {@const s = d.public_2026_m + d.tax_breaks_2026_m > 0 ? xt + 2 : ml}
              <path class="f-private" d={hbar(s, Math.max(xe, s + 2), y0, bh)} />
            {/if}
            <rect x={ml} y={y0 - 3} width={Math.max(xe - ml, 24)} height={bh + 6} fill="transparent" />
          </g>
          <text class="tick t-ink" x={W} y={y0 + bh / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{Math.round(d.public_share_pct)}%</text>
        {/each}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
