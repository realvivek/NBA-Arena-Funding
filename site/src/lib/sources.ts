import { SOURCES, type Source } from './copy';

export const ORIGIN_LABEL: Record<Source['origin'], string> = {
  government: 'Government',
  court: 'Court',
  team_or_league: 'Team or league',
  independent: 'Independent',
};
export const ORIGIN_ORDER: Source['origin'][] = ['government', 'court', 'team_or_league', 'independent'];

export function source(id: string): Source {
  const s = SOURCES[id];
  if (!s) throw new Error(`unknown source ${id}`);
  return s;
}

/** How a source is credited in a one-line source note: its publisher, or for this site's own ledgers, their name. */
export function creditName(s: Source): string {
  if (s.publisher === 'This site') return `${s.title.replace(/ \(.*$/, '').replace(/,.*$/, '')} (this site)`;
  return s.publisher;
}

/** A short name for a source in a list of links: publisher, then date. */
export function shortName(s: Source): string {
  const d = s.date === 'n.d.' ? '' : `, ${s.date.slice(0, 4)}`;
  return `${s.publisher}${d}`;
}

/**
 * Numbers sources in the order a page first cites them, so a paragraph's citations and the list at the end of
 * the page agree.
 */
export class Citations {
  order: string[] = [];
  add(ids: string[]): number[] {
    return ids.map((id) => {
      source(id);
      let i = this.order.indexOf(id);
      if (i < 0) {
        this.order.push(id);
        i = this.order.length - 1;
      }
      return i + 1;
    });
  }
  list(): { n: number; s: Source }[] {
    return this.order.map((id, i) => ({ n: i + 1, s: source(id) }));
  }
}

export function labelText(label: string): string {
  const parts: string[] = [];
  if (/a/.test(label)) parts.push('computed');
  if (/b/.test(label)) parts.push('primary document');
  if (/c/.test(label)) parts.push('press or secondary');
  if (/u/.test(label)) parts.push('unverified');
  return parts.join(', ');
}
