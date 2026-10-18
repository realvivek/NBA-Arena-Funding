/** Which dataset each figure draws, and the sources a figure cites (its own plus its dataset's). */
import { getEntry } from 'astro:content';
import { dataset } from './data';
import { ids } from './content';
import { sitePath } from './paths';

export const FIG_DATA: Record<string, string> = {
  bill: 'public-layers',
  values: 'team-values',
  trend: 'value-history',
  owners: 'ownership',
  rebuild: 'rebuild-by-year',
  arenas: 'arenas',
  map: 'arena-map',
  takeovers: 'takeovers',
  whopays: 'who-pays',
  households: 'households-local',
  uc: 'uc-bills',
  ongoing: 'ongoing',
  threats: 'threats',
  leases: 'leases',
  slc: 'slc-monthly',
  wcd: 'wcd-annual',
};

// Where each row's own sources are listed, for charts whose rows come from many documents.
export const FIG_RECORD: Record<string, { href: string; label: string }> = {
  rebuild: { href: sitePath('/arenas/'), label: "each arena's record" },
  arenas: { href: sitePath('/arenas/'), label: "each arena's record" },
  map: { href: sitePath('/arenas/'), label: "each arena's record" },
  takeovers: { href: sitePath('/arenas/'), label: "each arena's record" },
  households: { href: sitePath('/households/'), label: 'the households page' },
  uc: { href: sitePath('/tax-breaks/'), label: 'the tax-breaks page' },
  ongoing: { href: sitePath('/arenas/'), label: "each arena's record" },
  threats: { href: sitePath('/threats/#ledger'), label: 'the threat ledger' },
  leases: { href: sitePath('/leases/#every-lease'), label: 'the lease table' },
};

/** The sources a figure cites in its caption: its own and its dataset's, not each row's. */
export async function figureSources(id: string): Promise<string[]> {
  const fig = await getEntry('figures', id);
  if (!fig) throw new Error(`figure ${id} is not in src/content/figures.yaml`);
  if (!FIG_DATA[id]) throw new Error(`no dataset registered for figure ${id}`);
  if (fig.data.dataset !== FIG_DATA[id]) throw new Error(`figure ${id}: figures.yaml says ${fig.data.dataset}, registry says ${FIG_DATA[id]}`);
  return [...new Set([...ids(fig.data.sources), ...dataset(FIG_DATA[id]).base_sources])];
}
