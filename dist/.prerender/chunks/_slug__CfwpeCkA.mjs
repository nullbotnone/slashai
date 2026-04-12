import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { r as renderComponent, a as renderTemplate } from './prerender_DGualgz_.mjs';
import { g as getCollection, r as renderEntry } from './_astro_content_DU-8pFiy.mjs';
import { $ as $$ArticleLayout } from './ArticleLayout_BpsF4_jr.mjs';

async function getStaticPaths() {
  const agents = await getCollection("agents");
  return agents.map((post) => ({
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
  return renderTemplate`${renderComponent($$result, "ArticleLayout", $$ArticleLayout, { "title": post.data.title, "description": post.data.description, "pubDate": post.data.pubDate, "updatedDate": post.data.updatedDate, "tags": post.data.tags, "collection": "agents", "slug": slug }, { "default": async ($$result2) => renderTemplate` ${renderComponent($$result2, "Content", Content, {})} ` })}`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/agents/[slug].astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/agents/[slug].astro";
const $$url = "/agents/[slug]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$slug,
  file: $$file,
  getStaticPaths,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
