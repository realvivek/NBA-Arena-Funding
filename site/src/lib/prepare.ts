/**
 * Copy blocks rendered ahead of the page template, in reading order, so citation numbers follow the order a
 * reader meets the sources (components may render concurrently).
 */
import { paragraph, ALLOW, ids } from './content';
import { plain } from './copy';
import { figureSources } from './figures';
import type { Citations } from './sources';

type Ref = { id: string } | string;
type Step = { step: string; p: string; sources?: Ref[] };
type Block =
  | { p: string; sources?: Ref[] }
  | { fig: string }
  | { h3: string }
  | { quote: string; by: string; sources?: Ref[] }
  | { scrolly: string; steps: Step[] }
  | { teams: string; title: string; intro: string; sources?: Ref[] };
export type PreparedStep = { step: string; html: string; sources: string[]; numbers: number[] };
export type Prepared =
  | { kind: 'p'; html: string; sources: string[]; numbers: number[] }
  | { kind: 'fig'; id: string; numbers: number[] }
  | { kind: 'h3'; text: string }
  | { kind: 'quote'; html: string; by: string; sources: string[]; numbers: number[] }
  | { kind: 'scrolly'; id: string; numbers: number[]; steps: PreparedStep[] }
  | { kind: 'teams'; title: string; intro: string; sources: string[]; numbers: number[] };

export async function prepare(blocks: Block[], cites: Citations, where: string): Promise<Prepared[]> {
  const out: Prepared[] = [];
  for (const [i, b] of blocks.entries()) {
    const at = `${where} block ${i + 1}`;
    if ('p' in b) out.push({ kind: 'p', ...paragraph(b.p, b.sources ?? [], at, cites) });
    else if ('fig' in b) out.push({ kind: 'fig', id: b.fig, numbers: cites.add(await figureSources(b.fig)) });
    else if ('h3' in b) out.push({ kind: 'h3', text: plain(b.h3, { where: at, allow: ALLOW }) });
    else if ('quote' in b)
      out.push({ kind: 'quote', ...paragraph(b.quote, b.sources ?? [], at, cites), by: plain(b.by, { where: `${at} byline`, allow: ALLOW, sources: ids(b.sources) }) });
    else if ('scrolly' in b) {
      // the chart's title and sources come first, as the reader meets them, then each step
      const numbers = cites.add(await figureSources(b.scrolly));
      const steps = b.steps.map((s, j) => ({ step: s.step, ...paragraph(s.p, s.sources ?? [], `${at} step ${j + 1}`, cites) }));
      out.push({ kind: 'scrolly', id: b.scrolly, numbers, steps });
    } else if ('teams' in b) {
      if (b.teams !== 'all') throw new Error(`${at}: unknown team list ${b.teams}`);
      const intro = paragraph(b.intro, b.sources ?? [], `${at} intro`, cites);
      out.push({ kind: 'teams', title: plain(b.title, { where: `${at} title`, allow: ALLOW }), intro: intro.html, sources: intro.sources, numbers: intro.numbers });
    }
    else throw new Error(`${at}: unsupported block`);
  }
  return out;
}
