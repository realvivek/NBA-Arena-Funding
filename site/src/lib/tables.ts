/** "Show the data" tables for each chart. */
import { money, dollars, pct, TEAM_CITY } from './chart';
import type { Table } from './data';

const STATUS: Record<string, string> = { counted: 'Counted', pending: 'Pending', committed: 'Committed, not open' };
const CATEGORY: Record<string, string> = {
  new: 'New arena',
  existing: 'Existing arena',
  new_unopened: 'New arena, not open',
  district: 'District around an arena',
};

export function rebuildTable(rows: any[]): Table {
  return {
    columns: [
      { key: 'year', label: 'Year' },
      { key: 'arena', label: 'Arena' },
      { key: 'what', label: 'What' },
      { key: 'category', label: 'Counted as' },
      { key: 'status', label: 'Status' },
      { key: 'public', label: 'Public money (2026 $)', num: true },
      { key: 'sources', label: 'Sources' },
    ],
    rows: rows.map((r) => ({
      year: r.year,
      arena: TEAM_CITY[r.team] ?? r.team,
      what: r.description,
      category: CATEGORY[r.category],
      status: STATUS[r.status],
      public: money(r.public_2026_m),
      sources: { sources: r.sources },
    })),
  };
}

export { money, dollars, pct };
