import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const reviews = await getCollection('reviews');
  const roundups = await getCollection('roundups');
  const comparisons = await getCollection('comparisons');
  const guides = await getCollection('guides');

  const allPosts = [...reviews, ...roundups, ...comparisons, ...guides]
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  return rss({
    title: 'SlashAI — AI Tools for Solopreneurs',
    description: 'Honest reviews, practical guides, and real workflows for one-person businesses.',
    site: context.site!,
    items: allPosts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/${post.collection}/${post.slug}/`,
    })),
  });
}
