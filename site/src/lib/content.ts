import { parse } from 'yaml';
import allowText from '../content/allow.yaml?raw';
import { render, blockSources, type Context } from './copy';
import type { Citations } from './sources';

export const ALLOW: string[] = parse(allowText);

type Ref = { id: string } | string;
export const ids = (refs: Ref[] = []): string[] => refs.map((r) => (typeof r === 'string' ? r : r.id));

/** Render a paragraph: lint it, number its sources for the page, and return the HTML and citation numbers. */
export function paragraph(text: string, refs: Ref[], where: string, cites?: Citations, opts: Partial<Context> & { link?: boolean } = {}) {
  const own = ids(refs);
  const html = render(text, { where, sources: own, allow: ALLOW, ...opts });
  const all = blockSources(text, own);
  const numbers = cites ? cites.add(all) : [];
  return { html, sources: all, numbers };
}
