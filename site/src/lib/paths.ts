/**
 * Where the site is served from: the root of its domain on Render, /NBA-Arena-Funding/ on GitHub Pages (the Pages
 * workflow sets BASE_PATH at build time). Every link inside the site goes through `sitePath`, so it works under either.
 */
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

/** A path inside the site ('/arenas/#orl'), under the base the site is served from. */
export function sitePath(path: string): string {
  if (!path.startsWith('/')) throw new Error(`sitePath: not a path inside the site: ${path}`);
  return BASE + path;
}
