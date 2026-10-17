<script>
  // Chart 6: public money in the largest deals per household where each arena is.
  // Each bar adds the shares of every government that pays (city or county, then state).
  import { LayerCake, Svg } from 'layercake';
  import { scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, dollars, hbar, textWidth } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const name = (j) => (j === 'New York, NY' ? 'New York City' : j.replace(/, [A-Z]{2}$/, ''));
  const MARK = { UTA: 'upper bound', ORL: 'mostly visitor taxes', SAS: 'mostly visitor taxes' };
  const data = rows.map((r) => ({ ...r, name: name(r.jurisdiction) }));
  const W = narrow ? NARROW : WIDE;
  const lw = narrow ? 0 : Math.ceil(Math.max(...data.map((d) => textWidth(d.name)))) + 14;
  const rowH = narrow ? 36 : 22;
  const H = 6 + data.length * rowH;
  const vmax = Math.max(...data.map((d) => d.per_household_2026));
  const xr = [lw, W - (narrow ? 70 : 190)];
  const tip = (d) =>
    `${d.name}: ${dollars(d.per_household_2026)} per household` +
    (d.parts.length > 1 ? ` (${d.parts.map((p) => `${name(p.jurisdiction)} ${dollars(p.per_household_2026)}`).join(' + ')})` : '');
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake ssr {data} xScale={scaleLinear()} xDomain={[0, vmax]} xRange={xr} containerWidth={W} containerHeight={H}>
    {#snippet children(k)}
      {@const x = k.xScale}
      <Svg viewBox="0 0 {W} {H}" {label}>
        {#each data as d, i}
          {@const bh = 12}
          {@const by = narrow ? 6 + i * rowH + 17 : 6 + i * rowH + (rowH - bh) / 2}
          {#if narrow}
            <text class="t-ink" x="0" y={6 + i * rowH + 11} font-size={FONT}>{d.name}{#if MARK[d.team]}<tspan class="t-muted">, {MARK[d.team]}</tspan>{/if}</text>
          {:else}
            <text class="t-ink" x={lw - 10} y={by + bh / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{d.name}</text>
          {/if}
          <g data-tip={tip(d)}>
            {#each d.parts as p, j}
              {@const before = d.parts.slice(0, j).reduce((a, q) => a + q.per_household_2026, 0)}
              {@const s = x(before) + (j > 0 ? 2 : 0)}
              {@const e = x(before + p.per_household_2026)}
              {#if j === d.parts.length - 1}
                <path class={p.level === 3 && d.parts.length > 1 ? 'f-public-soft' : 'f-public'} d={hbar(s, Math.max(e, s + 2), by, bh)} />
              {:else}
                <rect class={p.level === 3 && d.parts.length > 1 ? 'f-public-soft' : 'f-public'} x={s} y={by} width={Math.max(e - s, 1)} height={bh} />
              {/if}
            {/each}
          </g>
          <text class="tick t-ink" x={x(d.per_household_2026) + 6} y={by + bh / 2} dy="0.32em" font-size={FONT}>{dollars(d.per_household_2026)}{#if !narrow && MARK[d.team]}<tspan class="t-muted" dx="8">{MARK[d.team]}</tspan>{/if}</text>
        {/each}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
