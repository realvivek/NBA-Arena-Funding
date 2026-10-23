<script>
  // Who voted for the Spurs arena tax (Bexar County's Proposition B, November 4, 2025). Left: precincts in five
  // groups holding equal numbers of households, by estimated median household income, highest first; each bar's
  // thickness is the group's share of all votes and its split is yes against no. Right (below on phones): every
  // precinct as a dot sized by votes and colored by the share voting yes, with the current and planned arena sites.
  import { WIDE, NARROW, FONT, textWidth } from '../../lib/chart';

  let { rows, precincts = [], map = [], variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const usd = (v) => '$' + Math.round(v).toLocaleString('en-US');
  const pc = (v) => `${Math.round(100 * v)}%`;
  const fifths = [...rows].sort((a, b) => b.fifth - a.fifth);
  const range = (r) => (r.fifth === 5 ? `${usd(r.income_min)} and up` : r.fifth === 1 ? `Up to ${usd(r.income_max)}` : `${usd(r.income_min)} to ${usd(r.income_max)}`);

  // the bars: thickness by share of all votes
  const gap = 4, head = narrow ? 40 : 30, total = narrow ? 230 : 250;
  const labelH = narrow ? 18 : 0;
  const lw = narrow ? 0 : Math.ceil(Math.max(...fifths.map((r) => textWidth(range(r))))) + 12;
  const bx0 = lw, bx1 = narrow ? W - 44 : 360;
  let y = head;
  const bars = fifths.map((r) => {
    const h = Math.max(total * r.vote_share, 16);
    const b = { ...r, y: y + labelH, h, xs: bx0 + (bx1 - bx0) * r.yes_share };
    y += labelH + h + gap;
    return b;
  });
  const barsH = y;
  const tipBar = (r) =>
    `Precincts with median household incomes ${range(r).replace(/^Up to/, 'up to')}: ${r.yes_votes.toLocaleString('en-US')} yes, ` +
    `${r.no_votes.toLocaleString('en-US')} no (${pc(r.yes_share)} yes); ${pc(r.vote_share)} of all votes; ` +
    `${pc(r.turnout)} of registered voters voted on it`;

  // the map: an equirectangular projection fitted to the county outline
  const outline = map.find((m) => m.kind === 'outline');
  const sites = map.filter((m) => m.kind === 'site');
  const ring = outline ? outline.coords[0] : [];
  const lat0 = 29.44, k = Math.cos((lat0 * Math.PI) / 180);
  const lons = ring.map((p) => p[0]), lats = ring.map((p) => p[1]);
  const [lonA, lonB, latA, latB] = [Math.min(...lons), Math.max(...lons), Math.min(...lats), Math.max(...lats)];
  const mapW = narrow ? W - 20 : W - 400;
  const mapH = (mapW * (latB - latA)) / ((lonB - lonA) * k);
  // the color key: under the bars on wide screens, between the bars and the map on phones (two rows of two)
  const keyY = narrow ? barsH + 30 : barsH + 14;
  const mx0 = narrow ? 10 : 400, my0 = narrow ? keyY + 44 : head - 6;
  const px = (lon) => mx0 + ((lon - lonA) / (lonB - lonA)) * mapW;
  const py = (lat) => my0 + ((latB - lat) / (latB - latA)) * mapH;
  const path = 'M' + ring.map((p) => `${px(p[0]).toFixed(1)},${py(p[1]).toFixed(1)}`).join('L') + 'Z';
  const vmax = Math.max(...precincts.map((p) => p.votes));
  const rr = (v) => (narrow ? 0.6 : 0.8) + (narrow ? 3.6 : 4.4) * Math.sqrt(v / vmax);
  const bin = (s) => (s >= 0.55 ? 'f-public' : s >= 0.5 ? 'f-public-soft' : s >= 0.45 ? 'f-orange-soft' : 'f-orange');
  const KEY = [
    { cls: 'f-public', txt: '55% yes or more', tip: '55% or more' },
    { cls: 'f-public-soft', txt: '50% to 55%', tip: '50% to 55%' },
    { cls: 'f-orange-soft', txt: '45% to 50%', tip: '45% to 50%' },
    { cls: 'f-orange', txt: 'Under 45% yes', tip: 'under 45%' },
  ];
  const keyAt = (i) => ({ x: (i % 2) * (narrow ? 150 : 170), y: keyY + Math.floor(i / 2) * 18 });
  // one path per color group (a circle per precinct as two arcs), larger dots first, to keep the page light
  const groups = KEY.map((kk) => {
    const ps = precincts.filter((p) => bin(p.yes_share) === kk.cls).sort((a, b) => b.votes - a.votes);
    const d = ps
      .map((p) => {
        const r = rr(p.votes), cx = px(p.lon), cy = py(p.lat);
        return `M${(cx - r).toFixed(1)},${cy.toFixed(1)}a${r.toFixed(1)},${r.toFixed(1)} 0 1,0 ${(2 * r).toFixed(1)},0a${r.toFixed(1)},${r.toFixed(1)} 0 1,0 ${(-2 * r).toFixed(1)},0`;
      })
      .join('');
    return { ...kk, n: ps.length, votes: ps.reduce((a, p) => a + p.votes, 0), d };
  });
  const H = Math.ceil(narrow ? my0 + mapH + 6 : Math.max(keyY + 36, my0 + mapH) + 6);
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    <text class="t-muted" x="0" y="13" font-size={FONT}>{narrow ? 'Median household income of the precincts' : 'Precincts by median household income'}</text>
    {#if !narrow}<text class="t-muted" x={W - 2} y="13" text-anchor="end" font-size={FONT}>Every precinct, sized by votes</text>{/if}
    <text class="t-muted" x={bx1 + 6} y={head - 8} font-size={FONT}>Votes</text>
    <!-- the bars -->
    {#each bars as b}
      {#if narrow}
        <text class="t-ink" x="0" y={b.y - 5} font-size={FONT}>{range(b)}</text>
      {:else}
        <text class="t-ink" x={lw - 10} y={b.y + b.h / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{range(b)}</text>
      {/if}
      <g data-tip={tipBar(b)}>
        <rect class="f-public" x={bx0} y={b.y} width={Math.max(b.xs - bx0 - 1, 1)} height={b.h} rx="3" />
        <rect class="f-orange" x={b.xs + 1} y={b.y} width={Math.max(bx1 - b.xs - 1, 1)} height={b.h} rx="3" />
      </g>
      <text class="t-inverse" x={bx0 + 7} y={b.y + b.h / 2} dy="0.32em" font-size={FONT}>{pc(b.yes_share)} yes</text>
      {#if bx1 - b.xs > 60}<text class="t-inverse" x={bx1 - 7} y={b.y + b.h / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{pc(1 - b.yes_share)} no</text>{/if}
      <text class="tick t-ink" x={bx1 + 6} y={b.y + b.h / 2} dy="0.32em" font-size={FONT}>{pc(b.vote_share)}</text>
    {/each}
    <line class="s-ink" x1={(bx0 + bx1) / 2} x2={(bx0 + bx1) / 2} y1={head - 4} y2={barsH - gap + 2} stroke-dasharray="3 3" />
    <text class="tick t-muted" x={(bx0 + bx1) / 2} y={head - 8} text-anchor="middle" font-size={FONT}>50%</text>
    <!-- the map -->
    {#if narrow}<text class="t-muted" x="0" y={keyY - 10} font-size={FONT}>Every precinct, sized by votes</text>{/if}
    <path class="land" d={path} />
    {#each groups as g}
      <path class={g.cls} d={g.d} data-tip={`${g.n} precincts where ${g.tip} voted yes, with ${g.votes.toLocaleString('en-US')} votes in all`} />
    {/each}
    {#each sites as s}
      {@const sx = px(s.lon)}
      {@const sy = py(s.lat)}
      {#if s.role === 'planned arena'}
        <rect class="s-ink site-mark" x={sx - 4} y={sy - 4} width="8" height="8" transform="rotate(45 {sx} {sy})" data-tip="Planned arena site: the former Institute of Texan Cultures at Hemisfair" />
        <text class="t-ink halo" x={sx - 9} y={sy + 16} text-anchor="end" font-size={FONT}>New arena</text>
      {:else}
        <circle class="s-ink site-ring" cx={sx} cy={sy} r="5" data-tip="Frost Bank Center, the current arena" />
        <text class="t-ink halo" x={sx + 9} y={sy - 8} font-size={FONT}>Current arena</text>
      {/if}
    {/each}
    {#each KEY as kk, i}
      {@const at = keyAt(i)}
      <circle class={kk.cls} cx={at.x + 5} cy={at.y + 7} r="5" />
      <text class="t-ink" x={at.x + 15} y={at.y + 7} dy="0.32em" font-size={FONT}>{kk.txt}</text>
    {/each}
  </svg>
</div>
