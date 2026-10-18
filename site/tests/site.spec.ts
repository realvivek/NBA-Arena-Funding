import { test, expect, type Page } from '@playwright/test';

const PAGES = ['/', '/who-is-behind/', '/arenas/', '/taxes/', '/tax-breaks/', '/threats/', '/leases/', '/households/', '/sources/', '/fact-check/'];

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
  await expect(page.locator('h1')).toHaveText('Taxpayers Paid for the NBA’s Arenas. Owners Kept the Gains.');
  await expect(page.locator('.findings li')).toHaveCount(6);
  for (const href of await page.$$eval('.findings a.go', (as) => as.map((a) => a.getAttribute('href') ?? '')))
    await expect(page.locator(href), href).toHaveCount(1);
  for (const id of ['ball', 'rebuild', 'whopays', 'households', 'trend', 'values', 'owners', 'leases'])
    await expect(page.locator(`#fig-${id}`)).toHaveCount(1);
});

test('the lead graphic follows the steps as the reader scrolls', async ({ browser }) => {
  for (const viewport of [{ width: 1280, height: 800 }, { width: 390, height: 844 }]) {
    const ctx = await browser.newContext({ viewport });
    const page = await ctx.newPage();
    await page.goto('/');
    const fig = page.locator('figure.scrolly');
    const steps = await fig.locator('.step').evaluateAll((els) => els.map((e) => (e as HTMLElement).dataset.step ?? ''));
    expect(steps.length).toBeGreaterThan(1);
    for (const s of steps) {
      await fig.locator(`.step[data-step="${s}"]`).evaluate((e) => e.scrollIntoView({ block: 'center' }));
      await expect(fig, `${viewport.width}px, step ${s}`).toHaveAttribute('data-step', s);
    }
    await ctx.close();
  }
});

test('the team list sorts and opens each team\'s record', async ({ page }) => {
  await page.goto('/');
  const rows = page.locator('.teams-list > li');
  await expect(rows).toHaveCount(30);
  await expect(page.locator('.teams-sort')).toBeVisible();
  await page.locator('.teams-sort button', { hasText: 'A to Z' }).click();
  await expect(rows.first()).toHaveAttribute('data-name', 'Atlanta Hawks');
  await expect(rows.first().locator('.tm-rank')).toHaveText('1');
  await page.locator('.teams-sort button', { hasText: 'Team value' }).click();
  await expect(rows.first()).toHaveAttribute('data-name', 'Golden State Warriors');
  await rows.first().locator('summary').click();
  await expect(rows.first().locator('.tm-body')).toBeVisible();
  await expect(rows.first().locator('.tm-body dt')).toHaveCount(await rows.first().locator('.tm-body dd').count());
});

test('without JavaScript the lead graphic shows its last step and the team list keeps its order', async ({ browser }) => {
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto('/');
  const fig = page.locator('figure.scrolly');
  const last = await fig.locator('.step').last().getAttribute('data-step');
  await expect(fig).toHaveAttribute('data-step', last ?? '');
  await expect(page.locator('.teams-sort')).toBeHidden();
  await expect(page.locator('.teams-list > li')).toHaveCount(30);
  await expect(page.locator('.teams-list > li').first()).toHaveAttribute('data-name', 'Brooklyn Nets');
  await ctx.close();
});
