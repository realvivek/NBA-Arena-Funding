<script>
  // The lead graphic: a basketball floating in water, sliced into layers whose areas are proportional to the public
  // money in each. Building the arenas is the part above the waterline; renovations, purchases, yearly payments and
  // tax breaks sit below it. Told in steps as the reader scrolls (see the [data-step] rules in global.css): each
  // layer below the line and its label carry classes the steps show (.lay-*, .lab-*). Without scripts the chart
  // rests in its last state, where every layer is lit.
  import { WIDE, NARROW, FONT, money } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const id = `ball-${variant}`;

  const layers = [...rows].sort((a, b) => a.ord - b.ord);
  const total = layers.reduce((a, l) => a + l.public_2026_m, 0);

  const W = narrow ? NARROW : WIDE;
  // on phones the steps scroll over the chart as cards, so the ball sits high and small
  const H = narrow ? 336 : 520;
  const r = narrow ? 128 : 196;
  const cx = narrow ? W / 2 : 232;
  const cy = narrow ? 196 : 306;
  const top = cy - r;

  // the height of a circular cap with a given share of the circle's area, by bisection
  const capArea = (h) => r * r * Math.acos((r - h) / r) - (r - h) * Math.sqrt(Math.max(0, 2 * r * h - h * h));
  const capH = (frac) => {
    let lo = 0, hi = 2 * r;
    for (let i = 0; i < 60; i++) {
      const mid = (lo + hi) / 2;
      if (capArea(mid) < frac * Math.PI * r * r) lo = mid;
      else hi = mid;
    }
    return (lo + hi) / 2;
  };
  const halfChord = (y) => Math.sqrt(Math.max(0, r * r - (y - cy) ** 2));

  let cum = 0;
  const bands = layers.map((l) => {
    const y0 = top + (cum ? capH(cum / total) : 0);
    cum += l.public_2026_m;
    const y1 = top + capH(Math.min(cum / total, 1));
    return { ...l, y0, y1, mid: (y0 + y1) / 2 };
  });
  const yw = bands[0].y1; // the waterline sits under the first layer
  const below = bands.slice(1);

  const seams = [
    `M${cx - r} ${cy} C${cx - r * 0.5} ${cy + r * 0.1} ${cx + r * 0.5} ${cy + r * 0.1} ${cx + r} ${cy}`,
    `M${cx} ${cy - r} C${cx + r * 0.08} ${cy - r * 0.4} ${cx + r * 0.08} ${cy + r * 0.4} ${cx} ${cy + r}`,
    `M${cx - r * 0.7} ${cy - r * 0.71} C${cx - r * 0.3} ${cy - r * 0.3} ${cx - r * 0.3} ${cy + r * 0.3} ${cx - r * 0.7} ${cy + r * 0.71}`,
    `M${cx + r * 0.7} ${cy - r * 0.71} C${cx + r * 0.3} ${cy - r * 0.3} ${cx + r * 0.3} ${cy + r * 0.3} ${cx + r * 0.7} ${cy + r * 0.71}`,
  ];
  const wave = Array.from({ length: Math.floor(W / 4) + 1 }, (_, i) => `${i * 4},${(yw + 2.2 * Math.sin((i * 4) / 13)).toFixed(1)}`).join(' ');
  const tip = (l) => `${l.name}: ${money(l.public_2026_m)} (2026 dollars), ${((100 * l.public_2026_m) / total).toFixed(0)}% of the total`;

  // wide: names and values at the right, with leaders to each layer; thin layers are spread apart
  const lx = cx + r + 40;
  const NAME = 15, VALUE = 21;
  const labelY = [];
  if (!narrow) {
    const gap = 50;
    bands.forEach((b, i) => {
      let y = i === 0 ? Math.min(b.mid, yw - 46) : b.mid;
      if (i > 0 && y - labelY[i - 1] < gap) y = labelY[i - 1] + gap;
      labelY.push(y);
    });
    const over = labelY[labelY.length - 1] - (H - 26);
    if (over > 0) for (let i = 2; i < labelY.length; i++) labelY[i] -= over;
  }

  // narrow: values inside the ball; the two thin layers share one label
  const inside = narrow
    ? [
        { key: bands[0].key, text: money(bands[0].public_2026_m), y: bands[0].mid + 20 },
        { key: bands[1].key, text: money(bands[1].public_2026_m), y: bands[1].mid + 6 },
        { key: `${bands[2].key} lab-${bands[3].key}`, text: `${money(bands[2].public_2026_m)} + ${money(bands[3].public_2026_m)}`, y: (bands[2].y0 + bands[3].y1) / 2 + 5, small: true },
        { key: bands[4].key, text: money(bands[4].public_2026_m), y: bands[4].mid + 4 },
      ]
    : [];
