/** "Show the data" tables for each chart: the same rows the chart draws, with their sources. */
import { money, dollars, TEAM_CITY } from './chart';
import type { Table } from './data';

const STATUS: Record<string, string> = { counted: 'Counted', pending: 'Pending', committed: 'Committed, not open' };
const CATEGORY: Record<string, string> = {
  new: 'New arena',
  existing: 'Existing arena',
  new_unopened: 'New arena, not open',
  district: 'District around an arena',
};
const pct = (v: number | null | undefined, d = 0) => (v == null ? '' : `${v.toFixed(d)}%`);
const m = (v: number | null | undefined) => (v == null ? '' : money(v));

export function rebuildTable(rows: any[]): Table {
  return {
    columns: [
      { key: 'year', label: 'Year' },
      { key: 'arena', label: 'City' },
      { key: 'what', label: 'What' },
      { key: 'category', label: 'Counted as' },
      { key: 'status', label: 'Status' },
      { key: 'public', label: 'Public money (2026 $)', num: true },
    ],
    rows: rows.map((r) => ({
      year: r.year,
      arena: { text: TEAM_CITY[r.team] ?? r.team, href: `/arenas/#${r.team.toLowerCase()}` },
      what: r.description,
      category: CATEGORY[r.category],
      status: STATUS[r.status],
      public: m(r.public_2026_m),
    })),
  };
}

export function arenasTable(rows: any[]): Table {
  return {
    columns: [
      { key: 'arena', label: 'Arena' },
      { key: 'opened', label: 'Opened', num: true },
      { key: 'public', label: 'Public (2026 $)', num: true },
      { key: 'breaks', label: 'Tax breaks', num: true },
      { key: 'private', label: 'Private', num: true },
      { key: 'share', label: 'Public share', num: true },
    ],
    rows: rows.map((r) => ({
      arena: { text: `${r.arena}, ${r.city}`, href: `/arenas/#${r.team.toLowerCase()}` },
      opened: r.opened,
      public: m(r.public_2026_m),
      breaks: r.tax_breaks_2026_m ? m(r.tax_breaks_2026_m) : '',
      private: m(r.private_2026_m),
      share: pct(r.public_share_pct),
    })),
  };
}

export function mapTable(rows: any[]): Table {
  return {
    columns: [
      { key: 'arena', label: 'Arena' },
      { key: 'public', label: 'Public money (2026 $)', num: true },
      { key: 'share', label: 'Public share', num: true },
      { key: 'where', label: 'Location', num: true },
      { key: 'sources', label: 'Location source' },
    ],
    rows: rows.map((r) => ({
      arena: { text: `${r.arena}, ${r.city}`, href: `/arenas/#${r.team.toLowerCase()}` },
      public: m(r.public_2026_m),
      share: pct(r.public_share_pct),
      where: `${r.lat.toFixed(3)}, ${r.lon.toFixed(3)}`,
      sources: { sources: r.sources },
    })),
  };
}

export function takeoversTable(rows: any[]): Table {
  return {
    columns: [
      { key: 'city', label: 'City' },
      { key: 'what', label: 'What' },
      { key: 'year', label: 'Year', num: true },
      { key: 'status', label: 'Status' },
      { key: 'public', label: 'Public (2026 $)', num: true },
      { key: 'private', label: 'Private', num: true },
    ],
    rows: rows.map((r) => ({
      city: { text: TEAM_CITY[r.team], href: `/arenas/#${r.team.toLowerCase()}` },
      what: r.description,
      year: r.year,
      status: r.core ? (r.status === 'binding' ? 'Binding' : 'Completed') : 'Pending',
      public: m(r.public_2026_m),
      private: r.kind === 'purchase' ? '' : m(r.private_2026_m),
    })),
  };
}

export function whoPaysTable(rows: any[]): Table {
  const PAYER: Record<string, string> = { visitors: 'Mostly visitors', residents: 'Mostly residents', other: 'Land, or not split by stream' };
  return {
    columns: [
      { key: 'name', label: 'Funding stream' },
      { key: 'payer', label: 'Who mostly pays' },
      { key: 'public', label: 'Public money (2026 $)', num: true },
      { key: 'share', label: 'Share', num: true },
    ],
    rows: rows.map((r) => ({ name: r.name, payer: PAYER[r.payer], public: m(r.public_2026_m), share: pct(r.share_pct, 1) })),
  };
}

export function householdsTable(rows: any[]): Table {
  const out: Table['rows'] = [];
  for (const r of rows)
    for (const p of r.parts)
      out.push({
        deal: { text: r.deal, href: `/arenas/#${r.team.toLowerCase()}` },
        where: p.jurisdiction,
        households: p.households.toLocaleString('en-US'),
        share: pct(100 * p.share),
        per: dollars(p.per_household_2026),
        total: r.parts.length > 1 ? dollars(r.per_household_2026) : '',
      });
  return {
    columns: [
      { key: 'deal', label: 'Deal' },
      { key: 'where', label: 'Paying jurisdiction' },
      { key: 'households', label: 'Households (2024)', num: true },
      { key: 'share', label: 'Share of the money', num: true },
      { key: 'per', label: 'Per household', num: true },
      { key: 'total', label: 'Total for the most local', num: true },
    ],
    rows: out,
  };
}

