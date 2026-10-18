<script>
  // The lead graphic: the public's bill for the arenas as a stack of bills, each worth $100 million, built from the
  // bottom up one kind of money at a time, each kind starting a new row. Building the arenas is blue and everything
  // after it orange; each kind's amount is printed beside the stack in large type, with a leader to its bills, and
  // brackets give the two shares. Told in steps as the reader scrolls (see the [data-step] rules in global.css):
  // bills not reached yet show as outlines and their labels are muted. Without scripts the chart rests in its last
  // state, every bill filled.
  import { WIDE, NARROW, FONT, money, textWidth } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const UNIT = 100; // $100 million a bill

  const layers = [...rows].sort((a, b) => a.ord - b.ord);
  const total = layers.reduce((a, l) => a + l.public_2026_m, 0);
  const share = (v) => `${Math.round((100 * v) / total)}%`;
  const long = (m) => (m >= 1000 ? `$${(m / 1000).toFixed(2)} billion` : `$${Math.round(m)} million`);

  // bills per kind, rounded so they add up to the rounded total (largest remainder)
  const n = Math.round(total / UNIT);
  const exact = layers.map((l) => l.public_2026_m / UNIT);
  const count = exact.map(Math.floor);
  const order = exact.map((e, i) => [e - Math.floor(e), i]).sort((a, b) => b[0] - a[0]);
  for (let k = 0; k < n - count.reduce((a, c) => a + c, 0); k++) count[order[k][1]] += 1;

  const W = narrow ? NARROW : WIDE;
  const cols = 6;
  const cw = narrow ? 22 : 40, ch = narrow ? 11 : 19, gap = narrow ? 3 : 4, sep = narrow ? 7 : 11;
  const colW = cols * cw + (cols - 1) * gap;
  const x0 = narrow ? W - colW : 300;
  const top = narrow ? 46 : 66;
  const rowsOf = count.map((c) => Math.max(1, Math.ceil(c / cols)));
  const colH = rowsOf.reduce((a, r) => a + r * ch + (r - 1) * gap, 0) + (rowsOf.length - 1) * sep;
  const H = top + colH + (narrow ? 8 : 12);

  // each kind fills whole rows from the left, bottom up; the next kind starts above a wider gap
  let base = top + colH; // the bottom edge of the next row to fill
  const kinds = layers.map((l, k) => {
    const cells = Array.from({ length: count[k] }, (_, j) => {
      const r = Math.floor(j / cols), c = j % cols;
      return { x: x0 + c * (cw + gap), y: base - (r + 1) * ch - r * gap };
    });
    const y1 = base, y0 = base - (rowsOf[k] * ch + (rowsOf[k] - 1) * gap);
    base = y0 - sep;
    return { ...l, cells, y0, y1, mid: (y0 + y1) / 2 };
  });

  // labels beside the stack: spread apart so they never overlap, from the bottom up
  const NUM = narrow ? 19 : 26, NAME = narrow ? FONT : 14;
  const minGap = narrow ? 42 : 56;
  const lx = narrow ? x0 - 12 : x0 - 34;
  const ly = [];
  for (let k = 0; k < kinds.length; k++) {
    let y = kinds[k].mid + NUM / 3;
    if (k > 0 && ly[k - 1] - y < minGap) y = ly[k - 1] - minGap;
    ly.push(y);
  }
  const over = Math.max(0, top + NUM - ly[ly.length - 1]);
  for (let k = 0; k < ly.length; k++) ly[k] += over;
  const nameOf = (l) => (narrow ? `${l.name} · ${share(l.public_2026_m)}` : l.name);

  // brackets: building, and everything after it
  const build = kinds[0];
  const rest = { y0: kinds[kinds.length - 1].y0, y1: kinds[1].y1 };
  const bx = x0 + colW + 14;
  const tip = (l) => `${l.name}: ${money(l.public_2026_m)} (2026 dollars), ${share(l.public_2026_m)} of the total`;
  const totalX = x0 + colW / 2;
</script>

<div class="plot billplot" style="aspect-ratio: {W} / {H}">
  <svg viewBox="0 0 {W} {H}" role="img" aria-label={label}>
    <g class="bs-key">
      <rect class="bs-bill bs-swatch" x="0" y="3" width={narrow ? 22 : 30} height={narrow ? 11 : 15} rx="2" />
      <text class="t-muted" x={narrow ? 30 : 38} y={narrow ? 13 : 15} font-size={FONT}>Each bill: $100 million</text>
    </g>
    <g class="bs-total">
      <text class="bs-num" x={totalX} y={top - (narrow ? 14 : 18)} text-anchor="middle" font-size={narrow ? 19 : 26}>{long(total)}{narrow ? '' : ' in all'}</text>
    </g>

    {#each kinds as l, k}
      <g class="bs-kind bs-{l.key} {k === 0 ? 'bs-first' : 'bs-after'}" data-tip={tip(l)}>
        {#each l.cells as c}
          <rect class="bs-bill" x={c.x} y={c.y} width={cw} height={ch} rx="2" />
          {#if !narrow}
            <rect class="bs-inner" x={c.x + 3} y={c.y + 3} width={cw - 6} height={ch - 6} rx="1" />
            <ellipse class="bs-inner" cx={c.x + cw / 2} cy={c.y + ch / 2} rx="5" ry="4" />
          {/if}
        {/each}
        {#if !narrow}
          <path class="bs-lead" d="M{lx + 6},{ly[k] - NUM / 3}H{lx + 16}L{x0 - 5},{l.mid}" />
        {/if}
        <text class="bs-num" x={lx} y={ly[k]} text-anchor="end" font-size={NUM}>{long(l.public_2026_m)}</text>
        <text class="bs-name" x={lx} y={ly[k] + NAME + 4} text-anchor="end" font-size={NAME}>{nameOf(l)}</text>
      </g>
    {/each}

    {#if !narrow}
      <g class="bs-brackets">
        {#each [{ y0: build.y0, y1: build.y1, v: build.public_2026_m, text: 'building' }, { y0: rest.y0, y1: rest.y1, v: total - build.public_2026_m, text: 'the rest' }] as b}
          <path class="bs-bracket" d="M{bx - 6},{b.y1}H{bx}V{b.y0}H{bx - 6}" />
          <text class="bs-num" x={bx + 10} y={(b.y0 + b.y1) / 2 + 2} font-size="22">{share(b.v)}</text>
          <text class="bs-name" x={bx + 10} y={(b.y0 + b.y1) / 2 + 20} font-size={FONT}>{b.text}</text>
        {/each}
      </g>
    {/if}
  </svg>
</div>
