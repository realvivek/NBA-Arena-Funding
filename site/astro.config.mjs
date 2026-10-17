// @ts-check
import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';

// A static site: every page and chart is rendered to HTML and SVG at build time.
export default defineConfig({
  site: 'https://nba-arena-funding.onrender.com',
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'auto' },
  integrations: [svelte()],
  devToolbar: { enabled: false },
});
