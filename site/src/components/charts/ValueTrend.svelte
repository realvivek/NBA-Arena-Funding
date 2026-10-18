<script>
  // The average NBA team value by year, from Forbes's lists, in the dollars of each year.
  import { WIDE, NARROW, FONT, money, moneyTick } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const pts = [...rows].sort((a, b) => a.year - b.year);
  const W = narrow ? NARROW : WIDE;
  const H = narrow ? 230 : 280;
  const ml = narrow ? 40 : 48, mr = narrow ? 14 : 20, mt = 26, mb = 26;
  const t0 = pts[0].year, t1 = pts[pts.length - 1].year;
  const vmax = Math.ceil(Math.max(...pts.map((p) => p.forbes_avg_b)));
  const sx = (t) => ml + ((t - t0) / (t1 - t0)) * (W - ml - mr);
  const sy = (v) => H - mb - (v / vmax) * (H - mb - mt);
  const step = narrow ? 2 : 1;
  const ticksY = Array.from({ length: Math.floor(vmax / step) + 1 }, (_, i) => i * step);
  const ticksX = narrow ? [2003, 2014, 2026] : [2003, 2007, 2011, 2014, 2018, 2022, 2026];
  const line = pts.map((p, i) => `${i ? 'L' : 'M'}${sx(p.year).toFixed(1)},${sy(p.forbes_avg_b).toFixed(1)}`).join('');
  const area = `${line}L${sx(t1).toFixed(1)},${sy(0)}L${sx(t0).toFixed(1)},${sy(0)}Z`;
  const first = pts[0], last = pts[pts.length - 1];
  const mark = pts.find((p) => p.year === 2014);
  const tip = (p) => `${p.year}: ${money(p.forbes_avg_b * 1000)} (${p.basis})`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each ticksY as t}
      <line class={t === 0 ? 'baseline' : 'grid'} x1={ml} x2={W - mr} y1={sy(t)} y2={sy(t)} />
      <text class="tick t-muted" x={ml - 6} y={sy(t)} dy="0.32em" text-anchor="end" font-size={FONT}>{moneyTick(t * 1000)}</text>
    {/each}
    {#each ticksX as t, i}
      <text class="tick t-muted" x={i === ticksX.length - 1 ? W - mr : sx(t)} y={H - mb + 18} text-anchor={i === ticksX.length - 1 ? 'end' : 'middle'} font-size={FONT}>{t}</text>
    {/each}
    <path class="trend-area" d={area} />
    <path class="trend-line" d={line} />
    {#each pts as p}
      <circle class="trend-dot" cx={sx(p.year)} cy={sy(p.forbes_avg_b)} r="3.5" data-tip={tip(p)} />
    {/each}
    <text class="ann-text halo" x={sx(first.year) + 8} y={sy(first.forbes_avg_b) - 12} font-size={FONT}>{money(first.forbes_avg_b * 1000)} in {first.year}</text>
    {#if mark && !narrow}
      <text class="ann-sub halo" x={sx(mark.year) - 6} y={sy(mark.forbes_avg_b) - 10} text-anchor="end" font-size={FONT}>{money(mark.forbes_avg_b * 1000)} in {mark.year}</text>
    {/if}
    <text class="ann-text halo" x={sx(last.year) - 8} y={sy(last.forbes_avg_b) - 12} text-anchor="end" font-size={FONT}>{money(last.forbes_avg_b * 1000, 1)} in {last.year}</text>
  </svg>
</div>
