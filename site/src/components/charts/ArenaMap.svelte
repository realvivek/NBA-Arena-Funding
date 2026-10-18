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
  import { WIDE, NARROW, FONT, money, textWidth, TEAM_CITY } from '../../lib/chart';

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
  // Labels for the ten largest, placed so that none covers a circle or another label: each tries spots around its
  // circle, near first, then farther out with a leader, and takes the one that collides least.
  const LH = 14;
  const boxOf = (x, y, w, a) => {
    const x0 = a === 'end' ? x - w : a === 'middle' ? x - w / 2 : x;
    return { x0: x0 - 2, x1: x0 + w + 2, y0: y - LH / 2, y1: y + LH / 2 };
  };
  const hitsCircle = (b, c) => {
    const nx = Math.max(b.x0, Math.min(c.px, b.x1)), ny = Math.max(b.y0, Math.min(c.py, b.y1));
    const d = Math.hypot(nx - c.px, ny - c.py);
    return d < c.rad + 1.5 ? c.rad + 1.5 - d + 4 : 0;
  };
  const hitsBox = (a, b) => {
    const ix = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), iy = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
    return ix > 0 && iy > 0 ? ix * iy : 0;
  };
  const legendTop = H - 60;
  const placed = [];
  const labels = [];
  const pointOf = Object.fromEntries(points.map((q) => [q.team, q]));
  for (const d of ranked.slice(0, 10).map((r) => pointOf[r.team])) {
    const w = textWidth(d.city, FONT) * 1.05;
    const near = d.rad + 4, far = d.rad + 16;
    const spots = [];
    for (const [dist, lead] of [[near, false], [far, true]])
      for (const [ux, uy] of [[1, 0], [-1, 0], [0, -1], [0, 1], [0.75, -0.75], [-0.75, -0.75], [0.75, 0.75], [-0.75, 0.75]]) {
        const a = ux > 0.1 ? 'start' : ux < -0.1 ? 'end' : 'middle';
        const x = d.px + ux * dist, y = d.py + uy * dist + (uy > 0.1 ? LH / 2 - 2 : uy < -0.1 ? -LH / 2 + 2 : 0);
        spots.push({ x, y, a, lead, ex: d.px + ux * (d.rad + 1), ey: d.py + uy * (d.rad + 1) });
      }
    let best = null;
    for (const [i, s] of spots.entries()) {
      const b = boxOf(s.x, s.y, w, s.a);
      let score = i * 0.01 + (s.lead ? 6 : 0);
      for (const c of points) score += hitsCircle(b, c) * (c.team === d.team ? 3 : 2);
      for (const q of placed) score += hitsBox(b, q) * 0.5;
      if (b.x0 < 0 || b.x1 > W || b.y0 < 0 || b.y1 > legendTop) score += 1000;
      if (!best || score < best.score) best = { ...s, b, score };
    }
    placed.push(best.b);
    labels.push({ ...best, city: d.city, team: d.team });
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
        {#each labels as l}
          {#if l.lead}
            <line class="ann-line" x1={l.ex} y1={l.ey} x2={l.a === 'start' ? l.b.x0 + 1 : l.a === 'end' ? l.b.x1 - 1 : l.x} y2={l.a === 'middle' ? (l.y > l.ey ? l.b.y0 : l.b.y1) : l.y} />
          {/if}
          <text class="t-ink halo" x={l.x} y={l.y} dy="0.32em" text-anchor={l.a} font-size={FONT}>{l.city}</text>
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
