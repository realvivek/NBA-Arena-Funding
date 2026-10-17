// @ts-check
import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';

// A static site: every page and chart is rendered to HTML and SVG at build time. Render serves it from the root
// of its domain; the GitHub Pages workflow sets SITE_URL and BASE_PATH to serve it from /NBA-Arena-Funding/.
export default defineConfig({
  site: process.env.SITE_URL || 'https://nba-arena-funding.onrender.com',
  base: process.env.BASE_PATH || '/',
  trailingSlash: 'always',
  build: { format: 'directory', inlineStylesheets: 'auto' },
  integrations: [svelte()],
  devToolbar: { enabled: false },
});
