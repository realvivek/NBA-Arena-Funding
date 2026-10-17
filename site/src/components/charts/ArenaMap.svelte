<script>
  // Chart 3: where the public money went. Circles sized by public money, shaded by public share of spending.
  // Wide: labeled map. Narrow: numbered circles above a ranked list.
  import { LayerCake, Svg } from 'layercake';
  import { scaleSqrt } from 'd3-scale';
  import { geoConicEqualArea, geoPath } from 'd3-geo';
  import { feature, mesh } from 'topojson-client';
  import { presimplify, simplify } from 'topojson-simplify';
  import us from 'us-atlas/states-10m.json';
  import world from 'world-atlas/countries-50m.json';
  import { WIDE, NARROW, FONT, money, TEAM_CITY } from '../../lib/chart';

  let { rows, variant = 'wide', label = '' } = $props();
  const narrow = variant === 'narrow';
  const W = narrow ? NARROW : WIDE;
  const H = narrow ? 230 : 440;

  const usS = simplify(presimplify(structuredClone(us)), narrow ? 0.05 : 0.01);
  const lower48 = (g) => !['02', '15', '60', '66', '69', '72', '78'].includes(g.id);
  const states = { type: 'FeatureCollection', features: feature(usS, usS.objects.states).features.filter(lower48) };
  const borders = mesh(usS, usS.objects.states, (a, b) => a !== b && lower48(a) && lower48(b));
  const worldS = simplify(presimplify(structuredClone(world)), narrow ? 0.05 : 0.01);
  const canada = feature(worldS, worldS.objects.countries).features.find((f) => f.id === '124');

  const pad = narrow ? 4 : 10;
  const projection = geoConicEqualArea().parallels([29.5, 45.5]).rotate([96, 0]).fitExtent([[pad, pad], [W - pad, H - (narrow ? 4 : 86)]], states);
  projection.clipExtent([[0, 0], [W, H]]);
  const path = geoPath(projection).digits(1);

  const maxPublic = Math.max(...rows.map((r) => r.public_2026_m));
  const r = scaleSqrt().domain([0, maxPublic]).range([0, narrow ? 15 : 26]);
  const BINS = [20, 40, 60, 80, 101];
  const bin = (s) => BINS.findIndex((b) => s < b) + 1;
  const ranked = [...rows].sort((a, b) => b.public_2026_m - a.public_2026_m);
  const rank = Object.fromEntries(ranked.map((d, i) => [d.team, i + 1]));
  const points = ranked
    .map((d) => {
      const [px, py] = projection([d.lon, d.lat]);
      return { ...d, px, py, rad: d.public_2026_m > 0 ? Math.max(r(d.public_2026_m), 2.5) : 2.5, city: TEAM_CITY[d.team] };
    })
    .reverse(); // small circles on top
  // labels for the ten largest; placement tuned where neighbors crowd
  const LABEL = { ORL: 'right', WAS: 'below-left', IND: 'left', CHA: 'right', MEM: 'left', UTA: 'right', NOP: 'below', BKN: 'right', HOU: 'left', CLE: 'above' };
  function labelPos(d) {
    const g = d.rad + 4;
    switch (LABEL[d.team]) {
      case 'left': return { x: d.px - g, y: d.py, a: 'end', dy: '0.32em' };
      case 'above': return { x: d.px, y: d.py - g, a: 'middle', dy: '0' };
      case 'below': return { x: d.px, y: d.py + g + 9, a: 'middle', dy: '0' };
      case 'below-left': return { x: d.px - d.rad * 0.6, y: d.py + g + 9, a: 'end', dy: '0' };
      default: return { x: d.px + g, y: d.py, a: 'start', dy: '0.32em' };
    }
  }
  const tip = (d) => `${d.arena}, ${d.city}: ${money(d.public_2026_m)} public, ${Math.round(d.public_share_pct)}% of all spending`;
  const legendY = H - 52;
</script>

<div class="plot" style="aspect-ratio: {W} / {H}">
  <LayerCake ssr data={points} containerWidth={W} containerHeight={H}>
    <Svg viewBox="0 0 {W} {H}" {label}>
      {#if canada}<path class="land-other" d={path(canada)} />{/if}
      <path class="land" d={path(states)} />
      <path d={path(borders)} fill="none" stroke="var(--surface)" stroke-width="1" />
      {#each points as d}
        {#if d.public_2026_m > 0}
          <circle class="seq-{bin(d.public_share_pct)} dot-ring" cx={d.px} cy={d.py} r={d.rad} data-tip={tip(d)} />
        {:else}
          <circle cx={d.px} cy={d.py} r={d.rad} fill="var(--surface)" stroke="var(--muted)" stroke-width="1.5" data-tip={tip(d)} />
        {/if}
      {/each}
      {#if !narrow}
        {#each points.filter((d) => LABEL[d.team]) as d}
          {@const p = labelPos(d)}
          <text class="t-ink" x={p.x} y={p.y} dy={p.dy} text-anchor={p.a} font-size={FONT} paint-order="stroke" stroke="var(--surface)" stroke-width="3">{d.city}</text>
        {/each}
        <g transform="translate(0,{legendY})">
          <text class="t-muted" x="0" y="0" font-size={FONT}>Public share of all spending</text>
          {#each BINS as b, i}
            <rect class="seq-{i + 1}" x={i * 76} y="8" width="72" height="10" rx="2" />
            <text class="tick t-muted" x={i * 76} y="34" font-size={FONT}>{i === 0 ? 'Under 20%' : `${BINS[i - 1]}-${i === 4 ? 100 : b}%`}</text>
          {/each}
          <text class="t-muted" x="400" y="0" font-size={FONT}>Public money</text>
          {#each [100, 500] as v, i}
            {@const cx = 400 + i * 64 + r(v)}
            <circle cx={cx} cy={48 - r(v)} r={r(v)} fill="none" stroke="var(--muted)" />
            <text class="tick t-muted" x={cx + r(v) + 4} y="48" font-size={FONT}>{money(v)}</text>
          {/each}
          <circle cx="566" cy="44" r="2.5" fill="var(--surface)" stroke="var(--muted)" stroke-width="1.5" />
          <text class="tick t-muted" x="574" y="48" font-size={FONT}>None found</text>
        </g>
      {:else}
        {#each points.filter((d) => rank[d.team] <= 10) as d}
          <text x={d.px} y={d.py} dy="0.35em" text-anchor="middle" font-size={FONT} font-weight="700" fill={bin(d.public_share_pct) >= 3 ? '#fff' : 'var(--ink)'}>{rank[d.team]}</text>
        {/each}
      {/if}
    </Svg>
  </LayerCake>
</div>
{#if narrow}
  <ol class="map-list">
    {#each ranked.slice(0, 10) as d}
      <li><span class="map-city">{TEAM_CITY[d.team]}</span> <span class="map-val">{money(d.public_2026_m)}, {Math.round(d.public_share_pct)}% public</span></li>
    {/each}
  </ol>
{/if}

<style>
  .map-list {
    margin: 8px 0 0;
    padding-left: 1.6em;
    font-size: 0.875rem;
    line-height: 1.5;
    columns: 2;
    column-gap: 16px;
  }
  .map-list li {
    break-inside: avoid;
  }
  .map-city {
    font-weight: 600;
  }
  .map-val {
    display: block;
    color: var(--ink-2);
    font-variant-numeric: tabular-nums;
  }
</style>
