/**
 * The ZIP lookup's data, compact, as a static file the lookup loads on first use: for each paying government its
 * name, level (1 city, 2 county, 3 state) and deals (team, arena, money per household, a note on who mostly pays),
 * and for each ZIP code area the governments it lies in (a negative number marks a ZIP code area partly inside).
 */
import type { APIRoute } from 'astro';
import { dataset } from '../lib/data';
import { STATS } from '../lib/copy';
import { TEAM_NAME } from '../lib/chart';

// who mostly pays, by the households chart's rule; a deal with pending money says so in its label instead
const note = (d: any): string =>
  d.pending_2026_m > 0
    ? ''
    : d.sales_share >= 0.5
      ? 'an upper bound: people who live elsewhere pay part of the sales tax'
      : d.visitors_share >= 0.5
        ? 'paid mostly by visitors, through hotel and car-rental taxes'
        : d.shared_share >= 0.5
          ? 'partly paid by visitors, through meal and ticket taxes'
          : '';

export const GET: APIRoute = () => {
  const rows = dataset('zip-lookup').rows as any[];
  const g = rows.map((r) => ({
    j: r.jurisdiction === 'New York, NY' ? 'New York City' : r.jurisdiction.replace(/ County, [A-Z]{2}$/, ' County').replace(/, [A-Z]{2}$/, ''),
    l: r.level,
    d: r.deals.map((d: any) => ({ t: TEAM_NAME[d.team], a: d.label, p: Math.round(d.per_household_2026), n: note(d) })),
  }));
  const z: Record<string, number[]> = {};
  rows.forEach((r, i) => {
    for (const zip of r.zips) (z[zip] ??= []).push(i);
    for (const zip of r.zips_part) (z[zip] ??= []).push(-(i + 1));
  });
  const body = { fed: Math.round(STATS.fed_per_household.value), g, z };
  return new Response(JSON.stringify(body), { headers: { 'Content-Type': 'application/json' } });
};
