import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead, b as addAttribute } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import { g as getCollection } from './_astro_content_DU-8pFiy.mjs';
import { t as toolsData } from './tools_BGqMe1Zc.mjs';

const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const allReviews = await getCollection("reviews");
  const allRoundups = await getCollection("roundups");
  const allComparisons = await getCollection("comparisons");
  const allAgents = await getCollection("agents");
  const recentPosts = [...allReviews, ...allRoundups, ...allComparisons, ...allAgents].sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()).slice(0, 6);
  const trendingTools = toolsData.filter((t) => t.featured).slice(0, 6);
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "AI Tools for Solopreneurs & Freelancers", "data-astro-cid-j7pv25f6": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero" data-astro-cid-j7pv25f6> <div class="container" data-astro-cid-j7pv25f6> <h1 data-astro-cid-j7pv25f6>AI tools that <span class="gradient-text" data-astro-cid-j7pv25f6>actually work</span><br data-astro-cid-j7pv25f6>for one-person businesses</h1> <p data-astro-cid-j7pv25f6>Honest reviews, practical guides, and real workflows. We test every tool so you don't have to waste time on ones that don't deliver.</p> </div> </section>  <section class="section-glow" data-astro-cid-j7pv25f6> <div class="container" data-astro-cid-j7pv25f6> <div class="section-header" data-astro-cid-j7pv25f6> <h2 data-astro-cid-j7pv25f6>Trending <span class="gradient-text" data-astro-cid-j7pv25f6>AI Tools</span></h2> <a href="/ai-tools/" class="see-all" data-astro-cid-j7pv25f6>See all ${toolsData.length} tools →</a> </div> <div class="trending-grid" data-astro-cid-j7pv25f6> ${trendingTools.map((tool) => renderTemplate`<a${addAttribute(`/tools/${tool.slug}/`, "href")} class="trending-card" data-astro-cid-j7pv25f6> <div class="trending-card-top" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>${tool.name}</h3> <span${addAttribute(`pricing-badge ${tool.pricing.toLowerCase()}`, "class")} data-astro-cid-j7pv25f6>${tool.pricing}</span> </div> <p data-astro-cid-j7pv25f6>${tool.description}</p> <span class="trending-category" data-astro-cid-j7pv25f6>${tool.category}</span> </a>`)} </div> </div> </section>  <section class="section-glow" data-astro-cid-j7pv25f6> <div class="container" data-astro-cid-j7pv25f6> <h2 style="margin-bottom: 1rem; font-size: 1.3rem;" data-astro-cid-j7pv25f6>Latest Articles</h2> <div class="card-grid" data-astro-cid-j7pv25f6> ${recentPosts.map((post) => {
    const slug = post.id.replace(/\.md$/, "");
    const collection = post.collection;
    const path = `/${collection}/${slug}/`;
    const tag = collection === "reviews" ? "Review" : collection === "roundups" ? "Roundup" : collection === "comparisons" ? "Comparison" : collection === "agents" ? "AI Agents" : "Guide";
    return renderTemplate`<a${addAttribute(path, "href")} class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>${post.data.title}</h3> <p data-astro-cid-j7pv25f6>${post.data.description}</p> <span class="tag" data-astro-cid-j7pv25f6>${tag}</span> </a>`;
  })} </div> </div> </section>  <section class="section-glow" data-astro-cid-j7pv25f6> <div class="container" data-astro-cid-j7pv25f6> <h2 style="margin-bottom: 1rem; font-size: 1.3rem;" data-astro-cid-j7pv25f6>Browse by Category</h2> <div class="card-grid" data-astro-cid-j7pv25f6> <a href="/ai-tools/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>🛠️ AI Tools Database</h3> <p data-astro-cid-j7pv25f6>45+ curated tools & agents with pricing, features, and direct links. Filter by category and find your perfect stack.</p> </a> <a href="/blog/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>📝 Blog</h3> <p data-astro-cid-j7pv25f6>Reviews, comparisons, roundups, and workflow guides. Honest takes tested on real freelance work.</p> </a> <a href="/agents/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>🤖 AI Agents</h3> <p data-astro-cid-j7pv25f6>Autonomous agents that handle email, research, customer support, and workflows while you sleep.</p> </a> <a href="/roundups/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>📊 Best-Of Roundups</h3> <p data-astro-cid-j7pv25f6>Curated lists of the best AI tools for every freelancer need — writing, design, productivity, and more.</p> </a> <a href="/build-your-stack/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>🧩 Build Your Stack</h3> <p data-astro-cid-j7pv25f6>Pick your role and budget — get a personalized AI toolkit recommended for your business.</p> </a> <a href="/compare/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>⚖️ Compare Tools</h3> <p data-astro-cid-j7pv25f6>Pick two AI tools and see how they stack up — pricing, features, pros, cons, side by side.</p> </a> <a href="/tutorials/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>📚 Tutorials</h3> <p data-astro-cid-j7pv25f6>Step-by-step guides to set up and use AI tools. Practical, tested, beginner-friendly.</p> </a> <a href="/guides/" class="card" style="text-decoration: none; color: inherit;" data-astro-cid-j7pv25f6> <h3 data-astro-cid-j7pv25f6>🗺️ Workflow Guides</h3> <p data-astro-cid-j7pv25f6>AI-powered workflows that save hours every week. Real setups you can copy today.</p> </a> </div> </div> </section> <section class="section-glow" style="margin-top: 1rem; text-align: center;" data-astro-cid-j7pv25f6> <div class="container" style="padding: 2rem 1.5rem;" data-astro-cid-j7pv25f6> <h2 style="font-size: 1.5rem; margin-bottom: 0.75rem;" data-astro-cid-j7pv25f6>The Slash<span style="background: linear-gradient(135deg, var(--color-accent), #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;" data-astro-cid-j7pv25f6>AI</span> Stack</h2> <p style="color: var(--color-text-secondary); max-width: 500px; margin: 0 auto 1.5rem;" data-astro-cid-j7pv25f6>Start free. Upgrade when revenue justifies it. Every tool we recommend is tested on real freelance work.</p> <a href="/roundups/best-ai-tools-freelancers/" style="display: inline-block; background: linear-gradient(135deg, var(--color-accent), #ec4899); color: white; padding: 0.75rem 2rem; border-radius: 50px; font-weight: 600; transition: all 0.3s; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);" data-astro-cid-j7pv25f6>
See the Stack →
</a> </div></section> ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/index.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/index.astro";
const $$url = "";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
