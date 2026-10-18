/** Shared setup for the reference pages: the page's copy entry, its prepared blocks and its citations. */
import { getEntry } from 'astro:content';
import { Citations } from './sources';
import { prepare, type Prepared } from './prepare';
import { plain, blockSources } from './copy';
import { paragraph, ids } from './content';

export async function referencePage(id: string) {
  const entry = await getEntry('pages', id);
  if (!entry) throw new Error(`page ${id} is not in src/content/pages.yaml`);
  const page = entry.data;
  const cites = new Citations();
  // the deck is numbered first, as the reader meets it, then the key figures under it
  paragraph(page.deck, page.sources, `${id} deck`, cites);
  if (page.tiles.length) cites.add(blockSources(page.tiles.map((t) => `${t.value} ${t.label}`).join(' '), ids(page.sources)));
  const blocks: Prepared[] = await prepare(page.blocks, cites, id);
  const notes: Prepared[] = await prepare(page.notes, cites, `${id} notes`);
  const title = plain(page.title, { where: `${id} title` });
  return { page, cites, blocks, notes, title };
}
