/**
 * Copy blocks rendered ahead of the page template, in reading order, so citation numbers follow the order a
 * reader meets the sources (components may render concurrently).
 */
import { paragraph } from './content';
import { figureSources } from './figures';
import type { Citations } from './sources';

type Ref = { id: string } | string;
type Block = { p: string; sources?: Ref[] } | { fig: string } | { h3: string } | { quote: string; by: string; sources?: Ref[] };
export type Prepared =
  | { kind: 'p'; html: string; sources: string[]; numbers: number[] }
  | { kind: 'fig'; id: string; numbers: number[] }
  | { kind: 'h3'; text: string };

export async function prepare(blocks: Block[], cites: Citations, where: string): Promise<Prepared[]> {
  const out: Prepared[] = [];
  for (const [i, b] of blocks.entries()) {
    if ('p' in b) out.push({ kind: 'p', ...paragraph(b.p, b.sources ?? [], `${where} block ${i + 1}`, cites) });
    else if ('fig' in b) out.push({ kind: 'fig', id: b.fig, numbers: cites.add(await figureSources(b.fig)) });
    else if ('h3' in b) out.push({ kind: 'h3', text: b.h3 });
    else throw new Error(`${where} block ${i + 1}: unsupported block`);
  }
  return out;
}
