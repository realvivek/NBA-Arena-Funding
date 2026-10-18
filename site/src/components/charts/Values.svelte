<script>
  // Team values against what owners paid and what the public put into each arena: for each team, the price its
  // controlling owner paid (in 2026 dollars) joined to the team's value now, and a bar for the public money in its
  // arena, all on one dollar scale. Prices that bought more or less than the team itself are left out of the line.
  import { WIDE, NARROW, FONT, money, moneyTick, textWidth, TEAM_NAME } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const short = (t) => (t === 'POR' ? 'Trail Blazers' : t === 'PHI' ? '76ers' : TEAM_NAME[t].split(' ').slice(-1)[0]);
  const data = [...rows].sort((a, b) => b.forbes_2026_b - a.forbes_2026_b || a.team.localeCompare(b.team));
  const comparable = (r) => r.price_m != null && r.price_scope !== 'not_comparable';

  const W = narrow ? NARROW : WIDE;
  const lw = Math.ceil(Math.max(...data.map((r) => textWidth(short(r.team))))) + 10;
  const x0 = lw + 8, x1 = W - (narrow ? 44 : 52);
  const vmax = Math.ceil(Math.max(...data.map((r) => r.forbes_2026_b)) / 2) * 2;
  const sx = (b) => x0 + (b / vmax) * (x1 - x0);
  const rowH = narrow ? 21 : 22, mt = 24;
  const H = mt + data.length * rowH + 6;
  const ticks = Array.from({ length: vmax / (narrow ? 4 : 2) + 1 }, (_, i) => i * (narrow ? 4 : 2));
  const tipPrice = (r) => `${TEAM_NAME[r.team]}: ${r.owner} paid ${money(r.price_m)} in ${r.price_year} (${money(r.price_2026_m)} in 2026 dollars)`;
  const tipValue = (r) => `${TEAM_NAME[r.team]}: worth ${money(r.forbes_2026_b * 1000)} (Forbes, October 2026)`;
  const tipPublic = (r) =>
    `${TEAM_NAME[r.team]}: ${money(r.public_2026_m)} of public money in the arena${r.tax_breaks_2026_m ? `, plus ${money(r.tax_breaks_2026_m)} in tax breaks` : ''} (2026 dollars)`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each ticks as t}
      <line class={t === 0 ? 'baseline' : 'grid'} x1={sx(t)} x2={sx(t)} y1={mt - 6} y2={H - 4} />
      <text class="tick t-muted" x={sx(t)} y={mt - 11} text-anchor="middle" font-size={FONT}>{moneyTick(t * 1000)}</text>
    {/each}
    {#each data as r, i}
      {@const y = mt + i * rowH + rowH / 2}
      {@const pub = r.public_2026_m + r.tax_breaks_2026_m}
      <text class="t-ink" x={lw} y={y} dy="0.32em" text-anchor="end" font-size={FONT}>{short(r.team)}</text>
      {#if pub > 0}
        <rect class="f-public" x={x0} y={y + 3} width={Math.max(sx(pub / 1000) - x0, 1.5)} height="5" rx="1.5" data-tip={tipPublic(r)} />
      {/if}
      {#if comparable(r)}
        <line class="db-line" x1={sx(r.price_2026_m / 1000)} x2={sx(r.forbes_2026_b)} y1={y - 3} y2={y - 3} />
        <circle class="db-paid" cx={sx(r.price_2026_m / 1000)} cy={y - 3} r="4" data-tip={tipPrice(r)} />
      {/if}
      <circle class="f-orange db-now" cx={sx(r.forbes_2026_b)} cy={y - 3} r="5" data-tip={tipValue(r)} />
      <text class="tick t-ink" x={sx(r.forbes_2026_b) + 9} y={y - 3} dy="0.32em" font-size={FONT}>{money(r.forbes_2026_b * 1000, 1)}</text>
    {/each}
  </svg>
</div>
