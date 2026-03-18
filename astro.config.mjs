// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://slashai.app',
  output: 'static',
  build: {
    format: 'directory'
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark'
    }
  }
});
