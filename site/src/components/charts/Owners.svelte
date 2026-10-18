<script>
  // Who owns the teams: one tile per team, marked by where its controlling owners made their money (a strip and a
  // label, so identity is never color alone) and listing the investment funds with a stake in the team or its
  // parent company. Tiles run from private equity and hedge funds, through other finance, to everyone else.
  import { WIDE, NARROW, FONT, textWidth, TEAM_NAME } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const SHORT_FUND = { 'Arctos Sports Partners': 'Arctos', 'Blue Owl HomeCourt': 'Blue Owl', 'Qatar Investment Authority': 'Qatar', 'Sixth Street': 'Sixth Street' };
  const name = (t) => (t === 'POR' ? 'Trail Blazers' : t === 'PHI' ? '76ers' : TEAM_NAME[t].split(' ').slice(-1)[0]);
  const W = narrow ? NARROW : WIDE;
  const cols = narrow ? 2 : 5;
  const gap = 6;
  const tw = (W - gap * (cols - 1)) / cols;
  const th = 78;
  const H = Math.ceil(rows.length / cols) * (th + gap) - gap;
  const cls = { private_equity: 'own-pe', other_finance: 'own-fin', other: 'own-other' };
  // labels that do not fit a tile wrap between words (widths are estimates, so with a margin)
  const fits = (t, weight = 400) => textWidth(t, FONT, weight) * 1.04 <= tw - 17;
  const wrap = (text, weight = 400) => {
    const lines = [];
    for (const w of text.split(' ')) {
      const last = lines[lines.length - 1];
      if (last && fits(`${last} ${w}`, weight)) lines[lines.length - 1] = `${last} ${w}`;
      else lines.push(w);
    }
    return lines;
  };
  const fieldLines = (f) => wrap(f);
  const fundLines = (funds) => {
    if (!funds.length) return [];
    // funds wrap between names, never inside one
    const names = funds.map((f) => SHORT_FUND[f] ?? f);
    const lines = [];
    names.forEach((n, i) => {
      const item = `${i ? '' : '+ '}${n}${i < names.length - 1 ? ',' : ''}`;
      const last = lines[lines.length - 1];
      if (last && fits(`${last} ${item}`, 600)) lines[lines.length - 1] = `${last} ${item}`;
      else lines.push(item);
    });
    return lines;
  };
  const tip = (r) => `${TEAM_NAME[r.team]}: ${r.owner}, ${r.owner_wealth}${r.funds.length ? `. Funds: ${r.funds.map((f, i) => `${f} (${r.stakes[i]})`).join('; ')}` : ''}`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each rows as r, i}
      {@const x = (i % cols) * (tw + gap)}
      {@const y = Math.floor(i / cols) * (th + gap)}
      {@const lines = fieldLines(r.owner_field)}
      <g class="own {cls[r.owner_class]}" data-tip={tip(r)}>
        <rect class="own-tile" {x} {y} width={tw} height={th} rx="3" />
        <rect class="own-strip" {x} {y} width="5" height={th} />
        <text class="t-strong" x={x + 13} y={y + 19} font-size={FONT}>{name(r.team)}</text>
        {#each lines as l, j}
          <text class="own-field" x={x + 13} y={y + 36 + j * 15} font-size={FONT}>{l}</text>
        {/each}
        {#each fundLines(r.funds) as l, j}
          <text class="own-funds" x={x + 13} y={y + th - 9 - (fundLines(r.funds).length - 1 - j) * 15} font-size={FONT}>{l}</text>
        {/each}
      </g>
    {/each}
  </svg>
</div>
