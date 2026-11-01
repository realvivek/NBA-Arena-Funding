<script>
  // The public money that came after the arenas opened, three ways. First what it paid for, one bar per kind on one
  // scale, with the arenas that took the most beneath; then two whole bars: whether it is owed under deals and laws
  // already in place or came in new deals, and whether voters or officials approved it.
  import { WIDE, NARROW, FONT, money, hbar, textWidth, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const NAME = {
    renovation: 'Renovations',
    break: 'Property-tax breaks',
    ongoing: 'Yearly payments',
    purchase: 'Buying arenas',
    owed: ['Owed under deals and laws already in place', 'Owed under earlier deals'],
    deal: ['New renovation and purchase deals', 'New deals'],
    officials: ['Councils, legislatures and appointed boards', 'Officials'],
    voters: ['Voters', 'Voters'],
  };
  const FILL = { renovation: 'f-orange', purchase: 'f-orange-soft', ongoing: 'f-aqua', break: 'f-public-soft', owed: 'f-orange', deal: 'f-private', officials: 'f-private', voters: 'f-public' };
  const list = (teams) => {
    const c = teams.map((t) => TEAM_CITY[t]);
    return c.length < 2 ? c.join('') : `${c.slice(0, -1).join(', ')} and ${c[c.length - 1]}`;
  };
  const what = rows.filter((r) => r.bar === 'what').sort((a, b) => b.value_2026_m - a.value_2026_m);
  const total = what.reduce((a, r) => a + r.value_2026_m, 0);
  const pct = (v) => `${Math.round((100 * v) / total)}%`;
  const note = (r) => (r.arenas <= 3 ? list(r.largest) : `${r.arenas} arenas; the most in ${list(r.largest)}`);

  // what it paid for: the kind at the left (above the bar on phones), the bar, its amount, the arenas beneath
  const lw = narrow ? 0 : 150;
  const vmax = what[0].value_2026_m;
  const bmax = narrow ? W - 92 : W - lw - 96;
  const rowH = narrow ? 64 : 46;
  const head1 = 14;
  const top1 = head1 + 16;
  const ws = what.map((r, i) => ({ ...r, y: top1 + i * rowH + (narrow ? 22 : 0), w: Math.max((bmax * r.value_2026_m) / vmax, 3) }));

  // the two whole bars, each part labeled at its end of the bar
  const bars = [
    { title: 'When it comes due', parts: ['owed', 'deal'] },
    { title: 'Who approved it', parts: ['officials', 'voters'] },
  ];
  const top2 = top1 + what.length * rowH + (narrow ? 26 : 22);
  const barH = 92;
  const H = top2 + bars.length * barH - 10;
  const gap = 2;
  for (const [i, b] of bars.entries()) {
    const parts = b.parts.map((k) => rows.find((r) => r.key === k) ?? { key: k, value_2026_m: 0 });
    const sum = parts.reduce((a, r) => a + r.value_2026_m, 0);
    let x = 0;
    b.y = top2 + i * barH;
    b.segs = parts.map((r, j) => {
      const w = (W * r.value_2026_m) / sum;
      const s = { ...r, x: x + (j > 0 ? gap / 2 : 0), w: w - gap / 2, share: Math.round((100 * r.value_2026_m) / sum), name: NAME[r.key][narrow ? 1 : 0] };
      x += w;
      return s;
    });
  }
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    <text class="t-strong" x="0" y={head1} font-size={FONT}>What it paid for<tspan class="t-muted" font-weight="400" dx="8">{money(total)} in all</tspan></text>
    {#each ws as r}
      <g data-tip={`${NAME[r.key]}: ${money(r.value_2026_m)}, ${pct(r.value_2026_m)} of the public money after opening (2026 dollars)`}>
        {#if narrow}
          <text class="t-ink" x="0" y={r.y - 12} font-size={FONT} font-weight="600">{NAME[r.key]}</text>
        {:else}
          <text class="t-ink" x="0" y={r.y + 5} font-size={FONT} font-weight="600">{NAME[r.key]}</text>
        {/if}
        <path class={FILL[r.key]} d={hbar(lw, lw + r.w, r.y - 6, 13, 3)} />
        <text class="tick t-strong" x={lw + r.w + 7} y={r.y + 5} font-size={FONT}>{money(r.value_2026_m)}<tspan class="t-muted" font-weight="400" dx="5">{pct(r.value_2026_m)}</tspan></text>
        <text class="t-muted" x={lw} y={r.y + 25} font-size={FONT}>{textWidth(note(r)) * 1.04 <= W - lw ? note(r) : list(r.largest)}</text>
      </g>
    {/each}

    {#each bars as b}
      <text class="t-strong" x="0" y={b.y} font-size={FONT}>{b.title}</text>
      <text class="t-ink" x="0" y={b.y + 20} font-size={FONT}>{b.segs[0].name}</text>
      <text class="t-strong" x="0" y={b.y + 36} font-size={FONT}>{money(b.segs[0].value_2026_m)}<tspan class="t-muted" font-weight="400" dx="5">{b.segs[0].share}%</tspan></text>
      <text class="t-ink" x={W} y={b.y + 20} text-anchor="end" font-size={FONT}>{b.segs[1].name}</text>
      <text class="t-strong" x={W} y={b.y + 36} text-anchor="end" font-size={FONT}>{money(b.segs[1].value_2026_m)}<tspan class="t-muted" font-weight="400" dx="5">{b.segs[1].share}%</tspan></text>
      {#each b.segs as s}
        <path class={FILL[s.key]} d={hbar(s.x, s.x + s.w, b.y + 46, 18, 3)} data-tip={`${NAME[s.key][0]}: ${money(s.value_2026_m)}, ${s.share}% (2026 dollars)`} />
      {/each}
    {/each}
  </svg>
</div>
