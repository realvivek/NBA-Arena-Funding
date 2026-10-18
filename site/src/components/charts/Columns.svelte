<script>
  // Simple column charts for the reference pages: Salt Lake City's monthly arena tax and the Wisconsin Center
  // District's yearly taxes by source (stacked).
  import { LayerCake, Svg } from 'layercake';
  import { scaleBand, scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, vbar, dollars } from '../../lib/chart';

  let { rows, kind = 'slc', variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const H = narrow ? 220 : 260;
  const ml = narrow ? 50 : 54, mr = 6, mt = 12, mb = 33;
  const SERIES = kind === 'wcd'
    ? [
        { key: 'room', cls: 'f-public', name: 'Hotel rooms', get: (r) => Number(r.basic_room) + Number(r.additional_room) },
        { key: 'fb', cls: 'f-orange', name: 'Food and drink', get: (r) => Number(r.food_beverage) },
        { key: 'car', cls: 'f-aqua', name: 'Car rentals', get: (r) => Number(r.car_rental) },
      ]
    : [{ key: 'usd', cls: 'f-public', name: 'Distribution', get: (r) => r.usd }];
  const data = (kind === 'wcd' ? rows.filter((r) => r.basic_room) : rows).map((r) => ({
    name: kind === 'wcd' ? r.year : r.month,
    parts: SERIES.map((s) => ({ ...s, v: s.get(r) })),
  }));
  const vmax = Math.max(...data.map((d) => d.parts.reduce((a, p) => a + p.v, 0)));
  const fmt = (v) => (v >= 1e6 ? `$${(v / 1e6).toFixed(v >= 1e7 ? 0 : 1)}M` : v === 0 ? '$0' : `$${Math.round(v / 1e3)}K`);
  const every = kind === 'wcd' ? 1 : narrow ? 6 : 3;
  const shortName = (n) => (kind === 'wcd' ? n.replace(' Jan-Sep', '*') : n);
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake
    ssr
    {data}
    xScale={scaleBand().paddingInner(0.3)}
    xDomain={data.map((d) => d.name)}
    xRange={[ml, W - mr]}
    yScale={scaleLinear()}
    yDomain={[0, vmax]}
    yRange={[H - mb, mt]}
    yNice={true}
    containerWidth={W}
    containerHeight={H}
  >
    {#snippet children(k)}
      {@const x = k.xScale}
      {@const y = k.yScale}
      {@const bw = Math.min(x.bandwidth(), 24)}
      <Svg viewBox="0 0 {W} {H}" {label}>
        {#each y.ticks(4) as t}
          <line class={t === 0 ? 'baseline' : 'grid'} x1={ml} x2={W - mr} y1={y(t)} y2={y(t)} />
          <text class="tick t-muted" x={ml - 6} y={y(t)} dy="0.32em" text-anchor="end" font-size={FONT}>{fmt(t)}</text>
        {/each}
        {#each data as d, i}
          {@const x0 = x(d.name) + (x.bandwidth() - bw) / 2}
          {#each d.parts as p, j}
            {@const below = d.parts.slice(0, j).reduce((a, q) => a + q.v, 0)}
            {@const top = j === d.parts.length - 1}
            {#if p.v > 0}
              {#if top}
                <path class={p.cls} d={vbar(x0, bw, y(below) - (j > 0 ? 2 : 0), y(below + p.v))} data-tip={`${d.name}, ${p.name}: ${dollars(p.v)}`} />
              {:else}
                <rect class={p.cls} x={x0} width={bw} y={y(below + p.v)} height={Math.max(y(below) - y(below + p.v) - (j > 0 ? 2 : 0), 1)} data-tip={`${d.name}, ${p.name}: ${dollars(p.v)}`} />
              {/if}
            {/if}
          {/each}
          {#if i % every === 0}
            <text class="tick t-muted" x={x(d.name) + x.bandwidth() / 2} y={H - mb + 21} text-anchor="middle" font-size={FONT}>{shortName(d.name)}</text>
          {/if}
        {/each}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
