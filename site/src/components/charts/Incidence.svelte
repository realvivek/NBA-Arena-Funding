<script>
  // How hard the taxes behind each arena's resident-paid money fall on the poorest households. For each arena and
  // kind of tax: the share of income that kind of tax takes in the state from the poorest fifth of households, as
  // a multiple of the share it takes from the richest one percent (ITEP, Who Pays?, 7th edition). Log scale, drawn
  // from 1x (the same share for both) toward the side the tax leans; dot area shows the money. On phones each row's
  // name sits above its line.
  import { WIDE, NARROW, FONT, money, textWidth } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const data = rows.map((r) => ({ ...r, poorer: r.ratio > 1 }));
  const lw = narrow ? 0 : Math.ceil(Math.max(...data.map((d) => textWidth(`${d.city} ${d.kind}`)))) + 16;
  const mt = 50;
  const rowH = narrow ? 36 : 22;
  const H = mt + data.length * rowH + 6;
  const lo = 0.3, hi = 30;
  const xr = [lw + 10, W - (narrow ? 30 : 40)];
  const x = (v) => xr[0] + ((Math.log(v) - Math.log(lo)) / (Math.log(hi) - Math.log(lo))) * (xr[1] - xr[0]);
  const ticks = narrow ? [0.5, 1, 2, 5, 10, 20] : [0.5, 1, 2, 5, 10, 20];
  const mmax = Math.max(...data.map((d) => d.public_2026_m));
  const rad = (m) => 3 + 5 * Math.sqrt(m / mmax);
  const times = (v) => `${v >= 9.5 ? Math.round(v) : v < 1.1 ? v.toFixed(2) : v.toFixed(1)}×`;
  const tickTxt = (v) => `${v}×`;
  const cy = (i) => mt + i * rowH + (narrow ? 25 : rowH / 2);
  const one = x(1);
  const tip = (d) =>
    `${d.city}, ${d.kind}: ${money(d.public_2026_m)} of residents' arena money. In ${d.state}, this kind of tax takes ` +
    `${(100 * d.poorest_share).toFixed(1)}% of income from the poorest fifth of households and ` +
    `${(100 * d.top1_share).toFixed(1)}% from the richest one percent (${times(d.ratio)}).`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    <!-- which way each side leans, above the axis -->
    {#if narrow}
      <text class="t-muted" x="0" y="13" font-size={FONT}>Richest pay more</text>
      <text class="t-muted" x={W} y="13" text-anchor="end" font-size={FONT}>Poorest pay more</text>
    {:else}
      <text class="t-muted" x={one - 8} y="13" text-anchor="end" font-size={FONT}>Takes more from the richest</text>
      <text class="t-muted" x={one + 8} y="13" font-size={FONT}>Takes more from the poorest</text>
    {/if}
    {#each ticks as t}
      <line class={t === 1 ? 'baseline' : 'grid'} x1={x(t)} x2={x(t)} y1={mt - 12} y2={H - 4} />
      <text class="tick t-muted" x={x(t)} y={mt - 18} text-anchor="middle" font-size={FONT}>{tickTxt(t)}</text>
    {/each}
    {#each data as d, i}
      {#if narrow}
        <text class="t-ink halo" x="0" y={mt + i * rowH + 11} font-size={FONT}>{d.city}<tspan class="t-muted">, {d.kind}</tspan></text>
      {:else}
        <text class="t-ink" x={lw - 6} y={cy(i)} dy="0.32em" text-anchor="end" font-size={FONT}>{d.city} <tspan class="t-muted">{d.kind}</tspan></text>
      {/if}
      <g data-tip={tip(d)}>
        <line class={d.poorer ? 's-orange' : 's-public'} x1={one} x2={x(d.ratio)} y1={cy(i)} y2={cy(i)} />
        <circle class={(d.poorer ? 'f-orange' : 'f-public') + ' dot-ring'} cx={x(d.ratio)} cy={cy(i)} r={rad(d.public_2026_m)} />
      </g>
      <!-- the value right of the dot, or for a tax leaning toward the richest, right of the 1x line -->
      <text class="tick t-ink" x={d.poorer ? x(d.ratio) + rad(d.public_2026_m) + 5 : one + 6} y={cy(i)} dy="0.32em" font-size={FONT}>{times(d.ratio)}</text>
    {/each}
  </svg>
</div>
