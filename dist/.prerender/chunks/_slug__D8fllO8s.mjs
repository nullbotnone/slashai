import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate, m as maybeRenderHead, b as addAttribute, F as Fragment } from './prerender_DGualgz_.mjs';
import { g as getCollection, r as renderEntry } from './_astro_content_DU-8pFiy.mjs';
import { $ as $$ArticleLayout } from './ArticleLayout_BpsF4_jr.mjs';
import { t as toolsData } from './tools_BGqMe1Zc.mjs';

async function getStaticPaths() {
  const tutorials = await getCollection("tutorials");
  return tutorials.map((post) => ({
    params: { slug: post.id.replace(/\.md$/, "") },
    props: { post }
  }));
}
const $$slug = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$slug;
  const { post } = Astro2.props;
  const { Content } = await renderEntry(post);
  const slug = post.id.replace(/\.md$/, "");
  const tool = toolsData.find((t) => t.name.toLowerCase() === post.data.toolName.toLowerCase() || t.slug === post.data.toolName.toLowerCase().replace(/\s+/g, "-"));
  return renderTemplate`${renderComponent($$result, "ArticleLayout", $$ArticleLayout, { "title": post.data.title, "description": post.data.description, "pubDate": post.data.pubDate, "updatedDate": post.data.updatedDate, "tags": post.data.tags, "collection": "tutorials", "slug": slug, "data-astro-cid-amgwr4wo": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<div class="tutorial-meta-box" data-astro-cid-amgwr4wo> <div class="tutorial-meta-item" data-astro-cid-amgwr4wo> <span class="meta-label" data-astro-cid-amgwr4wo>Tool</span> <span class="meta-value" data-astro-cid-amgwr4wo>${post.data.toolName}</span> </div> <div class="tutorial-meta-item" data-astro-cid-amgwr4wo> <span class="meta-label" data-astro-cid-amgwr4wo>Difficulty</span> <span class="meta-value" data-astro-cid-amgwr4wo>${post.data.difficulty}</span> </div> ${post.data.timeToComplete && renderTemplate`<div class="tutorial-meta-item" data-astro-cid-amgwr4wo> <span class="meta-label" data-astro-cid-amgwr4wo>Time</span> <span class="meta-value" data-astro-cid-amgwr4wo>⏱️ ${post.data.timeToComplete}</span> </div>`} </div> ${tool && renderTemplate`<div class="tool-links-box" data-astro-cid-amgwr4wo> <strong data-astro-cid-amgwr4wo>📚 ${post.data.toolName} Links:</strong> <a${addAttribute(tool.affiliateUrl || tool.url, "href")} target="_blank" rel="noopener" data-astro-cid-amgwr4wo>Website</a> <span class="link-sep" data-astro-cid-amgwr4wo>·</span> <a${addAttribute(`/tools/${tool.slug}/`, "href")} data-astro-cid-amgwr4wo>Our Review</a> ${(() => {
    const docsUrls = {
      "n8n": "https://docs.n8n.io/",
      "openclaw": "https://docs.openclaw.ai/"
    };
    const docsUrl = docsUrls[tool.slug] || `${tool.url}/docs`;
    return renderTemplate`${renderComponent($$result2, "Fragment", Fragment, { "data-astro-cid-amgwr4wo": true }, { "default": async ($$result3) => renderTemplate`<span class="link-sep" data-astro-cid-amgwr4wo>·</span><a${addAttribute(docsUrl, "href")} target="_blank" rel="noopener" data-astro-cid-amgwr4wo>Docs</a>` })}`;
  })()} </div>`}${renderComponent($$result2, "Content", Content, { "data-astro-cid-amgwr4wo": true })} ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/tutorials/[slug].astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/tutorials/[slug].astro";
const $$url = "/tutorials/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  getStaticPaths,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
