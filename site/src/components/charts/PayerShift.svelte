<script>
  // Who mostly pays, before and since 2014: one bar per period, split into taxes mostly paid by visitors, taxes
  // visitors and residents share, taxes mostly paid by residents, and land or money not split by stream. Labels sit
  // under their segments; a label that does not fit is left to the tooltip and the table.
  import { WIDE, NARROW, FONT, money, textWidth } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const ORDER = ['visitors', 'shared', 'residents', 'other'];
  const CLS = { visitors: 'f-orange', shared: 'f-orange-soft', residents: 'f-public', other: 'f-other' };
  const WORD = { visitors: 'visitors', shared: 'shared', residents: 'residents', other: 'not split' };
  const PAID = { visitors: 'taxes mostly paid by visitors', shared: 'meal and ticket taxes visitors and residents share', residents: 'taxes mostly paid by residents', other: 'land, or money not split by stream' };
  const NAME = { before: 'Before 2014', since: 'Since 2014' };
  const W = narrow ? NARROW : WIDE;
  const x0 = 0, x1 = W - 2, gap = 2, bh = narrow ? 22 : 26;
  const periods = ['before', 'since'].map((p) => {
    const parts = ORDER.map((payer) => rows.find((r) => r.period === p && r.payer === payer)).filter(Boolean);
    const total = parts.reduce((a, r) => a + r.public_2026_m, 0);
    let x = x0;
    const segs = parts.map((r, i) => {
      const w = ((x1 - x0) * r.public_2026_m) / total;
      const s = { ...r, x, w: Math.max(w - (i < parts.length - 1 ? gap : 0), 1) };
      x += w;
      return s;
    });
    // labels under the segments, left to right; a label pushed by the one before it slides right while it still
    // starts inside its own segment, and the last one is right-aligned at the bar's end when it is narrow
    let right = -Infinity;
    for (const s of segs) {
      const txt = narrow ? `${Math.round(s.share_pct)}%` : `${Math.round(s.share_pct)}% ${WORD[s.payer]}`;
      const tw = textWidth(txt);
      const last = s === segs[segs.length - 1];
      let lx = Math.max(s.x, right + 8), anchor = 'start';
      if (last && lx + tw > x1) {
        lx = x1;
        anchor = 'end';
      }
      const left = anchor === 'end' ? lx - tw : lx;
      const inside = anchor === 'end' || lx <= s.x + Math.max(s.w - 12, 0);
      s.label = left >= right + 8 && inside ? { txt, lx, anchor } : null;
      if (s.label) right = left + tw;
    }
    return { p, total, segs };
  });
  const rowH = bh + 64, mt = 2;
  const H = mt + periods.length * rowH - 16;
  const tip = (s, p) => `${NAME[p]}: ${money(s.public_2026_m)} from ${PAID[s.payer]}, ${s.share_pct.toFixed(1)}%`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each periods as g, i}
      {@const top = mt + i * rowH}
      <text class="t-strong" x="0" y={top + 14} font-size={FONT}>{NAME[g.p]}</text>
      <text class="tick t-muted" x={x1} y={top + 14} text-anchor="end" font-size={FONT}>{money(g.total)} in all</text>
      {#each g.segs as s}
        <rect class={CLS[s.payer]} x={s.x} y={top + 24} width={s.w} height={bh} rx="3" data-tip={tip(s, g.p)} />
        {#if s.label}
          <text class="tick t-ink" x={s.label.lx} y={top + 24 + bh + 17} text-anchor={s.label.anchor} font-size={FONT}>{s.label.txt}</text>
        {/if}
      {/each}
    {/each}
  </svg>
</div>
