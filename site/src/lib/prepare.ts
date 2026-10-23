/**
 * Copy blocks rendered ahead of the page template, in reading order, so citation numbers follow the order a
 * reader meets the sources (components may render concurrently).
 */
import { paragraph, ALLOW, ids } from './content';
import { plain, blockSources, tokenKeys } from './copy';
import { figureSources } from './figures';
import { dataset } from './data';
import { TEAM_NAME } from './chart';
import type { Citations } from './sources';

type Ref = { id: string } | string;
type Step = { step: string; p: string; sources?: Ref[] };
type Block =
  | { p: string; sources?: Ref[] }
  | { fig: string }
  | { h3: string }
  | { quote: string; by: string; sources?: Ref[] }
  | { scrolly: string; steps: Step[] }
  | { teams: string; title: string; intro: string; sources?: Ref[] }
  | { stats: { value: string; label: string }[]; sources?: Ref[] }
  | { cards: { title: string; value?: string; text: string; sources?: Ref[] }[] }
  | { funds: { fund: string; text: string; sources?: Ref[] }[] }
  | { reveal: string; value: string; sources?: Ref[] }
  | { lookup: string; title: string; intro: string; sources?: Ref[] };
export type PreparedStep = { step: string; html: string; sources: string[]; numbers: number[] };
export type Prepared =
  | { kind: 'p'; html: string; sources: string[]; numbers: number[] }
  | { kind: 'fig'; id: string; numbers: number[] }
  | { kind: 'h3'; text: string }
  | { kind: 'quote'; html: string; by: string; sources: string[]; numbers: number[] }
  | { kind: 'scrolly'; id: string; numbers: number[]; steps: PreparedStep[] }
  | { kind: 'teams'; title: string; intro: string; sources: string[]; numbers: number[] }
  | { kind: 'stats'; tiles: { value: string; label: string }[]; sources: string[]; numbers: number[] }
  | { kind: 'cards'; cards: PreparedCard[] }
  | { kind: 'funds'; funds: PreparedFund[] }
  | { kind: 'reveal'; lead: string; value: string; sources: string[]; numbers: number[] }
  | { kind: 'lookup'; id: string; title: string; intro: string; sources: string[]; numbers: number[] };
export type PreparedCard = { title: string; value?: string; text: string; sources: string[]; numbers: number[] };
export type PreparedFund = {
  fund: string;
  type: string;
  text: string;
  stakes: { team: string; name: string; stake: string; entered: string | null }[];
  sources: string[];
  numbers: number[];
};

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
    } else if ('stats' in b) {
      // key figures: each value is a computed number (a token), each label a short phrase; one list of sources
      const own = ids(b.sources);
      const tiles = b.stats.map((t, j) => {
        if (!tokenKeys(t.value).length) throw new Error(`${at} figure ${j + 1}: the value must be a token`);
        return { value: paragraph(t.value, own, `${at} figure ${j + 1}`).html, label: paragraph(t.label, own, `${at} figure ${j + 1} label`).html };
      });
      const all = blockSources(b.stats.map((t) => `${t.value} ${t.label}`).join(' '), own);
      out.push({ kind: 'stats', tiles, sources: all, numbers: cites.add(all) });
    } else if ('cards' in b) {
      const cards = b.cards.map((c, j) => {
        const where = `${at} card ${j + 1}`;
        const own = ids(c.sources);
        const all = blockSources(`${c.value ?? ''} ${c.text}`, own);
        return {
          title: plain(c.title, { where: `${where} title`, allow: ALLOW, sources: own }),
          value: c.value ? paragraph(c.value, all, `${where} value`).html : undefined,
          text: paragraph(c.text, all, `${where} text`).html,
          sources: all,
          numbers: cites.add(all),
        };
      });
      out.push({ kind: 'cards', cards });
    } else if ('funds' in b) {
      // each fund's stakes and their sources come from the data; the sentence about the fund from the copy
      const rows = dataset('investors').rows as any[];
      const named = new Set(b.funds.map((f) => f.fund));
      const missing = [...new Set(rows.map((r) => r.fund))].filter((f) => !named.has(f));
      if (missing.length) throw new Error(`${at}: funds with current stakes but no card: ${missing.join(', ')}`);
      const funds = b.funds.map((f, j) => {
        const own = rows.filter((r) => r.fund === f.fund);
        if (!own.length) throw new Error(`${at} fund ${j + 1}: no current stakes for ${f.fund}`);
        const text = paragraph(f.text, ids(f.sources), `${at} fund ${j + 1}`);
        const all = [...new Set([...text.sources, ...own.flatMap((r) => r.sources as string[])])];
        return {
          fund: f.fund,
          type: own[0].fund_type,
          text: text.html,
          stakes: own.map((r) => ({ team: r.team, name: TEAM_NAME[r.team], stake: r.stake, entered: r.entered })),
          sources: all,
          numbers: cites.add(all),
        };
      });
      out.push({ kind: 'funds', funds });
    } else if ('reveal' in b) {
      if (!tokenKeys(b.value).length) throw new Error(`${at}: the value must be a token`);
      const own = ids(b.sources);
      const all = blockSources(`${b.reveal} ${b.value}`, own);
      out.push({ kind: 'reveal', lead: paragraph(b.reveal, all, `${at} lead`).html, value: paragraph(b.value, all, `${at} value`).html, sources: all, numbers: cites.add(all) });
    } else if ('lookup' in b) {
      if (b.lookup !== 'zip') throw new Error(`${at}: unknown lookup ${b.lookup}`);
      const intro = paragraph(b.intro, b.sources ?? [], `${at} intro`, cites);
      out.push({ kind: 'lookup', id: b.lookup, title: plain(b.title, { where: `${at} title`, allow: ALLOW }), intro: intro.html, sources: intro.sources, numbers: intro.numbers });
    } else throw new Error(`${at}: unsupported block`);
  }
  return out;
}

/** The documents a list of blocks cites in its text, in reading order (figures list their own). */
export function textSources(blocks: Prepared[]): string[] {
  const out: string[] = [];
  const add = (ids: string[]) => ids.forEach((id) => !out.includes(id) && out.push(id));
  for (const b of blocks) {
    if (b.kind === 'p' || b.kind === 'quote' || b.kind === 'teams' || b.kind === 'stats' || b.kind === 'reveal' || b.kind === 'lookup') add(b.sources);
    else if (b.kind === 'scrolly') b.steps.forEach((s) => add(s.sources));
    else if (b.kind === 'cards') b.cards.forEach((c) => add(c.sources));
    else if (b.kind === 'funds') b.funds.forEach((f) => add(f.sources));
  }
  return out;
}
