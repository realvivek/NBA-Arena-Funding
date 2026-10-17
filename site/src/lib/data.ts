/** The pipeline's datasets, typed loosely: each has id, title, sources, columns, rows. */
import type { Cell, Column } from '../components/DataTable.astro';

export interface Dataset<R = Record<string, any>> {
  id: string;
  title: string;
  sources: string[];
  columns: string[];
  rows: R[];
  note: string;
  method: string;
}

const files = import.meta.glob('../generated/datasets/*.json', { eager: true, import: 'default' });

export function dataset<R = Record<string, any>>(id: string): Dataset<R> {
  const d = files[`../generated/datasets/${id}.json`] as Dataset<R> | undefined;
  if (!d) throw new Error(`no dataset ${id}; run pipeline/build.py`);
  return d;
}

export type Table = { columns: Column[]; rows: Record<string, Cell>[] };
