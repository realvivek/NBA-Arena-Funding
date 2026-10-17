/**
 * Copy rules and rendering. Every paragraph, heading, chart title and note on the site goes through here.
 *
 * Numbers in the copy are tokens: {{key}} renders the stat's prose form, {{key:short}}, {{key:title}} and
 * {{key:cap}} the other forms (see pipeline/fmt.py). The lint fails the build when the copy:
 * - types a dollar figure, a percentage, a number word or any numeral other than a year or a date,
 *   instead of using a token (names that contain numerals are listed in src/content/allow.yaml);
 * - has a numeral or token in a block that cites no source;
 * - uses an unknown token or source id;
 * - uses an em dash, an en dash or a double hyphen, a tool name, or marketing language.
 */
import stats from '../generated/stats.json';
import sources from '../generated/sources.json';

export type Variant = 'long' | 'short' | 'title' | 'cap';
export interface Stat {
  key: string;
  title: string;
  value: number;
  unit: string;
  basis: string;
  digits: number | null;
  label: string;
  sources: string[];
  display: Record<Variant, string>;
  note: string;
  method: string;
}
export interface Source {
  id: string;
  url: string;
  title: string;
  title_from: string;
  publisher: string;
  origin: 'government' | 'court' | 'team_or_league' | 'independent';
  date: string;
  checked: string;
  review?: string;
}

export const STATS = stats as unknown as Record<string, Stat>;
export const SOURCES: Record<string, Source> = Object.fromEntries((sources as Source[]).map((s) => [s.id, s]));

const TOKEN = /\{\{\s*([a-z][a-z0-9_]*)(?::(long|short|title|cap))?\s*\}\}/g;
const MONTH = '(?:Jan\\.|Feb\\.|March|April|May|June|July|Aug\\.|Sept\\.|Oct\\.|Nov\\.|Dec\\.)';
const DATE = new RegExp(`${MONTH} \\d{1,2}, (?:19|20)\\d\\d`, 'g');
const YEAR_RANGE = /\b(?:19|20)\d\d-(?:19|20)?\d\d\b/g;
const YEAR = /\b(?:19|20)\d\d\b/g;
const NUMBER_WORDS =
  /\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundreds?|thousands?|millions?|billions?|dozens?|half|halves|twice|double[ds]?|triple[ds]?|quadrupled?)\b/i;
const TOOL_NAMES = /\b(claude|anthropic|chatgpt|openai|gpt-?\d|llm|copilot|gemini|ai-generated|artificial intelligence)\b/i;
const MARKETING =
  /\b(shocking|staggering|stunning|jaw-dropping|unprecedented|groundbreaking|game-changing|massive|whopping|eye-popping|explosive|bombshell|incredible|amazing)\b/i;

export interface Context {
  where: string;
  sources?: string[];
  allow?: string[];
}

/** Stat keys used in a piece of copy, in order. */
export function tokenKeys(text: string): string[] {
  return [...text.matchAll(TOKEN)].map((m) => m[1]);
}

/** Every source a block cites: its own, then each token's. */
export function blockSources(text: string, own: string[] = []): string[] {
  const out = [...own];
  for (const key of tokenKeys(text)) for (const id of STATS[key]?.sources ?? []) if (!out.includes(id)) out.push(id);
  return out;
}

/** The numerals a reader sees in a block that were typed rather than computed: years and dates. */
export function typedNumbers(text: string, allow: string[] = []): string[] {
  let t = text.replace(TOKEN, ' ');
  for (const a of allow) t = t.split(a).join(' ');
  const found: string[] = [];
  t = t.replace(DATE, (m) => (found.push(m), ' '));
  t = t.replace(YEAR_RANGE, (m) => (found.push(m), ' '));
  t.replace(YEAR, (m) => (found.push(m), m));
  return found;
}

