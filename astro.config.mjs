// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://slashai.app',
  output: 'static',
  integrations: [sitemap()],
  build: {
    format: 'directory'
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark'
    }
  }
});
