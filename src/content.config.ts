import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const reviews = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/reviews' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().default('SlashAI'),
    tags: z.array(z.string()).default([]),
    affiliate: z.boolean().default(true),
    productName: z.string(),
    rating: z.number().min(1).max(10),
    price: z.string(),
    verdict: z.string(),
  }),
});

const roundups = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/roundups' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().default('SlashAI'),
    tags: z.array(z.string()).default([]),
    affiliate: z.boolean().default(true),
    itemCount: z.number(),
  }),
});

const comparisons = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/comparisons' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().default('SlashAI'),
    tags: z.array(z.string()).default([]),
    affiliate: z.boolean().default(true),
    productA: z.string(),
    productB: z.string(),
    winner: z.string().optional(),
  }),
});

const agents = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/agents' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().default('SlashAI'),
    tags: z.array(z.string()).default([]),
    affiliate: z.boolean().default(true),
    itemCount: z.number().optional(),
  }),
});

const guides = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().default('SlashAI'),
    tags: z.array(z.string()).default([]),
    affiliate: z.boolean().default(true),
  }),
});

const tutorials = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/tutorials' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    author: z.string().default('SlashAI'),
    tags: z.array(z.string()).default([]),
    toolName: z.string(),
    difficulty: z.enum(['Beginner', 'Intermediate', 'Advanced']).default('Beginner'),
    timeToComplete: z.string().optional(),
  }),
});

export const collections = {
  reviews,
  roundups,
  comparisons,
  agents,
  guides,
  tutorials,
};
