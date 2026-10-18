/** Every piece of copy on the site, with the numbers in it: for the fact-check page and the copy tests. */
import { getCollection } from 'astro:content';
import { tokenKeys, typedNumbers, blockSources } from './copy';
import { ALLOW, ids } from './content';
import { figureSources } from './figures';

export interface CopyItem {
  where: string;
  href: string;
  text: string;
  tokens: string[];
  typed: string[];
  sources: string[];
}

const slug = (t: string) => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function item(where: string, href: string, text: string, own: string[]): CopyItem {
  return { where, href, text, tokens: tokenKeys(text), typed: typedNumbers(text, ALLOW), sources: blockSources(text, own) };
}

type Block = Record<string, any>;

/** The copy in a list of blocks: paragraphs, steps, key figures, cards, the funds and pull quotes. */
function blockItems(blocks: Block[], where: string, href: string, figWhere: Map<string, { where: string; href: string }>): CopyItem[] {
  const out: CopyItem[] = [];
  let n = 0;
  for (const b of blocks) {
    const own = ids(b.sources);
    if ('p' in b) out.push(item(`${where}: paragraph ${++n}`, href, b.p, own));
    if ('quote' in b) out.push(item(`${where}: quote`, href, b.quote, own));
    if ('scrolly' in b) b.steps.forEach((s: Block, i: number) => out.push(item(`${where}: step ${i + 1}`, href, s.p, ids(s.sources))));
    if ('stats' in b)
      b.stats.forEach((t: Block) => out.push(item(`${where}: key figure`, href, `${t.value} ${t.label}`, own)));
    if ('cards' in b)
      b.cards.forEach((c: Block) => out.push(item(`${where}: card "${c.title}"`, href, `${c.value ?? ''} ${c.text}`.trim(), ids(c.sources))));
    if ('funds' in b) b.funds.forEach((f: Block) => out.push(item(`${where}: ${f.fund}`, href, f.text, ids(f.sources))));
    const fig = b.fig ?? b.scrolly;
    if (fig && !figWhere.has(fig)) figWhere.set(fig, { where, href });
  }
  return out;
}

export async function copyInventory(): Promise<CopyItem[]> {
  const out: CopyItem[] = [];
  const pages = await getCollection('pages');
  const story = (await getCollection('story')).sort((a, b) => a.data.n - b.data.n);
  const figures = await getCollection('figures');
  const figWhere = new Map<string, { where: string; href: string }>();

  for (const p of pages) {
    const own = ids(p.data.sources);
    const name = p.id === 'home' ? 'Story' : p.data.kicker.replace(/^The /, '').replace(/^./, (c) => c.toUpperCase());
    out.push(item(`${name}: headline`, p.data.path, p.data.title, own));
    out.push(item(`${name}: deck`, p.data.path, p.data.deck, own));
    p.data.tiles.forEach((t, i) => {
      out.push(item(`${name}: key figure ${i + 1}`, p.data.path, t.value, own));
      out.push(item(`${name}: key figure ${i + 1} label`, p.data.path, t.label, own));
    });
    for (const [part, blocks] of [['', p.data.blocks], [' note', p.data.notes]] as const)
      out.push(...blockItems(blocks, `${name}${part}`, p.data.path, figWhere));
  }
  for (const s of story) {
    const title = s.data.title ?? 'Opening';
    const href = s.data.title ? `/#${slug(s.data.title)}` : '/';
    out.push(...blockItems(s.data.blocks, `Story, ${title}`, href, figWhere));
  }
  for (const f of figures) {
    const at = figWhere.get(f.id) ?? { where: 'Chart', href: '/' };
    const own = await figureSources(f.id);
    const href = `${at.href.split('#')[0]}#fig-${f.id}`;
    out.push(item(`${at.where}, chart "${f.id}": title`, href, f.data.title, own));
    out.push(item(`${at.where}, chart "${f.id}": subtitle`, href, f.data.sub, own));
    f.data.notes.forEach((n, i) => out.push(item(`${at.where}, chart "${f.id}": note ${i + 1}`, href, n, own)));
  }
  return out;
}
