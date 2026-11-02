<script>
  // The arenas where the public has paid the most after opening night: one bar per arena, split by kind
  // (renovations, buying the arena, yearly payments, property-tax breaks), against a tick for the public money that
  // built it. Arenas where the money after opening is the larger have their names in bold. Every arena with public
  // money after opening is drawn, largest first.
  import { WIDE, NARROW, FONT, money, moneyTick, hbar, textWidth, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const KINDS = [
    { key: 'renovation', name: 'Renovations', cls: 'f-orange' },
    { key: 'purchase', name: 'Buying the arena', cls: 'f-orange-soft' },
    { key: 'ongoing', name: 'Yearly payments', cls: 'f-aqua' },
    { key: 'tax_breaks', name: 'Property-tax breaks', cls: 'f-public-soft' },
  ];
  const data = [...rows].filter((r) => r.after_2026_m > 0).sort((a, b) => b.after_2026_m - a.after_2026_m);
  const city = (t) => TEAM_CITY[t];
  const lw = Math.ceil(Math.max(...data.map((r) => textWidth(city(r.team), FONT, 650)))) + 10;
  const x0 = lw, x1 = W - (narrow ? 50 : 112);
  const vmax = Math.ceil(Math.max(...data.map((r) => Math.max(r.after_2026_m, r.build_2026_m))) / 250) * 250;
  const sx = (v) => x0 + ((x1 - x0) * v) / vmax;
  const rowH = narrow ? 24 : 26, bh = narrow ? 11 : 13, mt = 24;
  const H = mt + data.length * rowH + 4;
  const step = narrow ? 500 : 250;
  // whole or half billions only past $1 billion, so no tick label is rounded
  const ticks = Array.from({ length: vmax / step + 1 }, (_, i) => i * step).filter((t) => t < 1000 || t % 500 === 0);
  const segs = (r) => {
    let x = x0;
    return KINDS.filter((k) => r[k.key] > 0).map((k, i, arr) => {
      const w = sx(r[k.key]) - x0;
      const s = { ...k, v: r[k.key], x, w: Math.max(w - (i < arr.length - 1 ? 1.5 : 0), 1), last: i === arr.length - 1 };
      x += w;
      return s;
    });
  };
  // the amount sits just after its bar, unless the tick for the building money is in the way, then after the tick
  const labelX = (r) => {
    const xb = sx(r.after_2026_m), xt = r.build_2026_m > 0 ? sx(r.build_2026_m) : -Infinity;
    return xt <= xb + 2 || xb + 7 + textWidth(money(r.after_2026_m), FONT) + 8 <= xt ? xb + 7 : xt + 7;
  };
  const tip = (r) =>
    `${city(r.team)}: ${money(r.after_2026_m)} of public money since the arena opened (${KINDS.filter((k) => r[k.key] > 0)
      .map((k) => `${k.name.toLowerCase()} ${money(r[k.key])}`)
      .join(', ')}), against ${r.build_2026_m > 0 ? money(r.build_2026_m) : 'no public money'} to build it (2026 dollars)`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each ticks as t}
      <line class={t === 0 ? 'baseline' : 'grid'} x1={sx(t)} x2={sx(t)} y1={mt - 6} y2={H - 2} />
      <text class="tick t-muted" x={sx(t)} y={mt - 11} text-anchor={t === 0 ? 'start' : 'middle'} font-size={FONT}>{moneyTick(t)}</text>
    {/each}
    {#each data as r, i}
      {@const y = mt + i * rowH + (rowH - bh) / 2}
      <g data-tip={tip(r)}>
        <text class={r.more_after ? 't-strong' : 't-ink'} x={lw - 10} y={y + bh / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{city(r.team)}</text>
        {#each segs(r) as s}
          {#if s.last}
            <path class={s.cls} d={hbar(s.x, s.x + s.w, y, bh, 2.5)} />
          {:else}
            <rect class={s.cls} x={s.x} y={y} width={s.w} height={bh} />
          {/if}
        {/each}
        {#if r.build_2026_m > 0}
          <!-- what the public paid to build it -->
          <rect class="f-ink" x={sx(r.build_2026_m) - 1} y={y - 3} width="2" height={bh + 6} />
        {/if}
        <text class="tick t-ink" x={labelX(r)} y={y + bh / 2} dy="0.32em" font-size={FONT}>{money(r.after_2026_m)}{#if !narrow && r.build_2026_m === 0}<tspan class="t-muted" dx="6">built privately</tspan>{/if}</text>
      </g>
    {/each}
  </svg>
</div>
