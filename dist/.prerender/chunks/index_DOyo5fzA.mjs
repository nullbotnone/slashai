import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead, b as addAttribute } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import { g as getCollection } from './_astro_content_DU-8pFiy.mjs';

const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const reviews = (await getCollection("reviews")).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "AI Tool Reviews", "description": "In-depth reviews of AI tools tested on real freelance work." }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero"> <div class="container"> <h1>AI Tool <span class="gradient-text">Reviews</span></h1> <p>Honest, hands-on reviews. We test every tool on real freelance projects so you know what's worth your money.</p> </div> </section> <section class="section-glow"> <div class="container"> <div class="card-grid"> ${reviews.map((post) => renderTemplate`<a${addAttribute(`/reviews/${post.id.replace(/\.md$/, "")}/`, "href")} class="card" style="text-decoration: none; color: inherit;"> <h3>${post.data.title}</h3> <p>${post.data.description}</p> <span class="tag">Rating: ${post.data.rating}/10</span> <span class="tag">${post.data.price}</span> </a>`)} </div> </div> </section> ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/reviews/index.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/reviews/index.astro";
const $$url = "/reviews";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
