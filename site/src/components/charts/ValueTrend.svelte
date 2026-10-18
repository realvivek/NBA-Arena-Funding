<script>
  // The average NBA team value by year, from Forbes's lists, in the dollars of each year: the line, its first,
  // 2014 and last values, and a note with an arrow where the league's new media deals begin.
  import { WIDE, NARROW, FONT, money, moneyTick } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const pts = [...rows].sort((a, b) => a.year - b.year);
  const W = narrow ? NARROW : WIDE;
  const H = narrow ? 230 : 280;
  const ml = narrow ? 40 : 48, mr = narrow ? 14 : 20, mt = 26, mb = 29;
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
  const media = pts.find((p) => p.year === 2025);
  const tip = (p) => `${p.year}: ${money(p.forbes_avg_b * 1000)} (${p.basis})`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each ticksY as t}
      <line class={t === 0 ? 'baseline' : 'grid'} x1={ml} x2={W - mr} y1={sy(t)} y2={sy(t)} />
      <text class="tick t-muted" x={ml - 6} y={sy(t)} dy="0.32em" text-anchor="end" font-size={FONT}>{moneyTick(t * 1000)}</text>
    {/each}
    {#each ticksX as t, i}
      <text class="tick t-muted" x={i === ticksX.length - 1 ? W - mr : sx(t)} y={H - mb + 21} text-anchor={i === ticksX.length - 1 ? 'end' : 'middle'} font-size={FONT}>{t}</text>
    {/each}
    <path class="trend-area" d={area} />
    <path class="trend-line" d={line} />
    {#each pts as p}
      {@const shown = p === first || p === last || p === mark}
      <circle class={shown ? 'trend-dot' : 'hit'} cx={sx(p.year)} cy={sy(p.forbes_avg_b)} r={shown ? 4.5 : 9} data-tip={tip(p)} />
    {/each}
    {#if media && !narrow}
      <!-- the national media deals that began with the 2025-26 season -->
      {@const mx = sx(media.year)}
      {@const my = sy(media.forbes_avg_b)}
      <!-- the note sits in the open space left of the climb, its arrow pointing right at the 2025 value -->
      {@const nx = sx(2021.2)}
      <text class="ann-sub halo" x={nx} y={my - 6} text-anchor="end" font-size={FONT}>New national media deals</text>
      <text class="ann-sub halo" x={nx} y={my + 10} text-anchor="end" font-size={FONT}>begin with the 2025-26 season</text>
      <path class="ann-arrow" d="M{nx + 6},{my - 2} C{nx + 40},{my - 14} {mx - 40},{my - 12} {mx - 9},{my - 1}" />
      <path class="ann-arrow" d="M{mx - 16},{my - 6} L{mx - 9},{my - 1} L{mx - 17},{my + 2}" />
    {/if}
    <text class="ann-text halo" x={sx(first.year) + 8} y={sy(first.forbes_avg_b) - (narrow ? 16 : 12)} font-size={FONT}>{money(first.forbes_avg_b * 1000)} in {first.year}</text>
    {#if mark && !narrow}
      <text class="ann-sub halo" x={sx(mark.year) - 6} y={sy(mark.forbes_avg_b) - 10} text-anchor="end" font-size={FONT}>{money(mark.forbes_avg_b * 1000)} in {mark.year}</text>
    {/if}
    <text class="ann-text halo" x={sx(last.year) - 8} y={sy(last.forbes_avg_b) - 12} text-anchor="end" font-size={FONT}>{money(last.forbes_avg_b * 1000, 1)} in {last.year}</text>
  </svg>
</div>
