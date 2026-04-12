import { c as createComponent } from './astro-component_CM5sHQaA.mjs';
import 'piccolore';
import { a as renderTemplate, r as renderComponent, m as maybeRenderHead, b as addAttribute } from './prerender_DGualgz_.mjs';
import { $ as $$BaseLayout } from './BaseLayout_rjQaa7Nu.mjs';
import { g as getCollection } from './_astro_content_DU-8pFiy.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Index = createComponent(async ($$result, $$props, $$slots) => {
  const reviews = await getCollection("reviews");
  const roundups = await getCollection("roundups");
  const comparisons = await getCollection("comparisons");
  const agents = await getCollection("agents");
  const guides = await getCollection("guides");
  const tutorials = await getCollection("tutorials");
  const allPosts = [
    ...reviews.map((p) => ({ ...p, type: "Review", typeClass: "review" })),
    ...roundups.map((p) => ({ ...p, type: "Roundup", typeClass: "roundup" })),
    ...comparisons.map((p) => ({ ...p, type: "Comparison", typeClass: "comparison" })),
    ...agents.map((p) => ({ ...p, type: "AI Agents", typeClass: "agents" })),
    ...guides.map((p) => ({ ...p, type: "Guide", typeClass: "guide" })),
    ...tutorials.map((p) => ({ ...p, type: "Tutorial", typeClass: "tutorial" }))
  ].sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  const categories = [
    { name: "All", value: "" },
    { name: "Reviews", value: "reviews" },
    { name: "Roundups", value: "roundups" },
    { name: "Comparisons", value: "comparisons" },
    { name: "AI Agents", value: "agents" },
    { name: "Tutorials", value: "tutorials" },
    { name: "Guides", value: "guides" }
  ];
  return renderTemplate(_a || (_a = __template(["", "  <script>\n  const filterBtns = document.querySelectorAll('.filter-btn');\n  const blogGrid = document.getElementById('blog-grid');\n  const noResults = document.getElementById('no-results');\n  const searchInput = document.getElementById('blog-search');\n  let activeFilter = '';\n\n  function filterBlog() {\n    const search = searchInput.value.toLowerCase();\n    const cards = blogGrid.querySelectorAll('.blog-card');\n    let visible = 0;\n\n    cards.forEach(card => {\n      const matchesFilter = !activeFilter || card.dataset.collection === activeFilter;\n      const matchesSearch = !search || card.dataset.title.includes(search) || card.dataset.desc.includes(search);\n      \n      if (matchesFilter && matchesSearch) {\n        card.classList.remove('hidden');\n        visible++;\n      } else {\n        card.classList.add('hidden');\n      }\n    });\n\n    noResults.style.display = visible === 0 ? 'block' : 'none';\n  }\n\n  filterBtns.forEach(btn => {\n    btn.addEventListener('click', () => {\n      filterBtns.forEach(b => b.classList.remove('active'));\n      btn.classList.add('active');\n      activeFilter = btn.dataset.filter;\n      filterBlog();\n    });\n  });\n\n  searchInput.addEventListener('input', filterBlog);\n<\/script>"])), renderComponent($$result, "BaseLayout", $$BaseLayout, { "title": "Blog", "description": "AI tool reviews, comparisons, roundups, and workflow guides for solopreneurs and freelancers.", "data-astro-cid-5tznm7mj": true }, { "default": async ($$result2) => renderTemplate` ${maybeRenderHead()}<section class="hero" data-astro-cid-5tznm7mj> <div class="container" data-astro-cid-5tznm7mj> <h1 data-astro-cid-5tznm7mj>The <span class="gradient-text" data-astro-cid-5tznm7mj>Blog</span></h1> <p data-astro-cid-5tznm7mj>Reviews, comparisons, roundups, and guides. ${allPosts.length} articles and growing.</p> </div> </section> <section class="section-glow" data-astro-cid-5tznm7mj> <div class="container" data-astro-cid-5tznm7mj> <!-- Search --> <input type="text" id="blog-search" placeholder="🔍 Search articles..." class="blog-search" data-astro-cid-5tznm7mj> <!-- Category Filter --> <div class="blog-filters" data-astro-cid-5tznm7mj> ${categories.map((cat) => renderTemplate`<button${addAttribute(`filter-btn ${cat.value === "" ? "active" : ""}`, "class")}${addAttribute(cat.value, "data-filter")} data-astro-cid-5tznm7mj> ${cat.name} </button>`)} </div> <!-- Articles Grid --> <div class="blog-grid" id="blog-grid" data-astro-cid-5tznm7mj> ${allPosts.map((post) => {
    const slug = post.id.replace(/\.md$/, "");
    const path = `/${post.collection}/${slug}/`;
    return renderTemplate`<a${addAttribute(path, "href")} class="blog-card"${addAttribute(post.collection, "data-collection")}${addAttribute(post.data.title.toLowerCase(), "data-title")}${addAttribute(post.data.description.toLowerCase(), "data-desc")} data-astro-cid-5tznm7mj> <div class="blog-card-meta" data-astro-cid-5tznm7mj> <span${addAttribute(`type-badge ${post.typeClass}`, "class")} data-astro-cid-5tznm7mj>${post.type}</span> <time${addAttribute(post.data.pubDate.toISOString(), "datetime")} data-astro-cid-5tznm7mj> ${post.data.pubDate.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })} </time> </div> <h3 data-astro-cid-5tznm7mj>${post.data.title}</h3> <p data-astro-cid-5tznm7mj>${post.data.description}</p> </a>`;
  })} </div> <p class="no-results" id="no-results" style="display: none; text-align: center; color: var(--color-text-secondary); padding: 3rem 0;" data-astro-cid-5tznm7mj>
No articles in this category yet.
</p> </div> </section> ` }));
}, "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/blog/index.astro", void 0);

const $$file = "/home/rpi/.openclaw/workspace/projects/slashai/slashai/src/pages/blog/index.astro";
const $$url = "/blog";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$Index,
  file: $$file,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
