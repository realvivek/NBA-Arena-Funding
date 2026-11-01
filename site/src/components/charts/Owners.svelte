<script>
  // Who owns the teams: a tile for each team whose controlling owners made their money in finance or that an
  // investment fund holds a stake in, marked by where the owners made their money (a strip and a label, so identity
  // is never color alone) and listing, after a small marker, the funds with a stake in the team or its parent
  // company. Tiles run from private equity and hedge funds, through other finance, to fund stakes alone; the other
  // teams follow in a list, each with the field its owner made money in.
  import { WIDE, NARROW, FONT, textWidth, TEAM_NAME } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const SHORT_FUND = { 'Arctos Sports Partners': 'Arctos', 'Blue Owl HomeCourt': 'Blue Owl', 'Qatar Investment Authority': 'Qatar', 'Sixth Street': 'Sixth Street' };
  const name = (t) => (t === 'POR' ? 'Trail Blazers' : t === 'PHI' ? '76ers' : TEAM_NAME[t].split(' ').slice(-1)[0]);
  // tiles only for the teams with an owner from finance or a fund stake; the other teams in one list below
  const all = rows;
  const linked = (r) => r.owner_class !== 'other' || r.funds.length > 0;
  const shown = all.filter(linked);
  const rest = all.filter((r) => !linked(r));
  const W = narrow ? NARROW : WIDE;
  const cols = narrow ? 2 : 4;
  const gap = 6;
  const tw = (W - gap * (cols - 1)) / cols;
  const th = 78;
  const gridH = Math.ceil(shown.length / cols) * (th + gap) - gap;
  const restItems = rest.map((r) => `${name(r.team)}, ${r.owner_field.charAt(0).toLowerCase()}${r.owner_field.slice(1)}`);
  const restLines = [];
  for (const [i, it] of restItems.entries()) {
    const item = i < restItems.length - 1 ? `${it} ·` : it;
    const last = restLines[restLines.length - 1];
    if (last && textWidth(`${last} ${item}`, FONT) * 1.04 <= W - 4) restLines[restLines.length - 1] = `${last} ${item}`;
    else restLines.push(item);
  }
  const restTop = gridH + 30;
  const H = restTop + (narrow ? 39 : 22) + restLines.length * 18 - 8;
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
  // the funds line starts after a small marker, so it is a little narrower
  const fitsFund = (t) => textWidth(t, FONT, 600) * 1.04 <= tw - 29;
  const fundLines = (funds) => {
    if (!funds.length) return [];
    // funds wrap between names, never inside one
    const names = funds.map((f) => SHORT_FUND[f] ?? f);
    const lines = [];
    names.forEach((n, i) => {
      const item = `${n}${i < names.length - 1 ? ',' : ''}`;
      const last = lines[lines.length - 1];
      if (last && fitsFund(`${last} ${item}`)) lines[lines.length - 1] = `${last} ${item}`;
      else lines.push(item);
    });
    return lines;
  };
  const tip = (r) => `${TEAM_NAME[r.team]}: ${r.owner}, ${r.owner_wealth}${r.funds.length ? `. Funds: ${r.funds.map((f, i) => `${f} (${r.stakes[i]})`).join('; ')}` : ''}`;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    {#each shown as r, i}
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
          {@const ty = y + th - 9 - (fundLines(r.funds).length - 1 - j) * 15}
          {#if j === 0}<rect class="own-fund-mark" x={x + 13} y={ty - 9} width="8" height="8" rx="1.5" />{/if}
          <text class="own-funds" x={x + 25} y={ty} font-size={FONT}>{l}</text>
        {/each}
      </g>
    {/each}
    {#if narrow}
      <text class="t-strong" x="0" y={restTop} font-size={FONT}>The other {rest.length} teams</text>
      <text class="t-muted" x="0" y={restTop + 17} font-size={FONT}>Owners from other fields, no fund stake</text>
    {:else}
      <text class="t-strong" x="0" y={restTop} font-size={FONT}>The other {rest.length} teams<tspan class="t-muted" font-weight="400" dx="8">owners from other fields, no fund stake</tspan></text>
    {/if}
    {#each restLines as l, j}
      <text class="own-field" x="0" y={restTop + (narrow ? 39 : 22) + j * 18} font-size={FONT}>{l}</text>
    {/each}
  </svg>
</div>
