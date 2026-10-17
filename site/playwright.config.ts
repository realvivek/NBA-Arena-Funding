import { defineConfig, devices } from '@playwright/test';

// Runs against the built site (npm run build first). CHROMIUM_PATH points at a preinstalled browser when the
// one Playwright would download is not available.
const executablePath = process.env.CHROMIUM_PATH || undefined;

export default defineConfig({
  testDir: 'tests',
  fullyParallel: true,
  reporter: 'list',
  use: { baseURL: 'http://127.0.0.1:4321', launchOptions: { executablePath } },
  webServer: { command: 'npx astro preview --host 127.0.0.1 --port 4321 --ignore-lock', url: 'http://127.0.0.1:4321/', reuseExistingServer: true, timeout: 60_000 },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'], launchOptions: { executablePath } } }],
});
