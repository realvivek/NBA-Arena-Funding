<script>
  // Chart 1, the lead graphic: public money by year, one stacked column per year with a segment per arena, for
  // new arenas, existing ones and pending money on existing ones. A new arena still being built counts with the
  // new ones once its money is binding (Oklahoma City's, at face value in 2026), as it does in the ratio the copy
  // gives. Told in steps as the reader scrolls (see the [data-step] rules in global.css): marks and labels carry
  // classes the steps show or fade (.seg.new, .seg.existing, .seg.pending, .hl for the three arenas with the most
  // since 2014; .ann.a-new, .a-shift, .a-largest, .a-pending for the labels). Without scripts the chart rests in
  // its last state, where everything is drawn.
  import { LayerCake, Svg } from 'layercake';
  import { scaleBand, scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, money, moneyTick, vbar, textWidth, TEAM_CITY } from '../../lib/chart';
  import { STATS } from '../../lib/copy';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';

  const SINCE = 2014;
  const first = 1990;
  const keep = rows
    .filter(
      (r) =>
        ((r.category === 'new' || r.category === 'existing') && (r.status === 'counted' || r.status === 'pending')) ||
        (r.category === 'new_unopened' && r.binding),
    )
    .map((r) => (r.category === 'new_unopened' ? { ...r, category: 'new', building: true } : r));
  const last = Math.max(...keep.map((r) => r.year));
  const years = Array.from({ length: last - first + 1 }, (_, i) => first + i);

  // one segment per year, arena, category and status
  const groups = new Map();
  for (const r of keep) {
    const k = `${r.year}|${r.team}|${r.category}|${r.status}`;
    if (!groups.has(k))
      groups.set(k, { year: r.year, team: r.team, category: r.category, pending: r.status === 'pending', building: !!r.building, value: 0, what: [] });
    const g = groups.get(k);
    g.value += r.public_2026_m;
    g.what.push(r.description);
  }
  const rank = (g) => (g.category === 'new' ? 0 : g.pending ? 2 : 1);
  const segs = [];
  for (const year of years) {
    const list = [...groups.values()].filter((g) => g.year === year).sort((a, b) => rank(a) - rank(b) || b.value - a.value);
    let base = 0;
    for (const [i, g] of list.entries()) {
      segs.push({ ...g, y0: base, y1: base + g.value, top: i === list.length - 1 });
      base += g.value;
    }
  }
  const total = (year) => segs.filter((s) => s.year === year).reduce((a, s) => a + s.value, 0);
  const ymax = Math.max(...years.map(total));
  const yTop = Math.ceil(ymax / 500) * 500;

  // the largest renovations still under way, counted at face value in the last column, each labeled with its own amount
  const largest = segs
    .filter((s) => s.year === last && s.category === 'existing' && !s.pending)
    .sort((a, b) => b.value - a.value)
    .slice(0, narrow ? 3 : 4)
    .map((s) => [s.team, s.value]);
  const hl = new Set(largest.map(([t]) => t));
  // the largest new-arena columns before 2014: two on wide screens (at least five years apart), one on phones
  const bigNew = [];
  for (const s of segs.filter((g) => g.category === 'new' && g.year < SINCE).sort((a, b) => b.value - a.value))
    if (bigNew.length < (narrow ? 1 : 2) && bigNew.every((b) => Math.abs(b.year - s.year) >= 5)) bigNew.push(s);
  const pendingTotal = segs.filter((s) => s.pending).reduce((a, s) => a + s.value, 0);
  const pendingCities = [...new Set(segs.filter((s) => s.pending).map((s) => TEAM_CITY[s.team]))];

  const cls = (s) =>
    ['seg', s.category === 'new' ? 'new' : s.pending ? 'pending' : 'existing', s.year >= SINCE ? 'late' : 'early', hl.has(s.team) && s.year === last && s.category === 'existing' && !s.pending ? 'hl' : '']
      .filter(Boolean)
      .join(' ');
  const tip = (s) =>
    `${s.year}: ${TEAM_CITY[s.team]}, ${s.what.join('; ').toLowerCase()}: ${money(s.value)}${s.pending ? ', pending' : ''}${s.building ? ', under construction, at face value' : ''} (2026 dollars)`;

  const W = narrow ? NARROW : WIDE;
  const H = narrow ? 300 : 430;
  const ml = narrow ? 40 : 54;
  const mr = narrow ? 98 : 128;
  const mt = narrow ? 58 : 64;
  const mb = 29;
  const rebuild = STATS.rebuild_since_2014.display.short;
  const build = STATS.build_since_2014.display.short;
  const ticksX = narrow ? [1990, 2000, 2010, 2020] : [1990, 1995, 2000, 2005, 2010, 2014, 2020, 2026];
  const ticksY = narrow ? Array.from({ length: Math.floor(yTop / 1000) + 1 }, (_, i) => i * 1000) : Array.from({ length: yTop / 500 + 1 }, (_, i) => i * 500);

  // labels at the right of the last column: the pending total and its cities, then the largest renovations under way
  // below it, spread so no two overlap and joined to their segments by leaders
  const yS = scaleLinear().domain([0, yTop]).range([H - mb, mt]);
  const pend = segs.filter((s) => s.pending);
  const pendMid = pend.length ? (yS(Math.min(...pend.map((s) => s.y0))) + yS(Math.max(...pend.map((s) => s.y1)))) / 2 : 0;
  const pendTop = pendMid - 8 * (pendingCities.length + 1);
  const pendBottom = pend.length ? pendTop + 15 * pendingCities.length : mt;
  const bigLabels = largest
    .map(([team, value]) => {
      const s = segs.filter((g) => g.team === team && g.year === last && !g.pending && g.category === 'existing').sort((a, b) => b.value - a.value)[0];
      return s ? { team, value, mid: (yS(s.y0) + yS(s.y1)) / 2 } : null;
    })
    .filter(Boolean)
    .sort((a, b) => a.mid - b.mid);
  let floor = pendBottom + 22;
  for (const l of bigLabels) {
    l.ly = Math.max(l.mid, floor);
    floor = l.ly + 31;
  }
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake
    ssr
    data={segs}
    x="year"
    xScale={scaleBand().paddingInner(narrow ? 0.25 : 0.3)}
    xDomain={years}
    xRange={[ml, W - mr]}
    yScale={scaleLinear()}
    yDomain={[0, yTop]}
    yRange={[H - mb, mt]}
    containerWidth={W}
    containerHeight={H}
  >
    {#snippet children(k)}
      {@const x = k.xScale}
      {@const y = k.yScale}
      {@const bw = x.bandwidth()}
      {@const xr = x(last) + bw}
      <Svg viewBox="0 0 {W} {H}" {label}>
        <!-- the years since 2014 -->
        <rect class="band" x={x(SINCE) - (x.step() - bw) / 2} y={mt - 8} width={xr + 4 - (x(SINCE) - (x.step() - bw) / 2)} height={H - mb - mt + 8} />
        {#each ticksY as t}
          <line class={t === 0 ? 'baseline' : 'grid'} x1={ml} x2={xr} y1={y(t)} y2={y(t)} />
          <text class="tick t-muted" x={ml - 6} y={y(t)} dy="0.32em" text-anchor="end" font-size={FONT}>{moneyTick(t)}</text>
        {/each}
        {#each ticksX as t}
          <text class="tick t-muted" x={x(t) + bw / 2} y={H - mb + 20} text-anchor="middle" font-size={FONT}>{t}</text>
        {/each}

        {#each segs as s}
          {@const ya = y(s.y0) - (s.y0 > 0 ? 1 : 0)}
          {@const yb = y(s.y1)}
          {#if s.pending}
            <rect class="{cls(s)} f-pending-dash" x={x(s.year) + 0.6} y={yb + 0.6} width={bw - 1.2} height={Math.max(ya - yb - 1.2, 0.5)} rx="1.5" data-tip={tip(s)} />
          {:else if s.top}
            <path class="{cls(s)} {s.category === 'new' ? 'f-public' : 'f-orange'}" d={vbar(x(s.year), bw, ya, Math.min(yb, ya - 1), narrow ? 2 : 3)} data-tip={tip(s)} />
          {:else}
            <rect class="{cls(s)} {s.category === 'new' ? 'f-public' : 'f-orange'}" x={x(s.year)} y={yb} width={bw} height={Math.max(ya - yb, 0.75)} data-tip={tip(s)} />
          {/if}
        {/each}

        <!-- step 1: the largest new arenas before 2014 -->
        <g class="ann a-new">
          {#each bigNew as s}
            {@const cx = x(s.year) + bw / 2}
            {@const half = Math.max(textWidth(TEAM_CITY[s.team], FONT, 600), textWidth(`${money(s.value)}, ${s.year}`, FONT)) / 2 + 4}
            <!-- the label clears every column it spans, not only its own -->
            {@const clear = Math.min(...years.filter((yr) => Math.abs(x(yr) + bw / 2 - cx) <= half + bw / 2).map((yr) => y(total(yr))))}
            <text class="ann-text halo" x={cx} y={clear - 22} text-anchor="middle" font-size={FONT}>{TEAM_CITY[s.team]}</text>
            <text class="ann-sub halo" x={cx} y={clear - 7} text-anchor="middle" font-size={FONT}>{money(s.value)}, {s.year}</text>
          {/each}
        </g>

        <!-- step 2: since 2014 -->
        <g class="ann a-shift">
          <path class="ann-line" d="M{x(SINCE)},{mt - 2}V{mt - 8}H{xr}V{mt - 2}" />
          {#if narrow}
            <text class="ann-text halo" x={xr} y={mt - 38} text-anchor="end" font-size={FONT}>Since {SINCE}: {rebuild} to rebuild</text>
            <text class="ann-sub halo" x={xr} y={mt - 22} text-anchor="end" font-size={FONT}>{build} to build, with Oklahoma City's</text>
          {:else}
            <text class="ann-text halo" x={xr} y={mt - 38} text-anchor="end" font-size={FONT}>Since {SINCE}: {rebuild} to renovate or buy</text>
            <text class="ann-sub halo" x={xr} y={mt - 22} text-anchor="end" font-size={FONT}>{build} to build, counting Oklahoma City's</text>
          {/if}
        </g>

        <!-- step 3: the largest renovations under way, each with its own amount -->
        <g class="ann a-largest">
          {#each bigLabels as l}
            <path class="ann-line" d="M{xr + 2},{l.mid}H{xr + 5}V{l.ly}H{xr + 8}" />
            <text class="ann-text" x={xr + 11} y={l.ly - 3} font-size={FONT}>{TEAM_CITY[l.team]}</text>
            <text class="ann-sub" x={xr + 11} y={l.ly + 12} font-size={FONT}>{money(l.value)}{narrow ? '' : ' under way'}</text>
          {/each}
        </g>

        <!-- step 4: pending money on existing arenas -->
        <g class="ann a-pending">
          {#if pendingTotal > 0}
            {@const my = pendMid}
            {@const top = pendTop}
            <path class="ann-line" d="M{xr + 2},{my}H{xr + 8}" />
            {#if narrow}
              <text class="ann-text" x={xr + 11} y={top - 15} font-size={FONT}>Pending</text>
              <text class="ann-text" x={xr + 11} y={top} font-size={FONT}>{money(pendingTotal)}</text>
            {:else}
              <text class="ann-text" x={xr + 11} y={top} font-size={FONT}>Pending, {money(pendingTotal)}</text>
            {/if}
            {#each pendingCities as c, i}
              <text class="ann-sub" x={xr + 11} y={top + 15 * (i + 1)} font-size={FONT}>{c}</text>
            {/each}
          {/if}
        </g>
      </Svg>
    {/snippet}
  </LayerCake>
</div>
