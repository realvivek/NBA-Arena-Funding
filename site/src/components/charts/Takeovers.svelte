<script>
  // Chart 4: arenas built mainly with private money, then bought or rebuilt with public money, one lifeline each.
  // The first circle is the arena's construction, sized by what it cost, with the public share as a blue wedge;
  // the later circles are public money to buy or renovate it, at the year it came (pending money dashed). Circles
  // share one area scale, so a later deal can be read against what the building cost. Deals within three years of
  // each other are drawn as one circle.
  import { WIDE, NARROW, FONT, money, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';

  const teams = [...new Set(rows.map((r) => r.team))].map((team) => {
    const rs = rows.filter((r) => r.team === team);
    const con = rs.find((r) => r.kind === 'construction');
    const later = rs.filter((r) => r.kind !== 'construction' && r.public_2026_m > 0).sort((a, b) => a.year - b.year);
    const clusters = [];
    for (const r of later) {
      const c = clusters[clusters.length - 1];
      if (c && r.year - c.y1 <= 3) {
        c.y1 = r.year;
        c.items.push(r);
      } else clusters.push({ y0: r.year, y1: r.year, items: [r] });
    }
    for (const c of clusters) {
      c.counted = c.items.filter((r) => r.core).reduce((a, r) => a + r.public_2026_m, 0);
      c.pending = c.items.filter((r) => !r.core).reduce((a, r) => a + r.public_2026_m, 0);
      c.year = (c.y0 + c.y1) / 2;
      c.when = c.y0 === c.y1 ? `${c.y0}` : `${c.y0}-${String(c.y1).slice(2)}`;
    }
    const cost = con.public_2026_m + con.private_2026_m;
    return {
      team,
      city: TEAM_CITY[team],
      arena: con.arena,
      opened: con.opened,
      cost,
      share: cost > 0 ? con.public_2026_m / cost : 0,
      clusters,
      counted: clusters.reduce((a, c) => a + c.counted, 0),
      pending: clusters.reduce((a, c) => a + c.pending, 0),
    };
  });
  teams.sort((a, b) => b.counted + b.pending - (a.counted + a.pending));

  const vmax = Math.max(...teams.flatMap((t) => [t.cost, ...t.clusters.map((c) => c.counted + c.pending)]));
  const Y0 = 1985, Y1 = 2030;
  const W = narrow ? NARROW : WIDE;
  const rmax = narrow ? 14 : 21;
  const r = (v) => (v > 0 ? Math.max(2.5, rmax * Math.sqrt(v / vmax)) : 0);
  const lw = narrow ? 0 : 132;
  const rw = narrow ? 64 : 112;
  const tx0 = lw + (narrow ? 14 : 22);
  const tx1 = W - rw - (narrow ? 8 : 24);
  const xs = (y) => tx0 + ((y - Y0) / (Y1 - Y0)) * (tx1 - tx0);
  const mt = narrow ? 6 : 30;
  const rowH = 86;
  const lineY = narrow ? 46 : 44; // the lifeline's height within a row
  const H = mt + teams.length * rowH + 22;
  const ticks = [1990, 2000, 2010, 2020];
  const pct = (v) => `${Math.round(100 * v)}%`;
  // year labels go under their circles, or over them when they would run into the previous label
  const charW = 7.6;
  for (const t of teams) {
    let prevRight = -Infinity;
    for (const c of t.clusters) {
      const half = (c.when.length * charW) / 2;
      const x = xs(c.year);
      c.above = x - half < prevRight + 8;
      if (!c.above) prevRight = x + half;
    }
  }

  // a wedge for the public share of a circle, from twelve o'clock clockwise
  function wedge(cx, cy, rr, s) {
    if (s <= 0) return '';
    if (s >= 0.999) return `M${cx - rr},${cy}a${rr},${rr} 0 1,0 ${2 * rr},0a${rr},${rr} 0 1,0 ${-2 * rr},0Z`;
    const a = s * 2 * Math.PI;
    const x = cx + rr * Math.sin(a), y = cy - rr * Math.cos(a);
    return `M${cx},${cy}L${cx},${cy - rr}A${rr},${rr} 0 ${a > Math.PI ? 1 : 0},1 ${x},${y}Z`;
  }
  const tipBuilt = (t) => `${t.arena}, opened ${t.opened}: ${money(t.cost)} spent to build it, counting public land and site money, ${pct(t.share)} public (2026 dollars)`;
  const tipLater = (t, c) =>
    `${t.arena}, ${c.when}: ` +
    c.items.map((i) => `${i.description.toLowerCase()} ${money(i.public_2026_m)}${i.core ? '' : ' (pending)'}`).join('; ') +
    ' (public money, 2026 dollars)';
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each ticks as t}
      <line class="grid" x1={xs(t)} x2={xs(t)} y1={mt} y2={H - 20} />
      <text class="tick t-muted" x={xs(t)} y={H - 5} text-anchor="middle" font-size={FONT}>{t}</text>
    {/each}
    {#if !narrow}
      <text class="t-muted" x={W - 2} y={mt - 18} text-anchor="end" font-size={FONT}>Public money later</text>
    {/if}
    {#each teams as t, i}
      {@const y0 = mt + i * rowH}
      {@const cy = y0 + lineY}
      {@const last = t.clusters.length ? xs(t.clusters[t.clusters.length - 1].year) : xs(t.opened)}
      {@const cr = r(t.cost)}
      {#if narrow}
        <text class="t-ink" x="0" y={y0 + 12} font-size={FONT} font-weight="600">{t.city}<tspan class="t-muted" font-weight="400" dx="5">opened {t.opened}, {money(t.cost)} to build</tspan></text>
      {:else}
        <text class="t-ink" x="0" y={cy - 4} font-size={FONT} font-weight="600">{t.city}</text>
        <text class="t-muted" x="0" y={cy + 12} font-size={FONT}>opened {t.opened}</text>
      {/if}
      <line class="life" x1={xs(t.opened)} x2={last} y1={cy} y2={cy} />
      <g data-tip={tipBuilt(t)}>
        <circle class="f-private dot-ring" cx={xs(t.opened)} cy={cy} r={cr} />
        {#if t.share > 0}<path class="f-public" d={wedge(xs(t.opened), cy, cr, t.share)} />{/if}
      </g>
      {#if !narrow}
        <text class="t-muted" x={xs(t.opened)} y={cy - cr - 6} text-anchor="middle" font-size={FONT}>{pct(t.share)} public</text>
      {/if}
      {#each t.clusters as c}
        {@const cx = xs(c.year)}
        {@const ro = r(c.counted + c.pending)}
        {@const ri = r(c.counted)}
        <g data-tip={tipLater(t, c)}>
          {#if c.pending > 0}
            <circle class="f-pending dash" cx={cx} cy={cy} r={ro} />
          {/if}
          {#if c.counted > 0}
            <circle class="f-public dot-ring" cx={cx} cy={cy} r={ri} />
          {/if}
        </g>
        <text class="t-muted" x={cx} y={c.above ? cy - Math.max(ro, ri) - 6 : cy + Math.max(ro, ri) + 14} text-anchor="middle" font-size={FONT}>{c.when}</text>
      {/each}
      {#if t.pending > 0 && narrow}
        <text class="t-strong" x={W - 2} y={cy - 12} text-anchor="end" font-size={FONT}>{money(t.counted)}</text>
        <text class="t-muted" x={W - 2} y={cy + 4} text-anchor="end" font-size={FONT}>+{money(t.pending)}</text>
        <text class="t-muted" x={W - 2} y={cy + 19} text-anchor="end" font-size={FONT}>pending</text>
      {:else}
        <text class="t-strong" x={W - 2} y={cy - (t.pending ? 4 : -4)} text-anchor="end" font-size={FONT}>{money(t.counted)}</text>
        {#if t.pending > 0}
          <text class="t-muted" x={W - 2} y={cy + 12} text-anchor="end" font-size={FONT}>+{money(t.pending)} pending</text>
        {/if}
      {/if}
      {#if i < teams.length - 1}
        <line class="row-rule" x1="0" x2={W} y1={y0 + rowH - 1} y2={y0 + rowH - 1} />
      {/if}
    {/each}
  </svg>
</div>
