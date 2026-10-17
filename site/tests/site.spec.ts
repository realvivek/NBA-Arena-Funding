import { test, expect, type Page } from '@playwright/test';

const PAGES = ['/', '/arenas/', '/taxes/', '/tax-breaks/', '/threats/', '/leases/', '/households/', '/sources/', '/fact-check/'];

async function visit(page: Page, path: string) {
  const external: string[] = [];
  const errors: string[] = [];
  page.on('request', (r) => {
    const u = new URL(r.url());
    if (u.hostname !== '127.0.0.1' && u.protocol !== 'data:') external.push(r.url());
  });
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  const res = await page.goto(path, { waitUntil: 'networkidle' });
  return { res, external, errors };
}

for (const path of PAGES) {
  test.describe(path, () => {
    test('loads with no errors and no requests to other sites', async ({ page }) => {
      const { res, external, errors } = await visit(page, path);
      expect(res?.status()).toBe(200);
      expect(external).toEqual([]);
      expect(errors).toEqual([]);
    });

    test('has one h1 and no skipped heading levels', async ({ page }) => {
      await page.goto(path);
      const levels = await page.$$eval('main h1, main h2, main h3, main h4, main h5, main h6', (hs) => hs.map((h) => Number(h.tagName[1])));
      expect(levels.filter((l) => l === 1)).toHaveLength(1);
      for (let i = 1; i < levels.length; i++) expect(levels[i] - levels[i - 1], `heading after h${levels[i - 1]}`).toBeLessThanOrEqual(1);
    });

    test('has no em dashes in the copy', async ({ page }) => {
      await page.goto(path);
      const text = await page.locator('main').innerText();
      expect(text).not.toContain('—');
    });

    test('fits a 360px phone with no sideways scrolling, and chart text is at least 11px', async ({ browser }) => {
      const ctx = await browser.newContext({ viewport: { width: 360, height: 800 } });
      const page = await ctx.newPage();
      await page.goto(path);
      const [scroll, inner] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
      expect(scroll).toBeLessThanOrEqual(inner);
      const smallest = await page.evaluate(() => {
        let min = Infinity;
        for (const svg of Array.from(document.querySelectorAll<SVGSVGElement>('figure.chart svg'))) {
          const box = svg.getBoundingClientRect();
          if (!box.width || !svg.viewBox.baseVal || !svg.viewBox.baseVal.width) continue; // hidden layout
          const scale = box.width / svg.viewBox.baseVal.width;
          for (const t of Array.from(svg.querySelectorAll('text'))) {
            if (!t.textContent?.trim()) continue;
            min = Math.min(min, parseFloat(getComputedStyle(t).fontSize) * scale);
          }
        }
        return min;
      });
      if (smallest !== Infinity) expect(smallest).toBeGreaterThanOrEqual(11);
      await ctx.close();
    });

    test('works without JavaScript', async ({ browser }) => {
      const ctx = await browser.newContext({ javaScriptEnabled: false });
      const page = await ctx.newPage();
      await page.goto(path);
      await expect(page.locator('h1')).toBeVisible();
      const charts = await page.locator('figure.chart').count();
      if (charts) {
        await expect(page.locator('figure.chart .v-wide svg').first()).toBeVisible();
        expect(await page.locator('figure.chart details.data table').count()).toBe(charts);
      }
      await ctx.close();
    });
  });
}

test('every number in the copy links to its fact-check entry', async ({ page }) => {
  await page.goto('/fact-check/');
  const ids = new Set(await page.$$eval('tr[id]', (rows) => rows.map((r) => r.id)));
  for (const path of PAGES) {
    await page.goto(path);
    const keys = await page.$$eval('a.num', (as) => as.map((a) => new URL((a as HTMLAnchorElement).href).hash.slice(1)));
    for (const k of keys) expect(ids.has(k), `${path}: ${k}`).toBe(true);
  }
});

test('the story renders its headline, key figures and every chart', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('h1')).toHaveText("Taxpayers Are Now Paying to Rebuild the NBA’s Arenas");
  await expect(page.locator('.tile')).toHaveCount(3);
  for (const id of ['rebuild', 'arenas', 'map', 'takeovers', 'whopays', 'households', 'uc', 'ongoing', 'threats', 'leases'])
    await expect(page.locator(`#fig-${id}`)).toHaveCount(1);
});
