import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';

const $$404 = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Page Not Found", "description": "The page you're looking for doesn't exist.", "data-astro-cid-zetdm5md": true }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero" data-astro-cid-zetdm5md> <div class="container" data-astro-cid-zetdm5md> <h1 class="error-code" data-astro-cid-zetdm5md>404</h1> <p data-astro-cid-zetdm5md>That page doesn't exist — or it got automated away by an AI agent.</p> </div> </section> <section class="section-glow" data-astro-cid-zetdm5md> <div class="article-content" style="text-align: center;" data-astro-cid-zetdm5md> <p data-astro-cid-zetdm5md>Here are some places that <em data-astro-cid-zetdm5md>do</em> exist:</p> <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin: 2rem 0;" data-astro-cid-zetdm5md> <a href="/" class="card" style="text-decoration: none; color: inherit; display: inline-block; padding: 1rem 1.5rem;" data-astro-cid-zetdm5md> <h3 data-astro-cid-zetdm5md>🏠 Home</h3> </a> <a href="/ai-tools/" class="card" style="text-decoration: none; color: inherit; display: inline-block; padding: 1rem 1.5rem;" data-astro-cid-zetdm5md> <h3 data-astro-cid-zetdm5md>🛠️ AI Tools</h3> </a> <a href="/blog/" class="card" style="text-decoration: none; color: inherit; display: inline-block; padding: 1rem 1.5rem;" data-astro-cid-zetdm5md> <h3 data-astro-cid-zetdm5md>📝 Blog</h3> </a> <a href="/roundups/best-ai-tools-freelancers/" class="card" style="text-decoration: none; color: inherit; display: inline-block; padding: 1rem 1.5rem;" data-astro-cid-zetdm5md> <h3 data-astro-cid-zetdm5md>📊 Best AI Tools</h3> </a> </div> </div></section> ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/404.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/404.astro";
const $$url = "/404";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$404,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
