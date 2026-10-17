<script>
  // Chart 7: the United Center's property-tax bills under the 1989 formula, the estimated bill without it,
  // and the bills after it ended. Nominal dollars.
  import { LayerCake, Svg } from 'layercake';
  import { scaleLinear } from 'd3-scale';
  import { line, area } from 'd3-shape';
  import { WIDE, NARROW, FONT } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const H = narrow ? 250 : 300;
  const ml = narrow ? 44 : 50, mr = narrow ? 8 : 130, mt = 16, mb = 28;
  const formula = rows.filter((r) => r.period === 'formula');
  const all = rows;
  const lastFormula = Math.max(...formula.map((r) => r.tax_year));
  const first = Math.min(...all.map((r) => r.tax_year));
  const last = Math.max(...all.map((r) => r.tax_year));
  const ymax = Math.ceil(Math.max(...all.map((r) => Math.max(r.paid_m, r.without_formula_m ?? 0))) / 2) * 2;
  const ticksX = narrow ? [first, 2010, lastFormula, last] : [first, 2005, 2010, 2015, 2020, last];
  const m = (v) => (v === 0 ? '$0' : `$${v}M`);
  const tipPaid = (r) => `${r.tax_year}: bill $${r.paid_m.toFixed(1)}M` + (r.without_formula_m ? `; without the formula about $${r.without_formula_m.toFixed(1)}M` : '');
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake
    ssr
    data={all}
    x="tax_year"
    y="paid_m"
    xScale={scaleLinear()}
    xDomain={[first, last]}
    xRange={[ml, W - mr]}
    yScale={scaleLinear()}
    yDomain={[0, ymax]}
    yRange={[H - mb, mt]}
    containerWidth={W}
    containerHeight={H}
  >
    {#snippet children(k)}
      {@const x = k.xScale}
      {@const y = k.yScale}
      {@const gap = area().x((d) => x(d.tax_year)).y0((d) => y(d.paid_m)).y1((d) => y(d.without_formula_m))(formula)}
      {@const paid = line().x((d) => x(d.tax_year)).y((d) => y(d.paid_m))(all)}
      {@const without = line().x((d) => x(d.tax_year)).y((d) => y(d.without_formula_m))(formula)}
      {@const xEnd = (x(lastFormula) + x(lastFormula + 1)) / 2}
      <Svg viewBox="0 0 {W} {H}" {label}>
        {#each y.ticks(narrow ? 3 : 5) as t}
          <line class={t === 0 ? 'baseline' : 'grid'} x1={ml} x2={W - mr} y1={y(t)} y2={y(t)} />
          <text class="tick t-muted" x={ml - 6} y={y(t)} dy="0.32em" text-anchor="end" font-size={FONT}>{m(t)}</text>
        {/each}
        {#each ticksX as t}
          <text class="tick t-muted" x={x(t)} y={H - mb + 18} text-anchor={t === first ? 'start' : t === last ? 'end' : 'middle'} font-size={FONT}>{t}</text>
        {/each}
        <path class="area-public" d={gap} />
        <line x1={xEnd} x2={xEnd} y1={mt} y2={H - mb} stroke="var(--axis)" />
        <text class="t-muted" x={xEnd - 6} y={mt + 4} dy="0.7em" text-anchor="end" font-size={FONT}>Formula ends</text>
        <path class="s-other" d={without} />
        <path class="s-public" d={paid} />
        {#each all as r}
          <circle cx={x(r.tax_year)} cy={y(r.paid_m)} r="12" fill="transparent" data-tip={tipPaid(r)} />
        {/each}
        {@const lf = formula.find((r) => r.tax_year === lastFormula)}
        {@const la = all.at(-1)}
        <circle class="f-public dot-ring" cx={x(la.tax_year)} cy={y(la.paid_m)} r="4" />
        <circle cx={x(lf.tax_year)} cy={y(lf.without_formula_m)} r="4" fill="var(--other)" class="dot-ring" />
        {#if !narrow}
          <text class="t-ink" x={x(la.tax_year) + 10} y={y(la.paid_m)} dy="0.32em" font-size={FONT}>Bill paid</text>
          <text class="t-ink" x={x(lf.tax_year) - 8} y={y(lf.without_formula_m) - 12} text-anchor="end" font-size={FONT}>Estimated bill without the formula</text>
          <text class="t-muted" x={x(2008)} y={(y(formula.find((r) => r.tax_year === 2008).paid_m) + y(formula.find((r) => r.tax_year === 2008).without_formula_m)) / 2} dy="0.32em" text-anchor="middle" font-size={FONT}>Taxes not paid</text>
        {/if}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
