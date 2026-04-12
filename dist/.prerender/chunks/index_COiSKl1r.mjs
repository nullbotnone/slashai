import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead, b as addAttribute } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import { g as getCollection } from './_astro_content_DU-8pFiy.mjs';

const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const agents = (await getCollection("agents")).sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "AI Agents", "description": "AI agents that work autonomously for solopreneurs and freelancers." }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero"> <div class="container"> <h1>AI <span class="gradient-text">Agents</span></h1> <p>AI agents that plan, decide, and execute tasks autonomously — your virtual team that works 24/7.</p> </div> </section> <section class="section-glow"> <div class="container"> <div class="card-grid"> ${agents.map((post) => renderTemplate`<a${addAttribute(`/agents/${post.id.replace(/\.md$/, "")}/`, "href")} class="card" style="text-decoration: none; color: inherit;"> <h3>${post.data.title}</h3> <p>${post.data.description}</p> <span class="tag">AI Agents</span> </a>`)} </div> </div> </section> ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/agents/index.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/agents/index.astro";
const $$url = "/agents";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