/** Problems with a piece of copy; an empty list means it passes. */
export function lint(text: string, ctx: Context): string[] {
  const where = ctx.where;
  const problems: string[] = [];
  const allow = ctx.allow ?? [];
  for (const key of tokenKeys(text)) if (!STATS[key]) problems.push(`${where}: unknown number {{${key}}}`);
  for (const id of ctx.sources ?? []) if (!SOURCES[id]) problems.push(`${where}: unknown source id ${id}`);
  if (/[—–]|--/.test(text)) problems.push(`${where}: em dash, en dash or double hyphen`);
  if (TOOL_NAMES.test(text)) problems.push(`${where}: tool name in the copy`);
  const mk = text.match(MARKETING);
  if (mk) problems.push(`${where}: marketing language ("${mk[0]}")`);

  let t = text.replace(TOKEN, ' ');
  for (const a of allow) t = t.split(a).join(' ');
  t = t.replace(/\]\([^)]*\)/g, '] '); // link targets are not copy
  t = t.replace(/double[- ]count\w*/gi, ' '); // counting a dollar twice is not a quantity
  if (t.includes('$')) problems.push(`${where}: a dollar figure typed in the copy; use a token`);
  if (t.includes('%')) problems.push(`${where}: a percentage typed in the copy; use a token`);
  const nw = t.match(NUMBER_WORDS);
  if (nw) problems.push(`${where}: number word "${nw[0]}"; use a token`);
  t = t.replace(DATE, ' ').replace(YEAR_RANGE, ' ').replace(YEAR, ' ');
  const stray = t.match(/\d[\d,.]*/);
  if (stray) problems.push(`${where}: numeral "${stray[0]}" typed in the copy; use a token`);

  const hasNumbers = tokenKeys(text).length > 0 || typedNumbers(text, allow).length > 0;
  if (hasNumbers && blockSources(text, ctx.sources).length === 0) problems.push(`${where}: numbers with no source`);
  return problems;
}

export function assertClean(text: string, ctx: Context): void {
  const problems = lint(text, ctx);
  if (problems.length) throw new Error('Copy check failed:\n  ' + problems.join('\n  '));
}

export function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/** Typographer's quotes and apostrophes, for copy only (never for data or URLs). */
export function smartQuotes(s: string): string {
  return s
    .replace(/(^|[\s(\[\u2014])"/g, '$1\u201c')
    .replace(/"/g, '\u201d')
    .replace(/(\w)'(\w)/g, '$1\u2019$2')
    .replace(/(^|[\s(\[])'/g, '$1\u2018')
    .replace(/'/g, '\u2019');
}

/** Inline markup: *italic*, **bold**, [text](href). Everything else is escaped. */
function inline(s: string): string {
  let h = escapeHtml(s);
  h = h.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_m, txt, href) => {
    const ext = /^https?:/.test(href);
    return `<a href="${href}"${ext ? ' rel="noopener"' : ''}>${txt}</a>`;
  });
  h = h.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  h = h.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  return h;
}

/**
 * Copy to HTML. Tokens become their display form; with link=true each links to its fact-check entry.
 * Lints first, so a page cannot render copy that breaks the rules.
 */
export function render(text: string, ctx: Context & { link?: boolean }): string {
  assertClean(text, ctx);
  const marks: string[] = [];
  const withMarks = text.replace(TOKEN, (_m, key: string, variant: Variant = 'long') => {
    const s = STATS[key];
    const shown = escapeHtml(s.display[variant]);
    const html =
      ctx.link === false
        ? `<span class="num">${shown}</span>`
        : `<a class="num" href="/fact-check/#${key}" title="${escapeHtml(s.title)}">${shown}</a>`;
    marks.push(html);
    return `\u0000${marks.length - 1}\u0000`;
  });
  // quotes are curled before escaping; link targets are protected first
  const links: string[] = [];
  const protectedText = withMarks.replace(/\]\(([^)\s]+)\)/g, (_m, href) => (links.push(href), `](\u0001${links.length - 1}\u0001)`));
  const curled = smartQuotes(protectedText).replace(/\u0001(\d+)\u0001/g, (_m, i) => links[Number(i)]);
  return inline(curled).replace(/\u0000(\d+)\u0000/g, (_m, i) => marks[Number(i)]);
}

/** Plain text (for <title>, meta descriptions and aria labels). */
export function plain(text: string, ctx: Context): string {
  assertClean(text, ctx);
  return smartQuotes(text)
    .replace(TOKEN, (_m, key: string, variant: Variant = 'long') => STATS[key].display[variant])
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/\*+/g, '');
}

export function stat(key: string): Stat {
  const s = STATS[key];
  if (!s) throw new Error(`unknown stat ${key}`);
  return s;
}
