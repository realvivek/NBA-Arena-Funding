// Checks the built site (dist/) for links that would break where it is served: every link inside the site must
// start with the base path (BASE_PATH, '/' by default) and lead to a page that exists, with the anchor it names.
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, relative } from 'node:path';

const DIST = new URL('../dist/', import.meta.url).pathname;
const BASE = (process.env.BASE_PATH || '/').replace(/\/?$/, '/');
const pages = [];
(function walk(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) walk(p);
    else if (e.name.endsWith('.html')) pages.push(p);
  }
})(DIST);

const ids = new Map();
const idsOf = (file) => {
  if (!ids.has(file)) ids.set(file, new Set([...readFileSync(file, 'utf8').matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
  return ids.get(file);
};
const problems = [];
let checked = 0;
for (const page of pages) {
  const html = readFileSync(page, 'utf8');
  const here = relative(DIST, page);
  for (const [, attr, url] of html.matchAll(/\s(href|src)="(\/[^"]*)"/g)) {
    if (url.startsWith('//')) continue;
    checked++;
    if (!url.startsWith(BASE)) {
      problems.push(`${here}: ${attr}="${url}" is outside ${BASE}`);
      continue;
    }
    const [path, hash] = url.slice(BASE.length).split('#');
    const file = join(DIST, decodeURIComponent(path), path === '' || path.endsWith('/') ? 'index.html' : '');
    if (!existsSync(file)) problems.push(`${here}: ${url} has no page`);
    else if (hash && file.endsWith('.html') && !idsOf(file).has(decodeURIComponent(hash))) problems.push(`${here}: ${url} has no anchor`);
  }
  for (const [, hash] of html.matchAll(/\shref="#([^"]+)"/g)) {
    checked++;
    if (!idsOf(page).has(decodeURIComponent(hash))) problems.push(`${here}: #${hash} has no anchor`);
  }
}
if (problems.length) {
  console.error(problems.slice(0, 40).join('\n'));
  console.error(`${problems.length} broken links`);
  process.exit(1);
}
console.log(`${checked} links in ${pages.length} pages, all under ${BASE} and all found`);
