import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead, b as addAttribute, F as Fragment } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import { t as toolsData } from './tools_BGqMe1Zc.mjs';

function getStaticPaths() {
  return toolsData.map((tool) => ({
    params: { slug: tool.slug },
    props: { tool }
  }));
}
const $$slug = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$slug;
  const { tool } = Astro2.props;
  const relatedTools = toolsData.filter((t) => t.category === tool.category && t.slug !== tool.slug).slice(0, 3);
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": `${tool.name} Review`, "description": tool.description, "data-astro-cid-hof4g4vy": true }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero" data-astro-cid-hof4g4vy> <div class="container" data-astro-cid-hof4g4vy> <h1 data-astro-cid-hof4g4vy>${tool.name}</h1> <p data-astro-cid-hof4g4vy>${tool.description}</p> </div> </section> <section class="section-glow" data-astro-cid-hof4g4vy> <div class="article-content" data-astro-cid-hof4g4vy> <!-- Quick Info --> <div class="tool-info-grid" data-astro-cid-hof4g4vy> <div class="tool-info-card" data-astro-cid-hof4g4vy> <span class="info-label" data-astro-cid-hof4g4vy>Category</span> <span class="info-value" data-astro-cid-hof4g4vy>${tool.category}</span> </div> <div class="tool-info-card" data-astro-cid-hof4g4vy> <span class="info-label" data-astro-cid-hof4g4vy>Pricing</span> <span class="info-value" data-astro-cid-hof4g4vy>${tool.price}</span> </div> <div class="tool-info-card" data-astro-cid-hof4g4vy> <span class="info-label" data-astro-cid-hof4g4vy>Released</span> <span class="info-value" data-astro-cid-hof4g4vy>${tool.released}</span> </div> ${tool.affiliateCommission && renderTemplate`<div class="tool-info-card" data-astro-cid-hof4g4vy> <span class="info-label" data-astro-cid-hof4g4vy>Affiliate</span> <span class="info-value" data-astro-cid-hof4g4vy>${tool.affiliateCommission}</span> </div>`} </div> <!-- Visit Button --> <div style="text-align: center; margin: 2rem 0;" data-astro-cid-hof4g4vy> <a${addAttribute(tool.affiliateUrl || tool.url, "href")} target="_blank" rel="noopener" class="tool-cta" data-astro-cid-hof4g4vy>
Visit ${tool.name} →
</a> </div> <!-- About --> <h2 data-astro-cid-hof4g4vy>About ${tool.name}</h2> <p data-astro-cid-hof4g4vy>${tool.longDescription}</p> <h2 data-astro-cid-hof4g4vy>Pros & Cons</h2> <div class="pros-cons" data-astro-cid-hof4g4vy> <div class="pros" data-astro-cid-hof4g4vy> <h3 data-astro-cid-hof4g4vy>✅ Pros</h3> <ul data-astro-cid-hof4g4vy> ${tool.pros.map((pro) => renderTemplate`<li data-astro-cid-hof4g4vy>${pro}</li>`)} </ul> </div> <div class="cons" data-astro-cid-hof4g4vy> <h3 data-astro-cid-hof4g4vy>❌ Cons</h3> <ul data-astro-cid-hof4g4vy> ${tool.cons.map((con) => renderTemplate`<li data-astro-cid-hof4g4vy>${con}</li>`)} </ul> </div> </div> <h2 data-astro-cid-hof4g4vy>Best For</h2> <blockquote data-astro-cid-hof4g4vy>${tool.bestFor}</blockquote> <h2 data-astro-cid-hof4g4vy>Tags</h2> <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 2rem;" data-astro-cid-hof4g4vy> ${tool.tags.map((tag) => renderTemplate`<span class="tool-tag" data-astro-cid-hof4g4vy>${tag}</span>`)} </div> <!-- Related Tools --> ${relatedTools.length > 0 && renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-hof4g4vy": true }, { "default": ($$result3) => renderTemplate` <h2 data-astro-cid-hof4g4vy>More in ${tool.category}</h2> <div class="card-grid" data-astro-cid-hof4g4vy> ${relatedTools.map((rt) => renderTemplate`<a${addAttribute(`/tools/${rt.slug}/`, "href")} class="card" style="text-decoration: none; color: inherit;" data-astro-cid-hof4g4vy> <h3 data-astro-cid-hof4g4vy>${rt.name}</h3> <p data-astro-cid-hof4g4vy>${rt.description}</p> <span class="tag" data-astro-cid-hof4g4vy>${rt.price}</span> </a>`)} </div> ` })}`} <div class="disclosure" data-astro-cid-hof4g4vy> <strong data-astro-cid-hof4g4vy>Affiliate Disclosure:</strong> Some links may be affiliate links. We earn a commission at no extra cost to you if you sign up. See our <a href="/affiliate-disclosure/" data-astro-cid-hof4g4vy>Affiliate Disclosure</a>.
</div> </div> </section> ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/tools/[slug].astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/tools/[slug].astro";
const $$url = "/tools/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  getStaticPaths,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
