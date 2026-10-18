import { describe, expect, it } from 'vitest';
import fs from 'node:fs';
import { parse } from 'yaml';
import { lint, render, plain, typedNumbers, smartQuotes, STATS, SOURCES } from './copy';

const ALLOW: string[] = parse(fs.readFileSync(new URL('../content/allow.yaml', import.meta.url), 'utf8'));
const ctx = (sources: string[] = ['ledger']) => ({ where: 'test', sources, allow: ALLOW });

describe('copy check', () => {
  it('accepts tokens, years and dates with a source', () => {
    expect(lint('Since 2014, the public put {{core_public}} into arenas, as of Oct. 16, 2026.', ctx())).toEqual([]);
  });
  it('rejects typed dollar figures, percentages and numerals', () => {
    expect(lint('The public paid $9.3 billion.', ctx()).join()).toMatch(/dollar figure/);
    expect(lint('About 34 percent was public.', ctx()).join()).toMatch(/numeral "34"/);
    expect(lint('About 34% was public.', ctx()).join()).toMatch(/percentage/);
    expect(lint('Eleven leases end soon.', ctx()).join()).toMatch(/number word/);
    expect(lint('Three arenas opened.', ctx()).join()).toMatch(/number word "Three"/);
  });
  it('requires a source wherever there is a number', () => {
    expect(lint('Since 2014, much changed.', ctx([])).join()).toMatch(/no source/);
    expect(lint('No numbers here.', ctx([]))).toEqual([]);
  });
  it('rejects unknown tokens and sources', () => {
    expect(lint('{{no_such_stat}}', ctx()).join()).toMatch(/unknown number/);
    expect(lint('Text.', ctx(['no-such-source'])).join()).toMatch(/unknown source/);
  });
  it('rejects dashes, tool names and marketing language', () => {
    expect(lint('A deal — a big one.', ctx()).join()).toMatch(/dash/);
    expect(lint('A deal -- a big one.', ctx()).join()).toMatch(/dash/);
    expect(lint('Written with ChatGPT.', ctx()).join()).toMatch(/tool name/);
    expect(lint('A staggering deal.', ctx()).join()).toMatch(/marketing/);
  });
  it('lets names with numerals through only from the allowlist', () => {
    expect(lint('Golden 1 Center opened in 2016.', ctx())).toEqual([]);
    expect(lint('Golden 2 Center opened in 2016.', ctx()).join()).toMatch(/numeral "2"/);
    expect(lint('It is not double counted.', ctx())).toEqual([]);
  });
  it('finds the numbers typed in copy', () => {
    expect(typedNumbers('From 2002 to 2016, and on Oct. 16, 2026, with {{core_public}}.')).toEqual(['Oct. 16, 2026', '2002', '2016']);
  });
});

describe('rendering', () => {
  it('renders tokens with links to the fact check', () => {
    const html = render('Total: {{core_public}}.', ctx());
    expect(html).toContain('href="/fact-check/#core_public"');
    expect(html).toContain(STATS.core_public.display.long);
  });
  it('uses the requested form', () => {
    expect(plain('{{core_public:short}}', ctx())).toBe(STATS.core_public.display.short);
    expect(plain('{{takeover_n:cap}}', ctx())).toBe(STATS.takeover_n.display.cap);
  });
  it('escapes HTML and keeps link targets intact', () => {
    const html = render('A <b> tag and [a link](/fact-check/) with "quotes".', ctx());
    expect(html).toContain('&lt;b&gt;');
    expect(html).toContain('<a href="/fact-check/">a link</a>');
    expect(html).toContain('“quotes”');
  });
  it('curls quotes and apostrophes', () => {
    expect(smartQuotes(`Orlando's "arena" and 'the deal'`)).toBe('Orlando’s “arena” and ‘the deal’');
  });
});

describe('every piece of copy in the content files', () => {
  const read = (f: string) => parse(fs.readFileSync(new URL(`../content/${f}`, import.meta.url), 'utf8'));
  const story = read('story.yaml');
  const pages = read('pages.yaml');
  const figures = read('figures.yaml');
  const items: [string, string, string[]][] = [];
  // every piece of copy in a block: paragraphs, steps, quotes and their bylines, key figures, cards, the funds
  const blockCopy = (where: string, b: any) => {
    const own = b.sources ?? [];
    if (b.p) items.push([where, b.p, own]);
    if (b.reveal) items.push([`${where} reveal`, `${b.reveal} ${b.value}`, own]);
    if (b.h3) items.push([`${where} subhead`, b.h3, own]);
    if (b.quote) items.push([`${where} quote`, b.quote, own], [`${where} byline`, b.by, own]);
    for (const [i, s] of (b.steps ?? []).entries()) items.push([`${where} step ${i + 1}`, s.p, s.sources ?? []]);
    for (const t of b.stats ?? []) items.push([`${where} key figure`, `${t.value} ${t.label}`, own]);
    for (const c of b.cards ?? []) items.push([`${where} card ${c.title}`, `${c.title} ${c.value ?? ''} ${c.text}`, c.sources ?? []]);
    for (const f of b.funds ?? []) items.push([`${where} fund ${f.fund}`, f.text, f.sources ?? []]);
  };
  for (const [id, s] of Object.entries<any>(story)) {
    if (s.nav) items.push([`story ${id} short name`, s.nav, []]);
    s.blocks.forEach((b: any, i: number) => blockCopy(`story ${id} ${i + 1}`, b));
  }
  for (const [id, p] of Object.entries<any>(pages)) {
    for (const k of ['title', 'deck', 'description']) items.push([`page ${id} ${k}`, p[k], p.sources ?? []]);
    for (const [i, f] of (p.findings ?? []).entries()) items.push([`page ${id} finding ${i + 1}`, f.p, f.sources ?? []]);
    for (const t of p.tiles ?? []) items.push([`page ${id} tile`, `${t.value} ${t.label}`, p.sources ?? []]);
    for (const [i, b] of [...(p.blocks ?? []), ...(p.notes ?? [])].entries()) blockCopy(`page ${id} block ${i + 1}`, b);
  }
  for (const [id, f] of Object.entries<any>(figures))
    for (const t of [f.title, f.sub, ...(f.notes ?? [])]) items.push([`figure ${id}`, t, ['ledger', ...(f.sources ?? [])]]);

  it.each(items)('%s passes the copy check', (where, text, sources) => {
    expect(lint(text, { where, sources, allow: ALLOW })).toEqual([]);
  });
  it('cites only known sources', () => {
    for (const [, , sources] of items) for (const s of sources) expect(SOURCES[s], s).toBeDefined();
  });
});
