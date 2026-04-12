import rss from '@astrojs/rss';
import { g as getCollection } from './_astro_content_DU-8pFiy.mjs';

async function GET(context) {
  const reviews = await getCollection("reviews");
  const roundups = await getCollection("roundups");
  const comparisons = await getCollection("comparisons");
  const agents = await getCollection("agents");
  const guides = await getCollection("guides");
  const tutorials = await getCollection("tutorials");
  const allPosts = [...reviews, ...roundups, ...comparisons, ...agents, ...guides, ...tutorials].sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  return rss({
    title: "SlashAI — AI Tools for Solopreneurs",
    description: "Honest reviews, practical guides, and real workflows for one-person businesses.",
    site: context.site,
    items: allPosts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/${post.collection}/${post.id}/`
    }))
  });
}

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  GET
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
