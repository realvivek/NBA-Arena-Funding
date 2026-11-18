<script>
  // Stadiums and arenas in Las Vegas: what each cost and the public's part, in 2026 dollars, one row each. The
  // ballpark's public part is outlined because it is the cap in the 2023 law, not money paid out. The proposed NBA
  // arena is drawn as the range of its reported cost, hatched to the low end and outlined to the high end, because
  // nothing about who pays has been decided.
  import { WIDE, NARROW, FONT, money, moneyTick, hbar } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const data = rows;
  const top = (r) => r.cost_max_2026_m ?? r.cost_2026_m;
  const vmax = Math.ceil(Math.max(...data.map(top)) / 1000) * 1000;
  const x0 = 0, x1 = W - (narrow ? 6 : 10);
  const sx = (v) => x0 + ((x1 - x0) * v) / vmax;
  const ticks = Array.from({ length: vmax / 1000 + 1 }, (_, i) => i * 1000);
  const rowH = narrow ? 62 : 58, bh = 12, mt = 26;
  const H = mt + data.length * rowH;
  // "under construction, opening 2028" -> "opening 2028"; "proposed; no site chosen" -> "proposed"
  const brief = (s) => (s.includes('open') ? s.slice(s.search(/open/)) : s.split(/[;,]/)[0]);
  const meta = (r) => (narrow ? `${r.league}, ${brief(r.status)}` : `${r.league}, ${r.team}, ${r.status}`);
  const summary = (r) =>
    r.public_basis === 'none asked'
      ? `${money(r.cost_2026_m, 0)} to ${money(r.cost_max_2026_m, 0)}; no public money asked for yet`
      : r.public_basis === 'cap'
        ? `Up to ${money(r.public_2026_m)} public, of ${money(r.cost_2026_m)}`
        : r.public_2026_m > 0
          ? `${money(r.public_2026_m)} public, ${Math.round(r.public_share_pct)}% of ${money(r.cost_2026_m)}`
          : `${money(r.cost_2026_m)}, all private`;
  const decided = (r) =>
    r.decided === 'Private' ? 'Built without public money' : r.decided === 'Not decided' ? 'Nothing decided' : `Approved by the ${r.decided}`;
  const tip = (r) => `${r.venue} (${r.league}, ${r.team}), ${r.status}: ${summary(r)}, 2026 dollars. ${decided(r)}`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    <defs>
      <!-- diagonal hatching: a cost whose split between public and private money is not known -->
      <pattern id="lv-hatch-{variant}" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <line class="hatch" x1="0" y1="0" x2="0" y2="5" />
      </pattern>
    </defs>
    {#each ticks as t}
      <line class={t === 0 ? 'baseline' : 'grid'} x1={sx(t)} x2={sx(t)} y1={mt - 6} y2={H - 4} />
      <text class="tick t-muted" x={sx(t)} y={mt - 12} text-anchor={t === 0 ? 'start' : t === vmax ? 'end' : 'middle'} font-size={FONT}>{moneyTick(t)}</text>
    {/each}
    {#each data as r, i}
      {@const y = mt + i * rowH}
      {@const by = y + 38}
      {@const xp = sx(r.public_2026_m ?? 0)}
      {@const xe = sx(r.cost_2026_m)}
      <g data-tip={tip(r)}>
        <text class="t-strong halo" x="0" y={y + 14} font-size={FONT}>{r.venue}<tspan class="t-muted" font-weight="400" dx="6">{meta(r)}</tspan></text>
        <text class="t-ink halo" x="0" y={y + 30} font-size={FONT}>{summary(r)}</text>
        {#if r.public_basis === 'none asked'}
          <!-- the low end of the reported cost, hatched, and the rest of the range to the high end, outlined only -->
          <rect class="f-range" x={x0 + 0.6} y={by + 0.6} width={xe - x0 - 1.2} height={bh - 1.2} rx="2" fill="url(#lv-hatch-{variant})" />
          <rect class="f-range-end" x={xe + 0.6} y={by + 0.6} width={sx(r.cost_max_2026_m) - xe - 1.2} height={bh - 1.2} rx="2" />
        {:else}
          {#if r.public_2026_m > 0}
            <rect class={r.public_basis === 'cap' ? 'f-pending' : 'f-public'} x={x0 + (r.public_basis === 'cap' ? 0.75 : 0)} y={by + (r.public_basis === 'cap' ? 0.75 : 0)} width={xp - x0 - (r.public_basis === 'cap' ? 1.5 : 0)} height={bh - (r.public_basis === 'cap' ? 1.5 : 0)} />
          {/if}
          <path class="f-private" d={hbar(r.public_2026_m > 0 ? xp + 2 : x0, xe, by, bh, 2.5)} />
        {/if}
        <rect x={x0} y={y} width={W} height={rowH - 4} fill="transparent" />
      </g>
    {/each}
  </svg>
</div>
