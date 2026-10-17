<script>
  // Chart 4: arenas built mainly with private money, then bought or rebuilt with public money.
  // Each arena: what it cost to build (public and private) and the public money that came later.
  import { LayerCake, Svg } from 'layercake';
  import { scaleLinear } from 'd3-scale';
  import { WIDE, NARROW, FONT, money, hbar, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';

  const teams = [...new Set(rows.map((r) => r.team))].map((team) => {
    const rs = rows.filter((r) => r.team === team);
    const con = rs.find((r) => r.kind === 'construction');
    const later = rs.filter((r) => r.kind !== 'construction');
    return {
      team,
      city: TEAM_CITY[team],
      arena: con.arena,
      opened: con.opened,
      buildPublic: con.public_2026_m,
      buildPrivate: con.private_2026_m,
      laterCounted: later.filter((r) => r.core).reduce((a, r) => a + r.public_2026_m, 0),
      laterPending: later.filter((r) => !r.core).reduce((a, r) => a + r.public_2026_m, 0),
      years: [...new Set(later.filter((r) => r.public_2026_m > 0).map((r) => r.year))].sort(),
    };
  });
  teams.sort((a, b) => b.laterCounted + b.laterPending - (a.laterCounted + a.laterPending));
  const vmax = Math.max(...teams.map((t) => Math.max(t.buildPublic + t.buildPrivate, t.laterCounted + t.laterPending)));
  const share = (t) => Math.round((100 * t.buildPublic) / (t.buildPublic + t.buildPrivate));
  const tipBuild = (t) => `${t.arena}, opened ${t.opened}: built for ${money(t.buildPublic + t.buildPrivate)}, ${share(t)}% public (2026 dollars)`;
  const tipLater = (t) =>
    `${t.arena}: ${money(t.laterCounted)} of public money to buy or rebuild it` + (t.laterPending ? `, plus ${money(t.laterPending)} pending` : '');

  // wide
  const W = WIDE, rowH = 44, mt = 40;
  const H = mt + teams.length * rowH;
  const lw = 150, gap = 26;
  const pw = (W - lw - gap - 80) / 2;
  const p1 = lw, p2 = lw + pw + gap + 40;
  // narrow
  const NW = NARROW, blockH = 70, nmt = 8, nl = 44, nr = 74;
  const NH = nmt + teams.length * blockH;
</script>

{#if !narrow}
  <div class="plot" style="aspect-ratio: {W} / {H}">
    <LayerCake ssr data={teams} xScale={scaleLinear()} xDomain={[0, vmax]} xRange={[0, pw]} containerWidth={W} containerHeight={H}>
      {#snippet children(k)}
        {@const x = k.xScale}
        <Svg viewBox="0 0 {W} {H}" {label}>
          <text class="t-strong" x={p1} y={mt - 22} font-size={FONT}>To build it</text>
          <text class="t-strong" x={p2} y={mt - 22} font-size={FONT}>Later, to buy or rebuild it</text>
          {#each teams as t, i}
            {@const y0 = mt + i * rowH}
            {@const bh = 14}
            {@const by = y0 + 6}
            <line class="grid" x1="0" x2={W} y1={y0 - 6} y2={y0 - 6} />
            <text class="t-ink" x="0" y={by + 10} font-size={FONT} font-weight="600">{t.city}</text>
            <text class="t-muted" x="0" y={by + 27} font-size={FONT}>Opened {t.opened}</text>
            <g data-tip={tipBuild(t)}>
              {#if t.buildPublic > 0}
                <rect class="f-public" x={p1} y={by} width={Math.max(x(t.buildPublic), 1)} height={bh} />
              {/if}
              <path class="f-private" d={hbar(p1 + (t.buildPublic > 0 ? x(t.buildPublic) + 2 : 0), p1 + x(t.buildPublic + t.buildPrivate) + (t.buildPublic > 0 ? 2 : 0), by, bh)} />
            </g>
            <text class="t-muted" x={p1} y={by + 30} font-size={FONT}>{money(t.buildPublic + t.buildPrivate)}, {share(t)}% public</text>
            <g data-tip={tipLater(t)}>
              {#if t.laterCounted > 0}
                <path class="f-public" d={t.laterPending > 0 ? `M${p2},${by}h${x(t.laterCounted)}v${bh}h${-x(t.laterCounted)}Z` : hbar(p2, p2 + x(t.laterCounted), by, bh)} />
              {/if}
              {#if t.laterPending > 0}
                {@const s = p2 + (t.laterCounted > 0 ? x(t.laterCounted) + 2 : 0)}
                <rect class="f-pending" x={s + 0.75} y={by + 0.75} width={x(t.laterPending) - 1.5} height={bh - 1.5} rx="2" />
              {/if}
            </g>
            <text class="t-muted" x={p2} y={by + 30} font-size={FONT}>{money(t.laterCounted)}{t.laterPending ? ` + ${money(t.laterPending)} pending` : ''}, {t.years.join(', ')}</text>
          {/each}
        </Svg>
      {/snippet}
    </LayerCake>
  </div>
{:else}
  <div class="plot" style="aspect-ratio: {NW} / {NH}">
    <LayerCake ssr data={teams} xScale={scaleLinear()} xDomain={[0, vmax]} xRange={[nl, NW - nr]} containerWidth={NW} containerHeight={NH}>
      {#snippet children(k)}
        {@const x = k.xScale}
        <Svg viewBox="0 0 {NW} {NH}" {label}>
          {#each teams as t, i}
            {@const y0 = nmt + i * blockH}
            {@const bh = 12}
            <text class="t-ink" x="0" y={y0 + 12} font-size={FONT} font-weight="600">{t.city}<tspan class="t-muted" font-weight="400">, opened {t.opened}</tspan></text>
            <text class="t-muted" x="0" y={y0 + 30} dy="0.32em" font-size={FONT}>Built</text>
            <g data-tip={tipBuild(t)}>
              {#if t.buildPublic > 0}
                <rect class="f-public" x={nl} y={y0 + 24} width={Math.max(x(t.buildPublic) - nl, 1)} height={bh} />
              {/if}
              <path class="f-private" d={hbar(t.buildPublic > 0 ? x(t.buildPublic) + 2 : nl, x(t.buildPublic + t.buildPrivate) + (t.buildPublic > 0 ? 2 : 0), y0 + 24, bh)} />
            </g>
            <text class="t-muted" x={x(t.buildPublic + t.buildPrivate) + 6} y={y0 + 30} dy="0.32em" font-size={FONT}>{share(t)}% public</text>
            <text class="t-muted" x="0" y={y0 + 50} dy="0.32em" font-size={FONT}>Later</text>
            <g data-tip={tipLater(t)}>
              {#if t.laterCounted > 0}
                <path class="f-public" d={t.laterPending > 0 ? `M${nl},${y0 + 44}h${x(t.laterCounted) - nl}v${bh}h${-(x(t.laterCounted) - nl)}Z` : hbar(nl, x(t.laterCounted), y0 + 44, bh)} />
              {/if}
              {#if t.laterPending > 0}
                {@const s = t.laterCounted > 0 ? x(t.laterCounted) + 2 : nl}
                <rect class="f-pending" x={s + 0.75} y={y0 + 44.75} width={x(t.laterPending) - nl - 1.5} height={bh - 1.5} rx="2" />
              {/if}
            </g>
            <text class="t-muted" x={x(t.laterCounted + t.laterPending) + 6} y={y0 + 50} dy="0.32em" font-size={FONT}>{money(t.laterCounted + t.laterPending)}</text>
          {/each}
        </Svg>
      {/snippet}
    </LayerCake>
  </div>
{/if}
