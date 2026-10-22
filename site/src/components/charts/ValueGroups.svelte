<script>
  // The public money in each team's arena, with the teams in thirds of the league by value (Forbes, October 2026):
  // one bar per third, one segment per arena, all on one dollar scale. Tax breaks are not included.
  import { WIDE, NARROW, FONT, money, textWidth, TEAM_NAME } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const short = (t) => (t === 'POR' ? 'Trail Blazers' : t === 'PHI' ? '76ers' : TEAM_NAME[t].split(' ').slice(-1)[0]);
  const ranked = [...rows].sort((a, b) => b.forbes_2026_b - a.forbes_2026_b || a.team.localeCompare(b.team));
  const n = Math.round(ranked.length / 3);
  const NAMES = [`The ${n} most valuable teams`, `The next ${n}`, `The ${n} least valuable teams`];
  const groups = [0, 1, 2].map((g) => {
    const teams = ranked.slice(g * n, g === 2 ? ranked.length : (g + 1) * n);
    const funded = teams.filter((r) => r.public_2026_m > 0).sort((a, b) => b.public_2026_m - a.public_2026_m);
    return {
      name: NAMES[g],
      teams,
      funded,
      total: teams.reduce((a, r) => a + r.public_2026_m, 0),
      vmin: Math.min(...teams.map((r) => r.forbes_2026_b)),
      vmax: Math.max(...teams.map((r) => r.forbes_2026_b)),
    };
  });
  const W = narrow ? NARROW : WIDE;
  const x0 = 0, x1 = W - 2, gap = 2, bh = narrow ? 20 : 24;
  const tmax = Math.max(...groups.map((g) => g.total));
  const sx = (m) => x0 + ((x1 - x0) * m) / tmax;
  for (const g of groups) {
    let x = x0, right = -Infinity, stop = false;
    g.segs = g.funded.map((r) => {
      const w = sx(r.public_2026_m) - x0;
      const s = { ...r, x, w: Math.max(w - gap, 1) };
      x += w;
      // a name under the segment when it fits inside the segment's width and clears the one before; on phones the
      // names stop at the first segment too narrow for its name, so no segment is skipped
      const tw = textWidth(short(r.team));
      s.named = !stop && tw + 6 <= s.w && s.x >= right + 6;
      if (s.named) right = s.x + tw;
      else if (narrow) stop = true;
      return s;
    });
  }
  const headH = narrow ? 40 : 22;
  const rowH = headH + bh + 46;
  const H = groups.length * rowH - 18;
  const bn = (v) => `$${v.toFixed(1)}B`;
  const detail = (g) => {
    const full = `worth ${bn(g.vmin)} to ${bn(g.vmax)}; public money in ${g.funded.length} of ${g.teams.length} arenas`;
    if (!narrow) return full;
    const mid = `Worth ${bn(g.vmin)} to ${bn(g.vmax)}; money in ${g.funded.length} of ${g.teams.length} arenas`;
    return textWidth(mid) <= W ? mid : `Worth ${bn(g.vmin)} to ${bn(g.vmax)}`;
  };
  const tip = (r) =>
    `${TEAM_NAME[r.team]}: ${money(r.public_2026_m)} of public money in the arena (2026 dollars); team worth ${money(r.forbes_2026_b * 1000, 2)} (Forbes, October 2026)`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each groups as g, i}
      {@const top = i * rowH}
      {@const by = top + headH + 8}
      <text class="t-strong" x="0" y={top + 14} font-size={FONT}>{g.name}</text>
      <text class="t-strong" x={x1} y={top + 14} text-anchor="end" font-size={FONT}>{money(g.total)}</text>
      <text class="tick t-muted" x={narrow ? 0 : textWidth(g.name, FONT, 650) + 12} y={top + (narrow ? 32 : 14)} font-size={FONT}>{detail(g)}</text>
      <line class="grid" x1={x0} x2={x1} y1={by + bh / 2} y2={by + bh / 2} />
      {#each g.segs as s}
        <rect class="f-public" x={s.x} y={by} width={s.w} height={bh} rx="3" data-tip={tip(s)} />
        {#if s.named}
          <text class="tick t-ink" x={s.x} y={by + bh + 16} font-size={FONT}>{short(s.team)}</text>
        {/if}
      {/each}
    {/each}
  </svg>
</div>
