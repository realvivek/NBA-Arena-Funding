/**
 * Shared sizes and helpers for the charts. Each chart is drawn twice at build time: a wide layout (680 units,
 * shown from 640px up) and a narrow one (340 units, shown below that). Text is at least 13 units in both, so it
 * stays at 11px or more at every screen width the layout is shown at.
 */
export const WIDE = 680;
export const NARROW = 340;
export const FONT = 13;
export const FONT_SMALL = 13;
export type Variant = 'wide' | 'narrow';

// Approximate advance widths for Libre Franklin, in em, for laying out labels without a browser. Its figures are
// proportional: the one is narrow, the others wide.
const NARROW_CH = /[ijlt.,:;'|!()[\] ]/;
const WIDE_CH = /[MWmw@%]/;
export function textWidth(s: string, size = FONT, weight = 400): number {
  let em = 0;
  for (const ch of s) {
    if (NARROW_CH.test(ch)) em += 0.3;
    else if (WIDE_CH.test(ch)) em += 0.85;
    else if (/[A-Z]/.test(ch)) em += 0.66;
    else if (ch === '1') em += 0.47;
    else if (/[0-9]/.test(ch)) em += 0.69;
    else if (ch === '$') em += 0.6;
    else em += 0.53;
  }
  return em * size * (weight >= 600 ? 1.05 : 1);
}

/** Money in millions, compact, for labels: $0, $250M, $1.04B. Matches the stats' short form. */
export function money(m: number, digits?: number): string {
  if (m === 0) return '$0';
  if (Math.abs(m) >= 1000) return `$${(m / 1000).toFixed(digits ?? 2)}B`;
  if (Math.abs(m) >= 10) return `$${Math.round(m).toLocaleString('en-US')}M`;
  return `$${m.toFixed(digits ?? 1)}M`;
}

/** Axis tick money: no unnecessary decimals. */
export function moneyTick(m: number): string {
  if (m === 0) return '$0';
  if (Math.abs(m) >= 1000) {
    const b = m / 1000;
    return `$${Number.isInteger(b) ? b : b.toFixed(1)}B`;
  }
  return `$${Math.round(m)}M`;
}

export function dollars(v: number): string {
  return '$' + Math.round(v).toLocaleString('en-US');
}

export function pct(v: number, digits = 0): string {
  return `${v.toFixed(digits)}%`;
}

/** A bar with a 4px rounded data end and a square base: horizontal bars grow right, columns grow up. */
export function hbar(x0: number, x1: number, y: number, h: number, r = 4): string {
  const w = x1 - x0;
  if (w <= 0) return '';
  const rr = Math.min(r, w, h / 2);
  return `M${x0},${y}H${x1 - rr}Q${x1},${y} ${x1},${y + rr}V${y + h - rr}Q${x1},${y + h} ${x1 - rr},${y + h}H${x0}Z`;
}
export function vbar(x: number, w: number, y0: number, y1: number, r = 4): string {
  const h = y0 - y1;
  if (h <= 0) return '';
  const rr = Math.min(r, h, w / 2);
  return `M${x},${y0}V${y1 + rr}Q${x},${y1} ${x + rr},${y1}H${x + w - rr}Q${x + w},${y1} ${x + w},${y1 + rr}V${y0}Z`;
}

export const TEAM_CITY: Record<string, string> = {
  ATL: 'Atlanta', BOS: 'Boston', BKN: 'Brooklyn', CHA: 'Charlotte', CHI: 'Chicago', CLE: 'Cleveland', DAL: 'Dallas',
  DEN: 'Denver', DET: 'Detroit', GSW: 'San Francisco', HOU: 'Houston', IND: 'Indianapolis', LAC: 'Inglewood',
  LAL: 'Los Angeles', MEM: 'Memphis', MIA: 'Miami', MIL: 'Milwaukee', MIN: 'Minneapolis', NOP: 'New Orleans',
  NYK: 'New York', OKC: 'Oklahoma City', ORL: 'Orlando', PHI: 'Philadelphia', PHX: 'Phoenix', POR: 'Portland',
  SAC: 'Sacramento', SAS: 'San Antonio', TOR: 'Toronto', UTA: 'Salt Lake City', WAS: 'Washington',
};

/** Each team's full name (its market, not its arena's city: the Clippers play in Inglewood). */
export const TEAM_NAME: Record<string, string> = {
  ATL: 'Atlanta Hawks', BOS: 'Boston Celtics', BKN: 'Brooklyn Nets', CHA: 'Charlotte Hornets', CHI: 'Chicago Bulls',
  CLE: 'Cleveland Cavaliers', DAL: 'Dallas Mavericks', DEN: 'Denver Nuggets', DET: 'Detroit Pistons',
  GSW: 'Golden State Warriors', HOU: 'Houston Rockets', IND: 'Indiana Pacers', LAC: 'Los Angeles Clippers',
  LAL: 'Los Angeles Lakers', MEM: 'Memphis Grizzlies', MIA: 'Miami Heat', MIL: 'Milwaukee Bucks',
  MIN: 'Minnesota Timberwolves', NOP: 'New Orleans Pelicans', NYK: 'New York Knicks', OKC: 'Oklahoma City Thunder',
  ORL: 'Orlando Magic', PHI: 'Philadelphia 76ers', PHX: 'Phoenix Suns', POR: 'Portland Trail Blazers',
  SAC: 'Sacramento Kings', SAS: 'San Antonio Spurs', TOR: 'Toronto Raptors', UTA: 'Utah Jazz', WAS: 'Washington Wizards',
};
