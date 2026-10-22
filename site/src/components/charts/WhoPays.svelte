<script>
  // Chart 5: public capital money by funding stream, grouped by who mostly pays.
  import { LayerCake, Svg } from 'layercake';
  import { scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, money, hbar, textWidth } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const SHORT = {
    tourist: 'Hotel and car-rental taxes',
    meals: 'Meal and ticket taxes, some pooled',
    general: 'General funds, bonds and grants',
    sales: 'Dedicated sales tax',
    tif: 'Tax increment and tax capture',
    leaserev: 'Lease-revenue bonds',
    sin: 'Alcohol and tobacco taxes',
    mixed: 'Not split by stream',
    land: 'Land',
    infra: 'Infrastructure, stream not stated',
  };
  const GROUPS = [
    { payer: 'visitors', name: 'Taxes mostly paid by visitors', cls: 'f-orange' },
    { payer: 'shared', name: 'Taxes visitors and residents share', cls: 'f-orange-soft' },
    { payer: 'residents', name: 'Taxes mostly paid by residents', cls: 'f-public' },
    { payer: 'other', name: 'Land, or not split by stream', cls: 'f-other' },
  ];
  const groups = GROUPS.map((g) => {
    const items = rows.filter((r) => r.payer === g.payer).sort((a, b) => b.public_2026_m - a.public_2026_m);
    return { ...g, items, share: items.reduce((a, r) => a + r.share_pct, 0), total: items.reduce((a, r) => a + r.public_2026_m, 0) };
  });
  const vmax = Math.max(...rows.map((r) => r.public_2026_m));
  const W = narrow ? NARROW : WIDE;
  // wide: labels left of bars; narrow: labels above bars
  const lw = narrow ? 0 : Math.ceil(Math.max(...rows.map((r) => textWidth(SHORT[r.bucket])))) + 14;
  const rowH = narrow ? 34 : 22;
  const headH = 30;
  let y = 4;
  const layout = groups.map((g) => {
    const top = y;
    y += headH;
    const items = g.items.map((r) => {
      const it = { ...r, y };
      y += rowH;
      return it;
    });
    y += 10;
    return { ...g, top, items };
  });
  const H = y;
  const xr = [lw, W - (narrow ? 58 : 70)];
  const tip = (r) => `${SHORT[r.bucket]}: ${money(r.public_2026_m)}, ${r.share_pct.toFixed(1)}% of public capital money`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake ssr data={rows} xScale={scaleLinear()} xDomain={[0, vmax]} xRange={xr} containerWidth={W} containerHeight={H}>
    {#snippet children(k)}
      {@const x = k.xScale}
      <Svg viewBox="0 0 {W} {H}" {label}>
        {#each layout as g}
          <line class="baseline" x1="0" x2={W} y1={g.top + 0.5} y2={g.top + 0.5} />
          <text class="t-strong" x="0" y={g.top + 19} font-size={FONT}>{g.name}</text>
          <text class="t-strong" x={W} y={g.top + 19} text-anchor="end" font-size={FONT}>{g.share.toFixed(1)}%</text>
          {#each g.items as r}
            {@const bh = 12}
            {@const by = narrow ? r.y + 17 : r.y + (rowH - bh) / 2}
            {#if narrow}
              <text class="t-ink" x="0" y={r.y + 11} font-size={FONT}>{SHORT[r.bucket]}</text>
            {:else}
              <text class="t-ink" x={lw - 10} y={by + bh / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{SHORT[r.bucket]}</text>
            {/if}
            <path class={g.cls} d={hbar(xr[0], Math.max(x(r.public_2026_m), xr[0] + 2), by, bh)} data-tip={tip(r)} />
            <text class="tick t-ink" x={Math.max(x(r.public_2026_m), xr[0] + 2) + 6} y={by + bh / 2} dy="0.32em" font-size={FONT}>{money(r.public_2026_m)}</text>
          {/each}
        {/each}
      </Svg>
    {/snippet}
  </LayerCake>
</div>
