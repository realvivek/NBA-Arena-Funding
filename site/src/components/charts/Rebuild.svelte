<script>
  // Chart 1: public money by year for new arenas and for existing ones (counted money only).
  // Wide: columns by year. Narrow: horizontal bars by five-year period.
  import { LayerCake, Svg } from 'layercake';
  import { scaleBand, scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, money, moneyTick, vbar, hbar } from '../../lib/chart';
  import { STATS } from '../../lib/copy';

  let { rows, variant = 'wide', label = '' } = $props();

  const counted = rows.filter((r) => r.status === 'counted' && (r.category === 'new' || r.category === 'existing'));
  const first = 1990;
  const last = Math.max(...counted.map((r) => r.year));
  const years = Array.from({ length: last - first + 1 }, (_, i) => first + i);

  function sumBy(filter) {
    const out = { new: 0, existing: 0, newTeams: [], existingTeams: [] };
    for (const r of counted) {
      if (!filter(r)) continue;
      out[r.category] += r.public_2026_m;
      const list = r.category === 'new' ? out.newTeams : out.existingTeams;
      if (!list.includes(r.team)) list.push(r.team);
    }
    return out;
  }
  const byYear = years.map((year) => ({ year, ...sumBy((r) => r.year === year) }));
  const bins = [];
  for (let y0 = first; y0 <= last; y0 += 5) {
    const y1 = Math.min(y0 + 4, last);
    bins.push({ name: y1 === y0 ? `${y0}` : `${y0}-${String(y1).slice(2)}`, ...sumBy((r) => r.year >= y0 && r.year <= y1) });
  }

  const tip = (when, kind, v, teams) =>
    `${when}: ${money(v)} of public money for ${kind === 'new' ? 'new arenas' : 'existing arenas'} (${teams.join(', ')})`;

  // wide layout
  const W = WIDE, H = 330, ml = 58, mr = 10, mt = 46, mb = 30;
  const ymaxW = Math.max(...byYear.map((d) => d.new + d.existing));
  const yTop = Math.ceil(ymaxW / 250) * 250;
  const since = 2014;
  const rebuild = STATS.rebuild_since_2014.display.short;
  const build = STATS.build_since_2014.display.short;

  // narrow layout
  const NW = NARROW, rowH = 34, nmt = 6, nml = 70, nmr = 58;
  const NH = nmt + bins.length * rowH + 4;
  const xmaxN = Math.max(...bins.map((d) => d.new + d.existing));
</script>

{#if variant === 'wide'}
  <div class="plot" style="aspect-ratio: {W} / {H}">
    <LayerCake
      ssr
      data={byYear}
      x="year"
      y={(d) => d.new + d.existing}
      xScale={scaleBand().paddingInner(0.3)}
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
        {@const bw = Math.min(x.bandwidth(), 14)}
        {@const off = (x.bandwidth() - bw) / 2}
        <Svg viewBox="0 0 {W} {H}" {label}>
          {#each y.ticks(4) as t}
            <line class={t === 0 ? 'baseline' : 'grid'} x1={ml} x2={W - mr} y1={y(t)} y2={y(t)} />
            <text class="tick t-muted" x={ml - 6} y={y(t)} dy="0.32em" text-anchor="end" font-size={FONT}>{moneyTick(t)}</text>
          {/each}
          {#each byYear as d}
            {@const x0 = x(d.year) + off}
            {#if d.new > 0}
              {#if d.existing > 0}
                <rect class="f-public" x={x0} width={bw} y={y(d.new)} height={y(0) - y(d.new)} data-tip={tip(d.year, 'new', d.new, d.newTeams)} />
              {:else}
                <path class="f-public" d={vbar(x0, bw, y(0), y(d.new))} data-tip={tip(d.year, 'new', d.new, d.newTeams)} />
              {/if}
            {/if}
            {#if d.existing > 0}
              {@const base = d.new > 0 ? y(d.new) - 2 : y(0)}
              <path class="f-orange" d={vbar(x0, bw, base, Math.min(base - 1, y(d.new + d.existing) - (d.new > 0 ? 2 : 0)))} data-tip={tip(d.year, 'existing', d.existing, d.existingTeams)} />
            {/if}
          {/each}
          {#each years.filter((yr) => (yr % 5 === 0 && last - yr >= 3) || yr === last) as yr}
            <text class="tick t-muted" x={x(yr) + x.bandwidth() / 2} y={H - mb + 18} text-anchor="middle" font-size={FONT}>{yr}</text>
          {/each}
          <!-- the 2014-2026 bracket -->
          {@const bx0 = x(since)}
          {@const bx1 = x(last) + x.bandwidth()}
          <path class="s-ink" d="M{bx0},{mt - 6}V{mt - 12}H{bx1}V{mt - 6}" />
          <text class="t-ink" x={bx1} y={mt - 20} text-anchor="end" font-size={FONT}>
            Since {since}: <tspan class="t-strong">{rebuild}</tspan> to rebuild, <tspan class="t-strong">{build}</tspan> to build
          </text>
        </Svg>
      {/snippet}
    </LayerCake>
  </div>
{:else}
  <div class="plot" style="aspect-ratio: {NW} / {NH}">
    <LayerCake
      ssr
      data={bins}
      x={(d) => d.new + d.existing}
      y="name"
      xScale={scaleLinear()}
      xDomain={[0, xmaxN]}
      xRange={[nml, NW - nmr]}
      yScale={scaleBand().paddingInner(0.35)}
      yDomain={bins.map((b) => b.name)}
      yRange={[nmt, NH - 4]}
      containerWidth={NW}
      containerHeight={NH}
    >
      {#snippet children(k)}
        {@const x = k.xScale}
        {@const y = k.yScale}
        {@const bh = Math.min(y.bandwidth(), 18)}
        <Svg viewBox="0 0 {NW} {NH}" {label}>
          <line class="baseline" x1={nml} x2={nml} y1={nmt} y2={NH - 4} />
          {#each bins as d}
            {@const y0 = y(d.name) + (y.bandwidth() - bh) / 2}
            <text class="tick t-muted" x={nml - 8} y={y0 + bh / 2} dy="0.32em" text-anchor="end" font-size={FONT}>{d.name}</text>
            {#if d.new > 0}
              {#if d.existing > 0}
                <rect class="f-public" x={nml} y={y0} width={x(d.new) - nml} height={bh} data-tip={tip(d.name, 'new', d.new, d.newTeams)} />
              {:else}
                <path class="f-public" d={hbar(nml, x(d.new), y0, bh)} data-tip={tip(d.name, 'new', d.new, d.newTeams)} />
              {/if}
            {/if}
            {#if d.existing > 0}
              {@const s = d.new > 0 ? x(d.new) + 2 : nml}
              <path class="f-orange" d={hbar(s, Math.max(s + 1, x(d.new + d.existing) + (d.new > 0 ? 2 : 0)), y0, bh)} data-tip={tip(d.name, 'existing', d.existing, d.existingTeams)} />
            {/if}
            <text class="t-ink" x={x(d.new + d.existing) + (d.new > 0 && d.existing > 0 ? 8 : 6)} y={y0 + bh / 2} dy="0.32em" font-size={FONT}>{money(d.new + d.existing)}</text>
          {/each}
        </Svg>
      {/snippet}
    </LayerCake>
  </div>
{/if}
