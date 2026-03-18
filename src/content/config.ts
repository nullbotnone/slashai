import { z, defineCollection } from 'astro:content';

const articleSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.date(),
  updatedDate: z.date().optional(),
  author: z.string().default('SlashAI'),
  image: z.string().optional(),
  tags: z.array(z.string()).default([]),
  affiliate: z.boolean().default(true),
});

const reviews = defineCollection({
  type: 'content',
  schema: articleSchema.extend({
    productName: z.string(),
    rating: z.number().min(1).max(10),
    price: z.string(),
    verdict: z.string(),
  }),
});

const roundups = defineCollection({
  type: 'content',
  schema: articleSchema.extend({
    itemCount: z.number(),
  }),
});

const comparisons = defineCollection({
  type: 'content',
  schema: articleSchema.extend({
    productA: z.string(),
    productB: z.string(),
    winner: z.string().optional(),
  }),
});

const guides = defineCollection({
  type: 'content',
  schema: articleSchema,
});

export const collections = {
  reviews,
  roundups,
  comparisons,
  guides,
};