</script>

<div class="plot ballplot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    <defs>
      <radialGradient id="{id}-leather" cx="36%" cy="30%" r="78%">
        <stop offset="0" stop-color="#ffab66" /><stop offset=".55" stop-color="#e46f28" /><stop offset="1" stop-color="#9c4318" />
      </radialGradient>
      <pattern id="{id}-pebble" width="7" height="7" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1.1" fill="#4a2208" fill-opacity=".25" /><circle cx="5.5" cy="5.5" r="1.1" fill="#4a2208" fill-opacity=".25" />
      </pattern>
      <linearGradient id="{id}-water" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0" class="water-top" /><stop offset="1" class="water-bottom" />
      </linearGradient>
      <linearGradient id="{id}-fadeg" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0" stop-color="#fff" stop-opacity="0" /><stop offset=".1" stop-color="#fff" /><stop offset=".9" stop-color="#fff" /><stop offset="1" stop-color="#fff" stop-opacity="0" />
      </linearGradient>
      <mask id="{id}-fade"><rect x="0" y="0" width={W} height={H} fill="url(#{id}-fadeg)" /></mask>
      <clipPath id="{id}-circle"><circle {cx} {cy} {r} /></clipPath>
      {#each below as b}
        <clipPath id="{id}-c-{b.key}"><rect x="0" y={b.y0} width={W} height={b.y1 - b.y0} /></clipPath>
      {/each}
      <g id="{id}-art">
        <circle {cx} {cy} {r} fill="url(#{id}-leather)" />
        <circle {cx} {cy} {r} fill="url(#{id}-pebble)" />
        {#each seams as d}
          <path {d} fill="none" stroke="#2a160a" stroke-width={(5.5 * r) / 200} stroke-linecap="round" />
        {/each}
        <ellipse cx={cx - r * 0.38} cy={cy - r * 0.45} rx={r * 0.3} ry={r * 0.18} fill="#fff" fill-opacity=".14" transform="rotate(-30 {cx - r * 0.38} {cy - r * 0.45})" />
      </g>
    </defs>

    <!-- water behind the ball, the ball, then a veil of water over the part below the line -->
    <rect class="water" x="0" y={yw} width={W} height={H - yw} fill="url(#{id}-water)" mask="url(#{id}-fade)" />
    <use href="#{id}-art" data-tip={tip(bands[0])} />
    <g clip-path="url(#{id}-circle)"><rect class="veil" x="0" y={yw} width={W} height={H - yw} /></g>

    <!-- each layer below the line lights up at its step -->
    {#each below as b}
      <g class="lay lay-{b.key}" clip-path="url(#{id}-c-{b.key})" data-tip={tip(b)}><use href="#{id}-art" /></g>
    {/each}
    {#each below as b}
      {#if b.y1 < cy + r - 1}
        {@const hc = halfChord(b.y1)}
        <line class="slice" x1={cx - hc} x2={cx + hc} y1={b.y1} y2={b.y1} />
      {/if}
    {/each}
    <polyline class="waterline" points={wave} mask="url(#{id}-fade)" />

    {#if narrow}
      <g class="lab lab-total">
        <text class="t-strong" x={cx} y="30" text-anchor="middle" font-size="20">{money(total)} in all</text>
      </g>
      {#each inside as t}
        <text class="lab lab-{t.key} in-val" x={cx} y={t.y} text-anchor="middle" font-size={t.small ? FONT : 17}>{t.text}</text>
      {/each}
    {:else}
      <g class="lab lab-total">
        <text class="t-muted" x={lx} y="34" font-size={NAME}>All of it</text>
        <text class="t-strong" x={lx} y="66" font-size="28">{money(total)}</text>
      </g>
      {#each bands as b, i}
        {@const ex = cx + halfChord(b.mid)}
        {@const yl = labelY[i]}
        <g class="lab lab-{b.key}">
          <path class="ann-line" d="M{ex + 6},{b.mid}H{lx - 26}L{lx - 8},{yl - 6}" />
          <text class="t-ink" x={lx} y={yl - 10} font-size={NAME} font-weight="600">{b.name}</text>
          <text class="t-strong tick" x={lx} y={yl + 14} font-size={VALUE}>{money(b.public_2026_m)}</text>
        </g>
      {/each}
    {/if}
  </svg>
</div>
