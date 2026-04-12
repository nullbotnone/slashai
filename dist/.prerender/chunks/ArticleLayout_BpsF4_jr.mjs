import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { m as maybeRenderHead, b as addAttribute, a as renderTemplate, r as renderComponent, e as renderSlot } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import 'clsx';
import { g as getCollection } from './_astro_content_DU-8pFiy.mjs';

const $$RelatedArticles = createComponent(async ($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$RelatedArticles;
  const { currentSlug, currentCollection, tags = [], limit = 3 } = Astro2.props;
  const reviews = await getCollection("reviews");
  const roundups = await getCollection("roundups");
  const comparisons = await getCollection("comparisons");
  const agents = await getCollection("agents");
  const guides = await getCollection("guides");
  const tutorials = await getCollection("tutorials");
  const allPosts = [
    ...reviews.map((p) => ({ ...p, collection: "reviews", type: "Review" })),
    ...roundups.map((p) => ({ ...p, collection: "roundups", type: "Roundup" })),
    ...comparisons.map((p) => ({ ...p, collection: "comparisons", type: "Comparison" })),
    ...agents.map((p) => ({ ...p, collection: "agents", type: "AI Agents" })),
    ...guides.map((p) => ({ ...p, collection: "guides", type: "Guide" })),
    ...tutorials.map((p) => ({ ...p, collection: "tutorials", type: "Tutorial" }))
  ];
  const currentId = `${currentCollection}/${currentSlug}`;
  const scored = allPosts.filter((p) => {
    const postId = `${p.collection}/${p.id.replace(/\.md$/, "")}`;
    return postId !== currentId;
  }).map((p) => {
    const postTags = p.data.tags || [];
    const sharedCount = tags.filter((t) => postTags.includes(t)).length;
    return { ...p, score: sharedCount };
  }).sort((a, b) => b.score - a.score || b.data.pubDate.valueOf() - a.data.pubDate.valueOf()).slice(0, limit);
  if (scored.length === 0) return;
  return renderTemplate`${maybeRenderHead()}<section class="related-articles" data-astro-cid-2zkmu4eg> <h2 data-astro-cid-2zkmu4eg>Related Articles</h2> <div class="card-grid" data-astro-cid-2zkmu4eg> ${scored.map((post) => {
    const slug = post.id.replace(/\.md$/, "");
    const path = `/${post.collection}/${slug}/`;
    return renderTemplate`<a${addAttribute(path, "href")} class="card" style="text-decoration: none; color: inherit;" data-astro-cid-2zkmu4eg> <h3 data-astro-cid-2zkmu4eg>${post.data.title}</h3> <p data-astro-cid-2zkmu4eg>${post.data.description}</p> <span class="tag" data-astro-cid-2zkmu4eg>${post.type}</span> </a>`;
  })} </div> </section>`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/components/RelatedArticles.astro", void 0);

const $$ArticleLayout = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$props, $$slots);
  Astro2.self = $$ArticleLayout;
  const { title, description, pubDate, updatedDate, tags = [], collection = "", slug = "" } = Astro2.props;
  const formattedDate = pubDate.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  });
  const formattedUpdated = updatedDate?.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  });
  return renderTemplate`${renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": title, "description": description }, { "default": ($$result2) => renderTemplate` ${maybeRenderHead()}<article> <header class="article-header section-glow"> <div class="container"> <h1 class="article-title">${title}</h1> <div class="article-meta"> <time${addAttribute(pubDate.toISOString(), "datetime")}>${formattedDate}</time> ${updatedDate && renderTemplate`<span>· Updated ${formattedUpdated}</span>`} ${tags.length > 0 && renderTemplate`<span>· ${tags.join(", ")}</span>`} </div> </div> </header> <section class="section-glow"> <div class="article-content"> ${renderSlot($$result2, $$slots["default"])} <div class="disclosure"> <strong>Affiliate Disclosure:</strong> Some links in this article are affiliate links. If you sign up through them, we may earn a commission at no extra cost to you. We only recommend tools we've personally tested. See our full <a href="/affiliate-disclosure/">Affiliate Disclosure</a>.
</div> ${collection && slug && renderTemplate`${renderComponent($$result2, "RelatedArticles", $$RelatedArticles, { "currentSlug": slug, "currentCollection": collection, "tags": tags })}`} </div> </section> </article> ` })}
/div>`;
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/layouts/ArticleLayout.astro", void 0);

export { $$ArticleLayout as $ };