export function ucTable(rows: any[]): Table {
  const LABEL: Record<string, string> = { b: 'Primary document', c: 'Press or secondary (tax rate)' };
  return {
    columns: [
      { key: 'year', label: 'Tax year', num: true },
      { key: 'paid', label: 'Bill paid', num: true },
      { key: 'without', label: 'Estimated without the formula', num: true },
      { key: 'low', label: 'Low estimate', num: true },
      { key: 'label', label: 'Source of the bill' },
    ],
    rows: rows.map((r) => ({
      year: r.tax_year,
      paid: `$${r.paid_m.toFixed(2)}M`,
      without: r.without_formula_m ? `$${r.without_formula_m.toFixed(2)}M` : '',
      low: r.without_formula_low_m ? `$${r.without_formula_low_m.toFixed(2)}M` : '',
      label: r.period === 'formula' && r.tax_year < 2006 ? 'Computed from value, equalizer and rate' : LABEL[r.label] ?? r.label,
    })),
  };
}

export function ongoingTable(rows: any[]): Table {
  const groups = new Map<string, any[]>();
  for (const r of rows) {
    const k = `${r.team}|${r.description}`;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k)!.push(r);
  }
  return {
    columns: [
      { key: 'city', label: 'City' },
      { key: 'what', label: 'Payment' },
      { key: 'years', label: 'Years' },
      { key: 'n', label: 'Years paid', num: true },
      { key: 'nominal', label: 'Paid (then-year $)', num: true },
      { key: 'real', label: '2026 $', num: true },
    ],
    rows: [...groups.values()].map((g) => {
      const ys = g.map((r) => r.year);
      return {
        city: { text: TEAM_CITY[g[0].team], href: `/arenas/#${g[0].team.toLowerCase()}` },
        what: g[0].description,
        years: `${Math.min(...ys)}-${Math.max(...ys)}`,
        n: g.length,
        nominal: money(g.reduce((a, r) => a + r.public_nominal_m, 0)),
        real: money(g.reduce((a, r) => a + r.public_2026_m, 0)),
      };
    }),
  };
}

const CLASS: Record<string, string> = {
  explicit: 'Explicit',
  implied: 'Implied',
  official_cited: 'Cited by an official',
  lure_only: 'Another city luring a team',
  unclear: 'Unclear',
  none: 'None found',
};
export function threatsTable(rows: any[]): Table {
  return {
    columns: [
      { key: 'id', label: 'ID' },
      { key: 'team', label: 'Team' },
      { key: 'cls', label: 'Threat' },
      { key: 'threat', label: 'Threat date' },
      { key: 'approved', label: 'Money approved' },
      { key: 'lag', label: 'Months', num: true },
      { key: 'money', label: 'Public money (nominal)', num: true },
    ],
    rows: rows.map((r) => ({
      id: { text: r.id, href: `/threats/#${r.id.toLowerCase()}` },
      team: r.team,
      cls: CLASS[r.threat_class] ?? r.threat_class,
      threat: r.threat_date ?? '',
      approved: r.approval_date ?? '',
      lag: r.lag_months != null ? r.lag_months.toFixed(1) : '',
      money: r.money_usd_m != null ? money(r.money_usd_m) : '',
    })),
  };
}

export function leasesTable(rows: any[], full = false): Table {
  return {
    columns: [
      { key: 'arena', label: 'Arena' },
      { key: 'end', label: 'Ends', num: true },
      { key: 'terms', label: 'Term' },
      { key: 'outs', label: 'Exit terms and penalties' },
      { key: 'label', label: 'Label' },
      ...(full ? [{ key: 'sources', label: 'Sources' }] : []),
    ],
    rows: rows.map((r) => ({
      __id: full ? r.team.toLowerCase() : undefined,
      arena: { text: `${r.arena}, ${TEAM_CITY[r.team]}`, href: `/arenas/#${r.team.toLowerCase()}` },
      end: r.term_end_year ?? '',
      terms: r.term_and_nonrelocation ?? '',
      outs: r.outs_penalties_notes ?? '',
      label: r.label ? { label: r.label } : '',
      sources: { sources: r.sources },
    })),
  };
}

export function slcTable(rows: any[]): Table {
  return {
    columns: [
      { key: 'month', label: 'Month' },
      { key: 'usd', label: 'Distribution', num: true },
    ],
    rows: rows.map((r) => ({ month: r.month, usd: dollars(r.usd) })),
  };
}

export function wcdTable(rows: any[]): Table {
  const d = (v: string | null) => (v ? dollars(Number(v)) : '');
  return {
    columns: [
      { key: 'year', label: 'Year' },
      { key: 'basic', label: 'Basic room tax', num: true },
      { key: 'add', label: 'Additional room tax', num: true },
      { key: 'fb', label: 'Food and drink', num: true },
      { key: 'car', label: 'Car rental', num: true },
      { key: 'total', label: 'Total', num: true },
    ],
    rows: rows.map((r) => ({ year: r.year, basic: d(r.basic_room), add: d(r.additional_room), fb: d(r.food_beverage), car: d(r.car_rental), total: d(r.total) })),
  };
}
