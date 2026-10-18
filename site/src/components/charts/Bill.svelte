<script>
  // The lead graphic: the public's bill for the arenas, built up one kind of money at a time. Each bar starts where
  // the one above it ends, so the bars add up to the total in the last row, and every row carries its name, its
  // amount and its share. Told in steps as the reader scrolls (see the [data-step] rules in global.css): rows not
  // reached yet show as outlines, the current row is marked, and without scripts the chart rests in its last state.
  import { WIDE, NARROW, FONT, money, textWidth, hbar } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';

  const layers = [...rows].sort((a, b) => a.ord - b.ord);
  const total = layers.reduce((a, l) => a + l.public_2026_m, 0);
  const share = (v) => `${Math.round((100 * v) / total)}%`;

  const W = narrow ? NARROW : WIDE;
  // wide: names in a column at the left, amounts and shares in columns at the right
  // narrow: the name and the amount on one line, the bar under them across the full width
  const x0 = narrow ? 0 : 172;
  const x1 = narrow ? W : 532;
  const xAmt = narrow ? W : 624;
  const xShare = W;
  const head = narrow ? 22 : 26;
  const rowH = narrow ? 44 : 46;
  const bh = narrow ? 16 : 26;
  const AMT = narrow ? 15 : 18;
  const sx = (v) => x0 + ((x1 - x0) * v) / total;

  let cum = 0;
  const bars = layers.map((l, i) => {
    const a = cum;
    cum += l.public_2026_m;
    const top = head + i * rowH;
    const by = narrow ? top + 21 : top + (rowH - bh) / 2;
    return { ...l, a, b: cum, top, by };
  });
  const ruleY = head + layers.length * rowH + 8;
  const tTop = ruleY + 8;
  const tbh = narrow ? 20 : 30;
  const tby = narrow ? tTop + 21 : tTop + 6;
  const build = bars[0];
  const xb = sx(build.b);
  const brY = tby + tbh + 10;
  const H = brY + (narrow ? 34 : 30);

  const tip = (name, v) => `${name}: ${money(v)} (2026 dollars), ${share(v)} of the total`;
  const amtW = (t) => textWidth(t, AMT, 700);
  // a bracket under the total bar for each part, with its label centered under it
  const brackets = [
    { from: x0, to: xb - 1, text: `Building: ${share(build.public_2026_m)}` },
    { from: xb + 1, to: x1, text: `The rest: ${share(total - build.public_2026_m)}` },
  ];
</script>

<div class="plot billplot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    <text class="t-muted" x="0" y={head - 10} font-size={FONT}>Public money for</text>
    {#if narrow}
      <text class="t-muted" x={W} y={head - 10} font-size={FONT} text-anchor="end">2026 dollars</text>
    {:else}
      <text class="t-muted" x={xAmt} y={head - 10} font-size={FONT} text-anchor="end">2026 dollars</text>
      <text class="t-muted" x={xShare} y={head - 10} font-size={FONT} text-anchor="end">Share</text>
    {/if}

    {#each bars as r}
      {@const amt = money(r.public_2026_m)}
      <g class="bl-row bl-{r.key}" data-tip={tip(r.name, r.public_2026_m)}>
        <rect class="bl-mark" x={-6} y={r.top + 2} width={W + 12} height={rowH - 4} rx="4" />
        <path class="bl-ghost" d={hbar(sx(r.a), Math.max(sx(r.b), sx(r.a) + 2), r.by, bh)} />
        <path class="bl-solid" d={hbar(sx(r.a), Math.max(sx(r.b), sx(r.a) + 2), r.by, bh)} />
        {#if narrow}
          <text class="bl-name" x="0" y={r.top + 15} font-size={FONT}>{r.name}</text>
          <text class="bl-amt" x={xAmt} y={r.top + 15} font-size={AMT} text-anchor="end">{amt}</text>
          <text class="bl-share" x={xAmt - amtW(amt) - 8} y={r.top + 15} font-size={FONT} text-anchor="end">{share(r.public_2026_m)}</text>
        {:else}
          <text class="bl-name" x="0" y={r.by + bh / 2 + 5} font-size="15">{r.name}</text>
          <text class="bl-amt" x={xAmt} y={r.by + bh / 2 + 6} font-size={AMT} text-anchor="end">{amt}</text>
          <text class="bl-share" x={xShare} y={r.by + bh / 2 + 5} font-size={FONT} text-anchor="end">{share(r.public_2026_m)}</text>
        {/if}
      </g>
    {/each}

    <!-- each bar starts under the end of the one above it (on phones the labels sit between the bars) -->
    {#if !narrow}
      {#each bars.slice(1) as r, i}
        <path class="bl-conn" d="M{sx(r.a)},{bars[i].by + bh}V{r.by}" />
      {/each}
    {/if}
    <line class="bl-rule" x1="0" x2={W} y1={ruleY} y2={ruleY} />
    <g class="bl-row bl-total" data-tip={tip('All public money', total)}>
      <rect class="bl-mark" x={-6} y={tTop} width={W + 12} height={H - tTop} rx="4" />
      <path class="bl-ghost" d={hbar(x0, xb - 1, tby, tbh, 0)} />
      <path class="bl-ghost" d={hbar(xb + 1, x1, tby, tbh)} />
      <path class="bl-solid" d={hbar(x0, xb - 1, tby, tbh, 0)} />
      <path class="bl-solid" d={hbar(xb + 1, x1, tby, tbh)} />
      {#if narrow}
        <text class="bl-name bl-name-total" x="0" y={tTop + 15} font-size="15">All public money</text>
        <text class="bl-amt" x={xAmt} y={tTop + 15} font-size="17" text-anchor="end">{money(total)}</text>
      {:else}
        <text class="bl-name bl-name-total" x="0" y={tby + tbh / 2 + 6} font-size="16">All public money</text>
        <text class="bl-amt" x={xAmt} y={tby + tbh / 2 + 7} font-size="21" text-anchor="end">{money(total)}</text>
        <text class="bl-share" x={xShare} y={tby + tbh / 2 + 5} font-size={FONT} text-anchor="end">100%</text>
      {/if}
      {#each brackets as k}
        <path class="bl-bracket" d="M{k.from},{brY - 5}V{brY}H{k.to}V{brY - 5}" />
        <text class="bl-brlabel" x={(k.from + k.to) / 2} y={brY + 17} font-size={FONT} text-anchor="middle">{k.text}</text>
      {/each}
    </g>
    <!-- the end of the building bar, carried down to the total -->
    <path class="bl-guide" d="M{xb},{build.by + bh}V{tby + tbh}" />
  </svg>
</div>
